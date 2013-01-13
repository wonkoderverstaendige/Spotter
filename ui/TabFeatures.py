# -*- coding: utf-8 -*-
"""
Created on Sun Jan 13 14:19:24 2013
@author: <Ronny Eichler> ronny.eichler@gmail.com


"""

import sys
from PyQt4 import QtGui, QtCore

sys.path.append('./ui')
from tab_featuresUi import Ui_tab_features

class TabFeatures(QtGui.QWidget, Ui_tab_features):
    
    name = None
    
    def __init__(self, parent, label = None):
        if label == None:
            self.name = "newFeature"
        else:
            self.name = label
        super(QtGui.QWidget, self).__init__(parent)
        self.setupUi(self)
        
        self.combo_label.setEditText(label)
