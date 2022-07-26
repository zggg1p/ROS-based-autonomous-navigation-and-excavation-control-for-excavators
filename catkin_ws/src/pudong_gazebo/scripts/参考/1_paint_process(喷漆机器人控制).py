#!/usr/bin/env python
#-*- coding:utf-8   -*-
 

import rospy, sys
import tf
import math
import cmd
from std_msgs.msg import Float64 
from geometry_msgs.msg import Twist
# move_base规划所需库
import actionlib
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from geometry_msgs.msg import PoseWithCovarianceStamped
from actionlib_msgs.msg import *
# moveit规划所需库
import moveit_commander
from moveit_commander import MoveGroupCommander
from geometry_msgs.msg import Pose
from copy import deepcopy

# Nav point position
point0 = [(1.500,-2.000,0.000),(0.000,0.000,0.000)]
point1 = [(1.500,-4.000,0.000),(0.000,0.000,0.000)]
# Topics
UPPER_CMD_TOPIC  = '/elfin5/upper_link_position_controller/command'
TOPIC_BASE_PLANAR = '/cmd_vel'
# Default move speed
DEFAULT_SPEED_LIN = 1.0
DEFAULT_SPEED_ANG = 1.0


### Navigation function ###
def goal_pose(pose):
    goal_pose=MoveBaseGoal()
    goal_pose.target_pose.header.frame_id="map"
    goal_pose.target_pose.pose.position.x=pose[0][0]
    goal_pose.target_pose.pose.position.y=pose[0][1]
    goal_pose.target_pose.pose.position.z=pose[0][2]

    x,y,z,w=tf.transformations.quaternion_from_euler(pose[1][0],pose[1][1],pose[1][2])
 
    goal_pose.target_pose.pose.orientation.x=x
    goal_pose.target_pose.pose.orientation.y=y
    goal_pose.target_pose.pose.orientation.z=z
    goal_pose.target_pose.pose.orientation.w=w
    return goal_pose

### Move functions ###
def get_twist(length_x, length_y, angle_z):
    msg = Twist()
    if length_x != 0:
	msg.linear.x = ( length_x / math.fabs(length_x) ) * DEFAULT_SPEED_LIN
    else:
	msg.linear.x = 0

    if length_y != 0:
	msg.linear.y = ( length_y / math.fabs(length_y) ) * DEFAULT_SPEED_LIN
    else:
	msg.linear.y = 0

    if angle_z != 0:
	msg.angular.z = ( angle_z / math.fabs(angle_z) ) * DEFAULT_SPEED_ANG
    else:
	msg.angular.z = 0
    rospy.loginfo("Twist now is ("+str(msg.linear.x)+str(msg.linear.y)+str(msg.angular.z)+")")
    return msg

def get_duration(length, speed):
    return float(math.fabs(length / speed))

def move_dipan(pub, msg, duration):
    pub.publish(msg)
    rospy.sleep(duration)
    msg_init = get_twist(0.0, 0.0, 0.0) 
    pub.publish(msg_init)



class PaintProcess():

    def __init__(self):
        # 初始化ROS节点
        rospy.init_node('paint_process', anonymous=True)
        # 初始化参数
        self.pub_upper = rospy.Publisher(UPPER_CMD_TOPIC, Float64, queue_size=10)
        self.pub_cmd = rospy.Publisher(TOPIC_BASE_PLANAR, Twist, queue_size=10)
	self.height = 0

    # Base move command
    def move_command(self, length_x, length_y, angle_z):
	msg = get_twist(length_x, length_y, angle_z)
	if length_x != 0:
	    duration = get_duration(length_x, DEFAULT_SPEED_LIN)
	    rospy.loginfo("duration is length_x / DEFAULT_SPEED_LIN = " + str(duration) + " s")
	elif length_y != 0:
	    duration = get_duration(length_y, DEFAULT_SPEED_LIN)
	    rospy.loginfo("duration is length_y / DEFAULT_SPEED_LIN = " + str(duration) + " s")
	else:
	    duration = get_duration(angle_z, DEFAULT_SPEED_ANG)
	    rospy.loginfo("duration is angle_z / DEFAULT_SPEED_LIN = " + str(duration) + " s")

	move_dipan(self.pub_cmd, msg, duration)

    # Navigation command
    def nav_to_point(self, pose):
        #创建MoveBaseAction client
        client = actionlib.SimpleActionClient('move_base',MoveBaseAction)
        #等待MoveBaseAction server启动
        client.wait_for_server()
        #开始导航
        #try:  
        rospy.sleep(1)
        goal = goal_pose(pose)
        client.send_goal(goal)
        client.wait_for_result()
        rospy.sleep(2)
        rospy.loginfo("Nav to point1 finished.")

    # Upper command
    def up_to_height(self, height):
	self.height = height
	self.pub_upper.publish(self.height)
        rospy.loginfo("Up to height = " + str(self.height) + " m")

    def go_initial_pose1(self, pose, height):

	self.pub_upper.publish(height)

	moveit_commander.roscpp_initialize(sys.argv)
        cartesian = rospy.get_param('~cartesian', True)
        arm = MoveGroupCommander('elfin_arm')
        arm.allow_replanning(True)
        arm.set_pose_reference_frame('base_link')
        arm.set_goal_position_tolerance(0.01)
        arm.set_goal_orientation_tolerance(0.01)
        arm.set_max_acceleration_scaling_factor(0.5)
        arm.set_max_velocity_scaling_factor(0.5)
        end_effector_link = arm.get_end_effector_link()
        # 控制机械臂到第一喷漆位置
        arm.set_named_target(pose)
        arm.go()
        rospy.sleep(1)
    def go_initial_pose2(self, pose, height):
	moveit_commander.roscpp_initialize(sys.argv)
        cartesian = rospy.get_param('~cartesian', True)
        arm = MoveGroupCommander('elfin_arm')
        arm.allow_replanning(True)
        arm.set_pose_reference_frame('base_link')
        arm.set_goal_position_tolerance(0.01)
        arm.set_goal_orientation_tolerance(0.01)
        arm.set_max_acceleration_scaling_factor(0.5)
        arm.set_max_velocity_scaling_factor(0.5)
        end_effector_link = arm.get_end_effector_link()
        # 控制机械臂到第一喷漆位置
        arm.set_named_target(pose)
        arm.go()
        rospy.sleep(1)

	self.pub_upper.publish(height)

    def arm_cartesian_move_up(self, pose1, pose2):
        # 初始化move_group的API
        moveit_commander.roscpp_initialize(sys.argv)

        cartesian = rospy.get_param('~cartesian', True)
        arm = MoveGroupCommander('elfin_arm')
        arm.allow_replanning(True)
        arm.set_pose_reference_frame('base_link')
        arm.set_goal_position_tolerance(0.01)
        arm.set_goal_orientation_tolerance(0.01)
        arm.set_max_acceleration_scaling_factor(0.5)
        arm.set_max_velocity_scaling_factor(0.5)
        end_effector_link = arm.get_end_effector_link()

        # 控制机械臂到第一喷漆位置
        arm.set_named_target(pose1)
        arm.go()
        rospy.sleep(1)

        # 获取当前位姿数据最为机械臂运动的起始位姿
        start_pose = arm.get_current_pose(end_effector_link).pose
                
        # 初始化路点列表
        waypoints = []
        #拷贝对象
        wpose = deepcopy(start_pose)

        #process 1
        wpose.position.x += 1.0

        if cartesian:  
            waypoints.append(deepcopy(wpose))
        else:        
            arm.set_pose_target(wpose) 
            arm.go()
            rospy.sleep(2)

        #process 2
        wpose.position.z -= 0.2
 
        if cartesian:
            waypoints.append(deepcopy(wpose))
        else:
            arm.set_pose_target(wpose)
            arm.go()
            rospy.sleep(2)

        #process 3
        wpose.position.x -= 1.0

        if cartesian:  
            waypoints.append(deepcopy(wpose))
        else:        
            arm.set_pose_target(wpose) 
            arm.go()
            rospy.sleep(2)


        #规划过程
        if cartesian:
		fraction = 0.0  
		maxtries = 200 
		attempts = 0  

		arm.set_start_state_to_current_state()

		while fraction < 1.0 and attempts < maxtries:

		    (plan, fraction) = arm.compute_cartesian_path (
		                            waypoints,   
		                            0.01,       
		                            0.0,        
		                            True)       
		    
		    attempts += 1
		    # 打印运动规划进程
		    if attempts % 10 == 0:
		        rospy.loginfo("Still trying after " + str(attempts) + " attempts...")
		             
		# 如果路径规划成功（覆盖率100%）,则开始控制机械臂运动
		if fraction == 1.0:
		    rospy.loginfo("Path computed successfully. Moving the arm.")
		    arm.execute(plan)
		    rospy.loginfo("Path execution complete.")
		# 如果路径规划失败，则打印失败信息
		else:
		    rospy.loginfo("Path planning failed with only " + str(fraction) + " success after " + str(maxtries) + " attempts.")  

		rospy.sleep(1)

        # 控制机械臂先回到初始化位置
        arm.set_named_target(pose2)
        arm.go()
        rospy.sleep(1)
        
        arm.set_named_target(pose2)
        arm.go()
        rospy.sleep(1)

    def arm_cartesian_move_down(self, pose1, pose2):
        # 初始化move_group的API
        moveit_commander.roscpp_initialize(sys.argv)

        cartesian = rospy.get_param('~cartesian', True)
        arm = MoveGroupCommander('elfin_arm')
        arm.allow_replanning(True)
        arm.set_pose_reference_frame('base_link')
        arm.set_goal_position_tolerance(0.01)
        arm.set_goal_orientation_tolerance(0.01)
        arm.set_max_acceleration_scaling_factor(0.5)
        arm.set_max_velocity_scaling_factor(0.5)
        end_effector_link = arm.get_end_effector_link()

        # 控制机械臂到第一喷漆位置
        arm.set_named_target('paint_pose5')
        arm.go()
        rospy.sleep(1)

        # 获取当前位姿数据最为机械臂运动的起始位姿
        start_pose = arm.get_current_pose(end_effector_link).pose
                
        # 初始化路点列表
        waypoints = []
        #拷贝对象
        wpose = deepcopy(start_pose)

        #process 1
        wpose.position.x += 1.0
 
        if cartesian:
            waypoints.append(deepcopy(wpose))
        else:
            arm.set_pose_target(wpose)
            arm.go()
            rospy.sleep(2)

        #process 2
        wpose.position.x -= 1.0

        if cartesian:  
            waypoints.append(deepcopy(wpose))
        else:        
            arm.set_pose_target(wpose) 
            arm.go()
            rospy.sleep(2)


        #规划过程
        if cartesian:
		fraction = 0.0  
		maxtries = 200 
		attempts = 0  

		arm.set_start_state_to_current_state()

		while fraction < 1.0 and attempts < maxtries:

		    (plan, fraction) = arm.compute_cartesian_path (
		                            waypoints,   
		                            0.01,       
		                            0.0,        
		                            True)       
		    
		    attempts += 1
		    # 打印运动规划进程
		    if attempts % 10 == 0:
		        rospy.loginfo("Still trying after " + str(attempts) + " attempts...")
		             
		# 如果路径规划成功（覆盖率100%）,则开始控制机械臂运动
		if fraction == 1.0:
		    rospy.loginfo("Path computed successfully. Moving the arm.")
		    arm.execute(plan)
		    rospy.loginfo("Path execution complete.")
		# 如果路径规划失败，则打印失败信息
		else:
		    rospy.loginfo("Path planning failed with only " + str(fraction) + " success after " + str(maxtries) + " attempts.")  

		rospy.sleep(1)

        # 控制机械臂先回到初始化位置
        arm.set_named_target(pose2)
        arm.go()
        rospy.sleep(1)
        
        arm.set_named_target(pose2)
        arm.go()
        rospy.sleep(1)


if __name__ == '__main__':

    pp = PaintProcess()

    ### Navigation ###
    pp.up_to_height(0.0)
    rospy.sleep(1)
    pp.nav_to_point(point0)
    rospy.sleep(1)
    pp.nav_to_point(point1)
    rospy.sleep(1)

    pp.move_command(0.0, 0.0, 0.0)
    rospy.sleep(1)

    pp.move_command(0.0, 0.0, -2.70)    
    rospy.sleep(1)

    pp.move_command(-0.2, 0.0, 0.0)
    rospy.sleep(2)

    pp.move_command(0.0, 0.4, 0.0)
    rospy.sleep(2)


    ### Paint process ###
    #pp.up_to_height(1.2)
    #rospy.sleep(1)
    pp.go_initial_pose2('paint_pose1', 1.2)
    rospy.sleep(1)
    pp.arm_cartesian_move_up('paint_pose1','paint_pose1')
    rospy.sleep(1)
    pp.up_to_height(0.8)
    rospy.sleep(1)
    pp.arm_cartesian_move_up('paint_pose1','paint_pose1')
    rospy.sleep(1)
    pp.up_to_height(0.4)
    rospy.sleep(1)
    pp.arm_cartesian_move_up('paint_pose1','paint_pose1')
    rospy.sleep(1)
    pp.up_to_height(0.0)
    rospy.sleep(1)
    pp.arm_cartesian_move_up('paint_pose1','home')
    rospy.sleep(1)
    # End of the front process
    # Start down process
    pp.move_command(0.0, -0.4, 0.0)
    rospy.sleep(1)
    pp.go_initial_pose1('paint_pose5', 0.4)
    rospy.sleep(1)
    pp.move_command(0.0, 0.4, 0.0)
    rospy.sleep(1)
    pp.arm_cartesian_move_down('paint_pose5','paint_pose5')
    rospy.sleep(1)
    pp.up_to_height(0.2)
    rospy.sleep(1)
    pp.arm_cartesian_move_down('paint_pose5','paint_pose5')
    rospy.sleep(1)
    pp.move_command(0.0, -0.4, 0.0)
    rospy.sleep(1)
    pp.go_initial_pose2('home', 0.0)
    rospy.sleep(1)
    # End of the paint position 1
