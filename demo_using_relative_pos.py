#! /usr/bin/env python
# -*- coding: utf-8 -*-
# PTZ controlled by Sony Dual Shock 4 Controller
# by Kenny


"""
Pan and Tilt:
[pan speed] : 1(low speed) – 24(high speed)；
[tilt speed]: 1(low speed) – 20(high speed).

Zoom:
[action] including：zoomin，zoomout，zoomstop；
[zoom speed]: 0(low speed) – 7(high speed)。

Focus
[action] including：focusin，focusout，focusstop；
[focus speed]: 0(low speed) – 7(high speed)

Preset Position control：
[action] including：posset，poscall;
[positionnumber]: 0-89，100-254
"""


import os
import pprint
import pygame
import math
import control_cmd

os.environ['SDL_VIDEODRIVER'] = 'dummy'

import time

class PS4Controller(object):
    """Class representing the PS4 controller. Pretty straightforward functionality."""

    controller = None
    axis_data = None
    button_data = None
    hat_data = None

    def init(self):
        """Initialize the joystick components"""

        pygame.init()
        pygame.joystick.init()
        self.controller = pygame.joystick.Joystick(0)
        self.controller.init()

        self.ptz = control_cmd.PTZ()

    def listen(self):
        # init.
        if not self.axis_data:
            self.axis_data = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

        if not self.button_data:
            self.button_data = {}
            for i in range(self.controller.get_numbuttons()):
                self.button_data[i] = False

        if not self.hat_data:
            self.hat_data = {}
            for i in range(self.controller.get_numhats()):
                self.hat_data[i] = (0, 0)

        # states
        """Listen for events to happen"""
        while True:
            # t = time.time()
            for event in pygame.event.get():
                if event.type == pygame.JOYAXISMOTION:
                    self.axis_data[event.axis] = int(event.value*10)
                elif event.type == pygame.JOYBUTTONDOWN:
                    self.button_data[event.button] = True
                elif event.type == pygame.JOYBUTTONUP:
                    self.button_data[event.button] = False
                elif event.type == pygame.JOYHATMOTION:
                    self.hat_data[event.hat] = event.value

                # Insert your code on what you would like to happen for each event here!
                # In the current setup, I have the state simply printing out to
                # the screen.

                os.system('clear')
                # print(self.button_data)
                # print(self.axis_data)
                # print(self.hat_data)

                # (pan{0~24}, tilt{1~20}
                leftjoystick_pan = self.axis_data[0]
                leftjoystick_tilt = self.axis_data[1]
                leftjoystick_pan_abs = abs(leftjoystick_pan)
                leftjoystick_tilt_abs = abs(leftjoystick_tilt)
                vv = math.floor(leftjoystick_pan_abs/10 * 12)
                ww = math.floor(leftjoystick_tilt_abs)
                if self.button_data[5] == False:
                    if vv != 0:
                        vv += 12
                    if ww != 0:
                        ww += 10

                # p = 0(low) - 7(high)
                tele_speed = round(self.axis_data[4] / 10 * 7)
                wide_speed = round(self.axis_data[5] / 10 * 7)
                # cmd display
                # print('{}   {}'.format(vv, ww), end='\r', flush=True)
                
                # drive
                x = decTohex(leftjoystick_pan,leftjoystick_pan_abs)
                y = decTohex(leftjoystick_tilt,leftjoystick_tilt_abs)

                if (leftjoystick_pan == 0 and leftjoystick_tilt == 0):
                    self.ptz.pt_stop(vv, ww)
                elif (leftjoystick_pan != 0 and leftjoystick_tilt != 0):
                    self.ptz.ptdrive_relative_pos(vv, ww, x, y)
                print(x,y,end='\r')
                # zoom
                if tele_speed > 0:
                    self.ptz.tele(tele_speed)
                elif wide_speed > 0:
                    self.ptz.wide(wide_speed)
                elif tele_speed == 0 or wide_speed == 0:
                    self.ptz.zoomstop()
                # home
                if self.button_data[12]:
                    self.ptz.home()
                # termination
                if self.button_data[8] and self.button_data[9]:
                    del self.ptz
                    exit()

                # print(self.axis_data[2], self.axis_data[3])
                # print(self.axis_data[4], self.axis_data[5])
            # print('{}ms'.format(int((time.time()-t)*1000)), end='\r', flush=True)
def decTohex(d,abs_d):
    try:
        return '{:04X}'.format(int(d/abs_d) & 0xffff)
    except:
        return '0000'

if __name__ == "__main__":
    ps4 = PS4Controller()
    ps4.init()
    ps4.listen()
