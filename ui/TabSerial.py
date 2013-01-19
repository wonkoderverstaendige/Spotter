# -*- coding: utf-8 -*-
"""
Created on Sun Jan 18 21:13:54 2013
@author: <Ronny Eichler> ronny.eichler@gmail.com


"""

import sys
from PyQt4 import QtGui, QtCore

sys.path.append('./ui')
from tab_serialUi import Ui_tab_serial

tab_type = "region"

class Tab(QtGui.QWidget, Ui_tab_serial):

    label = None
    serial = None
    accept_events = False
    tab_type = "serial"

    def __init__(self, parent, serial_handle, label = None):
        self.serial = serial_handle
        if label == None:
            self.label = self.serial.label
        else:
            self.label = label
            self.serial.label = label
        
        super(QtGui.QWidget, self).__init__(parent)
        self.setupUi(self)
        
        self.connect(self.btn_serial_refresh, QtCore.SIGNAL('clicked()'), self.refresh_port_list)
        self.connect(self.btn_serial_connect, QtCore.SIGNAL('clicked()'), self.toggle_connection)
        
        self.refresh_port_list()
        self.update()


    def update(self):
        if self.serial.is_open():
            self.lbl_bytes_sent.setText(str(self.serial.bytes_tx()) + ' B')
            self.lbl_bytes_received.setText(str(self.serial.bytes_rx()) + ' B')
    
    def refresh_port_list(self):
        """ Populates the list of available serial ports in the machine.
        May not work under windows at all. Would then require the user to 
        provide the proper port. Either via command line or typing it into the
        combobox.
        """
        candidate = None
        for p in self.serial.list_ports():
            print p
            if len(p) > 2 and "USB" in p[2]:
                candidate = p
            self.combo_serialports.addItem(p[0])
        if candidate:
            self.combo_serialports.setCurrentIndex(self.combo_serialports.findText(candidate[0]))


    def toggle_connection(self):
        self.btn_serial_connect.setText('Connecting...')
        self.serial.serial_port = str(self.combo_serialports.currentText())
        if self.serial.open_serial(self.serial.serial_port):
                    self.btn_serial_connect.setText('Connected!')
                    self.btn_serial_connect.setCheckable(True)
                    self.btn_serial_connect.setChecked(True)