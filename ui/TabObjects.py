# -*- coding: utf-8 -*-
"""
Created on Sun Jan 13 14:19:24 2013
@author: <Ronny Eichler> ronny.eichler@gmail.com


"""

import sys
from PyQt4 import QtGui, QtCore

sys.path.append('./ui')
from tab_objectsUi import Ui_tab_objects

tab_type = "object"

class Tab(QtGui.QWidget, Ui_tab_objects):
    
    name = None
    led = None
    
    def __init__(self, parent, object_handle, label = None):
        if label == None:
            self.name = tab_type
        else:
            self.name = tab_type
        super(QtGui.QWidget, self).__init__(parent)
        self.setupUi(self)
        
        self.combo_label.setEditText(self.name)
