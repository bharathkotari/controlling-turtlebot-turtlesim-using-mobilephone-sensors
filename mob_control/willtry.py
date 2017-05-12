#!/usr/bin/env python

# Copyright (c) 2011, Willow Garage, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of the Willow Garage, Inc. nor the names of its
#      contributors may be used to endorse or promote products derived from
#       this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import rospy

from geometry_msgs.msg import Twist

import sys, select, termios, tty
import socket
import math

msg = """

controlling turtlebot/turtlesim with mobilephone sensors 
original codes and tutorials at  for keyboard teleop https://github.com/turtlebot/turtlebot/tree/kinetic/turtlebot_teleop/scripts 
 for hyperimu getting the udp stream https://github.com/ianovir/HIMUServer


edited by 
>>bharath kotari 

tweek the things to your need

directions:	1.hold the mobile phone horizontally parallel to the ground
		2.tilt the mobile towards front to move forward
		3.tilt the mobile towards back to move backward
		4.tilt the mobile right  to move right
		5.tilt the mobile left  to move left
                            >>>>cheers<<<<<<

CTRL-C to quit
"""
#print("hello there")

moveBindings = {
	'i':(1,0),
	'o':(1,-1),
	'j':(0,1),
	'l':(0,-1),
	'u':(1,1),
	',':(-1,0),
	'.':(-1,1),
	'm':(-1,-1),
}

speedBindings={
	'q':(1.1,1.1),
	'z':(.9,.9),
	'w':(1.1,1),
	'x':(.9,1),
	'e':(1,1.1),
	'c':(1,.9),
}
def strings2Floats(listString):
	out=[]
	for j in range(0, len(listString)-1):
		out.append( float(listString[j]))
	return out	
speed = .2
turn = 1

def vels(speed,turn):
	return "currently:\tspeed %s\tturn %s " % (speed,turn)

if __name__=="__main__":
	rospy.init_node('mob_control')
	pub = rospy.Publisher('/mobile_base/commands/velocity', Twist, queue_size=1) #this line creates an object to publish to turtlebot control
	pub1 = rospy.Publisher('/turtle1/cmd_vel', Twist, queue_size=1) # yes you are right , this line creates an object to publish to turtlesim turtle control
	settings = termios.tcgetattr(sys.stdin)
	timeout = 20  #timeout in seconds
	bufferSize=1024 #bytes
	packSeparator="#"
	go=True;
	
			
	x = 0
	th = 0
	status = 0
	count = 0
	acc = 0.1
	target_speed = 0
	target_turn = 0
	control_speed = 0
	control_turn = 0
	UDPSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)	# creates a socket for udp transmission
	UDPSocket.settimeout(timeout)					# sets a time limit for no connection
	serverAddress = ('', 3478) 					 #listens for data stream from port 3478 , feel free to change to any port you like
 	print('Listening on port ' + str(3478))
	UDPSocket.bind(serverAddress)					# binds that socket to the address and port
	while go:
		[data,attr] = UDPSocket.recvfrom(bufferSize)#continuesly receive from that port into buffer 
		datastream=(data.decode("utf-8"))         #decode the data
		try:
			print msg
			print vels(speed,turn)
			key=''	
			packages = datastream.split(packSeparator)  '''splits the data stream based on # why ?? because "hyper imu" transfers aensor values separated by
									 ',' and ending with '#'     '''
			for pack in packages:
				try:
					pack = pack+","
					lFloat =strings2Floats(pack.split(","))
 					numSensors = int(math.floor(len(lFloat)/3))
					for i in range(0,numSensors):
	 	 				p=lFloat[i*3:3*(i + 1)]
	  					print('Sensor' + str(i+1) +  ": " + str(p))
					if lFloat[0]<=0:    # ok ,here i just re-mapped the keys based on the sensor values coming from mobilephone 
						key='i'
						x=1
					elif lFloat[0]>1:
						key=','
						x=(-1)
					if lFloat[1]<=-2:
						key='j'
					elif lFloat[1]>2:
						key='l'
					else :
						th=0
					if key in moveBindings.keys():
						#print(x)  for debugging
						th = moveBindings[key][1]
						#print(th)  for debugging
						count = 0
					elif key in speedBindings.keys():
						speed = speed * speedBindings[key][0]
						turn = turn * speedBindings[key][1]
						count = 0
						print vels(speed,turn)
					if (status == 14):
						print msg
						status = (status + 1) % 15
					elif key == ' ' or key == 'k' :
						x = 0
						th = 0
						control_speed = 0
						control_turn = 0
					else:
						count = count + 1
						if count > 4:
							x = 0
							th = 0
						if (key == '\x03'):
							break
					#print(" speed = %s",speed)
					target_speed = 0.7 * x  # here you can vary the speed , 0.7 works well for me
					target_turn = turn * th

					if target_speed > control_speed:
						control_speed = min( target_speed, control_speed + 0.02 )
					elif target_speed < control_speed:
						control_speed = max( target_speed, control_speed - 0.02 )
					else:
						control_speed = target_speed

					if target_turn > control_turn:
						control_turn = min( target_turn, control_turn + 0.1 )
					elif target_turn < control_turn:
						control_turn = max( target_turn, control_turn - 0.1 )
					else:
						control_turn = target_turn

					twist = Twist()
					twist1=Twist()
									# publishes data to turtlebot topic(/mobile_base/commands/velocity)
					twist.linear.x = control_speed; twist.linear.y = 0; twist.linear.z = 0  
					twist.angular.x = 0; twist.angular.y = 0; twist.angular.z = control_turn
									# publishes data to turtlesim topic(/turtle1/cmd_vel)
					twist1.linear.x = control_speed; twist1.linear.y = 0; twist1.linear.z = 0 
					twist1.angular.x = 0; twist1.angular.y = 0; twist1.angular.z = control_turn
					pub.publish(twist)
					pub1.publish(twist1)
				except:
					pass			

		except:
			pass
	UDPSocket.close() # relese the port


