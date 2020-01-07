k#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 17 10:53:02 2019

@author: wouter
"""

from urx import Robot
import numpy as np
import math
from Spiral_weld_0 import *

#XYZ coordinates of spiral weld end
x, y, z = [180,100,150]

#Iterations
it = 500

#Radius of the pipe
r = 230

#Starting position
start = [-0.7550, 0.00384, 0.57738, math.pi, 0, 0]
start_circle = [-0.7550 - 0.150, -0.00384, 0.57738, math.pi, 0, 0]

#Arcmovements
spiral_move = spiralweld(x, y, z, it, r, start)
spiral_move_back = spiralweldback(x, y, z, it, r, start)

if __name__ == "__main__":
    
    robot = Robot("192.168.0.20", True)
    
    try:
            
        print('Moving to start position')
        
        robot.movel(start)
        
        print('Moving 150 mm in y direction')
        
        robot.movel([-0.150,0,0,0,0,0], relative = True)
        
        print('Weld is not detected')
            
        quartercircle(230, start_circle, 'iterated')
        
        print('Weld is detected')
        
        robot.movels(quartercircle(230, start_circle), vel = 2, acc = 0.5)
        
        print('Going to start position')
        
        robot.movel(start, vel = 2, acc = 0.5)
        
        print('Grinding...')
        
        robot.movels(spiral_move)
        robot.movels(spiral_move_back)
        
        
    finally:
        print('Movement done')
        robot.close() 





    