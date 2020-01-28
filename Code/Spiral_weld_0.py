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
import pyfirmata 

robot = Robot("192.168.0.20", True)
arduino = serial.Serial('/dev/cu.usbmodem144201', 9600)

#board = Arduino('/dev/cu.usbmodem144101')
#it = util.Iterator(board)

board = pyfirmata.Arduino('/dev/cu.usbmodem144201')
it = pyfirmata.util.Iterator(board)
it.start()

induxion_sensor = board.get_pin('a:0:0')
end_switch = board.get_pin('a:1:0')
induxion_end_switch = board.get_pin('a:2:0')



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
    
    if length == 0 or length == 1:
        length = 2
         
    print('Length of quarter circle =', length)
    print('-------------------------')
    
    x_weld = x_cir[0:length]
    y_weld = y_cir[0:length]
    
    pose_list = []
    
    rx_list = np.linspace(start[3], weld[3], length)# abs(math.pi-abs(weld[3])) + math.pi, length) #((y / radius)+1) * math.pi, length)
    
    x_list = np.linspace(start[0], weld[0], length)
    
    for i in range(0, length):
          
        x = x_list[i] 
        y = start[1] + (x_weld[i] - x_weld[0])
        z = start[2] + (y_weld[i] - y_weld[0])
        rx = rx_list[i]
        ry = start[4]
        rz = start[5]

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
    
    rx_list = np.linspace(abs(pos[3]), 0.5*math.pi, len(x_cir))
    
    for i in range(0,len(y_cir)):
    
        x = pos[0] 
        y = pos[1] + x_cir[i]/1000 
        z = pos[2] + (y_cir[i]/1000 - y_cir[0]/1000)
        rx = rx_list[i]
        ry = pos[4]
        rz = pos[5]

        pose_list += [[x, y, z, rx, ry, rz]]
    return pose_list

def grindsetup(r, pos):
    
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
        ry = pos[4]
        rz = pos[5]

        pose_list += [[x, y, z, rx, ry, rz]]
    return pose_list

def spiralcoords(start, weldpos):
    x = abs(start[1] - weldpos[1]) * 1000
    y = abs(start[2] - weldpos[2]) * 1000
    z = abs(start[0] - weldpos[0]) * 1000
    return x, y, z

def sensor_grind_coords(sensor):
    x = sensor[0]
    y = sensor[1]
    z = sensor[2]
    rx = sensor[3]
    ry = sensor[4]
    rz = sensor[5]
    grindcoord = [x - 0.375, y - 0.00, z + 0.013, 3.14, 0.0, -0.244]
    return grindcoord

def offset(sensor, x1, y1, z1):
    x = sensor[0]
    y = sensor[1]
    z = sensor[2]
    rx = sensor[3]
    ry = sensor[4]
    rz = sensor[5]
    grindcoord = [x + x1, y + y1, z + z1, rx, ry, rz]
    return grindcoord

def arduinocheck():
            
    print('Checking arduino......')
    print('-------------------------')
        
    for i in range(0,100):
        data = arduino.readline().decode(encoding="utf-8", errors='ignore').rstrip("\r\n")
        data = str.split(data)
        i+=1
        print(data)
    return data


def induxion():  
#    board.analog[0].enable_reporting()
#    indux = float(board.analog[0].read())
    
#    data1 = arduino.readline().decode(encoding="utf-8", errors='ignore').rstrip("\r\n")      
#    data =  str.split(data1)
#    indux = int(data[0])
#    print('Inudxion sensor data -', indux)
#    return indux
    data = induxion.read()
    print('Induxion data =', data)
    
    return (float(data))

def switch():    
#    data1 = arduino.readline().decode(encoding="utf-8", errors='ignore').rstrip("\r\n")
#    data =  str.split(data1)
#    
#    try:
#        switch = int(data[1])
#    except IndexError:
#        switch = 300
#    except ValueError:
#        switch = 300
#    
#    print('End switch data =', switch)
#    return switch 
    data = end_switch.read()
    print('End switch data =', data)
    
    return (float(data))

def endstop_grinder():
#    board.analog[2].enable_reporting()
#    switch = float(board.analog[2].read()
    
#    data1 = arduino.readline().decode(encoding="utf-8", errors='ignore').rstrip("\r\n")
#    data =  str.split(data1)
#    try:
#        switch = int(data[2])
#    except IndexError:
#        switch = 300
#    
#    print('End switch data =', switch)
#    return switch

    data = induxion_end_switch.read()
    print('End switch data =', data)
    
    return (float(data))

def weldfunction(startgrinder, welposgrinder, r, vel, acc):
    
    startpos = offset(startgrinder, 0, 0, 0.025)
    welpos = offset(welposgrinder, 0, 0, 0.025)
    
    robot.movels(spiralback(startpos, welpos, r + 78), vel = vel, acc = acc)
    robot.movels(spiralcoordinates(startgrinder, welposgrinder, r + 78), vel = vel, acc = acc)

    startpos = offset(startgrinder, 0, 0, 0.020)
    welpos = offset(welposgrinder, 0, 0, 0.020)   
    
    robot.movels(spiralback(startpos, welpos, r + 78), vel = vel, acc = acc)
    robot.movels(spiralcoordinates(startgrinder, welposgrinder, r + 78), vel = vel, acc = acc)
    
    startpos = offset(startgrinder, 0, 0, 0.015)
    welpos = offset(welposgrinder, 0, 0, 0.015) 
    
    robot.movels(spiralback(startpos, welpos, r + 78), vel = vel, acc = acc)
    robot.movels(spiralcoordinates(startgrinder, welposgrinder, r + 78), vel = vel, acc = acc)
    
    startpos = offset(startgrinder, 0, 0, 0.010)
    welpos = offset(welposgrinder, 0, 0, 0.010) 
    
    robot.movels(spiralback(startpos, welpos, r + 78), vel = vel, acc = acc)
    robot.movels(spiralcoordinates(startgrinder, welposgrinder, r + 78), vel = vel, acc = acc)
    
    startpos = offset(startgrinder, 0, 0, 0.005)
    welpos = offset(welposgrinder, 0, 0, 0.005) 
    
    robot.movels(spiralback(startpos, welpos, r + 78), vel = vel, acc = acc)
    robot.movels(spiralcoordinates(startgrinder, welposgrinder, r + 78), vel = vel, acc = acc)
    

#def setting_zero_grind(r, pos):
#    
#    pos_y = np.linspace(pos[1], pos[1] - 0.1, 100)
#    rx_list = np.linspace(abs(pos[3]), 1.10*math.pi, 100)
#    
#    pose_list = []
#            
#    for i in range(0, 95):
#    
#        x = pos[0]
#        y = pos_y[i]
#        z = pos[2]
#        rx = rx_list[i]
#        ry = pos[4]
#        rz = pos[5]
#
#        pose_list += [[x, y, z, rx, ry, rz]]
#      
#    return pose_list
    
#def sensor_grind_coords_flipped(sensor):
#    x = sensor[0]
#    y = sensor[1]
#    z = sensor[2]
#    rx = 0
#    ry = 3.14
#    rz = 0
#    grindcoord = [x + 0.175, y, z + 0.040, rx, ry, rz]
#    return grindcoord



