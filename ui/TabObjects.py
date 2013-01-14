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

    def __init__(self, parent, object_handle, label = None):
        self.object = object_handle
        self.all_leds = parent.spotter.tracker.leds
        if label == None:
            self.name = tab_type
        else:
            self.name = tab_type
        super(QtGui.QWidget, self).__init__(parent)
        self.setupUi(self)

        # Fill combo box with all available LEDs
        for l in self.all_leds:
           self.combo_features.addItem(l.label)

        # Fill list with LEDs linked to this object
        for l in self.object.linked_leds:
            self.list_leds.addItem(l.label)

        self.connect(self.btn_link_feature, QtCore.SIGNAL('clicked()'), self.link_led)
        self.connect(self.btn_unlink_feature, QtCore.SIGNAL('clicked()'), self.unlink_led)

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

    def link_led(self):
        self.object.linked_leds.append(self.all_leds[self.combo_features.currentIndex()])
        self.list_leds.addItem(self.combo_features.currentText())

    def unlink_led(self):
        # The order in the list is reversed for some reason.
        if self.list_leds.count():
            selection_idx = self.list_leds.count() - self.list_leds.currentRow() -1
#            print (self.list_leds.count(), selection_idx, self.list_leds.currentRow())
            self.object.linked_leds.pop(selection_idx)
            self.list_leds.takeItem(self.list_leds.currentRow())

    def update_object(self):
        if self.name == None:
            print "Empty object tab! This should not have happened!"
            return