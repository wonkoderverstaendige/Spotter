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

    def __init__( self, serial_port ):
        if serial_port:
            self.serial_port = serial_port
            self.open_serial(self.serial_port)
            
        self.inst_buffer = []
            
        self.set_ranges()

    def open_serial(self, serial_port):
        self.close()
        print "Opening port "+ serial_port
        self.serial_device = arduino.Arduino(serial_port)
        return self.serial_device.connected

    def send(self):
        if len(self.inst_buffer):
            self.send_point2analog(self.inst_buffer.pop())
#        if not self.serial_device:
#            return
#
#        num1 = utils.scale(coords[0], self.X_range, self.DAC_range)
#        num2 = utils.scale(coords[1], self.Y_range, self.DAC_range)
#
#        sendString = str(int(num1) ) + '\t'
##        print sendString
#        rb = self.serial_device.write( sendString )
#        self.serial_device.flush()
#
#        sendString = str(int(num2) ) + '\n'
##        print sendString
#        rb = self.serial_device.write( sendString )
#        self.serial_device.flush()
        
    def send_point2analog(self, point):
        t = time.clock()
        scaled_point = geom.map_points(point, self.range_xy, self.range_dac)
        if self.is_open():
#            print(point, scaled_point)
            self.serial_device.send_instruction(0, scaled_point[0])
            self.serial_device.send_instruction(1, scaled_point[1])
#        print ("instruction took: ", (time.clock() - t)*1000)

    def set_ranges(self, xy = (639, 359), dac = (4095, 4095)):
        self.range_xy = xy
        self.range_dac = dac

    def read( self, length ):
        if not self.serial_device:
            return
        print 'start reading'
        rt =  self.serial_device.read(length)
        print 'rt: ' + rt
        
    def read_all(self):
        self.serial_device.read_all_bytes()

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



#############################################################
if __name__ == '__main__':
#############################################################
    chatter = Chatter()
    chatter.send(300)
    chatter.send(300)
#    for n in range(10):
#        chatter.serialTest()
    print 'Done'
    time.sleep(5)
    chatter.close()