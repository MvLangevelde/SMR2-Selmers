#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 13 18:02:54 2019

@author: wouter
"""
import numpy as np
import math 
from urx import Robot
import serial

robot = Robot("192.168.0.20", True)
arduino = serial.Serial('/dev/cu.usbmodem144201', 9600)

def spiralcoordinates(start, weld, radius1):
    
    radius = radius1 / 1000
    
    theta = np.linspace(0, 2*np.pi, 1000)
    
    radius = np.sqrt(radius**2)
    
    xr = radius*np.cos(theta)
    yr = radius*np.sin(theta)
    
    x_cir1 = xr[0:250]
    y_cir1 = yr[0:250]
    x_cir = x_cir1[::-1]
    y_cir = y_cir1[::-1]
    
    x = abs(start[0] - weld[0]) 
    y = abs(start[1] - weld[1])
    z = radius - abs(start[2] - weld[2]) 
    
    print('Spiralweld coordinate =', [x, y, z])
    
    length = int(250 - ((math.atan(z/y)) * (125 / (0.25 * math.pi))))
         
    print('Length of quarter circle =', length)
    print('Angle of rx =', abs(math.pi-abs(weld[3])) + math.pi )
    print('-------------------------')
    
    x_weld = x_cir[0:length]
    y_weld = y_cir[0:length]
    
    pose_list = []
    
    rx_list = np.linspace(start[3], abs(math.pi-abs(weld[3])) + math.pi, length) #((y / radius)+1) * math.pi, length)
    
    x_list = np.linspace(start[0], weld[0], length)
    
    for i in range(0, length):
          
        x = x_list[i] 
        y = start[1] - (x_weld[i] - x_weld[0])
        z = start[2] + (y_weld[i] - y_weld[0])
        rx = rx_list[i]
        ry = 0
        rz = 0

        pose_list += [[x, y, z, rx, ry, rz]]
                   
    return pose_list   

def spiralback(start, weld, radius1):
    pose_list = spiralcoordinates(start, weld, radius1)
    pose_list_back = pose_list[::-1]
    return pose_list_back

def quartercircle(r, pos):
    
    print('Searching for weld......')
    print('-------------------------')
    
    theta = np.linspace(0, 2*np.pi, 1000)
    
    radius = np.sqrt(r**2)
    
    x = radius*np.cos(theta)
    y = radius*np.sin(theta)
    
    x_cir1 = x[0:250]
    y_cir1 = y[0:250]
    x_cir = x_cir1[::-1]
    y_cir = y_cir1[::-1]
    
    pose_list = []
    
    rx_list = np.linspace(abs(pos[3]), 1.5*math.pi, len(x_cir))
    
    for i in range(0,len(y_cir)):
    
        x = pos[0]
        y = pos[1] - x_cir[i]/1000 
        z = pos[2] + (y_cir[i]/1000 - y_cir[0]/1000)
        rx = rx_list[i]
        ry = 0
        rz = 0

        pose_list += [[x, y, z, rx, ry, rz]]
                           
    return pose_list

def arduinocheck():
            
    print('Checking arduino......')
    print('-------------------------')
    
    for i in range(0,30):
        arduino = serial.Serial('/dev/cu.usbmodem144201', 9600)
        data = arduino.readline().decode(encoding="utf-8", errors='ignore').rstrip("\r\n")
        i+=1
    return data

def spiralcoords(start, weldpos):
    x = abs(start[1] - weldpos[1]) * 1000
    y = abs(start[2] - weldpos[2]) * 1000
    z = abs(start[0] - weldpos[0]) * 1000
    return x, y, z

def induxion():  
    data1 = arduino.readline().decode(encoding="utf-8", errors='ignore').rstrip("\r\n")      
    data =  str.split(data1)
    indux = int(data[0])
    return indux

def switch():
    data1 = arduino.readline().decode(encoding="utf-8", errors='ignore').rstrip("\r\n")
    data =  str.split(data1)
    switch = int(data[1])
#    print('End switch data =', switch)
    return switch
