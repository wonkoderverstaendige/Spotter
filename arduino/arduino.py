# -*- coding: utf-8 -*-
"""
Created on Sat Jan  5 16:54:29 2013

@author: <Ronny Eichler> ronny.eichler@gmail.com

A lot of the handling is done the way Firmata handles the boards

TODO: How does the non-blocking pass_time function work exactly?
"""

import sys
import serial
import time

VERSION = 0.1

class Arduino(object):
    firmware_version = None
    connected = False
    
    def __init__(self, port, baudrate=57600):
        self.sp = serial.Serial(port, baudrate)
        self.pass_time(3)
        
        self.portString = port
        
        self.sp.flushInput()
        self.sp.write('V') # request version as handshake
        for n in range(100):
            if self.bytes_available():
                self.firmware_version = self.sp.readline()
                self.connected = True
                print "Connected to " + str(self.firmware_version)
                break
            self.pass_time(0.01)
            

    def __str__(self):
        return "Board %s on %s" % (self.name, self.sp.port)

    def __del__(self):
        ''' 
        The connection with the a board can get messed up when a script is
        closed without calling board.exit() (which closes the serial
        connection). Therefore also do it here and hope it helps.
        '''
        self.exit()

    def read_all_bytes(self):
        return self.sp.readall()
        
    def read_line(self):
        return self.sp.readline()

    def bytes_available(self):
        return self.sp.inWaiting()

    def send_as_two_bytes(self, val):
        self.sp.write(chr(val % 128) + chr(val >> 7))

    def exit(self):
        """ Call this to exit cleanly. """
        if hasattr(self, 'sp'):
            self.sp.close()    

    def pass_time(self, t):
        """ 
        Non-blocking time-out for ''t'' seconds.
        """
        cont = time.time() + t
        while time.time() < cont:
            time.sleep(0)
        
        
if __name__ == "__main__":
    testboard = Arduino(sys.argv[1])
    while True:
        if testboard.bytes_available():
            byte = ord(testboard.sp.read(1))
            if byte == 2:
                print "RIGHT"
            if byte == 1:
                print "LEFT"
            if byte == 3:
                print "BOTH"
            testboard.sp.flushInput()
            time.sleep(0.005)
    
    sys.exit(0)