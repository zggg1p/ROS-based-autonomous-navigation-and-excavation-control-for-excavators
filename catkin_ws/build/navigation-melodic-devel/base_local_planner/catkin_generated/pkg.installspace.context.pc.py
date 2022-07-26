# generated from catkin/cmake/template/pkg.context.pc.in
CATKIN_PACKAGE_PREFIX = ""
PROJECT_PKG_CONFIG_INCLUDE_DIRS = "${prefix}/include".split(';') if "${prefix}/include" != "" else []
PROJECT_CATKIN_DEPENDS = "angles;costmap_2d;dynamic_reconfigure;geometry_msgs;message_runtime;nav_core;nav_msgs;pluginlib;roscpp;sensor_msgs;std_msgs;tf2;tf2_ros;voxel_grid".replace(';', ' ')
PKG_CONFIG_LIBRARIES_WITH_PREFIX = "-lbase_local_planner;-ltrajectory_planner_ros".split(';') if "-lbase_local_planner;-ltrajectory_planner_ros" != "" else []
PROJECT_NAME = "base_local_planner"
PROJECT_SPACE_DIR = "/home/lenovo/catkin_ws/install"
PROJECT_VERSION = "1.16.7"
