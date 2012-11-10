# -*- coding: utf-8 -*-
"""
Created on Tue Nov 06 03:42:47 2012
@author: <Ronny Eichler> ronny.eichler@gmail.com

Send signals to Serial Port based on events like line crossing or ROI occupancy.

Usage:
    funker.py --source SRC [--outfile DST] [options]
    funker.py -h | --help

Options:
    -h --help           Show this screen
    -f --fps FPS        Fps for camera and video
    -s --source SRC     Path to file or device ID [default: 0]
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

import sys, serial, time
from serial.tools import list_ports
sys.path.append('./lib')
sys.path.append('./lib/docopt')
#from docopt import docopt
import utils

class Funker:
    ser = None
    port = None

    def __init__( self, port = 2, X_range = (0, 639), DAC_range = (0, 4095) ):

        self.X_range = X_range
        self.DAC_range = DAC_range
        
        for l in list_ports.comports():
            print l

        self.port = port

        self.ser = serial.Serial( self.port, 9600, 8, 'N', 1, timeout=1 )
        print 'Opened serial port ' + self.ser.portstr  # check which port was really used


    def send( self, num ):

        num = max(self.X_range) if num > max(self.X_range) else num
        num = min(self.X_range) if num < min(self.X_range) else num

        num = utils.scale(num, self.X_range, self.DAC_range)

        sendString = str(int(num) ) + '\n'
        rb = self.ser.write( sendString )
        self.ser.flush()
#        print sendString
#        print 'Wrote ' + str(rb) + ' Bytes'
##        print 'start reading:'
##        rt =  self.ser.read(10)
##        print 'rt1: ' + rt       
        
    def read( self, length ):
        print 'start reading'
        rt =  self.ser.read(length)
        print 'rt: ' + rt
        

    def serialTest( self ):
        self.ser.write( '1000\n' )
        self.ser.flush()
        time.sleep(5.00)
        
        print 'start reading:'
        rt =  self.ser.read(10)
        print 'rt1: ' + rt
        rt =  self.ser.read(10)
        print 'rt2: ' + rt


    def close( self ):
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