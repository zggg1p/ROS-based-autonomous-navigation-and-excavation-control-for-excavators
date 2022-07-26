#!/usr/bin/env python
# coding=utf-8

import rospy, sys
from gazebo_msgs.srv import *
from geometry_msgs.msg import Pose
from gazebo_msgs.srv import SpawnModel


initial_pose = Pose()
initial_pose.position.x = 11.0
initial_pose.position.y = 7.0
initial_pose.position.z = 2.0


def sc_shikuai(name):
	model_name = "haoduomiantiaa_" + str(name)
	spawn_model_prox(model_name, sdff, "", initial_pose, "world")
	# rospy.sleep(0.1)


if __name__ == '__main__':
	rospy.init_node('shikuai_shengcheng')
	rospy.wait_for_service('/gazebo/spawn_sdf_model')
	spawn_model_prox = rospy.ServiceProxy('gazebo/spawn_sdf_model', SpawnModel)

	f = open('model_editor_models/1m_haoduomianti/model.sdf', 'r')
	sdff = f.read()

	for name in range(100, 200):
		sc_shikuai(name)
