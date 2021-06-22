# -*- coding: utf-8 -*-
"""
Created on Tue Jun 15 10:12:56 2021
@author: QI YU
@email: yq123456leo@outlook.com
"""


import os
path = "C:/Users/surface/Desktop/red pillar"
filelist = os.listdir(path) #该文件夹下所有的文件（包括文件夹）
count=1#设置图片编号从1开始
for file in filelist:#打印出所有图片原始的文件名
    print(file)
for file in filelist:   #遍历所有文件
    Olddir=os.path.join(path,file)   #原来的文件路径
    if os.path.isdir(Olddir):   #如果是文件夹则跳过
        continue
    filename=os.path.splitext(file)[0]   #文件名
    filetype=os.path.splitext(file)[1]   #文件扩展名
    Newdir=os.path.join(path,str(count).zfill(6)+filetype)  #用字符串函数zfill 以0补全所需位数
    os.rename(Olddir,Newdir)#重命名
    count += 1