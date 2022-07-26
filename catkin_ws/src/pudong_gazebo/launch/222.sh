#!/bin/bash

gnome-terminal -- bash -c "rosrun pudong_gazebo guding_cswj.py"
sleep 8

gnome-terminal -- bash -c "rosrun pudong_gazebo nav_test.py"

