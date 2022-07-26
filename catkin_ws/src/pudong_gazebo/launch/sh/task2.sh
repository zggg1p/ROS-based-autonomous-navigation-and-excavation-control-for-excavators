#!/bin/bash

gnome-terminal -- bash -c "roslaunch pudong_gazebo model_spawn.launch"
sleep 3

gnome-terminal -- bash -c "roslaunch pudong_gazebo joint_state_node.launch"
sleep 1

gnome-terminal -- bash -c "roslaunch pudong_gazebo moveit_excution.launch"

sleep 8

gnome-terminal -- bash -c "roslaunch pudong_gazebo navigation_demo.launch"

#sleep 4

#gnome-terminal -- bash -c "rosrun pudong_gazebo reconstructed_excavator_control.py"



