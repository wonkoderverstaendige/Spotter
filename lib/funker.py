# -*- coding: utf-8 -*-
"""
Created on Tue Nov 06 03:42:47 2012
@author: <Ronny Eichler> ronny.eichler@gmail.com

Send signals to Serial Port based on events like line crossing or ROI occupancy.

Usage:
    funker.py --port PORT [options]
    funker.py -h | --help

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
import serial
import time
from serial.tools import list_ports

#project libraries
sys.path.append('./lib')
import utils

#command line handling
sys.path.append('./lib/docopt')
from docopt import docopt


#TODO:
#    - Find proper port by trying to connect to all ports on list till
#    successful handshake with Arduino
#    - get required data from Arduino (i.e. all hardware specifics)
#    - define data protocol (i.e. RS232 like?)

class Funker:
    ser = None
    port = None

    def __init__( self, port, X_range = (0, 639), Y_range = (0, 359), DAC_range = (0, 4095) ):

        if port and not port=="None":
            self.X_range = X_range
            self.Y_range = Y_range
            self.DAC_range = DAC_range

            for l in list_ports.comports():
                print l

            self.port = port

            self.ser = serial.Serial( self.port, 9600, 8, 'N', 1, timeout=1 )
            print 'Opened serial port ' + self.ser.portstr  # check which port was really used
        else:
            print "No serial used"


    def send( self, coords ):
        if not self.ser:
            return
#        num = max(self.X_range) if num > max(self.X_range) else num
#        num = min(self.X_range) if num < min(self.X_range) else num

        num1 = utils.scale(coords[0], self.X_range, self.DAC_range)
        num2 = utils.scale(coords[1], self.Y_range, self.DAC_range)

        sendString = str(int(num1) ) + '\t'
#        print sendString
        rb = self.ser.write( sendString )
        self.ser.flush()

        sendString = str(int(num2) ) + '\n'
#        print sendString
        rb = self.ser.write( sendString )
        self.ser.flush()


#        print sendString
#        print 'Wrote ' + str(rb) + ' Bytes'
##        print 'start reading:'
##        rt =  self.ser.read(10)
##        print 'rt1: ' + rt

    def read( self, length ):
        if not self.ser:
            return
        print 'start reading'
        rt =  self.ser.read(length)
        print 'rt: ' + rt


    def serialTest( self ):
        if not self.ser:
            return
        self.ser.write( '1000\n' )
        self.ser.flush()
        time.sleep(5.00)

        print 'start reading:'
        rt =  self.ser.read(10)
        print 'rt1: ' + rt
        rt =  self.ser.read(10)
        print 'rt2: ' + rt


    def close( self ):
        if self.ser:
            self.ser.close()             # close port




if __name__ == '__main__':
    funker = Funker()
    funker.send(300)
    funker.send(300)
#    for n in range(10):
#        funker.serialTest()
    print 'Done'
    time.sleep(5)
    funker.close()