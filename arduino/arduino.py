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
import struct

VERSION = 0.1

class Pin(object):
    def __init__(self, idx, instruction, pin_type):
        self.id = idx
        self.instruction = instruction
        self.type = pin_type
        self.label = ''.join([pin_type, '.', str(idx)])

        self.slot = None
        self.available = True

class Arduino(object):
    firmware_version = None
    connected = False


    def __init__(self, port, baudrate=57600):
        self.sp = serial.Serial(port, baudrate)
        self.pass_time(3)

        self.bytes_sent = 0
        self.bytes_received = 0

        self.pins = dict(dac=None, digital=None, pwm=None, adc=None)

        self.portString = port
#        self.sp.flushInput()

#        mirror_test_val = 4095
#        for n in xrange(100):
#            self.send_instructions([['report', 0, mirror_test_val],
#                                    ['report', 1, 0],
#                                    ['report', 2, 0]])
#            if self.bytes_available():
#                self.connected = True
#                print("   --> Connected after " + str(n) + " tries.")
#                responses = map(int, self.read_all_bytes().splitlines())
#                if int(responses[0]) == mirror_test_val:
#                    print '   --> Mirror test passed!'
#                self.pins['dac'] = Pin(responses[1], 1)
#                self.pins['digital'] = Pin(responses[2], 2)
#                print '   --> SPI_DAC pins available:', self.pins['dac'].n
#                print '   --> Digital pins available:', self.pins['digital'].n
#                break
#            self.pass_time(0.01)

    def __str__(self):
        return "Board %s on %s" % (self.name, self.sp.port)

    def __del__(self):
        """ The connection with the a board can get messed up when a script is
        closed without calling board.exit() (which closes the serial
        connection). Therefore also do it here and hope it helps.
        """
        self.close()

    def is_open(self):
        return self.sp.isOpen()

    def get_pins(self):
        self.send_instructions([['report', 1, 0], ['report', 2, 0]])
        # give arduino time to respond
        self.pass_time(0.1)
        if self.bytes_available():
            responses = map(int, self.read_all_bytes().splitlines())
            # Analog pins are of type 1
            self.pins['dac'] = [Pin(idx, 1, 'DAC') for idx in xrange(responses[0])]
            # Digital Pins are type 2
            self.pins['digital'] = [Pin(idx, 2, 'DO') for idx in xrange(responses[1])]

            print '   --> SPI_DAC pins available:', len(self.pins['dac'])
            print '   --> Digital pins available:', len(self.pins['digital'])
            return True
        else:
            return None

    def read_all_bytes(self):
        msg = ''
        msg = self.sp.read(self.bytes_available())
        self.bytes_received += len(msg)
        return msg

    def read_line(self):
        msg = self.sp.readline()
        self.bytes_received += len(msg)
        return msg

    def bytes_available(self):
        return self.sp.inWaiting()

    def send_as_two_bytes(self, val):
        self.sp.write(chr(val % 128) + chr(val >> 7))

    def send_instructions(self, instruction_list):
        """ Send command byte followed by two data bytes. struct packs short
        unsigned value ('H') as two bytes, big endian.
        Type (3LSB bits) + Address (next 3 bits)
        DAC/SPI         DigitalOut
        H AO.0          P DO.0
        I AO.1          Q DO.1
        J AO.2          R DO.2
        K AO.3          S DO.3
        L AO.4          T DO.4
        M AO.5          U DO.5
        N AO.6          V DO.6
        O AO.7          W DO.7
        """
        msg = ''
        for i in instruction_list:
            if i[0] == 'report':
                msg = msg + chr(0 + i[1])
            elif i[0] == 'dac':
                msg = msg + chr(ord('H') + i[1])
            elif i[0] == 'digital':
                msg = msg + chr(ord('P') + i[1])
            msg = msg + struct.pack('H', i[2]) + '\n'

        # write all instructions as on string to reduce the amount of
        # time spent in the annoying 4ms delay arduino spends on serial
        # communication according to
        self.sp.write(msg)
        self.bytes_sent += len(msg)

    def close(self):
        """ Call this to exit cleanly. """
        if hasattr(self, 'sp'):
            self.sp.close()
        self.bytes_received = 0
        self.bytes_sent = 0


    def pass_time(self, t):
        """
        Non-blocking time-out for t seconds.
        """
        cont = time.time() + t
        while time.time() < cont:
            time.sleep(0)


#############################################################
if __name__ == "__main__":
#############################################################
    testboard = Arduino(sys.argv[1])
#    while True:
#        if testboard.bytes_available():
#            byte = ord(testboard.sp.read(1))
#            if byte == 2:
#                print "RIGHT"
#            if byte == 1:
#                print "LEFT"
#            if byte == 3:
#                print "BOTH"
#            testboard.sp.flushInput()
#            time.sleep(0.005)
    sys.exit(0)