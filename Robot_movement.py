#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 17 10:53:02 2019

@author: wouter
"""

from urx import Robot
import numpy as np
import math
from Spiral_weld_0 import *
import time
import serial

#Radius of the pipe
r = 328 

#Starting position
start = [0.708, 0.155, 0.000, math.pi, 0, 0]

if __name__ == "__main__":
    
    robot = Robot("192.168.0.20", True)
    
    try:
            
        print('-------------------------')
        print('Setting TCP to [0, 0, 0]')
        print('-------------------------')
    
        robot.set_tcp([0,0,0,0,0,0])
        
        print('Moving to start position......')
        print('-------------------------')
        
        robot.movel(start, vel = 2.0, acc = 1.0)
        arduinocheck()
        
        robot.movel([0, 0, -0.500, 0, 0, 0], relative = True, wait = False, vel = 0.003, acc = 1)
        
        print('End switch checking...')
        print('-------------------------')
    
        while True:                   
            if switch() >= 300:
                robot.stop()
                print('Found the pipe!')
                print('-------------------------')
                start = robot.getl()
                break
        
        print('Moving 15 cm forward......')
        print('-------------------------')
        
        robot.movel([-0.150,0,0,0,0,0], relative = True)#, vel = 2.0, acc = 1.0)
        start_circle = robot.getl()
        
        print('Searching for weld......')
        print('-------------------------')

        arduinocheck()
        robot.movels(quartercircle(r, start_circle), wait = False)
             
        while True:           
            if induxion() <= 3:
                robot.stop()
                print('Found the weld!')
                print('-------------------------')
                welpos = robot.getl()
                x, y, z = spiralcoords(start, welpos)
                break
        
        robot.movel([0,0,y/1000,0,0,0], relative = True)#, vel = 2.0, acc = 1.0)
        robot.movel(start)#, vel = 2.0, acc = 1.0)
        robot.movels(spiralcoordinates(start, welpos, r))
        robot.movels(spiralback(start, welpos, r))
        
    finally:
        print('Movement done')
        robot.close() 





    
