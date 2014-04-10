"""
Created on Sun Jan 13 14:19:24 2013
@author: <Ronny Eichler> ronny.eichler@gmail.com

Status Bar widget holding fps counter, frame buffer indicator, etc.
"""

from PyQt4 import QtGui, QtCore
from statusBarUi import Ui_statusBar


class StatusBar(QtGui.QWidget, Ui_statusBar):
    gui_fps = 30
    fps_low = False
    fps_low_now = False

    def __init__(self, parent):
        super(StatusBar, self).__init__()
        super(QtGui.QWidget, self).__init__(parent)
        self.setupUi(self)
