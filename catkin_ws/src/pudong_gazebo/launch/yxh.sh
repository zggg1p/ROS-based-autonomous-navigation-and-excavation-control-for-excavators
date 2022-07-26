#!/bin/bash

gnome-terminal -- bash -c "roslaunch pudong_gazebo model_spawn.launch"
sleep 8

gnome-terminal -- bash -c "roslaunch pudong_gazebo joint_state_node.launch"
sleep 5

gnome-terminal -- bash -c "roslaunch pudong_gazebo moveit_excution.launch"
sleep 8

gnome-terminal -- bash -c "roslaunch pudong_gazebo rviz_slam.launch"
sleep 5

gnome-terminal -- bash -c "roslaunch pudong_gazebo pointcloud_to_laserscan.launch"
sleep 5

gnome-terminal -- bash -c "rosrun pudong_gazebo guding_cswj.py"
sleep 8

gnome-terminal -- bash -c "roslaunch mbot_navigation gmapping.launch"
sleep 5

gnome-terminal -- bash -c "roslaunch mbot_teleop mbot_teleop.launch"




