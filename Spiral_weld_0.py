 oo#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 13 18:02:54 2019

@author: wouter
"""
import numpy as np
import math 
from urx import Robot

robot = Robot("192.168.0.20", True)

def spiralweld(x_p, y, z, it, r, pos):

    def teta(x,y):
        if y == 0:
            return 0
        teta = math.atan(x/y)
        return teta
    
    Xref, Yref, Zref = [0,r,0]
    Xmes, Ymes, Zmes = [x_p,y,z]
    
    Xref_cil = (Xref**2+Yref**2)**0.5
    Yref_cil = teta(Xref, Yref)
    Zref_cil = Zref
    
    Xmes_cil = (Xmes**2+Ymes**2)**0.5
    Ymes_cil = teta(Xmes, Ymes)
    Zmes_cil = Zmes
    
    def cylindercoords():
        x_l = np.linspace(Xref_cil,Xmes_cil,it)
        y_l = np.linspace(Yref_cil, Ymes_cil, it)
        z_l = np.linspace(Zref_cil, Zmes_cil, it)
    
        return x_l,y_l,z_l
    
    Xc = cylindercoords()[0]
    Yc = cylindercoords()[1]
    Zc = cylindercoords()[2]
    
    def cartesiancoords():
        x_l = []
        y_l = []
        z_l = Zc
        
        for i in range(0,it):
            x_l1 = r*math.cos(Yc[i]) 
            y_l1 = r*math.sin(Yc[i])
    
            x_l.append(x_l1)
            y_l.append(y_l1)
        
        return x_l, y_l, z_l
    
    Xf = cartesiancoords()[0] 
    Yf = cartesiancoords()[1]
    Zf = cartesiancoords()[2]
        
    def arcmove():        
        x = pos[0]
        y = pos[1]
        z = pos[2]
        rx = math.pi
        ry = 0
        rz = 0
        
        pose_list = []
        
        for i in range(it):
            x = pos[0] - (Zf[i]/1000)
            y = pos[1] + (Yf[i]/1000)
            z = pos[2] + (Xf[i]/1000) - (Xf[0]/1000)
            rx += (((x_p-20) / r) * (- 0.5 * math.pi))/it
            
            pose_list += [[x, y, z, rx, ry, rz]]
         
        return pose_list
    
    return arcmove()

def spiralweldback(x_p, y, z, it, r, pos):
    pose_list = spiralweld(x_p, y, z, it, r, pos)
    pose_list_back = pose_list[::-1]
    return pose_list_back

def quartercircle(r, pos, iterated):
    
    theta = np.linspace(0, 2*np.pi, 200)
    
    radius = np.sqrt(r**2)
    
    x = radius*np.cos(theta)
    y = radius*np.sin(theta)
    
    x_cir1 = x[0:50]
    y_cir1 = y[0:50]
    x_cir = x_cir1[::-1]
    y_cir = y_cir1[::-1]
    
    pose_list = []
    
    rx_list = np.linspace(pos[3], 0.5*math.pi, len(x_cir))
    
    for i in range(0,len(y_cir)):
        x = pos[0]
        y = pos[1] + x_cir[i]/1000 
        z = pos[2] + (y_cir[i]/1000 - y_cir[0]/1000)
        rx = rx_list[i]
        ry = pos[4]
        rz = pos[5]

        pose_list += [[x, y, z, rx, ry, rz]]
        
        if iterated == 'iterated':
            robot.movel([x, y, z, rx, ry, rz], vel = 1, acc = 0.2)

    return pose_list

def quartercircleback(r, pos):
    pose_list = quartercircle(r, pos, 'false')
    pose_list_back = pose_list[::-1]
    return pose_list_back

def spiralweldback(x_p, y, z, it, r, pos):

    def teta(x,y):
        if y == 0:
            return 0
        teta = math.atan(x/y)
        return teta
    
    Xref, Yref, Zref = [0,r,0]
    Xmes, Ymes, Zmes = [x_p,y,z]
    
    Xref_cil = (Xref**2+Yref**2)**0.5
    Yref_cil = teta(Xref, Yref)
    Zref_cil = Zref
    
    Xmes_cil = (Xmes**2+Ymes**2)**0.5
    Ymes_cil = teta(Xmes, Ymes)
    Zmes_cil = Zmes
    
    def cylindercoords():
        x_l = np.linspace(Xref_cil,Xmes_cil,it)
        y_l = np.linspace(Yref_cil, Ymes_cil, it)
        z_l = np.linspace(Zref_cil, Zmes_cil, it)
    
        return x_l,y_l,z_l
    
    Xc = cylindercoords()[0]
    Yc = cylindercoords()[1]
    Zc = cylindercoords()[2]
    
    def cartesiancoords():
        x_l = []
        y_l = []
        z_l = Zc
        
        for i in range(0,it):
            x_l1 = r*math.cos(Yc[i]) 
            y_l1 = r*math.sin(Yc[i])
    
            x_l.append(x_l1)
            y_l.append(y_l1)
        
        return x_l, y_l, z_l
    
    Xf = cartesiancoords()[0] 
    Yf = cartesiancoords()[1]
    Zf = cartesiancoords()[2]
        
    def arcmove():        
        x = pos[0]
        y = pos[1]
        z = pos[2]
        rx = math.pi
        ry = 0
        rz = 0
        
        pose_list = []
        
        rx_list = np.linspace(pos[3], 0.5*math.pi, it)
        
        for i in range(it):
            x = pos[0] - (Zf[i]/1000)
            y = pos[1] + (Yf[i]/1000)
            z = pos[2] + (Xf[i]/1000) - (Xf[0]/1000)
            rx = rx_list[i]
            
            pose_list += [[x, y, z, rx, ry, rz]]
         
        return pose_list
    
    return arcmove()


    
    
    










    
    
        
        


