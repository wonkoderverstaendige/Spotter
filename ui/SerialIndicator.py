# -*- coding: utf-8 -*-
"""
Created on Wed Apr 03 21:51:53 2013

@author: fsm
"""

import sys
from PyQt4 import QtGui, QtCore

sys.path.append('./ui')
from arduino_indicator_widget import Ui_indicator

class SerialIndicator(QtGui.QWidget, Ui_indicator):

    connected = False

    def __init__(self, serial_wrapper, parent=None):
        super(SerialIndicator, self).__init__(parent)
        self.setupUi(self)
        self.serial_wrapper = serial_wrapper

        self.update_label()

        self.check_timer = QtCore.QTimer(self)
        self.check_timer.timeout.connect(self.refresh)
        self.check_timer.start(1000)

    def refresh(self):
        state = self.serial_wrapper.is_connected()
        if not self.connected == state:
            self.connected = state

            self.update_label()

    def update_label(self):
            if self.connected:
                self.lbl_indicator.setPixmap(QtGui.QPixmap("./ui/arduino_on.png"))
            else:
                self.lbl_indicator.setPixmap(QtGui.QPixmap("./ui/arduino_off_warning.png"))
