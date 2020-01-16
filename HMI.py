from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.lang import Builder
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.clock import Clock
from functools import partial
import Spiral_weld_0 as sw
import serial
from urx import Robot
import math


#Window.fullscreen = 'auto'

class Home(Screen):
    pass
        
class Control(Screen):

    d = ''
    log_string = ''
    state = 0
    robot = Robot("192.168.0.20", True)
    arduino = serial.Serial('/dev/cu.usbmodem144201', 9600)
    start = [0.708, 0.155, 0.000, math.pi, 0, 0]

        
    def __init__(self, **kwargs):
        super(Control, self).__init__(**kwargs)
        self.Build()
    
    def Build(self):
        self.log = GridLayout(cols = 1, size_hint = (0.5, 1), pos_hint = {'x':0.5, 'y':0})
        
        self.rightside = TextInput(text = "CONSOLE\n\n" + self.log_string)             
        self.log.add_widget(self.rightside)
        
        self.add_widget(self.log)        
    
    def ConfirmDiameter(self):
        self.d = self.ids.diameter.text
        
        if self.d:
            try:
                int(self.d)
            except:
                self.log_string = "Not a valid input (no integer)" 
            else:
                if int(self.d) == 0:
                    self.log_string = "Not a valid input (zero input)"                     
                else:
                    self.log_string = "The diameter is set at " + self.d + " mm\n"
                    self.r = int(self.d)/2
        else:
            self.log_string = "Not a valid input (no input)"
                
        self.Refresh()

    def Start(self):
        if ("The diameter is set" in self.log_string):
            self.robot.set_tcp([0,0,0,0,0,0])
            self.robot.movel(self.start, vel = 2.0, acc = 1.0)
            if self.state == 0:
                self.state = 1
                self.Start()
            elif self.state == 1:
                sw.arduinocheck()
                self.robot.movel([0, 0, -0.500, 0, 0, 0], relative = True, wait = False, vel = 0.003, acc = 1)
                Clock.schedule_interval(self.CheckForPipe,1/10)
            elif self.state == 2:
                sw.arduinocheck()
                self.robot.set_analog_out(0, 0.5)
                Clock.schedule_interval(self.CheckForWeld,1/10)
            elif self.state == 3:
                sw.arduinocheck()
                self.robot.movels(sw.quartercircle(self.r, self.start_circle), wait = False)
                Clock.schedule_interval(self.WeldDirection,1/10)
            elif self.state == 4:
                Clock.schedule_interval(self.Set,1/10)
            elif self.state == 5:
                self.Grinding()
        elif ("The diameter is set" not in self.log_string and self.state == 0):
            self.log_string = "No diameter set"
            self.Refresh()
        print(self.state)
            
    def CheckForPipe(self,dt):
        if "Approach pipe\n" not in self.log_string:
            self.log_string += "Approach pipe\n"
            self.Refresh()
        if sw.switch() <= 3:
            self.robot.stop()
            self.start = self.robot.getl()
            Clock.unschedule(self.CheckForPipe)
            self.state = 2
            self.log_string += "Tool on pipe\n"
            self.Refresh()
            self.Start()
            
    def CheckForWeld(self,dt):
        if "Looking for weld\n" not in self.log_string:
            self.log_string += "Looking for weld\n"
            self.Refresh()
        if sw.induxion() <= 3:
            self.robot.set_analog_out(0, 0)
            Clock.unschedule(self.CheckForWeld)
            self.state = 3
            self.log_string += "Weld detected\n"
            self.Refresh()
            self.Start()
    
    def WeldDirection(self,dt):
        if "Finding weld direction\n" not in self.log_string:
            self.log_string += "Finding weld direction\n"
            self.Refresh()
        if sw.induxion() <= 3:
            self.robot.stop()
            self.welpos = self.robot.getl()
            x, self.y, z = sw.spiralcoords(self.start, self.welpos)
            Clock.unschedule(self.WeldDirection)               
        if (x >= -0.025 and x <= 0.025):
            self.state = 4
            self.log_string += "Direction is parallel to axis of rotation\n"
            self.Refresh()
        else:
            self.state = 4
            self.log_string = "Direction has angle to axis of rotation\nAngle is " + self.angle + " degrees\n"
            self.Refresh()
            self.Start()
            
    def Set(self,dt):
        if "Tuning on pipe\n" not in self.log_string:
            self.log_string += "Tuning on pipe\n"
            self.Refresh()
        #movement to pipe
        self.state = 5
        self.log_string += "Finished"
        self.Refresh()        
        self.Start()
    
    def Grinding(self,dt):
        if "Grinding in progress\n" not in self.log_string:
            self.log_string += "Grinding in progress\n"
            self.Refresh()
        self.robot.movel([0,0,self.y/1000,0,0,0], relative = True)#, vel = 2.0, acc = 1.0)
        self.robot.movel(self.start)#, vel = 2.0, acc = 1.0)
        self.robot.movels(sw.spiralcoordinates(self.start, self.welpos, self.r))
        self.robot.movels(sw.spiralback(self.start, self.welpos, self.r))
        self.state = 0
        self.log_string += "Finished\n-------------------------" 
        self.Refresh()
        
    def Refresh(self):
        self.clear_widgets()
        self.__init__()

class WindowManager(ScreenManager):
    pass
    
kv = Builder.load_file("HMI.kv")
    
class HMI(App):
    def build(self):
        return kv

if __name__ == "__main__":
    HMI().run()