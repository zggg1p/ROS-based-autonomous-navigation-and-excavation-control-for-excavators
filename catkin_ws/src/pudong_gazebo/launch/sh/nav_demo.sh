#!/bin/bash

gnome-terminal -- bash -c "roslaunch pudong_gazebo model_spawn.launch"
sleep 10

gnome-terminal -- bash -c "roslaunch pudong_gazebo joint_state_node.launch"
sleep 10

gnome-terminal -- bash -c "roslaunch pudong_gazebo moveit_excution.launch"
sleep 10

gnome-terminal -- bash -c "rosrun pudong_gazebo guding_cswj.py"
sleep 10

gnome-terminal -- bash -c "roslaunch mbot_navigation nav_cloister_demo.launch"
