import socket
import threading
import time
import sys
import os
import struct

import json
import argparse
import pickle

import queue
import numpy as np
import cv2
import detect
import faceDetection


# global variables
global_cache = queue.Queue()
yolo_cache = queue.Queue()
face_cache = queue.Queue()
face_res = queue.Queue()
g_res_from_yolo = queue.Queue()

status = 0
mutex = threading.Lock()        # mutex semaphore for status

def Yolov3():
    detect.YoloDet(yolo_cache, g_res_from_yolo)

def FaceDetect():
    while True:
        frame = face_cache.get()
        res = faceDetection.process(frame, status)
        face_res.put(res)

'''
def GetRes():
    while True:
        res = g_res_from_yolo.get()
        
        for det in res:
            label, xywh = det
            print('Detect: %s Coordinate: %s' % (label, str(xywh)))
'''
	
# ---------------------------------------------------------
def recvall(sock):
    BUFF_SIZE = 4096 # 4 KiB
    data = b''
    while True:
        part = sock.recv(BUFF_SIZE)
        data += part
        if len(part) < BUFF_SIZE:
            # either 0 or end of data
            break         
    return data

def socket_service(network):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('', network.sport))
        s.listen(10)
    except socket.error as msg:
        print (msg)
        sys.exit(1)
    print ('Waiting connection...')

    while 1:
        conn, addr = s.accept()
        t = threading.Thread(target = deal_data, args=(conn, addr, network, ))
        t.start()

def deal_data(conn, addr, network):
    print('Accept new connection frochem {0}'.format(addr))
    welcome_msg = 'Hi, Welcome to the server!'
    conn.send(welcome_msg.encode())
    
    payload_size = struct.calcsize(">L")
    data = b''
    while 1:        
        while len(data) < payload_size:
        	data+=conn.recv(4096)
        
        #print("Done Recv: {}".format(len(data)))
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack(">L", packed_msg_size)[0]
        #print("msg_size: {}".format(msg_size))
        while len(data) < msg_size:
        	data += conn.recv(4096)
        frame_data = data[:msg_size]
        data = data[msg_size:]
        
        frame = pickle.loads(frame_data, fix_imports = True, encoding = "bytes")
        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
        #cv2.imwrite('runs/test/p%d.jpg' % index, frame)
        
        global_cache.put(frame)
        
        
        
        '''
        index += 1
        if index > 4:
            yolo_cache.put(frame)
            cv2.imwrite('runs/test/p%d.jpg' % index, frame)
            print("Receive Frame: %d" % yolo_cache.qsize())
        else:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            cmd = {}
            client_socket.sendto(json.dumps(cmd).encode(), (network.rip, network.rport))
        '''
        
# ---------------------------------------------------------

def rescale_frame(frame, percent=75):
    	width = int(frame.shape[1] * percent/ 100)
    	height = int(frame.shape[0] * percent/ 100)
    	dim = (width, height)
    	return cv2.resize(frame, dim, interpolation =cv2.INTER_AREA)


import convertYoloResToCmd
def sendCommand(network):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    colors = ['red', 'green', 'yellow']; pointer = 0
    current_color = colors[pointer]
    print(current_color)
    #current_color = 'pillar'
    
    last = False
    while 1:
        global status
        mutex.acquire()
        if status == 0:
            mutex.release()
            f_res = face_res.get()
            if f_res:
                mutex.acquire()
                status = 2
                print('changed status: %d' % status)
                mutex.release()
                cmd = {'Status Change': 1}
                client_socket.sendto(json.dumps(cmd).encode(), (network.rip, network.rport))
            else:
                cmd = {'Status Remain': 1}
                client_socket.sendto(json.dumps(cmd).encode(), (network.rip, network.rport))
        
        elif status == 2:   
            mutex.release()
            yoloRes = g_res_from_yolo.get()
            cmd, flag = convertYoloResToCmd.process(yoloRes, current_color, last)
            print(cmd)
            # send
            client_socket.sendto(json.dumps(cmd).encode(), (network.rip, network.rport))
            if flag:
                mutex.acquire()
                status = 1
                mutex.release()
        
        elif status == 1:
            mutex.release()
            has_face, f_res = face_res.get()
            if has_face:
                if f_res:
                    mutex.acquire()
                    status = 3
                    mutex.release()
                    
                    current_color = 'white'
                    cmd['ACT'] = 0
                    cmd['ACT2'] = 3
                    client_socket.sendto(json.dumps(cmd).encode(), (network.rip, network.rport))
                else:
                    mutex.acquire()
                    status = 2
                    mutex.release()
                    
                    pointer += 1
                    if pointer < len(colors):
                        current_color = colors[pointer]
                    else:
                        break
                    
                    cmd = {'ACT': 3}
                    print(cmd)
                    client_socket.sendto(json.dumps(cmd).encode(), (network.rip, network.rport))
            
            else:
                cmd = {'ACT': 1}
                client_socket.sendto(json.dumps(cmd).encode(), (network.rip, network.rport))
        
        elif status == 3:
            mutex.release()
            yoloRes = g_res_from_yolo.get()
            cmd, flag = convertYoloResToCmd.FinalDrop(yoloRes, last)
            print(cmd)
            client_socket.sendto(json.dumps(cmd).encode(), (network.rip, network.rport))
            if flag:
                print('Job Done!')
                sys.exit(1)
        
        else:
            mutex.release()

def Deliver():
    while True:
        frame = global_cache.get()
        mutex.acquire()
        if (status == 0) or (status == 1):
            print('wrong deliver status: %d' % status)
            mutex.release()
            face_cache.put(frame)
        else:
            print('right deliver status: %d' % status)
            mutex.release()
            yolo_cache.put(frame)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--rip', type = str, default = '192.168.43.45', help = 'robot IP')
    parser.add_argument('--rport', type = int, default = 63266, help = 'robot port')
    parser.add_argument('--sport', type = int, default = 63265, help = 'server port')
    network = parser.parse_args()
    
    p1 = threading.Thread(target = socket_service, args = (network, ))
    p1.start()
    p2 = threading.Thread(target = Deliver, args = ())
    p2.start()
    p3 = threading.Thread(target = Yolov3, args = ())
    p3.start()
    p4 = threading.Thread(target = FaceDetect, args = ())
    p4.start()
    p5 = threading.Thread(target = sendCommand, args = (network, ))
    p5.start()    	
    	
    	
    	
