#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 17 10:53:02 2019

@author: wouter
"""

from urx import Robot
from Spiral_weld_0 import *
import time
import serial

#Radius of the pipe
r = 320

#Starting position
start = [1.345, -0.168, -0.030, 3.13, 0.00, 0.00]

if __name__ == "__main__":
    
    robot = Robot("192.168.0.20", True)
    
    try:
        print('Initializing......')
        print('-------------------------')
        
        #Initializing the voltages to zero
        robot.set_analog_out(0, 0.0)
        robot.set_analog_out(1, 0.0)
        robot.set_tool_voltage(0)
        robot.set_digital_out(1, False)
        
        time.sleep(1)
        
        print('Moving to start position......')
        print('-------------------------')
        
        #Move to the common start position
        robot.movel(start, vel = 1.0, acc = 1.0)
                
        arduinocheck()
        
        #Move down till the endswitch hits the pipe
        robot.movel([0, 0, -0.500, 0, 0, 0], relative = True, wait = False, vel = 0.007, acc = 1)
        
        print('End switch checking...')
        print('-------------------------')
        
        while True:                   
            if switch() <= 3:
                robot.stop()
                print('Found the pipe!')
                print('-------------------------')
                robot.movel([0, 0, -0.010, 0, 0, 0], relative = True, vel = 0.003, acc = 1)
                start = robot.getl()
                startgrinder = sensor_grind_coords(start)
                startgrinder_offset = offset(startgrinder, 0, 0, 0.030)      
                arduinocheck()
                break
        
        ############################################
        
        print('Rotating pipe......')
        print('-------------------------')
                
        #Put the rotator on, stop if the induxion sensor finds the weld
        robot.set_analog_out(0, 0.5)
        
        print('Searching for weld......')
        print('-------------------------')
        
        while True:
            if induxion() <= 3:
                robot.set_analog_out(0, 0)
                print('Found the weld!')
                print('-------------------------')
                break
            
        ############################################
        
        print('Moving 15 cm forward......')
        print('-------------------------')
        
        #Move up and go ... cm forward for the second coordinate of the weld
        robot.movel([0, 0, 0.03, 0, 0, 0], relative = True)
        robot.movel([-0.110,0.0,0,0,0,0], relative = True, wait = True, vel = 2.0, acc = 1.0)
        robot.movel([0, 0, -0.03, 0, 0, 0], relative = True)
        
        #Beginningpoint for weld searching
        start_circle = robot.getl()
                
        print('Searching for weld......')
        print('-------------------------')
            
        #Start searching for the second weld coordinate, stop if the induxion sensor finds the weld
        arduinocheck()
        
        robot.movels(quartercircle(r, start_circle), wait = False)
             
        while True:           
            if induxion() <= 3:
                robot.stop()
                print('Found the weld!')
                print('-------------------------')
                welpos = robot.getl()
                welposgrinder = sensor_grind_coords(welpos)
                welposgrinder_offset = offset(welposgrinder, 0, 0, 0.030)
                x_w, y_w, z_w = spiralcoords(start, welpos)
                break
            
        ############################################
 
        print('Moving to start position for grinding......')
        print('-------------------------')
        
        #Move to a safe position to start the grinding process
        robot.movel([0,0,y_w/1000 + 0.090,0,0,0], relative = True)#, vel = 2.0, acc = 1.0)
        robot.movel(startgrinder_offset, vel = 2.0, acc = 1.0)
        
        #Go to a position next to the weld to calibrate the grinder
        robot.movels(grindsetup(r + 78, startgrinder_offset), wait = False)
        time.sleep(10)
        robot.stop()
        
        #Move down untill the induxion sensor finds the pipe
        #robot.movel([0, 0, -0.500, 0, 0, 0], relative = True, wait = False, vel = 0.003, acc = 1)
        arduinocheck()
        robot.translate_tool([0,0,1], vel = 0.002, acc = 1, wait = False)
        
        while True:
            if endstop_grinder() <= 50:
                robot.stop()
                robot.translate_tool([0,0,-0.004], vel = 0.002, acc = 1, wait = False)
                print('Reached orientation point')
                print('-------------------------')
                time.sleep(1)
                robot.set_digital_out(1, True)
                break
            
        ############################################
        
        #Ready to grind...
        
        print('Going to grinding point')
        print('-------------------------')      
        
        #Move up from orientation point
        robot.movel([0, 0, 0.04, 0, 0, 0], relative = True)#, vel = 2.0, acc = 1.0)
        
        #Move to the beginning of the weld
        robot.movel(startgrinder_offset, vel = 2.0, acc = 1.0)
         
        #Move to the x position of the second weldpoint
        robot.movel([0, 0 + (x_w / 1000), 0, 0, 0, 0], relative = True, vel = 2.0, acc = 1.0)
        
        welposgrinder_offset = offset(welposgrinder_offset, 0.03, 0, 0)
        startgrinder_offset = offset(startgrinder_offset, 0.03, 0, 0)
        welposgrinder = offset(welposgrinder, 0.03, 0, 0)
        startgrinder = offset(startgrinder, 0.03, 0, 0)
        
        #Move to the second weldpoint to start grinding
        robot.movel(welposgrinder_offset, vel = 2.0, acc = 1.0)
        
        welposgrinder_1 = offset(welposgrinder, 0, 0, 0.005)
        startgrinder_1 = offset(startgrinder, 0, 0, 0.005)
        
        welposgrinder_2 = offset(welposgrinder, 0, 0, 0.002)
        startgrinder_2 = offset(startgrinder, 0, 0, 0.002)
        
        #Set grinder
        robot.set_analog_out(1, 0.5)
        
        arduinocheck()
        
        #Grind the weld....
        robot.movels(spiralback(startgrinder_1, welposgrinder_1, r + 78), vel = 0.010, acc = 0.2)#, vel = 0.005, acc = 1)
        robot.movel([0.04, -((40*x_w)/z_w)/1000, ((40*y_w)/z_w)/1000, 0, 0, 0], relative = True)
        
        robot.movel([0, 0, 0.04, 0, 0, 0], relative = True, vel = 2.0, acc = 1.0)
        robot.movel([0, 0 + (x_w / 1000), 0, 0, 0, 0], relative = True, vel = 2.0, acc = 1.0)
        robot.movel(welposgrinder_offset, vel = 2.0, acc = 1.0)
        
        robot.movels(spiralback(startgrinder_2, welposgrinder_2, r + 78), vel = 0.005, acc = 0.2)#, vel = 0.005, acc = 1)
        robot.movel([0.04, -((40*x_w)/z_w)/1000, ((40*y_w)/z_w)/1000, 0, 0, 0], relative = True)
        
        robot.movel([0, 0, 0.010, 0, 0, 0], relative = True, vel = 2.0, acc = 1.0)
        robot.movel([0, 0 + (x_w / 1000), 0, 0, 0, 0], relative = True, vel = 2.0, acc = 1.0)
        robot.movel(welposgrinder_offset, vel = 2.0, acc = 1.0)
        
        robot.movels(spiralback(startgrinder, welposgrinder, r + 78), vel = 0.010, acc = 0.2)#, vel = 0.005, acc = 1)
        robot.movel([0.04, -((40*x_w)/z_w)/1000, ((40*y_w)/z_w)/1000, 0, 0, 0], relative = True)
#        
        robot.movel([0, 0, 0.04, 0, 0, 0], relative = True, vel = 2.0, acc = 1.0)
        
#        robot.movel([0.100, 0, 0, 0, 0, 0], relative = True, wait = False)
#        
#        while True:
#            if endstop_grinder() > 50:
#                robot.movel([0.05, -, 0, 0, 0, 0], relative = True)
#                robot.movel([0, 0, 0.05, 0, 0, 0], relative = True)
#                robot.movel(welposgrinder_offset)#, vel = 2.0, acc = 1.0)
#                print('Reached end of the weld')
#                print('-------------------------')
#                break
            
#        robot.movels(spiralback(startgrinder, welposgrinder, r + 78))#, vel = 0.005, acc = 1)
#        robot.movel([0.100, 0, 0, 0, 0, 0], relative = True, wait = False)
#        
#        while True:
#            if endstop_grinder() <= 50:
#                robot.movel([0.05, ((x_w/1000) / (z_w/1000) ), 0, 0, 0, 0], relative = True)
#                robot.movel([0, 0, 0.05, 0, 0, 0], relative = True)
#                robot.movel(welposgrinder_offset, vel = 2.0, acc = 1.0)
#                print('Reached end of the weld')
#                print('-------------------------')
#                break
        
        
        
#        robot.movel([0, 0, 0.03, 0, 0, 0], relative = True)
#        robot.movel(welposgrinder_offset, vel = 2.0, acc = 1.0)
#        
#        robot.movels(spiralback(startgrinder, welposgrinder, r + 78))
#        robot.movel([0.040, 0, 0., 0, 0, 0], relative = True)
#        
#        robot.movel([0, 0, 0.03, 0, 0, 0], relative = True)
#        robot.movel(welposgrinder_offset, vel = 2.0, acc = 1.0)
#        
#        robot.movels(spiralback(startgrinder, welposgrinder, r + 78))
#        robot.movel([0.040, 0, 0., 0, 0, 0], relative = True)
        
#        robot.movels(spiralcoordinates(startgrinder, welposgrinder, r + 78))#, vel = 0.005, acc = 1) 
#        robot.movels(spiralback(startgrinder, welposgrinder, r + 78))#, vel = 0.005, acc = 1)
#        robot.movel([0.030, 0, 0., 0, 0, 0], relative = True)
#        robot.movels(spiralcoordinates(startgrinder, welposgrinder, r + 78))#, vel = 0.005, acc = 1) 
#        robot.movels(spiralback(startgrinder, welposgrinder, r + 78))#, vel = 0.005, acc = 1)
#        robot.movel([0.030, 0, 0., 0, 0, 0], relative = True)
#        robot.movels(spiralcoordinates(startgrinder, welposgrinder, r + 78))#, vel = 0.005, acc = 1) 
#
        robot.set_analog_out(0, 0.0)
        robot.set_analog_out(1, 0.0)
        robot.set_tool_voltage(0)
        robot.set_digital_out(1, False)
        
        robot.movel(start)

                   
    finally:
        robot.set_analog_out(0, 0.0)
        robot.set_analog_out(1, 0.0)
        robot.set_tool_voltage(0)
        robot.set_digital_out(1, False)
        
        print('Movement done')
        robot.close() 
        
        
        
        
#        #Make the grinding move
#        robot.movels(spiralback(startgrinder, welposgrinder, r + 78), vel = 0.001, acc = 1)
#        
#        #Continue a bit further
#        robot.movel([0.080,0,0,0,0,0], relative = True)
                
#        while True:
#            arduinocheck()
#            if induxion() <= 3:
#                robot.movel([0, 0, 0.03, 0, 0, 0], relative = True)
#                robot.movels(spiralcoordinates(start, welpos, r))
#                robot.movels(spiralback(start, welpos, r))
#                robot.movel([0, 0, -0.03, 0, 0, 0], relative = True)
#            
#            if induxion() >= 3:
#                break
