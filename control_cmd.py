#! /usr/bin/env python
# -*- coding: utf-8 -*-
# PTZ control over TCP/UDP
# by Kenny
import socket
# default camera address
cam_addr = 1
"""
Error Messages Command
    y = x+8, where x is the camera address
"""
Syntax_Error = "90 60 02 FF"
Command_Buffer_Full = "90 60 03 FF"
Command_Canceled = "90 6{} 04 FF".format(cam_addr+8)
No_Socket = "90 6{} 05 FF".format(cam_addr+8)
Command_Not_Executable = "90 6{} 41 FF".format(cam_addr+8)

"""
Preset Command
    - Memory Number(=0 to 127) 
    - speed grade,the values are (0x1~0x18）
"""
CAM_Memory_Reset = "81 01 04 3F 00 {:02} FF"
CAM_Memory_Set = "81 01 04 3F 01 {:02} FF"
CAM_Memory_Recall = "81 01 04 3F 02 {:02} FF"
Preset_Recall_Speed = "81 01 06 01 {:02} FF "


"""
Pan Tilt Drive Command
    - Pan speed 0x01 (low speed) to 0x18 (high speed)
    - Tilt speed 0x01 (low speed) to 0x14 (high speed)

    - YYYY: Pan Position ZZZZ: Tilt Position
"""
Pan_TiltDrive_Up = "81 01 06 01 {:02X} {:02X} 03 01 FF"
Pan_TiltDrive_Down = "81 01 06 01 {:02X} {:02X} 03 02 FF"
Pan_TiltDrive_Left = "81 01 06 01 {:02X} {:02X} 01 03 FF"
Pan_TiltDrive_Right = "81 01 06 01 {:02X} {:02X} 02 03 FF"
Pan_TiltDrive_UpLeft = "81 01 06 01 {:02X} {:02X} 01 01 FF"
Pan_TiltDrive_UpRight = "81 01 06 01 {:02X} {:02X} 02 01 FF"
Pan_TiltDrive_DownLeft = "81 01 06 01 {:02X} {:02X} 01 02 FF"
Pan_TiltDrive_DownRight = "81 01 06 01 {:02X} {:02X} 02 02 FF"
Pan_TiltDrive_Stop = "81 01 06 01 {:02X} {:02X} 03 03 FF"
Pan_TiltDrive_AbsolutePosition = "81 01 06 02 {:02X} {:02X} 0{} 0{} 0{} 0{} 0{} 0{} 0{} 0{} FF"
Pan_TiltDrive_RelativePosition = "81 01 06 03 {:02X} {:02X} 0{} 0{} 0{} 0{} 0{} 0{} 0{} 0{} FF"

Pan_TiltDrive_Home = "81 01 06 04 FF"
Pan_TiltDrive_Reset = "81 01 06 05 FF"

"""
Zoom Command
    speed: 0(low) - 7(high) 
"""
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


class VISCA():

    def __init__(self, ip=IP_ADDRESS, port=UDP_PORT):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.connect((ip, port))

    def __del__(self):
        self.sock.close()

    def send(self, str):
        self.sock.send(bytes.fromhex(str))

    def receive(self):
        data = self.sock.recv(self.BUFFER_SIZE)
        return data.hex()


class PTZ():

    def __init__(self):
        self.visca = VISCA()

        # init states for sockect logic
        #private
        self.zooming = False
        self.driving = False

    def __del__(self):
        del self.visca
        
    def home(self):
        self.visca.send(Pan_TiltDrive_Home)

    def pt_stop(self, p_speed, t_speed):
        if self.driving:
            self.driving = False
            self.visca.send(Pan_TiltDrive_Stop.format(24, 20))

    def up(self, p_speed, t_speed):
        self.visca.send(Pan_TiltDrive_Up.format(p_speed, t_speed))

    def down(self, p_speed, t_speed):
        self.visca.send(Pan_TiltDrive_Down.format(p_speed, t_speed))
    
    def left(self, p_speed, t_speed):
        self.visca.send(Pan_TiltDrive_Left.format(p_speed, t_speed))

    def right(self, p_speed, t_speed):
        self.visca.send(Pan_TiltDrive_Right.format(p_speed, t_speed))

    def upleft(self, p_speed, t_speed):
        self.visca.send(Pan_TiltDrive_UpLeft.format(p_speed, t_speed))

    def upright(self, p_speed, t_speed):
        self.visca.send(Pan_TiltDrive_UpRight.format(p_speed, t_speed))

    def downleft(self, p_speed, t_speed):
        self.visca.send(Pan_TiltDrive_DownLeft.format(p_speed, t_speed))

    def downright(self, p_speed, t_speed):
        self.visca.send(Pan_TiltDrive_DownRight.format(p_speed, t_speed))

    def tele(self, p):
        self.zooming = True
        self.visca.send(CAM_Zoom_Tele_V.format(p))

    def wide(self, p):
        self.zooming = True
        self.visca.send(CAM_Zoom_Wide_V.format(p))

    def zoomstop(self):
        if self.zooming:
            self.zooming = False
            self.visca.send(CAM_Zoom_Stop)

    def ptdrive_relative_pos(self, p_speed, t_speed, x_loc, y_loc):
        lx = list(x_loc)
        ly = list(y_loc)
        self.visca.send(Pan_TiltDrive_RelativePosition.format(p_speed, t_speed, lx[0],lx[1],lx[2],lx[3],ly[0],ly[1],ly[2],ly[3]))
