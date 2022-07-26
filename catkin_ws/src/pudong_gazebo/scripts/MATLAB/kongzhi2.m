cmdpub = rospublisher('/cmd_vel',rostype.geometry_msgs_Twist);
pause(3) % Wait to ensure publisher is setup
cmdmsg = rosmessage(cmdpub);
cmdmsg.Linear.X = 0.4;
cmdmsg.Angular.Z = 0.2;
send(cmdpub,cmdmsg);
