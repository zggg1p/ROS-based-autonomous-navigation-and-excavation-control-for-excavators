#!/usr/bin/env python
#coding=utf-8
 
import rospy
from gazebo_msgs.srv import *
 
rospy.init_node('p_robot_env')
rospy.wait_for_service('/gazebo/set_model_state')
 
set_state_service = rospy.ServiceProxy('/gazebo/set_model_state', SetModelState)
objstate = SetModelStateRequest()  # Create an object of type SetModelStateRequest
 
# set red cube pose
objstate.model_state.model_name = "blue_cube"
objstate.model_state.pose.position.x = 0.5
objstate.model_state.pose.position.y = 0.5
objstate.model_state.pose.position.z = 0.5
objstate.model_state.pose.orientation.w = 1
objstate.model_state.pose.orientation.x = 0
objstate.model_state.pose.orientation.y = 0
objstate.model_state.pose.orientation.z = 0
objstate.model_state.twist.linear.x = 0.0
objstate.model_state.twist.linear.y = 0.0
objstate.model_state.twist.linear.z = 0.0
objstate.model_state.twist.angular.x = 0.0
objstate.model_state.twist.angular.y = 0.0
objstate.model_state.twist.angular.z = 0.0
objstate.model_state.reference_frame = "world"
 
result = set_state_service(objstate)
