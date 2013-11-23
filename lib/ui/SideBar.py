# -*- coding: utf-8 -*-
"""
Created on Sun Jan 13 14:19:24 2013
@author: <Ronny Eichler> ronny.eichler@gmail.com


"""

import sys
from PyQt4 import QtGui, QtCore

sys.path.append('./ui')
sys.path.append('./ui/designer')

from MainTabPage import Page
from side_barUi import Ui_side_bar

import TabFeatures
import TabObjects
import TabRegions
import TabSerial

class SideBar(QtGui.QWidget, Ui_side_bar):

    def __init__(self, parent):
        super(QtGui.QWidget, self).__init__(parent)

        self.setupUi(self)

        self.features_page = Page(self, "Features", TabFeatures.Tab)
        self.tabs_main.insertTab(-1, self.features_page, self.features_page.label)

        self.objects_page = Page(self, "Objects", TabObjects.Tab)
        self.tabs_main.insertTab(-1, self.objects_page, self.objects_page.label)

        self.regions_page = Page(self, "Regions", TabRegions.Tab)
        self.tabs_main.insertTab(-1, self.regions_page, self.regions_page.label)

        self.serial_page = Page(self, "Serial", TabSerial.Tab)
        self.tabs_main.insertTab(-1, self.serial_page, self.serial_page.label)

