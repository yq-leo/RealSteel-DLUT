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
# thread safe queue
g_frame_cache = queue.Queue()
g_res_from_yolo = queue.Queue()

# ---------------------------------------------------------
import numpy as np
import cv2
#import yolo
import detect

def process():
    detect.YoloDet(g_frame_cache, g_res_from_yolo)

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
        s.bind(('', network.s_port))
        s.listen(10)
    except socket.error as msg:
        print (msg)
        sys.exit(1)
    print ('Waiting connection...')

    while 1:
        conn, addr = s.accept()
        t = threading.Thread(target = deal_data, args=(conn, addr))
        t.start()

def deal_data(conn, addr):
    print('Accept new connection frochem {0}'.format(addr))
    welcome_msg = 'Hi, Welcome to the server!'
    conn.send(welcome_msg.encode())
    
    payload_size = struct.calcsize(">L")
    data = b''
    while 1:        
        while len(data) < payload_size:
        	data+=conn.recv(4096)
        
        print("Done Recv: {}".format(len(data)))
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack(">L", packed_msg_size)[0]
        print("msg_size: {}".format(msg_size))
        while len(data) < msg_size:
        	data += conn.recv(4096)
        frame_data = data[:msg_size]
        data = data[msg_size:]
        
        frame = pickle.loads(frame_data, fix_imports = True, encoding = "bytes")
        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
        g_frame_cache.put(frame)
        
# ---------------------------------------------------------

def rescale_frame(frame, percent=75):
    	width = int(frame.shape[1] * percent/ 100)
    	height = int(frame.shape[0] * percent/ 100)
    	dim = (width, height)
    	return cv2.resize(frame, dim, interpolation =cv2.INTER_AREA)


import convertYoloResToCmd
def sendCommand(network):
	client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	while 1:
		if not g_res_from_yolo.empty():
			yoloRes = g_res_from_yolo.get()
			cmd = convertYoloResToCmd.process(yoloRes)
			# send
			client_socket.sendto(cmd.encode(), (network.r_ip, network.r_port))				
			

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--r_ip', type = str, default = '10.5.86.36', help = 'robot IP')
    parser.add_argument('--r_port', type = int, default = 63266, help = 'robot port')
    parser.add_argument('--s_port', type = int, default = 63265, help = 'server port')
    network = parser.parse_args()
    
    p1 = threading.Thread(target = socket_service, args = (network, ))
    p1.start()
    p2 = threading.Thread(target = process, args = ())
    p2.start()
    #p3 = threading.Thread(target = GetRes, args = ())
    #p3.start()
    p4 = threading.Thread(target = sendCommand, args = (network, ))
    p4.start()    	
    	
    	
    	
