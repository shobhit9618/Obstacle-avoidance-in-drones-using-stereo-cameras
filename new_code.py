# !/usr/bin/env python
from __future__ import division
import rospy
import numpy as np
import array
from stereo_msgs.msg import DisparityImage
from sensor_msgs.msg import Image
import cv2
from cv_bridge import CvBridge, CvBridgeError


flag = True
depth_arr = []
count = 1;
bridge1 = CvBridge()

def left_callback(image_a):
	left_arr = bridge1.imgmsg_to_cv2(image_a, desired_encoding="mono8")	
	cv2.rectangle(left_arr,(15,25),(200,150),(0,0,255),1)
	cv2.imshow("left", left_arr)
	if cv2.waitKey(1) and 0xFF == ord('q'):
		pass

bridge = CvBridge()


def callback(data):
	global flag, count
	if(flag):
		depth = np.fromstring(data.image.data, np.uint8)
		
		img_arr = bridge.imgmsg_to_cv2(data.image, desired_encoding="8UC1")
		#cv2.imshow("1", img_arr)
		#cv2.waitKey()

		focal = data.f
		base = data.T
	
		depth_arr = focal*base/img_arr
		#cv2.imshow("1", img_arr);
		# Splits the depth array into 5 grids		
		forward_arr = depth_arr[130:260, 200:440]
		left_arr = depth_arr[130:260, 0:200]
		right_arr = depth_arr[130:260, 440:640]
		top_arr = depth_arr[0:130, 200:440]
		bottom_arr = depth_arr[260:400, 200:440]

		# Find the minimum depth in each grid
		forward_d = np.min(forward_arr)
		left_d = np.min(left_arr)
		right_d = np.min(right_arr)
		top_d = np.min(top_arr)
		bottom_d = np.min(bottom_arr)

		# Counts number of instances of minimum depth in each grid to remove noise in data
		f_count = (forward_arr==forward_d).sum()
		l_count = (left_arr==left_d).sum()
		r_count = (right_arr==right_d).sum()
		t_count = (top_arr==top_d).sum()
		b_count = (bottom_arr==bottom_d).sum()

		n = 25;
		if (forward_d > 1.0) and (f_count>n):
			print "Forward: " ,forward_d, left_d, right_d, top_d, bottom_d
		elif ((left_d-right_d)>0) and (l_count>n) and (r_count>n):
			print "Left: " ,forward_d, left_d, right_d, top_d, bottom_d
		elif ((right_d-left_d)>0) and (r_count>n) and (l_count>n):
			print "Right: " ,forward_d,left_d, right_d, top_d, bottom_d
		elif ((top_d-bottom_d)>0) and (t_count>n) and (b_count>n):
			print "Top: " ,forward_d, left_d, right_d, top_d, bottom_d
		else:
			print "Hold: " ,forward_d, left_d, right_d,top_d,bottom_d
		count = count + 1;


		
		
def listener():
	rospy.init_node('listener', anonymous=True)
	rospy.Subscriber("/my_stereo/disparity", DisparityImage, callback)
	rospy.Subscriber("/my_stereo/left/image_rect_color", Image, left_callback)
	rospy.spin()

if __name__ == '__main__':
	listener()	
