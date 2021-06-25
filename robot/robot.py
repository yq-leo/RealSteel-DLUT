'''
Author: your name
Date: 2021-06-24 15:55:55
LastEditTime: 2021-06-25 15:25:28
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: /login/Users/mac/Desktop/sycTest.py
'''
'''
Author: your name
Date: 2021-06-24 15:55:55
LastEditTime: 2021-06-24 15:55:56
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: /login/Users/mac/Desktop/sycTest.py
'''
import socket  
import time 
import sys
import json
from robotPi import robotPi
from robotpi_serOp import serOp
from Sodiers_client import Client

import queue

g_check = queue.Queue()


class Soldiers(robotPi):
    def __init__(self):
        print("Sir, yes sir!")
        super().__init__()
        
        self.ser = serOp()

    def attention(self):
        PORT = 63266
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        address = ('', PORT)  
        server_socket.bind(address)  
        server_socket.settimeout(10)
        n = 0
        while True:
            try:  
                now = time.time()
                receive_data, client = server_socket.recvfrom(1024)
                cmd = json.loads(receive_data.decode())
                print(cmd)
                #if(n >= 4):
                self.take_commands(cmd)
                #else:
                    #soldier.movement.turn_left(10, 100)
                g_check.get(1)
                n += 1
            except socket.timeout: 
                print ("tme out")
        soldier.movement.wave_hands()

    def take_commands(self, order):
        if(len(order) == 0):
            # soldier.movement.turn_left(30, 200)
            time.sleep(10)
            return
        key = list(order.keys());
        if "MF" in key:
            soldier.movement.move_forward(70, order["MF"])
        elif "TL" in key:
            soldier.movement.turn_left(40, order["TL"])
        elif "TR" in key:
            soldier.movement.turn_right(40, order["TR"])
        elif order["cmd"] == "b":
            soldier.movement.move_backward(50, order["time"])
        elif order["cmd"] == "tl":
            soldier.movement.turn_left(50, order["time"])
        elif order["cmd"] == "tr":
            soldier.movement.turn_right(50, order["time"])
        elif "ACT" in key:
            soldier.movement.take_action(50, order["ACT"])
        # time.sleep(0.5)

soldier = Soldiers()

import cv2
import io
import socket
import struct
import time
import pickle
import zlib

def camera():
    SERVE_HOST = '10.5.233.175'
    SERVE_PORT = 63265

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVE_HOST, 63265))
    connection = client_socket.makefile('wb')

    cam = cv2.VideoCapture(0)

    img_counter = 0

    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
    
    flag = 0

    while True:
        
        if not g_check.empty():
            continue
        g_check.put(1)
        for i in range(10):
            ret, frame = cam.read()
            time.sleep(0.1)
        frame = rescale_frame(frame, 50)
        result, frame = cv2.imencode('.jpg', frame, encode_param)
        data = pickle.dumps(frame, 0)
        size = len(data)
        print("{}: {}".format(img_counter, size))
        client_socket.sendall(struct.pack(">L", size) + data)
        img_counter += 1
        time.sleep(1)
    cam.release()

def rescale_frame(frame, percent=75):
    width = int(frame.shape[1] * percent/ 100)
    height = int(frame.shape[0] * percent/ 100)
    dim = (width, height)
    return cv2.resize(frame, dim, interpolation =cv2.INTER_AREA)	

def recv() :
    soldier.attention()
   
import threading
if __name__ == "__main__":
    p1 = threading.Thread(target=recv, args=())
    p1.start()
    p2 = threading.Thread(target=camera, args=())
    p2.start()
    exit(0)

