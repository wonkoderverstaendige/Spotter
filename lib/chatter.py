# -*- coding: utf-8 -*-
"""
Created on Tue Nov 06 03:42:47 2012
@author: <Ronny Eichler> ronny.eichler@gmail.com

Send signals to Serial Port based on events like line crossing or ROI occupancy.

Usage:
    chatter.py --port PORT [options]
    chatter.py -h | --help

Options:
    -h --help           Show this screen
    -f --fps FPS        Fps for camera and video
    -s --source SRC     Path to file or device ID [default: 0]
    -S --Serial         Serial port to uC [default: None]
    -o --outfile DST    Path to video out file [default: None]
    -d --dims DIMS      Frame size [default: 320x200]
    -H --Headless       Run without interface
    -D --DEBUG          Verbose output

To do:
    - destination file name may consist of tokens to automatically create,
      i.e., %date%now%iterator3$fixedstring
    - track low res, but store full resolution
    - can never overwrite a file

"""

import sys
#import serial
import time
from serial.tools import list_ports

#project libraries
sys.path.append('./lib')
import utilities as utils
import geometry as geom

#command line handling
sys.path.append('./lib/docopt')
from docopt import docopt

sys.path.append('./arduino')
import arduino

#TODO:
#    - Find proper port by trying to connect to all ports on list till
#    successful handshake with Arduino
#    - get required data from Arduino (i.e. all hardware specifics)
#    - define data protocol (i.e. RS232 like?)

class Chatter:
    serial_device = None
    port = None
    label = 'Arduino'

    def __init__( self, serial_port, frame_size = (639, 359), max_dac = 4095 ):
        if serial_port:
            self.serial_port = serial_port
            self.open_serial(self.serial_port)
            
        self.inst_buffer = []
        
        self.range_xy = frame_size
        
        self.factor_dac = (4095 - 256.0) / max(frame_size)
        self.offset_dac = max_dac - self.factor_dac * max(frame_size)
        dr = int(self.factor_dac) * max(frame_size)
        print ('DAC factor: ' + str(self.factor_dac))
        print ('DAC offset: ' + str(self.offset_dac))
        self.range_dac = (dr, dr)


    def open_serial(self, serial_port):
        self.close()
        print "Opening port "+ serial_port
        self.serial_device = arduino.Arduino(serial_port)
        return self.serial_device.connected

    def send(self):
        if not self.serial_device:
            return
        if len(self.inst_buffer):
            self.send_point2analog(self.inst_buffer.pop())
#        self.serial_device.flush()
        
    def send_point2analog(self, point):
#        t = time.clock()
#        scaled_point = geom.map_points(point, self.range_xy, self.range_dac)
        scaled_point = self.map_point(point)
        if self.is_open():
            self.serial_device.send_instructions([[0, scaled_point[0]], 
                                                  [1, scaled_point[1]]])
#        print ("instruction took: ", (time.clock() - t)*1000)


    def map_point(self, point):
        coord_max = max(self.range_xy)
        
        # center point coordinates into range
        xc = point[0] + (coord_max - self.range_xy[0])/2.0
        # Y coordinate has to be flipped, origin is _upper_ left corner
        yc = (self.range_xy[1] - point[1]) + (coord_max - self.range_xy[1])/2.0
        xc = int(xc * self.factor_dac + self.offset_dac)
        yc = int(yc * self.factor_dac + self.offset_dac)
        return (xc, yc)



#    def read( self, length ):
#        if not self.serial_device:
#            return
#        rt =  self.serial_device.read(length)
        
    def read_all(self):
        if not self.serial_device:
            return
        return self.serial_device.read_all_bytes()
        
        
    def read_line(self):
        if not self.serial_device:
            return
        return self.serial_device.read_line()


    def is_open(self):
        return (self.serial_device and self.serial_device.is_open())
        
    def bytes_tx(self):
        if self.serial_device:
            return self.serial_device.bytes_sent
        else:
            return None

    def bytes_rx(self):
        if self.serial_device:
            return self.serial_device.bytes_received
        else:
            return None
            
    def bytes_available(self):
        if self.serial_device:
            return self.serial_device.bytes_available()
        else:
            return None
            
    def list_ports(self):
        return list_ports.comports()

    def close(self):
        print 'Closing Serial'
        if self.serial_device:
            self.serial_device.close()

    def test_scan_frame(self, stepsize = 4):
        """
        scan through all points in frame size, pause between
        each point for [delay] milliseconds
        """
        for y in xrange(0, self.range_xy[1]+1, stepsize):
            t = time.clock()
            for x in xrange(0, self.range_xy[0]+1, stepsize):
                self.send_point2analog((x, y))
                self.read_all()
            print("line: " + str(y) + " t: " + str((time.clock() - t)) + " s")
        
        self.send_point2analog((0, 0))
        self.read_all()
        time.sleep(0.5)
          
        for x in xrange(0, self.range_xy[0]+1, stepsize):
            t = time.clock()
            for y in xrange(0, self.range_xy[1]+1, stepsize):
                self.send_point2analog((x, y))
                self.read_all()
            print("column: " + str(x) + " t: " + str((time.clock() - t)) + " s")          
          
               
#############################################################
if __name__ == '__main__':
#############################################################
    chatter = Chatter('COM4')
    chatter.test_scan_frame(stepsize = 2)
    print 'Done'
#    time.sleep(2)
    chatter.close()