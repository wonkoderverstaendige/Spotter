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
    prefixes = ['CMD', 'DAC', 'DO', 'PWM']
    types = ['report', 'dac', 'digital', 'pwm']
    def __init__(self, idx, type_id):
        self.id = idx
        self.type_id = type_id
        self.type = self.types[type_id]
        self.label = ''.join([self.prefixes[type_id], '.', str(idx)])

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

        self.pins = dict(dac=[], digital=[], pwm=[], adc=[])

        self.portString = port
#        self.sp.flushInput()

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
        self.send_instructions([[0, 1, 0], [0, 2, 0]])
        # give arduino time to respond
        self.pass_time(0.1)
        if self.bytes_available():
            responses = map(int, self.read_all_bytes().splitlines())
            dac_pins = [Pin(idx, 1) for idx in xrange(responses[0])]
            dig_pins = [Pin(idx, 2) for idx in xrange(responses[1])]
            # Analog pins are of type 1
            self.pins['dac'].extend(dac_pins)
            # Digital Pins are type 2
            self.pins['digital'].extend(dig_pins)

            print '   --> SPI_DAC pins available:', len(self.pins['dac'])
            print '   --> Digital pins available:', len(self.pins['digital'])
            return True
        return False


    def null_pins(self, pins=None):
        """ Reset the given pins to zero (0, low). If no pins given, do all."""
        if self.is_open():
            instr = []
            for pkey in self.pins.iterkeys():
                for p in self.pins[pkey]:
                    instr.append([p.type_id, p.id, 0])
            self.send_instructions(instr)


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
        Type 0 = report
        Type 1 = dac
        Type 2 = digital
        Type 3 = PWM (not implemented!)
        Instruction: Type (3LSB bits) + Address (next 3 bits) and 2 data bytes
        DAC/SPI     Digital
        H DAC.0     P DO.0
        I DAC.1     Q DO.1
        J DAC.2     R DO.2
        K DAC.3     S DO.3
        L DAC.4     T DO.4
        M DAC.5     U DO.5
        N DAC.6     V DO.6
        O DAC.7     W DO.7
        """
        msg = ''
        cmd_vals = [0, ord('H'), ord('P')]
        for i in instruction_list:
            # instruction and address
            msg += chr(cmd_vals[i[0]] + i[1])
            data = i[2] if not i[2] == None else 0
            msg = msg + struct.pack('H', data) + '\n'

        # all instructions as one string to reduce the amount of
        # time spent in 4ms delay arduino spends on serial commmunication
        self.sp.write(msg)
        self.bytes_sent += len(msg)

    def close(self):
        """ Call this to exit cleanly. """
        if hasattr(self, 'sp'):
            self.null_pins()
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