# -*- coding: utf-8 -*-
"""
Created on Sun Jan 13 14:19:24 2013
@author: <Ronny Eichler> ronny.eichler@gmail.com


"""

from PyQt4 import QtGui

from MainTabPage import Page
from side_barUi import Ui_side_bar

import TabFeatures
import TabObjects
import TabRegions
import TabSerial


class SideBar(QtGui.QWidget, Ui_side_bar):

    def __init__(self, *args, **kwargs):
        QtGui.QWidget.__init__(self)
        #super(QtGui.QWidget, self).__init__(parent)

        self.setupUi(self)

        self.features_page = Page("Features", TabFeatures.Tab, *args, **kwargs)
        self.tabs_main.insertTab(-1, self.features_page, self.features_page.label)

        self.objects_page = Page("Objects", TabObjects.Tab, *args, **kwargs)
        self.tabs_main.insertTab(-1, self.objects_page, self.objects_page.label)

        self.regions_page = Page("Regions", TabRegions.Tab, *args, **kwargs)
        self.tabs_main.insertTab(-1, self.regions_page, self.regions_page.label)

        self.serial_page = Page("Serial", TabSerial.Tab, *args, **kwargs)
        self.tabs_main.insertTab(-1, self.serial_page, self.serial_page.label)
