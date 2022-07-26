clear
rosshutdown;%先关闭之前的ROS节点 
rosinit; %运行此行命令之前需要打开ROS和示例
robot = rospublisher('/cmd_vel');
velmsg = rosmessage(robot);
laser = rossubscriber('/scan');
spinVelocity = 0.6;       % Angular velocity (rad/s)
forwardVelocity = 0.5;    % Linear velocity (m/s)
backwardVelocity = -0.5; % Linear velocity (reverse) (m/s)
distanceThreshold = 0.5;  % Distance threshold (m) for turning
tic;
  while toc < 100
      % Collect information from laser scan
      scan = receive(laser);
      plot(scan);
      data = readCartesian(scan);
      x = data(:,1);
      y = data(:,2);
      % Compute distance of the closest obstacle
      dist = sqrt(x.^2 + y.^2);
      minDist = min(dist);     
      % Command robot action
      if minDist < distanceThreshold
          % If close to obstacle, back up slightly and spin
          velmsg.Angular.Z = spinVelocity;
          velmsg.Linear.X = backwardVelocity;
      else
          % Continue on forward path
          velmsg.Linear.X = forwardVelocity;
          velmsg.Angular.Z = 0;
      end   
      send(robot,velmsg);
  end

velmsg.Angular.Z = 0;
velmsg.Linear.X = 0;
send(robot,velmsg)

