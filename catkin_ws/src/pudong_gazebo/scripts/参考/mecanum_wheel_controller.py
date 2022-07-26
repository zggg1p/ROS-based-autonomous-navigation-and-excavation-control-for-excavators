#!/usr/bin/env python


# This file is a subscriber of the topic 'cmd_vel', when the mecanum wheel base got the command of #controller "teleop_twist_keyboard.py", the linear and angular speed will be automatically transfered to the mecanum wheel's rotation speed. Thus, the mecanum wheels will rotation as the real condition.


import roslib; #roslib.load_manifest('cmd_vel_transfer')
import rospy

from geometry_msgs.msg import Twist
from std_msgs.msg import Float64


### List of topics ###
# First letter :  F=front, R=rear
# Second letter : L=left,  R=right
# FL = Front left wheel
TOPIC_FR_CMD = '/elfin5/d_wr2_velocity_controller/command'
TOPIC_FL_CMD = '/elfin5/d_wl1_velocity_controller/command'
TOPIC_RL_CMD = '/elfin5/d_wr1_velocity_controller/command'
TOPIC_RR_CMD = '/elfin5/d_wl2_velocity_controller/command'

### Parameters of the mecanum base ### 
DEFAULT_HALF_DIPAN_LENGTH = 0.25
DEFAULT_HALF_DIPAN_WIDTH = 0.243
DEFAULT_WHEEL_RADIUS = 0.06


class CmdVelTransfer():
    
    def __init__(self):
        rospy.init_node('cmd_vel_transfer')
        nodename = rospy.get_name()
        rospy.loginfo("%s started" % nodename)

        self.a = DEFAULT_HALF_DIPAN_WIDTH
        self.b = DEFAULT_HALF_DIPAN_LENGTH
        self.r = DEFAULT_WHEEL_RADIUS

        ### Publish to the specific wheel's topic ###
        self.pub_fr_motor = rospy.Publisher(TOPIC_FR_CMD, Float64,queue_size=10)
        self.pub_fl_motor = rospy.Publisher(TOPIC_FL_CMD, Float64,queue_size=10)
        self.pub_rl_motor = rospy.Publisher(TOPIC_RL_CMD, Float64,queue_size=10)
        self.pub_rr_motor = rospy.Publisher(TOPIC_RR_CMD, Float64,queue_size=10)

        ### Subscribe the topic cmd_vel, later please see def twistCallback ###
        rospy.Subscriber('cmd_vel', Twist, self.twistCallback)

        self.rate = rospy.get_param("~rate", 40)
        self.timeout_ticks = rospy.get_param("~timeout_ticks", 2)

        self.w1 = 0
        self.w2 = 0
        self.w3 = 0
        self.w4 = 0


    def spin(self):
        r = rospy.Rate(self.rate)
        idle = rospy.Rate(10)
        then = rospy.Time.now()
        self.ticks_since_target = self.timeout_ticks
    
        ###### main loop  ######
        while not rospy.is_shutdown():
        
            while not rospy.is_shutdown() and self.ticks_since_target < self.timeout_ticks:
                self.spinOnce()
                r.sleep()
            idle.sleep()


    def spinOnce(self):
        ### Calculate the rotation speed of each mecanum wheel and pub them ###
        self.w1 = ( self.vel_y - self.vel_x + ( self.a + self.b ) * self.ang_z ) / self.r
        self.w2 = ( self.vel_y + self.vel_x - ( self.a + self.b ) * self.ang_z ) / self.r
        self.w3 = ( self.vel_y - self.vel_x - ( self.a + self.b ) * self.ang_z ) / self.r
        self.w4 = ( self.vel_y + self.vel_x + ( self.a + self.b ) * self.ang_z ) / self.r

        self.pub_fr_motor.publish(self.w1)
        self.pub_fl_motor.publish(self.w2)
        self.pub_rl_motor.publish(self.w3)
        self.pub_rr_motor.publish(self.w4)

        self.ticks_since_target += 1


    def twistCallback(self,msg):
        self.ticks_since_target = 0

        ###  Get the value of twist ###
        self.vel_x = msg.linear.x
        self.vel_y = msg.linear.y
        self.ang_z = msg.angular.z

if __name__ == '__main__':
    cmdveltransfer = CmdVelTransfer()
    cmdveltransfer.spin()
