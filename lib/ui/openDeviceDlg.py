# -*- coding: utf-8 -*-
"""
Created on 3/31/14 2:37 AM 2013
@author: <'reichler'> ronny.eichler@gmail.com

OpenGL widget to draw video and primitives onto a GL context
"""

from PyQt4 import QtCore, QtGui
from openDeviceDlgUi import Ui_DeviceDialog


class OpenDeviceDlg(QtGui.QDialog, Ui_DeviceDialog):

    def __init__(self, parent=None):
        super(OpenDeviceDlg, self).__init__(parent)
        self.setupUi(self)