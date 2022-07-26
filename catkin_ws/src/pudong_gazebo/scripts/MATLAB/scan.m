clear
rosshutdown;%先关闭之前的ROS节点
rosinit;
laser = rossubscriber('/scan');
scan = receive(laser,3);
figure
plot(scan);

