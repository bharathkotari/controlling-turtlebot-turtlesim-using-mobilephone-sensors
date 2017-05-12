# controlling-turtlebot-turtlesim-using-mobilephone-sensors
control the turtlebot/turtlesim in ROS using mobilephone sensors using "hyper imu " android app and udp protocol

i have just edited the keyboard teleop file so that it can be operated from android mobile
thank the original authors . look at the bottom of this page for links .

this code may contain so much unused code . because i was lazy to remove that . remove that if you want neat good looking code.
or uset it like i dont care .
also you can tweek this code so that it can work for hector quadrotor . do it if you want . 

how to use this code
1. place this entire folder in ~/(your ROS workspace)/src/
2. build the package using catkin_make mob_control
3. and run the command "rosrun mob_control willtry.py"  ( source the workspace if this is not working using "source devel/setup.bash")
4. run that app first and run this command .

how to initilise hyperimu app
1. just see your routers/computer ip address using ifconfig in linux
2. go to settings > select udp 
 -> and edit the ip address of target
 -> and give the port number as 3478 or your own port.
 -> set the sampling time low , 50 ms worked well for me
3. select the sensors from list of sensors
 -> i have selected Accelerometer to control the direction
4. come back to app homepage and touch the round animation or whatever it is.

original codes and tutorials at  for keyboard teleop https://github.com/turtlebot/turtlebot/tree/kinetic/turtlebot_teleop/scripts 
 for hyperimu getting the udp stream https://github.com/ianovir/HIMUServer

