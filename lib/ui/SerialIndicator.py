#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 03 21:51:53 2013
@author: <Ronny Eichler> ronny.eichler@gmail.com

Checks state of serial connection and updates indicator Icon.
"""

import os
from PyQt4 import QtGui, QtCore
from serialIndicatorUi import Ui_indicator


class SerialIndicator(QtGui.QWidget, Ui_indicator):
    serial_wrapper = None

    def __init__(self, serial_wrapper=None, parent=None):
        super(SerialIndicator, self).__init__(parent)
        self.setupUi(self)
        self.connected = False
        self.warning = 0

        self.icon_connected = QtGui.QPixmap("./lib/ui/arduino_on.png")
        self.icon_disconnected = QtGui.QPixmap("./lib/ui/arduino_off.png")
        #self.icon_warning = QtGui.QPixmap("./lib/ui/arduino_off_warning.png")
        self.lbl_warning.setStyleSheet(' QLabel {color: red}')

        self.lbl_icon.mouseReleaseEvent = self.disable_warning
        self.lbl_warning.mouseReleaseEvent = self.disable_warning

        self.check_timer = QtCore.QTimer(self)
        self.check_timer.timeout.connect(self.refresh)

        if serial_wrapper is not None:
            self.initialize(serial_wrapper)

    def initialize(self, serial_wrapper):
        """Actually run things once the serial object is initated.
        """
        self.serial_wrapper = serial_wrapper

        self.refresh()
        self.check_timer.start(1000)

    def refresh(self):
        state = self.serial_wrapper.is_connected()

        # Connection state changed
        if self.connected != state:
            self.connected = state

            if self.connected:
                self.lbl_icon.setPixmap(self.icon_connected)
                self.lbl_warning.setText('')
                self.warning = 0
            else:
                self.lbl_icon.setPixmap(self.icon_disconnected)
                self.warning = 2

        # 1-sec refresh
        if self.warning:
            self.blink()

    def disable_warning(self, *args):
        if self.warning:
            self.lbl_warning.setText('')
            self.warning = 0

    def blink(self):
        """
        Show super obnoxious warning if the connection to Arduino was severed.
        """
        if self.warning % 2:
            self.lbl_warning.setText('')
        else:
            self.lbl_warning.setText('DISCONNECTED!')
        self.warning += 1