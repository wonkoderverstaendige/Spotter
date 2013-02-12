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
import re
import time
import platform

os_str = platform.system().lower()
if len(os_str) > 0:
    is_nix = os_str.find('linux') > -1 or os_str.find('darwin') > -1
    is_win = os_str.find("win") > -1
if is_nix:
    from serial.tools import list_ports
elif is_win:
    import _winreg as winreg
    import itertools
else:
    raise EnvironmentError("Operating system not recognized!")

print os_str

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
#        print ('DAC factor: ' + str(self.factor_dac))
#        print ('DAC offset: ' + str(self.offset_dac))
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
        if not self.serial_device:
            return
        if point == None:
            scaled_point = (0, 0)
        else:
            scaled_point = self.map_point(point)

        if self.is_open():
            self.serial_device.send_instructions([['dac', 0, scaled_point[0]],
                                                  ['dac', 1, scaled_point[1]]])

    def send_trigger_state(self, addr, data):
        if not self.serial_device:
            return
        if self.is_open():
            self.serial_device.send_instructions([['digital', addr, data]])


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


###############################################################################
# These two methods are directly taken from Eli Bendersky's example code:
# http://eli.thegreenplace.net/2009/07/31/listing-all-serial-ports-on-windows-with-python
###############################################################################
    def enum_win_ports(self):
        """ Uses the Win32 registry to return an
            iterator of serial (COM) ports
            existing on this computer.
        """
        path = 'HARDWARE\\DEVICEMAP\\SERIALCOMM'
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
        except WindowsError:
            raise IterationError

        for i in itertools.count():
            try:
                val = winreg.EnumValue(key, i)
                yield str(val[1])
            except EnvironmentError:
                break

    def full_port_name(self, portname):
        """ Given a port-name (of the form COM7,
            COM12, CNCA0, etc.) returns a full
            name suitable for opening with the
            Serial class.
        """
        m = re.match('^COM(\d+)$', portname)
        if m and int(m.group(1)) < 10:
            return portname
        return '\\\\.\\' + portname
###############################################################################

    def list_ports(self):
        """
        List all serial ports visible.

        On Windows, serial.tools.comports() does not return all ports, and
        seems to reliable miss the Serial port of the Arduinos. Not sure why,
        it seems to be widely used in examples. Maybe I am not using the
        iterator correctly. So for Windows, I'm using code from the always
        interesting Eli Bendersky, see comment above.
        """
        if is_nix:
            portlist = [p for p in list_ports.comports()]
        if is_win:
            portlist = [(p, self.full_port_name(p)) for p in self.enum_win_ports()]
            portlist.reverse()
        return portlist


    def close(self):
        """
        Close serial port if any device connected. May cause trouble if
        port remains open!
        """
        if self.serial_device:
            print 'Closing Serial'
            self.serial_device.close()


    def test_scan_frame(self, stepsize = 4):
        """
        scan through all points in frame size and give their coordinates
        as analog values via DACs, Stepsize to keep it at a reasonable
        time frame...
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
    chatter = Chatter(sys.argv[1])
    chatter.test_scan_frame(stepsize = 2)
    print 'Done'
#    time.sleep(2)
    chatter.close()