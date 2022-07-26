#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy, sys
import tf
import math
import cmd
from std_msgs.msg import Float64
from geometry_msgs.msg import Twist
import csv

# move_base
import actionlib
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from geometry_msgs.msg import PoseWithCovarianceStamped
from actionlib_msgs.msg import *

# moveit_group
import moveit_commander
from moveit_commander import MoveGroupCommander
from geometry_msgs.msg import Pose
from copy import deepcopy

# Topics
TOPIC_BASE_PLANAR = '/cmd_vel'

PI = 3.14159265

# Default move speed
DEFAULT_SPEED_LIN = 1.5
DEFAULT_SPEED_ANG = 0.05
point1 = [(11.1700, 3.1, 0.393328), (0.000, 0.000, 0.7)]


# Navigation function
def goal_pose_transfer(pose):
    goal_pose = MoveBaseGoal()
    goal_pose.target_pose.header.frame_id = "map"
    goal_pose.target_pose.pose.position.x = pose[0][0]
    goal_pose.target_pose.pose.position.y = pose[0][1]
    goal_pose.target_pose.pose.position.z = pose[0][2]

    x, y, z, w = tf.transformations.quaternion_from_euler(pose[1][0], pose[1][1], pose[1][2])

    goal_pose.target_pose.pose.orientation.x = x
    goal_pose.target_pose.pose.orientation.y = y
    goal_pose.target_pose.pose.orientation.z = z
    goal_pose.target_pose.pose.orientation.w = w
    return goal_pose


def get_twist(length_x, length_y, angle_z):
    msg = Twist()
    if length_x != 0:
        msg.linear.x = (length_x / math.fabs(length_x)) * DEFAULT_SPEED_LIN
    else:
        msg.linear.x = 0

    if length_y != 0:
        msg.linear.y = (length_y / math.fabs(length_y)) * DEFAULT_SPEED_LIN
    else:
        msg.linear.y = 0

    if angle_z != 0:
        msg.angular.z = (angle_z / math.fabs(angle_z)) * DEFAULT_SPEED_ANG
    else:
        msg.angular.z = 0
    rospy.loginfo("Twist now is (" + str(msg.linear.x) + " " + str(msg.linear.y) + " " + str(msg.angular.z) + ")")
    return msg


def get_duration(length, speed):
    return float(math.fabs(length / speed))


def move_dipan(pub, msg, duration):
    pub.publish(msg)
    rospy.sleep(duration)
    msg_init = get_twist(0.0, 0.0, 0.0)
    pub.publish(msg_init)


def angle_to_rad(joint_list):
    # 将导入的角度列表转化为弧度列表
    new_list = joint_list[:]
    for rank in range(0, len(joint_list)):
        if type(joint_list[rank]) == int:
            new_list[rank] = float(joint_list[rank] * PI / 180)
    return new_list


class BaseMoveCalculator():
    """该类用来根据目标位置控制底盘的运动"""

    def __init__(self):
        self.pub_cmd = rospy.Publisher(TOPIC_BASE_PLANAR, Twist, queue_size=10)

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

    def stop_move(self):
        speed = get_twist(0.0, 0.0, 0.0)
        self.pub_cmd.publish(speed)

    def nav_to_point(self, pose):
        # 创建MoveBaseAction client
        client = actionlib.SimpleActionClient('move_base', MoveBaseAction)
        # 等待MoveBaseAction server启动
        client.wait_for_server()
        # 开始导航
        # try:
        rospy.sleep(1)
        goal = goal_pose_transfer(pose)
        client.send_goal(goal)
        client.wait_for_result()
        rospy.sleep(2)
        rospy.loginfo("Nav to point1 finished.")


class Excavator():
    """该类用来控制挖掘机铲斗控制链的运动"""

    def __init__(self):
        # 初始化ROS节点
        rospy.init_node('wajue_process', anonymous=True)
        # 初始化参数
        self.joint_value_list = []

    def data_transfer(self, fl_name):
        """输入csv文件的完整文件名，返回一个包含所有路点数据的嵌套列表"""
        filename = 'catkin_ws/src/pudong_gazebo/scripts/waypoint_dates/' + fl_name
        dates = []
        with open(filename, 'r') as waypoints:
            reader = csv.reader(waypoints)
            for i, row in enumerate(reader):
                dates.append(row)

        joint_value = [0.0, 0.0, 0.0, 0.0]

        for data in dates:
            for i in range(0, 4):
                joint_value[i] = float(data[i].strip())
            joint_value_transfer = joint_value[:]
            self.joint_value_list.append(joint_value_transfer)

        # print self.joint_value_list

    def excavator_joint_waypoints_command(self):
        """根据joint_value_list执行挖掘机应经过的点位"""
        moveit_commander.roscpp_initialize(sys.argv)
        arm = moveit_commander.MoveGroupCommander('wajueji')
        arm.set_goal_joint_tolerance(0.001)
        arm.set_max_acceleration_scaling_factor(1.0)
        arm.set_max_velocity_scaling_factor(1.0)
        arm.allow_replanning(True)

        for joint_positions in self.joint_value_list:
            print joint_positions
            arm.set_start_state_to_current_state()
            arm.set_joint_value_target(angle_to_rad(joint_positions))
            arm.go()
            arm.stop()

    def single_joint_positions_command(self, joint1, joint2, joint3, joint4, max_vel=1.0):
        """到达目标点位，角度或弧度都可以"""
        moveit_commander.roscpp_initialize(sys.argv)
        arm = moveit_commander.MoveGroupCommander('wajueji')
        arm.set_goal_joint_tolerance(0.001)
        arm.set_max_acceleration_scaling_factor(1.0)
        arm.set_max_velocity_scaling_factor(max_vel)

        arm.set_start_state_to_current_state()
        joint_positions = [joint1, joint2, joint3, joint4]
        arm.set_joint_value_target(angle_to_rad(joint_positions))
        arm.go()
        arm.stop()

    def multi_joint_positions_command(self, joint1):
        """底座与车身位置固定时的挖掘规划"""
        moveit_commander.roscpp_initialize(sys.argv)
        arm = moveit_commander.MoveGroupCommander('wajueji')
        arm.set_goal_joint_tolerance(0.001)
        arm.set_max_acceleration_scaling_factor(1.0)
        arm.set_max_velocity_scaling_factor(0.5)

        joint_positions = [joint1, -0.593412, 0.872665, 0.209436]
        arm.set_joint_value_target(angle_to_rad(joint_positions))
        arm.go()
        arm.stop()
        joint_positions = [joint1, -0.069813, -0.488692, -0.471239]
        arm.set_joint_value_target(angle_to_rad(joint_positions))
        arm.go()
        arm.stop()
        joint_positions = [joint1, 0.069813, -0.383972, -0.471239]
        arm.set_joint_value_target(angle_to_rad(joint_positions))
        arm.go()
        arm.stop()
        joint_positions = [joint1, 0.069813, -0.226893, 0.174533]
        arm.set_joint_value_target(angle_to_rad(joint_positions))
        arm.go()
        arm.stop()
        joint_positions = [joint1, -0.104720, -0.0, 0.575959]
        arm.set_joint_value_target(angle_to_rad(joint_positions))
        arm.go()
        arm.stop()

    def list_command(self):
        """
        joint_positions = [0, -17, 0, -29]
        joint_positions = [0, -13, 9, -49]
        joint_positions = [0, -15, 24, -74]
        joint_positions = [0, 1, 48, -68]
        joint_positions = [0, 7, 57, -61]
        joint_positions = [0, -7, 49, -9]

        joint_positions = [0, -17, 0, -29]
        joint_positions = [0, -6, 3, -44]
        joint_positions = [0, -6, 22, -56]
        joint_positions = [0, 2, 48, -78]
        joint_positions = [0, 1, 52, -49]
        joint_positions = [0, -21, 37, 11]

        joint_positions = [0, -17, 0, -29]
        joint_positions = [0, 10, -39, -14]
        joint_positions = [0, 1, 6, -31]
        joint_positions = [0, -6, 19, 2]
        joint_positions = [0, -21, 37, 11]

        joint_positions = [-16, -17, 0, -29]
        joint_positions = [-16, -13, 9, -49]
        joint_positions = [-16, -15, 24, -74]
        joint_positions = [-16, 2, 49, -79]
        joint_positions = [-16, -12, 57, -20]
        """
        # 一次挖掘
        self.joint_value_list = [[0, -17, 0, -29], [0, -13, 9, -49], [0, -15, 24, -74], [0, 1, 48, -68],
                                 [0, 7, 57, -61], [0, -7, 49, -9]]
        self.excavator_joint_waypoints_command()
        # 一次挖掘完后放置,慢速旋转0.015
        self.single_joint_positions_command(95, -23, -3, 53, max_vel=1.0)
        self.single_joint_positions_command(95, -8, -5, -42, max_vel=1.0)
        self.single_joint_positions_command(95, -18, -21, 8)

        # 二次挖掘
        self.joint_value_list = [[0, -17, 0, -29], [0, -6, 3, -44], [0, -6, 22, -56], [0, 2, 48, -78],
                                 [0, 1, 52, -49], [0, -21, 37, 11]]
        self.excavator_joint_waypoints_command()
        # 二次挖掘完后放置,慢速旋转
        self.single_joint_positions_command(95, -23, -3, 53, max_vel=1.0)
        self.single_joint_positions_command(95, -8, -5, -42, max_vel=1.0)
        self.single_joint_positions_command(95, -18, -21, 8)

        # 三次挖掘
        self.joint_value_list = [[0, -17, 0, -29], [0, 10, -39, -14], [0, 1, 6, -31], [0, -6, 19, 2],
                                 [0, -21, 37, 11]]
        self.excavator_joint_waypoints_command()
        # 三次挖掘完后放置,慢速旋转
        self.single_joint_positions_command(95, -23, -3, 53, max_vel=1.0)
        self.single_joint_positions_command(95, -8, -5, -42, max_vel=1.0)
        self.single_joint_positions_command(95, -18, -21, 8)

        # 四次挖掘
        self.joint_value_list = [[-16, -17, 0, -29], [-16, -13, 9, -49], [-16, -15, 24, -74],
                                 [-16, 2, 49, -79], [-16, -12, 57, -20]]
        self.excavator_joint_waypoints_command()
        # 四次挖掘完后放置,慢速旋转
        self.single_joint_positions_command(95, -23, -3, 53, max_vel=1.0)
        self.single_joint_positions_command(95, -8, -5, -42, max_vel=1.0)
        self.single_joint_positions_command(95, -18, -21, 8)

        # 五次挖掘
        self.joint_value_list = [[-16, -17, 0, -29], [-16, 10, -39, -14], [-16, 1, 6, -31], [-16, -6, 19, 2],
                                 [-16, -21, 37, 11]]
        self.excavator_joint_waypoints_command()
        # 五次挖掘完后放置,慢速旋转
        self.single_joint_positions_command(95, -23, -3, 53, max_vel=1.0)
        self.single_joint_positions_command(95, -8, -5, -42, max_vel=1.0)
        self.single_joint_positions_command(95, -18, -21, 8)

        # 六次挖掘
        self.joint_value_list = [[-7, -17, 0, -29], [-7, 10, -39, -14], [-7, 1, 6, -31], [-7, -6, 19, 2],
                                 [-7, -21, 37, 11]]
        self.excavator_joint_waypoints_command()
        # 六次挖掘完后放置,慢速旋转
        self.single_joint_positions_command(95, -23, -3, 53, max_vel=1.0)
        self.single_joint_positions_command(95, -8, -5, -42, max_vel=1.0)
        self.single_joint_positions_command(95, -18, -21, 8)

        # 七次挖掘
        self.joint_value_list = [[9, -17, 0, -29], [9, 10, -39, -14], [9, 1, 6, -31], [9, -6, 19, 2],
                                 [9, -21, 37, 11]]
        self.excavator_joint_waypoints_command()
        # 七次挖掘完后放置,慢速旋转
        self.single_joint_positions_command(95, -23, -3, 53, max_vel=1.0)
        self.single_joint_positions_command(95, -8, -5, -42, max_vel=1.0)
        self.single_joint_positions_command(95, -18, -21, 8)

        # 第八次挖掘
        self.joint_value_list = [[15, -17, 0, -29], [15, -6, 3, -44], [15, -1, 1, -47], [15, -2, 23, -53],
                                 [15, -1, 41, -69], [15, -9, 48, -11]]
        self.excavator_joint_waypoints_command()
        # 第八次挖掘完后放置,慢速旋转
        self.single_joint_positions_command(95, -23, -3, 53, max_vel=1.0)
        self.single_joint_positions_command(95, -8, -5, -42, max_vel=1.0)
        self.single_joint_positions_command(95, -18, -21, 8)

        # 第九次挖掘
        self.joint_value_list = [[0, -17, 0, -29], [0, -6, 3, -44], [0, -1, 1, -47], [0, -2, 23, -53],
                                 [0, -1, 41, -69], [0, -9, 48, -11]]
        self.excavator_joint_waypoints_command()
        # 第九次挖掘完后放置,慢速旋转
        self.single_joint_positions_command(95, -23, -3, 53, max_vel=1.0)
        self.single_joint_positions_command(95, -8, -5, -42, max_vel=1.0)
        self.single_joint_positions_command(95, -18, -21, 8)

        # 第十次挖掘
        self.joint_value_list = [[-7, -17, 0, -29], [-7, -6, 3, -44], [-7, -1, 1, -47], [-7, -2, 23, -53],
                                 [-7, -1, 41, -69], [-7, -9, 48, -11]]
        self.excavator_joint_waypoints_command()
        # 第十次挖掘完后放置,慢速旋转
        self.single_joint_positions_command(95, -23, -3, 53, max_vel=1.0)
        self.single_joint_positions_command(95, -8, -5, -42, max_vel=1.0)
        self.single_joint_positions_command(95, -18, -21, 8)


if __name__ == '__main__':
    ex = Excavator()
    bmc = BaseMoveCalculator()


    ex.data_transfer('data1.csv')
    #ex.excavator_joint_waypoints_command()

    ex.single_joint_positions_command(0.0, -0.593412, 0.872665, 0.209436)
    bmc.nav_to_point(point1)
    rospy.sleep(1)

    #ex.multi_joint_positions_command(0.0)
    ex.list_command()
    #rospy.sleep(1)
    #ex.single_joint_positions_command(1.151917, -0.471239, 0.453786, 0.401426, max_vel=0.04)
    #ex.single_joint_positions_command(1.151917, -0.209440, -0.383972, -0.226893)
