# !/usr/bin/env python
import rospy
import numpy as np
from sensor_msgs.msg import Image
from stereo_msgs.msg import DisparityImage
# from flyt_python import api
from geometry_msgs.msg import TwistStamped
import cv2
from cv_bridge import CvBridge, CvBridgeError
import math
import time


flag = True
bridge1 = CvBridge()

def left_callback(image_a):
	left_arr = bridge1.imgmsg_to_cv2(image_a, desired_encoding="bgr8")	
	cv2.rectangle(left_arr,(c,a),(d,b),(0,0,255),1)
	cv2.putText(left_arr,"Min. Distance",(c+40,a+40), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255,0,0),2)
	cv2.putText(left_arr,str(front_d),(c+40,a+55), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255,0,0),2)
	cv2.imshow("left_r", left_arr)
	if cv2.waitKey(1) and 0xFF == ord('q'):
		pass

bridge = CvBridge()
def callback(data):
	global front_arr, a, b, c, d, front_d
	if(flag):	
		image_arr = bridge.imgmsg_to_cv2(data.image, desired_encoding="8UC1") # Converts the depth image into a 640 X 480 grid
		
		focal = data.f
		base = data.T
		image_arr[image_arr==0] = 1;
		#image_arr[image_arr>40] = 1;
		depth_arr = focal*base/image_arr
		# Removes all zeroes from the data
		#depth_arr[depth_arr<0.6] = 50;		
		
		a = 130; b = 260; c = 200; d = 440
		front_arr = depth_arr[a:b, c:d]
		front_d = np.min(front_arr);
		f_count = (front_arr==front_d).sum()
		k = 1;
		while front_d > 0.75:
			if f_count > 50:
				front_arr = depth_arr[130:260, 200:440]
				print "Towards goal!: ", front_d, f_count
				time.sleep(3)
				return
			im_arr = focal*base/front_d
			front_d = focal*base/(im_arr-k)
			k = k+1;
			f_count = (front_arr==front_d).sum()

	
		l = 1;
		for i in range(-50,50):
			for j in range(-50,50):
				a = 130+i; b = 260+i; c = 200+j; d = 440+j
				front_arr = depth_arr[a:b, c:d]
				front_d = np.min(front_arr)
				f_count = (front_arr==front_d).sum()
				print "Searching...", front_d, f_count
				while front_d > 0.75:
					if f_count > 50:
						a = 130+i; b = 260+i; c = 200+j; d = 440+j
						print "Moving", front_d, f_count
						time.sleep(3)
						return
					im_arr = focal*base/front_d
					front_d = focal*base/(im_arr-l)
					l = l+1;
					f_count = (front_arr==front_d).sum()

		
		m =1;
		for i in range(0,270):
			for j in range(0,400):
				a = i; b = 130+i; c = j; d = 240+j
				front_arr = depth_arr[a:b, c:d]
				front_d = np.min(front_arr)
				f_count = (front_arr==front_d).sum()
				print "Again Searching...", front_d, f_count
				while front_d > 0.75:
					if f_count > 50:
						print "Again Moving", front_d, f_count
						a = i; b = 130+i; c = j; d = 240+j
						time.sleep(3)
						return
					im_arr = focal*base/front_d
					front_d = focal*base/(im_arr-m)
					m = m+1;
					f_count = (front_arr==front_d).sum()

	
		print "Hold!"
		# flag = False	


# Listener function to subscribe to ros topics
def listener():
	rospy.init_node('listener', anonymous=True)
	rospy.Subscriber("/my_stereo/disparity", DisparityImage, callback)
	rospy.Subscriber("/my_stereo/left/image_rect_color", Image, left_callback)
	rospy.spin()


if __name__ == '__main__':
	listener()	
	
