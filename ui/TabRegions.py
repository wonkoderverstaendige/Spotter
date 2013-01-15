# -*- coding: utf-8 -*-
"""
Created on Sun Jan 13 14:19:24 2013
@author: <Ronny Eichler> ronny.eichler@gmail.com


"""

import sys
from PyQt4 import QtGui, QtCore

sys.path.append('./ui')
from tab_regionsUi import Ui_tab_regions

tab_type = "region"

class Tab(QtGui.QWidget, Ui_tab_regions):

    name = None
    accept_region = False

    def __init__(self, parent, region_handle, label = None):
        self.region = region_handle
        if label == None:
            self.name = self.region.label
        else:
            self.name = label
            self.region.label = label
        super(QtGui.QWidget, self).__init__(parent)
        self.setupUi(self)

        self.connect(self.btn_select_region, QtCore.SIGNAL('toggled(bool)'), self.select_region)

        self.select_signal = QtCore.pyqtSignal(object)

        self.update()


    def update(self):
        if self.name == None:
            print "empty tab"
            return

    def select_region(self, state):
        self.accept_region = state


    def process_region(self, region):
        pass
        print region

    def add_region(self, region):
        self.tree_regions.addTopLevelItem(region)

    def update_region(self):
        if self.name == None:
            print "Empty object tab! This should not have happened!"
            return
