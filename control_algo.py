import socket
from threading import Thread, Event
from time import sleep, time
from queue import Queue
import queue
import numpy as np

Pan_TiltDrive_Up = "81 01 06 01 {:02X} {:02X} 03 01 FF"
Pan_TiltDrive_Down = "81 01 06 01 {:02X} {:02X} 03 02 FF"
Pan_TiltDrive_Left = "81 01 06 01 {:02X} {:02X} 01 03 FF"
Pan_TiltDrive_Right = "81 01 06 01 {:02X} {:02X} 02 03 FF"
Pan_TiltDrive_UpLeft = "81 01 06 01 {:02X} {:02X} 01 01 FF"
Pan_TiltDrive_UpRight = "81 01 06 01 {:02X} {:02X} 02 01 FF"
Pan_TiltDrive_DownLeft = "81 01 06 01 {:02X} {:02X} 01 02 FF"
Pan_TiltDrive_DownRight = "81 01 06 01 {:02X} {:02X} 02 02 FF"
Pan_TiltDrive_Stop = "81 01 06 01 {:02X} {:02X} 03 03 FF"
Pan_TiltDrive_AbsolutePosition = "81 01 06 02 {:02X} {:02X} 0Y 0Y 0Y 0Y 0Z 0Z 0Z 0Z FF"
Pan_TiltDrive_RelativePosition = "81 01 06 03 {:02X} {:02X} 0Y 0Y 0Y 0Y 0Z 0Z 0Z 0Z FF"

Pan_TiltDrive_Home = "81 01 06 04 FF"
Pan_TiltDrive_Reset = "81 01 06 05 FF"

CAM_Zoom_Stop = "81 01 04 07 00 FF"
CAM_Zoom_Tele = "81 01 04 07 02 FF"
CAM_Zoom_Wide = "81 01 04 07 03 FF"
CAM_Zoom_Tele_V = "81 01 04 07 2p FF"
CAM_Zoom_Wide_V = "81 01 04 07 3p FF"
CAM_ZOOM_Direct = "81 01 04 47 0p 0q 0r 0s FF"

CAM_ZoomPosInq = "81 09 04 47 FF"
CAM_PanTiltPosInq = "81 09 06 12 FF"

TCP_IP = '192.168.32.208'
TCP_PORT = 5678


class VISCA():
    def __init__(self, TCP_IP=TCP_IP, TCP_PORT=TCP_PORT):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((TCP_IP, TCP_PORT))
        self.BUFFER_SIZE = 16
        self.sq = Queue(maxsize=3)

    def __del__(self):
        self.sock.close()

    def send(self, str):
        self.sock.send(bytes.fromhex(str))

    def receive(self):
        data = self.sock.recv(self.BUFFER_SIZE)
        return data.hex()

    def wait_finish(self):
        data = self.sock.recv(self.BUFFER_SIZE)
        if len(data) < 6:
            data += self.sock.recv(self.BUFFER_SIZE)
        return data

    def test_response(self, n=100):
        all = []
        for i in range(n):
            self.send(Pan_TiltDrive_Stop.format(0, 0))
            stime = time()
            d = self.wait_finish()
            print(d, d.hex(), len(d), len(d.hex()))
            all.append(time() - stime)
        t = np.array(all)
        return {'avg': np.average(t), 'max': np.max(t), 'min': np.min(t)}


class Cam():
    """
    Use Thread to send and stop the cam command
    """
    def __init__(self, win_size):
        self.visca = VISCA()
        self.threshold = 70
        self.p_speed = 10
        self.t_speed = 3
        self.waittime = 0.1
        self.center = (int(round(win_size[0] / 2)), int(round(win_size[1] * 1 / 3)))
        self.command_q = Queue(maxsize=5)
        # self.stopthread = Thread(target=self.stopping_thread, daemon=True)
        # self.stopping = Event()
        self.sending_thread = Thread(target=self.sending_thread, daemon=True)
        self.sending_thread.start()
        # self.stopthread.start()


    def __del__(self):
        pass


    def stopping_thread(self):
        while True:
            # self.stopping.wait()
            # self.stopping.clear()
            # if self.command_q.empty():
            #     sleep(self.waittime)
            #     if self.comman1000d_q.empty():
            #         self.stop()
            #         # self.cq.put(self.cq.get() + 1)
            #         print("Stop")
            pass

    def sending_thread(self):
        while True:
            # self.stopping.clear()
            # command = self.command_q.get(block=True, timeout=None)
            # self.visca.send(command)
            # self.visca.wait_finish()
            # print("Sent {}".format(command))
            # if self.command_q.empty():
                # sleep(self.waittime)
                # self.stopping.set()
            try:
                command = self.command_q.get(block=True, timeout=self.waittime)
                self.visca.send(command)
                sleep(self.waittime)
            except queue.Empty:
                self.stop()
                print("Stop")



    def p_speed_control(self, diff):
        # self.p_speed = 3 + (abs(diff) - 50) // 50 #pan speed
        pass

    def t_speed_control(self, diff):
        # self.t_speed = 2 + (abs(diff) - 50) // 75 #tile speed
        pass

    def stop(self):
        self.visca.send("81 01 06 01 {:02X} {:02X} 03 03 FF".format(self.p_speed, self.t_speed))
        # self.visca.wait_finish()

    def up(self):
        self.command_q.put(Pan_TiltDrive_Up.format(self.p_speed, self.t_speed))

    def down(self):
        self.command_q.put(Pan_TiltDrive_Down.format(self.p_speed, self.t_speed))

    def left(self):
        self.command_q.put(Pan_TiltDrive_Left.format(self.p_speed, self.t_speed))

    def right(self):
        self.command_q.put(Pan_TiltDrive_Right.format(self.p_speed, self.t_speed))

    def upleft(self):
        self.command_q.put(Pan_TiltDrive_UpLeft.format(self.p_speed, self.t_speed))

    def upright(self):
        self.command_q.put(Pan_TiltDrive_UpRight.format(self.p_speed, self.t_speed))

    def downleft(self):
        self.command_q.put(Pan_TiltDrive_DownLeft.format(self.p_speed, self.t_speed))

    def downright(self):
        self.command_q.put(Pan_TiltDrive_DownRight.format(self.p_speed, self.t_speed))

    # def up(self, diff):
    #     self.p_speed_control(diff)
    #     self.visca.send(Pan_TiltDrive_Up.format(self.p_speed, self.t_speed))
    #     self.visca.wait_finish()
    #
    #
    # def down(self, diff):
    #     self.p_speed_control(diff)
    #     self.visca.send(Pan_TiltDrive_Down.format(self.p_speed, self.t_speed))
    #     self.visca.wait_finish()
    #
    #
    # def left(self, diff):
    #     self.p_speed_control(diff)
    #     self.visca.send(Pan_TiltDrive_Left.format(self.p_speed, self.t_speed))
    #     self.visca.wait_finish()
    #
    #
    # def right(self, diff):
    #     self.p_speed_control(diff)
    #     self.visca.send(Pan_TiltDrive_Right.format(self.p_speed, self.t_speed))
    #     self.visca.wait_finish()
    #
    #
    # def upleft(self, diff1, diff2):
    #     self.p_speed_control(diff1)
    #     self.t_speed_control(diff2)
    #     self.visca.send(Pan_TiltDrive_UpLeft.format(self.p_speed, self.t_speed))
    #     self.visca.wait_finish()
    #
    #
    # def upright(self, diff1, diff2):
    #     self.p_speed_control(diff1)
    #     self.t_speed_control(diff2)
    #     self.visca.send(Pan_TiltDrive_UpRight.format(self.p_speed, self.t_speed))
    #     self.visca.wait_finish()
    #
    #
    # def downleft(self, diff1, diff2):
    #     self.p_speed_control(diff1)
    #     self.t_speed_control(diff2)
    #     self.visca.send(Pan_TiltDrive_DownLeft.format(self.p_speed, self.t_speed))
    #     self.visca.wait_finish()
    #
    #
    # def downright(self, diff1, diff2):
    #     self.p_speed_control(diff1)
    #     self.t_speed_control(diff2)
    #     self.visca.send(Pan_TiltDrive_DownRight.format(self.p_speed, self.t_speed))
    #     self.visca.wait_finish()

    def home(self):
        self.visca.send(Pan_TiltDrive_Home)


# if __name__ == '__main__':
#     visca = VISCA()
#     start_time = time.time()
#     # while True:
#     #     key = getkey.getkey()
#     #     print("{:.3f} : key {}".format(time.time() - start_time, getkey.key.name(key)))
#     #
#     #     action = {
#     #         getkey.keys.HOME: visca.home,
#     #         getkey.keys.ENTER: visca.reset,
#     #         getkey.keys.UP: visca.up,
#     #         getkey.keys.DOWN: visca.down,
#     #         getkey.keys.LEFT: visca.left,
#     #         getkey.keys.RIGHT: visca.right,
#     #         getkey.keys.PAGE_UP: visca.zoomin,
#     #         getkey.keys.PAGE_DOWN: visca.zoomout
#     #     }
#     #     action[key]()


if __name__ == '__main__':

    cam = Cam((1920, 1080))
    for i in range(60):
        cam.right()
        sleep(0.16)
    cam.stop()
    for i in range(60):
        cam.left()
    sleep(3)
