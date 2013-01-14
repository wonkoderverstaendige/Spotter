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
        self.object = object_handle
        if label == None:
            self.name = tab_type
        else:
            self.name = tab_type
        super(QtGui.QWidget, self).__init__(parent)
        self.setupUi(self)
        
        self.update()
        
    def update(self):
        if self.name == None:
            print "empty tab"
            return
            
        if self.object.guessed_pos:
            self.lbl_x.setText(str(self.object.guessed_pos[0]))
            self.lbl_y.setText(str(self.object.guessed_pos[1]))
        else:
            self.lbl_x.setText('---')
            self.lbl_y.setText('---')


    def update_object(self):
        if self.name == None:
            print "Empty object tab! This should not have happened!"
            return