import cv2
import numpy as np
import os
import face_recognition

def process(frame,status):
    if status == 0:
        face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        if len(faces)>0:
              cv2.imwrite('./%s.jpg'%str(0),frame)
              first_image = face_recognition.load_image_file("./0.jpg")
              first_encoding = face_recognition.face_encodings(first_image)
              if(len(first_encoding)>0):
                  print("检测到人脸！")
                  return True
              else:
                  print("检测到人脸，拍照不标准！")
                  return False
        else:
            print("未检测到人脸！")
            return False
        
    if status == 1:
        face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        if len(faces)>0:
             cv2.imwrite('./%s.jpg' % str(1), frame)
             print("开始检测！")
             first_image = face_recognition.load_image_file("./0.jpg")
             second_image = face_recognition.load_image_file("./1.jpg")
             first_encoding = face_recognition.face_encodings(first_image)[0]
             print(type(first_encoding))
             second_encoding = face_recognition.face_encodings(second_image)
             if(len(second_encoding) > 0):
                 results = face_recognition.compare_faces([first_encoding], second_encoding[0],0.5)
                 print("相似性：")
                 return True, results[0]
             else:
                 print("拍摄到的人脸不标准！")
                 return False, False;
        else:
            print("未拍摄到人脸！")
            return False, False

if __name__ == "__main__":
    status = 1      # 0: set out 1: start detect 2: do nothing
    frame = cv2.imread('joey.jpg')
    flag = process(frame, status)
    print(flag)


