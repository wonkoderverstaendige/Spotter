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

import sys, serial
from serial.tools import list_ports


class Funker:
    ser = None
    port = None

    def __init__( self, port = 0 ):

        for l in list_ports.comports():
            print l

        self.port = port

        self.ser = serial.Serial( self.port )
        print 'Opened serial port ' + self.ser.portstr  # check which port was really used


    def send( self, num ):
        byte_str = chr( num )
        rb = self.ser.write( byte_str )
        print 'Wrote ' + str(rb) + ' Bytes'


    def close( self ):
        self.ser.close()             # close port


if __name__ == '__main__':
    funker = Funker()
    funker.send(12)
    funker.close()