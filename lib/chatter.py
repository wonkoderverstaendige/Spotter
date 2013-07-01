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
from random import randint

os_str = platform.system().lower()
if len(os_str) > 0:
    if os_str.find('linux') > -1 or os_str.find('darwin') > -1:
        is_nix = True
        is_win = False
    else:
        is_nix = False #os_str.find("win") > -1
        is_win = True

if is_nix:
    from serial.tools import list_ports
elif is_win:
    import _winreg as winreg
    import itertools
else:
    raise EnvironmentError("Operating system not recognized!")


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

N_TRIES = 5

class Chatter:
    serial_device = None
    serial_port = None
    label = 'Arduino'
    connected = False

    def __init__(self, port, frame_size=(639, 359), max_dac=4095, auto=False):
        self.range_xy = frame_size

        self.factor_dac = (max_dac - 256.0) / max(frame_size)
        self.offset_dac = max_dac - self.factor_dac * max(frame_size)
        dr = int(self.factor_dac) * max(frame_size)
#        print ('DAC factor: ' + str(self.factor_dac))
#        print ('DAC offset: ' + str(self.offset_dac))
        self.range_dac = (dr, dr)

        self.auto = auto

        if port or auto:
            #CHECK ALL AVAILABLE PORTS FOR CONNECTION?
            # --> ON WINDOWS ALL, ON LINUX ONLY IF CANDIDATE!
            self.auto_connect(port)

    def auto_connect(self, port=None):
        """
        Try to connect to specific port. If no port specified, try to connect
        to all ports on the portlist. If any of them replies correctly, stop
        and be happy about the connection!
        """
        if port:
            if isinstance(port, basestring):
                portlist = [(port, port)]
            else:
                portlist = [port]
        else:
            portlist = self.list_ports()
#
#        print portlist

        for p in portlist:
            try:
                if self.open_serial(p[1]) and self.test_connection():
                    self.serial_port = p[1]
                    self.connected = True
                    return self.connected
            except Exception, e:
                print str(e)
                print 'This port was broken!'
        self.connected = False
        return self.connected

    def open_serial(self, port):
        self.close()
        print "Opening port "+ port
        self.serial_device = arduino.Arduino(port)
        if self.serial_device.is_open():
            self.serial_port = port
        return self.serial_device.is_open()

    def test_connection(self, test_vals=None):
        """
        Sends values from list test_vals to Arduino and compares response.
        If no response or reponse not matching, the test fails.
        """
        if not test_vals:
            test_vals = [0, self.range_dac[0], randint(0, 4095)]
        instructions = []
        for v in test_vals:
            instructions.append([0, 0, v])

        for n in xrange(N_TRIES):
            self.serial_device.send_instructions(instructions)
            time.sleep(0.1)
            if self.bytes_available():
                if test_vals == map(int, self.read_all().splitlines()):
                    if self.serial_device.get_pins():
                        return True
        return False

    def update_pins(self, slots):
        """ instr: [type, instr, data, index]"""
        if not self.connected:
            return

        instr = []
        for s in slots:
            if s.state_idx == None:
                instr.append([s.pin.type_id, s.pin.id, s.state()])
            else:
                data = s.state(s.state_idx)
                if s.type == 'digital':
                    if data:
                        data = 100 # pin HIGH if larger 0
                    else:
                        data = 0
                elif s.type == 'dac':
                    if data == None:
                        data = 0
                    else:
                        data = self.scale_point(data)[s.state_idx]
                instr.append([s.pin.type_id, s.pin.id, data])
        self.serial_device.send_instructions(instr)

    def pins_for_slot(self, slot):
        return self.pins(slot.type)

    def scale_point(self, point):
        coord_max = max(self.range_xy)

        # center point coordinates into range
        xc = point[0] + (coord_max - self.range_xy[0])/2.0
        # Y coordinate has to be flipped, origin is _upper_ left corner
        yc = (self.range_xy[1] - point[1]) + (coord_max - self.range_xy[1])/2.0
        xc = int(xc * self.factor_dac + self.offset_dac)
        yc = int(yc * self.factor_dac + self.offset_dac)
        return (xc, yc)

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

    def is_connected(self):
        return (self.connected) #self.is_open() and

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

    def pins(self, pin_type):
        if self.serial_device:
            try:
                return self.serial_device.pins[pin_type]
            except:
                return []
        else:
            return []


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
            return
#            raise EnvironmentError

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
        List all serial visible serial ports.

        On Windows, serial.tools.comports() does not return all ports, and
        seems to reliable miss the Serial port of the Arduinos. Not sure why,
        it seems to be widely used in examples. Maybe I am not using the
        iterator correctly. So for Windows, I'm using code from the always
        interesting Eli Bendersky, see above.
        """
        if is_nix:
            portlist = [p for p in list_ports.comports()]
        if is_win:
            portlist = [(p, self.full_port_name(p)) for p in self.enum_win_ports()]
        return self.clean_portlist(portlist)

    def clean_portlist(self, portlist):
        """
        Remove unlikely ports like Bluetooth modems etc. and sort in descending
        likelihood of usefulness.
        """
        if is_nix:
            for p in portlist:
                print p
        else:
            portlist.reverse()

        return portlist

    def close(self):
        """
        Close serial port if any device connected. May cause trouble if
        port remains open!
        """
        self.connected = False
        if self.serial_device:
            print 'Closing Serial'
            self.serial_device.close()

    def test_scan_frame(self, stepsize=4):
        """
        scan through all points in frame size and give their coordinates
        as analog values via DACs, Stepsize to keep it in a reasonable
        time frame...
        """
        for y in xrange(0, self.range_xy[1]+1, stepsize):
            t = time.clock()
            for x in xrange(0, self.range_xy[0]+1, stepsize):
                data = self.scale_point((x, y))
                self.serial_device.send_instructions([[1, 0, data[0]], [1, 1, data[1]]])
                self.read_all()
            print("line: " + str(y) + " t: " + str((time.clock() - t)) + " s")

        self.serial_device.send_instructions([[1, 0, 0], [1, 1, 0]])
        self.read_all()
        time.sleep(0.5)

        for x in xrange(0, self.range_xy[0]+1, stepsize):
            t = time.clock()
            for y in xrange(0, self.range_xy[1]+1, stepsize):
                data = self.scale_point((x, y))
                self.serial_device.send_instructions([[1, 0, data[0]], [1, 1, data[1]]])
            print("column: " + str(x) + " t: " + str((time.clock() - t)) + " s")

        self.serial_device.send_instructions([[1, 0, 0], [1, 1, 0]])
        self.read_all()
        time.sleep(0.5)

#############################################################
if __name__ == '__main__':
#############################################################
    chatter = Chatter(sys.argv[1])
    chatter.test_scan_frame(stepsize=2)
    chatter.close()