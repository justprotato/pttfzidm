import sys
temp = sys.stdout
sys.stdout = open('nul','w')
import pygame
sys.stdout = temp
del temp

import numpy as np
from time import time, sleep
import socket


Pan_TiltDrive_Up = "81 01 06 01 {:02X} {:02X} 03 01 FF"
Pan_TiltDrive_Down = "81 01 06 01 {:02X} {:02X} 03 02 FF"
Pan_TiltDrive_Left = "81 01 06 01 {:02X} {:02X} 01 03 FF"
Pan_TiltDrive_Right = "81 01 06 01 {:02X} {:02X} 02 03 FF"
Pan_TiltDrive_UpLeft = "81 01 06 01 {:02X} {:02X} 01 01 FF"
Pan_TiltDrive_UpRight = "81 01 06 01 {:02X} {:02X} 02 01 FF"
Pan_TiltDrive_DownLeft = "81 01 06 01 {:02X} {:02X} 01 02 FF"
Pan_TiltDrive_DownRight = "81 01 06 01 {:02X} {:02X} 02 02 FF"
Pan_TiltDrive_Stop = "81 01 06 01 {:02X} {:02X} 03 03 FF"
Pan_TiltDrive_AbsolutePosition = "81 01 06 02 {:02X} {:02X} 0{:01X} 0{:01X} 0{:01X} 0{:01X} 0{:01X} 0{:01X} 0{:01X} 0{:01X} FF"
Pan_TiltDrive_RelativePosition = "81 01 06 03 {:02X} {:02X} 0{:01X} 0{:01X} 0{:01X} 0{:01X} 0{:01X} 0{:01X} 0{:01X} 0{:01X} FF"

Pan_TiltDrive_Home = "81 01 06 04 FF"
Pan_TiltDrive_Reset = "81 01 06 05 FF"

CAM_Zoom_Stop = "81 01 04 07 00 FF"
CAM_Zoom_Tele = "81 01 04 07 02 FF"
CAM_Zoom_Wide = "81 01 04 07 03 FF"
CAM_Zoom_Tele_V = "81 01 04 07 2{:01X} FF"
CAM_Zoom_Wide_V = "81 01 04 07 3{:01X} FF"
CAM_ZOOM_Direct = "81 01 04 47 0p 0q 0r 0s FF"

CAM_ZoomPosInq = "81 09 04 47 FF"
CAM_PanTiltPosInq = "81 09 06 12 FF"

IP_ADDRESS = '192.168.0.100'
TCP_PORT = 5678
UDP_PORT = 1259

# max psepeed = 24 (from 0x01 to 0x18 (0 - 24)
# max tspeed = 20 ( from 0x01 to 0x14 (0 - 20)

VISCA_HEX = {
				's': lambda pspeed,tspeed: Pan_TiltDrive_Stop.format(int(pspeed),int(tspeed)),
				'u': lambda pspeed,tspeed: Pan_TiltDrive_Up.format(int(pspeed),int(tspeed)),
				'd': lambda pspeed,tspeed: Pan_TiltDrive_Down.format(int(pspeed),int(tspeed)),
				'l': lambda pspeed,tspeed: Pan_TiltDrive_Left.format(int(pspeed),int(tspeed)),
				'r': lambda pspeed,tspeed: Pan_TiltDrive_Right.format(int(pspeed),int(tspeed)),
				'ul': lambda pspeed,tspeed: Pan_TiltDrive_UpLeft.format(int(pspeed),int(tspeed)),
				'ur': lambda pspeed,tspeed: Pan_TiltDrive_UpRight.format(int(pspeed),int(tspeed)),
				'dl': lambda pspeed,tspeed: Pan_TiltDrive_DownLeft.format(int(pspeed),int(tspeed)),
				'dr': lambda pspeed,tspeed: Pan_TiltDrive_DownRight.format(int(pspeed),int(tspeed)),
				'home': Pan_TiltDrive_Home,
				'abspos': lambda pspeed, tspeed, panpos,tilpos: Pan_TiltDrive_AbsolutePosition.format(int(pspeed),int(tspeed),0,0,0,0,0,0,0,0),
				'revpos': lambda pspeed, tspeed, panpos,tilpos: Pan_TiltDrive_RelativePosition.format(int(pspeed),int(tspeed),0,0,0,0,0,0,0,0)
				# panpos: -2448 to 2448
				# tilpos: -1296 to 1295
			}

class VISCA():
	def __init__(self, ip=IP_ADDRESS, port=UDP_PORT):
		self.sock = None
		if port==UDP_PORT:
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		elif port==TCP_PORT:
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		else:
			raise Exception('port Must be either UDP_PORT or TCP_PORT, but <port>={} founded'.format(port))
		self.sock.connect((ip, port))
		self.BUFFER_SIZE = 16

	def __del__(self):
		self.sock.close()
		
	def send(self, str):
		self.sock.send(bytes.fromhex(str))
		self.receive()
		self.receive()
		
		
	def receive(self):
		data = self.sock.recv(self.BUFFER_SIZE)
		return data.hex()

class PTZ(VISCA):
	def __init__(self,ip=IP_ADDRESS, port=TCP_PORT):
		super(PTZ,self).__init__(ip,port)

	def home(self):
		self.send(VISCA_HEX['home'])
		
	def pt_stop(self, p_speed=24, t_speed=20):
		# self.send(Pan_TiltDrive_Stop.format(24, 20))
		self.send(VISCA_HEX['s'](p_speed,p_speed))
		
	def up(self, p_speed=8, t_speed=8):
		# self.send(Pan_TiltDrive_Up.format(p_speed, t_speed))
		self.send(VISCA_HEX['u'](p_speed,t_speed))
		
	def down(self, p_speed=8, t_speed=8):
		# self.send(Pan_TiltDrive_Down.format(p_speed, t_speed))
		self.send(VISCA_HEX['d'](p_speed,t_speed))
    
	def left(self, p_speed=8, t_speed=8):
		# self.send(Pan_TiltDrive_Left.format(p_speed, t_speed))
		self.send(VISCA_HEX['l'](p_speed,t_speed))
		
	def right(self, p_speed=8, t_speed=8):
		# self.send(Pan_TiltDrive_Right.format(p_speed, t_speed))
		print((p_speed,t_speed))
		self.send(VISCA_HEX['r'](p_speed,t_speed))

	def upleft(self, p_speed=8, t_speed=8):
		# self.send(Pan_TiltDrive_UpLeft.format(p_speed, t_speed))
		self.send(VISCA_HEX['ul'](p_speed,t_speed))

	def upright(self, p_speed=8, t_speed=8):
		# self.send(Pan_TiltDrive_UpRight.format(p_speed, t_speed))
		self.send(VISCA_HEX['ur'](p_speed,t_speed))

	def downleft(self, p_speed=8, t_speed=8):
		# self.send(Pan_TiltDrive_DownLeft.format(p_speed, t_speed))
		self.send(VISCA_HEX['dl'](p_speed,t_speed))

	def downright(self, p_speed=8, t_speed=8):
		# self.send(Pan_TiltDrive_DownRight.format(p_speed, t_speed))
		self.send(VISCA_HEX['dr'](p_speed,t_speed))

	# def tele(self, p):
		# self.send(CAM_Zoom_Tele_V.format(p))

	# def wide(self, p):
		# self.send(CAM_Zoom_Wide_V.format(p))

	# def zoomstop(self):
		# self.send(CAM_Zoom_Stop)

# Axis : 6
# 0 : left mushroom x (+ve right)
# 1 : left mushroom y (+ve down)
# 2 : right mushroom x (+ve right)
# 3 : right mushroom y (+ve down)
# 4 : R2 (pressed = +1, un pressed = -1)
# 5 : L2 (pressed = +1, un pressed = -1)
#
# Ball : 0
#
# Hat : 1
# 0: cross (tuple of X,Y) (+ve = right, up)
#
# Button : 14
# 0: squre
# 1: X
# 2: Cicle
# 3: triangle
# 4: L1
# 5: R1
# 6: 
# 7: 
# 8: share
# 9: option
# 10: left mushroom
# 11: right mushroom
# 12: home
# 13: pannel

class PS4():
	def __init__(self):
		pygame.init()
		self.ptz = PTZ()
		self.j = pygame.joystick.Joystick(0)
		self.j.init()
		
		self.buttons = np.zeros((self.j.get_numbuttons(),),dtype=bool)
		self.hat = (0,0)
		self.newaxis = np.zeros((self.j.get_numaxes(),),dtype=float)
		self.oldaxis = np.zeros((self.j.get_numaxes(),),dtype=float)
	def check_buttons(self):
		print(self.j.get_init())
		print(self.j.get_name())
		print(self.j.get_numaxes())
		print(self.j.get_numballs())
		print(self.j.get_numbuttons())
		print(self.j.get_numhats())
		while True:
			for event in pygame.event.get():
				# press button
				if event.type==pygame.JOYBUTTONDOWN:
					print("Button {} down".format(event.button))
					# self.buttons[event.button]=True
				# release button
				elif event.type==pygame.JOYBUTTONUP:
					print("Button {} up".format(event.button))
					# self.buttons[event.button]=False
				# axis
				elif event.type==pygame.JOYAXISMOTION:
					print("axis {}, value {}".format(event.axis,event.value))
					# self.axis[event.axis] = event.value
				# hat
				elif event.type==pygame.JOYHATMOTION:
					print("hat {}, value {}".format(event.hat,event.value))
					# self.hat = event.value
			
		return

	def loop(self):
		while True:
				has_event = {}
				events = pygame.event.get()
				# if len(events)==0:
					# self.oldaxis = self.newaxis
				for event in events:
					# press button
					if event.type==pygame.JOYBUTTONDOWN:
						#print("Button {} down".format(event.button))
						self.buttons[event.button]=True
						has_event['butdw']=True
					# release button
					elif event.type==pygame.JOYBUTTONUP:
						#print("Button {} up".format(event.button))
						self.buttons[event.button]=False
						has_event['butup']=True
					# axis
					elif event.type==pygame.JOYAXISMOTION:
						#print("axis {}, value {}".format(event.axis,event.value))
						self.oldaxis[event.axis] = self.newaxis[event.axis]
						self.newaxis[event.axis] = event.value
						has_event['axis']=True
					# hat
					elif event.type==pygame.JOYHATMOTION:
						#print("hat {}, value {}".format(event.hat,event.value))
						self.hat = event.value
						has_event['hat']=True
				if has_event.get('hat',False) and False:
					print(self.hat)
					if self.hat==(0,0):
						self.ptz.pt_stop()
					elif self.hat==(1,0):
						self.ptz.right(10,10)
					elif self.hat==(-1,0):
						self.ptz.left(10,10)
					elif self.hat==(0,1):
						self.ptz.up(10,10)
					elif self.hat==(0,-1):
						self.ptz.down(10,10)
					elif self.hat==(1,1):
						self.ptz.upright(10,10)
					elif self.hat==(1,-1):
						self.ptz.downright(10,10)
					elif self.hat==(-1,1):
						self.ptz.upleft(10,10)
					elif self.hat==(-1,-1):
						self.ptz.downleft(10,10) 
				if has_event.get('butdw',False):
					if self.buttons[8]:
						break
					if self.buttons[12]:
						self.ptz.home()
				if has_event.get('axis',False) or True:
					# print("{:.5f},{:.5f}".format(self.newaxis[0],abs(self.newaxis[0]-self.oldaxis[0])*144//6))
					# if abs(self.newaxis[0]-self.oldaxis[0])*144//6>1:
						print("{:.5f}".format(self.newaxis[0]))
						if abs(self.newaxis[0])*144//12<1:
							print("Zero")
							self.ptz.pt_stop()
						elif self.newaxis[0]>0:
							print((self.newaxis[0]*144)//12)
							self.ptz.right((self.newaxis[0]*144)//12,10) #12 step, 12^2 // 12
						elif self.newaxis[0]<0:
							print((self.newaxis[0]*144)//12)
							self.ptz.left((-self.newaxis[0]*144)//12,10)
						else:
							raise Exception('Error, NaN')
		return			
		


if __name__=="__main__":
	ps4=PS4()
	ps4.loop()
	print("End of Program")