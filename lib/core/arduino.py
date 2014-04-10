# -*- coding: utf-8 -*-
"""
Created on Sat Jan  5 16:54:29 2013

@author: <Ronny Eichler> ronny.eichler@gmail.com

A lot of the handling is done the way Firmata handles the boards

TODO: How does the non-blocking pass_time function work exactly?
"""
import logging

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
    name = 'Arduino'

    def __init__(self, port, baud_rate=57600):

        self.log = logging.getLogger(__name__)

        self.sp = serial.Serial(port, baud_rate)
        self.pass_time(3)

        self.bytes_sent = 0
        self.bytes_received = 0

        self.pins = dict(dac=[], digital=[], pwm=[], adc=[])

        self.port_string = port
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
        return self.sp is not None and self.sp.isOpen()

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

            self.log.info('%d DAC pins available', len(self.pins['dac']))
            self.log.info('%d digital output pins available', len(self.pins['digital']))
            return True
        return False

    def read_all_bytes(self):
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
        """
        Send command byte followed by two data bytes. struct packs short
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
        cmd_values = [0, ord('H'), ord('P')]
        try:
            for i in instruction_list:
                # instruction and address
                msg += chr(cmd_values[i[0]] + i[1])
                data = i[2] if i[2] is not None else 0
                msg = msg + struct.pack('H', data) + '\n'
        except struct.error as error:
            self.log.error(error)

        # all instructions as one string to reduce the amount of
        # time spent in 4ms delay arduino spends on serial communication
        if self.sp is None:
            return False
        try:
            self.sp.write(msg)
        except serial.serialutil.SerialTimeoutException, error:  # or writeTimeoutError
            self.log.error(error)
            self.sp = None
            self.close()
            return False

        self.bytes_sent += len(msg)
        return True

    def close(self):
        """ Call this to exit a bit cleaner. """
        self.log.info("Closing Serial")
        if hasattr(self, 'sp') and self.sp is not None:
            self.null_pins()
            self.sp.close()
        self.bytes_received = 0
        self.bytes_sent = 0

    def null_pins(self):
        """ Reset the given pins to zero (0, low). If no pins given, do all. """
        if self.is_open():
            instr = []
            for pin_key in self.pins.iterkeys():
                for p in self.pins[pin_key]:
                    instr.append([p.type_id, p.id, 0])
            self.send_instructions(instr)

    @staticmethod
    def pass_time(duration):
        """ Non-blocking time-out for t seconds. """
        cont = time.time() + duration
        while time.time() < cont:
            time.sleep(0)


#############################################################
if __name__ == "__main__":
#############################################################
    test_board = Arduino(sys.argv[1])
#    while True:
#        if test_board.bytes_available():
#            byte = ord(test_board.sp.read(1))
#            if byte == 2:
#                print "RIGHT"
#            if byte == 1:
#                print "LEFT"
#            if byte == 3:
#                print "BOTH"
#            test_board.sp.flushInput()
#            time.sleep(0.005)
    sys.exit(0)