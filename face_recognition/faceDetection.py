import cv2
import numpy as np
import os
import face_recognition

def process(frame,status):
    if status==0:
        face_cascade = cv2.CascadeClassifier('./haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        if len(faces)>0:
              # for (x, y, w, h) in faces:
              #     img = cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
              #     # 重设置图像尺寸 200*200
              #     f = cv2.resize(gray[y:y + h, x:x + w], (200, 200))
              #     cv2.imwrite('./%s.jpg' % str(0), f)
              cv2.imwrite('./%s.jpg'%str(0),frame)
              first_image = face_recognition.load_image_file("./0.jpg")
              first_encoding = face_recognition.face_encodings(first_image)
              if(len(first_encoding)>0):
                  return True
              else:
                  return False
        else:
            return False
    if status==1:
        face_cascade = cv2.CascadeClassifier('./haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        if len(faces)>0:
             # for (x, y, w, h) in faces:
             #    img = cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
             #    # 重设置图像尺寸 200*200
             #    f = cv2.resize(gray[y:y + h, x:x + w], (200, 200))
             cv2.imwrite('./%s.jpg' % str(1), faces)
             print("开始检测！")
             first_image = face_recognition.load_image_file("./0.jpg")
             second_image = face_recognition.load_image_file("./1.jpg")
             first_encoding = face_recognition.face_encodings(first_image)[0]
             print(type(first_encoding))
             second_encoding = face_recognition.face_encodings(second_image)[0]
             if(len(second_encoding)>0):
                 results = face_recognition.compare_faces([first_encoding], second_encoding,0.8)
                 print("相似性：")
                 return results[0]
             else:
                 return False;
        else:
            return False


