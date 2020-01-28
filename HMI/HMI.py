from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.floatlayout import FloatLayout
from kivy.lang import Builder
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.clock import Clock
from functools import partial
import Spiral_weld_0 as sw
import serial
from urx import Robot
import math
import time

Window.fullscreen = 'auto'

class Home(Screen):
    pass
        
class Control(Screen):

    d = ''
    log_string = ''
    state = 0
    robot = Robot("192.168.0.20", True)
    arduino = serial.Serial('/dev/cu.usbmodem144101', 9600)
    start = [1.381, 0.164, -0.104, 3.12, -0.0014, -0.1275]
        
    def __init__(self, **kwargs):
        super(Control, self).__init__(**kwargs)
        self.Build()
    
    def Build(self):
        self.log = GridLayout(cols = 1, size_hint = (0.5, 1), pos_hint = {'x':0.5, 'y':0})
        
        self.rightside = TextInput(text = "CONSOLE\n\n" + self.log_string, font_size = 20)             
        self.log.add_widget(self.rightside)
        
        self.add_widget(self.log)        
    
    def ConfirmDiameter(self):
        if self.state == 0:
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
                        self.log_string = "The diameter is set at " + self.d + " mm\nPress 'Start grinding'\n"
                        self.r = int(self.d)/2
            else:
                self.log_string = "Not a valid input (no input)"

            self.Refresh()

    def Start(self):
        print(self.log_string)
        if ("The diameter is set" in self.log_string):
            
            #Startup & homing
            if self.state == 0:
                self.robot.set_analog_out(0, 0.0)
                self.robot.wet_analog_out(1, 0.0)
                self.robot.set_tool_voltage(0)
                self.robot.set_digital_out(1, False)
                self.log_string += "Homing\n"
                self.Refresh()
                self.robot.movel(self.start, vel = 1.0, acc = 1.0)
                self.state = 1
                self.Start()
            
            #Go to pipe
            elif self.state == 1:
                sw.arduinocheck()
                self.robot.movel([0, 0, -0.500, 0, 0, 0], relative = True, wait = False, vel = 0.007, acc = 1)
                Clock.schedule_interval(self.CheckForPipe,1/1000)
                
            #Looking for weld
            elif self.state == 2:
                self.robot.set_analog_out(0, 0.5)
                Clock.schedule_interval(self.CheckForWeld,1/1000)
                
            #Looking for direction
            elif self.state == 3:
                self.robot.movel([0, 0, 0.03, 0, 0, 0], relative = True)
                self.robot.movel([-0.090, 0, 0, 0, 0, 0], relative = True, wait = True)
                self.robot.movel([0, 0, -0.03, 0, 0, 0], relative = True)
                self.start_circle = self.robot.getl()
                sw.arduinocheck()
                self.robot.movels(sw.quartercircle(self.r, self.start_circle), wait = False)
                Clock.schedule_interval(self.WeldDirection,1/1000)
                
            #Set grinder on pipe
            elif self.state == 4:
                self.robot.movel([0, 0, self.y_w/1000 + 0.090, 0, 0, 0], relative = True)
                self.robot.movel(self.startgrinder_offset, vel = 2.0, acc = 1.0)
                self.robot.movels(sw.grindsetup(self.r + 78, self.startgrinder_offset), wait = False)
                time.sleep(10)
                self.robot.stop()
                self.robot.translate_tool([0, 0, 1], vel = 0.003, acc = 1, wait = False)
                Clock.schedule_interval(self.Set,1/1000)
            
            #Grinding
            elif self.state == 5:
                self.Grinding()
                
            #Finishing and resetting process
            elif self.state == 6:
                self.Reset()
            
        elif ("The diameter is set" not in self.log_string and self.state == 0):
            self.log_string = "No diameter set"
            self.Refresh()
        
    def Stop(self):
        if self.state != 0:
            Clock.unschedule(self.CheckForPipe)
            Clock.unschedule(self.CheckForWeld)
            Clock.unschedule(self.WeldDirection)               
            Clock.unschedule(self.Set)
            self.robot.stop()
            self.log_string += "STOPPING PROCESS!\nHoming\n"
            self.Refresh()
            self.robot.movel(self.start)#, vel = 2.0, acc = 1.0) #first go to safe position
            self.log_string += "PROCESS STOPPED AND RESET!\nPress 'Start grinding' to restart the process \nor enter different diameter than " + self.d + "\n"
            self.state = 0
            self.Refresh()
            
    def CheckForPipe(self,dt):
        if "Approach pipe\n" not in self.log_string:
            self.log_string += "Approach pipe\n"
            self.Refresh()
        if sw.switch() <= 0.1:
            self.robot.stop()
            Clock.unschedule(self.CheckForPipe)
            self.robot.movel([0, 0, -0.006, 0, 0, 0], relative = True, vel = 0.003, acc = 1)
            self.start = self.robot.getl()
            self.startgrinder = sw.sensor_grind_coords(self.start)
            self.startgrinder_flipped = sw.sensor_grind_coords_flipped(self.start)
            self.startgrinder_offset = sw.offset(self.startgrinder_flipped, 0, 0, 0.030)
            self.state = 2
            self.log_string += "Tool on pipe\n"
            self.Refresh()
            self.Start()
            
    def CheckForWeld(self,dt):
        if "Looking for weld\n" not in self.log_string:
            self.log_string += "Looking for weld\n"
            self.Refresh()
        if sw.induxion() <= 0.1:
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
        if sw.induxion() <= 0.1:
            self.robot.stop()
            Clock.unschedule(self.WeldDirection)
            self.welpos = self.robot.getl()
            self.welposgrinder = sw.sensor_grind_coords(self.welpos)
            self.welposgrinder_flipped = sw.sensor_grind_coords_flipped(self.welpos)
            self.welposgrinder_offset = sw.offset(self.welposgrinder, 0, 0, 0.030)
            self.welposgrinder_flipped_offset = sw.offset(self.welposgrinder_flipped, 0, 0, 0.030)
            self.x_w, self.y_w, self.z_w = sw.spiralcoords(self.start, self.welpos)               
            if (self.x_w >= -0.05 and self.x_w <= 0.05):
                self.state = 4
                self.log_string += "Weld is straight\n"
            elif self.x_w > 0.05:
                self.state = 4
                self.log_string += "Weld is spiraling\n"
            self.Refresh()
            self.Start()
            
    def Set(self,dt):
        if "Tuning on pipe\n" not in self.log_string:
            self.log_string += "Tuning on pipe\n"
            self.Refresh()
        if sw.endstop_grinder() <= 0.1:
            self.robot.stop()
            Clock.unschedule(self.Set)
            self.robot.set_digital_out(1,True)
            self.state = 5
            self.log_string += "Tool tuned\n"
            self.Refresh()
            self.Start()
    
    def Grinding(self,dt):
        if "Grinding in progress\n" not in self.log_string:
            self.log_string += "Grinding in progress\n(PRESS DEAD MAN'S SWITCH TO TURN ON TOOL AND KEEP PRESSED)\n"
            self.Refresh()
        self.robot.movel([0, 0, 0.04, 0, 0, 0], relative = True)#, vel = 2.0, acc = 1.0)
        self.robot.movel(self.startgrinder_offset)
        self.robot.movel([0, 0 + (self.d_x / 1000), 0, 0, 0, 0], relative = True)
        self.robot.movel(self.welposgrinder_offset)
        self.robot.set_tool_voltage(24)
        self.robot.set_analog_out(1, 0.5)
        sw.weldfunction(self.startgrinder, self.welposgrinder, self.r, vel = 0.005, acc = 1)
        self.state = 6
        self.log_string += "Grinding finished\n(DEAD MAN'S SWITCH CAN BE RELEASED)\n" 
        self.Refresh()
        self.Start()
        
    def Reset(self,dt):
        self.robot.set_analog_out(0, 0.0)
        self.robot.set_analog_out(1, 0.0)
        self.robot.set_tool_voltage(0)
        self.robot.set_digital_out(1, False)
        self.state = 0
        self.log_string += "Everything is reset\n----------END----------"
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