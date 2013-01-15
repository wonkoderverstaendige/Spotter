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
        self.all_feature = parent.spotter.tracker.leds
        if label == None:
            self.name = self.object.label
        else:
            self.name = label
            self.object.label  = label
        super(QtGui.QWidget, self).__init__(parent)
        self.setupUi(self)



        # Fill tree/list with all available LEDs and mark linked as checked
        for l in self.all_feature:
            feature_item = QtGui.QTreeWidgetItem([l.label])
            feature_item.feature = l
            if feature_item.feature in self.object.linked_leds:
                feature_item.setCheckState(0,QtCore.Qt.Checked)
            else:
                feature_item.setCheckState(0,QtCore.Qt.Unchecked)
            self.tree_link_features.addTopLevelItem(feature_item)

        # I could not get the signal to work in the old connection syntax,
        # so I had to use the new one here. The new one is of course nice, but
        # I'd rather stick to the old for consistency. :(
        # NVM! It works with the old one, but why do I need that star?
#        self.tree_link_features.itemChanged.connect(self.itemChanged)
        self.connect(self.tree_link_features, QtCore.SIGNAL('itemChanged(QTreeWidgetItem *, int)'), self.itemChanged)

        self.connect(self.ckb_track, QtCore.SIGNAL('stateChanged(int)'), self.update_object)
        self.connect(self.ckb_trace, QtCore.SIGNAL('stateChanged(int)'), self.update_object)

        self.update()


    def itemChanged(self, item, column):
        """ Checks for differences in checkbox states and linked items.
        If any item in the tree widget is changed, which should only be
        the case if the user checks/unchecks a checkbox to link/unlink a
        feature.
        """
        feature_is_linked = (item.feature in self.object.linked_leds)
        if not item.checkState(column) == feature_is_linked:
            if item.checkState(column):
                self.link_feature(item.feature)
            else:
                self.unlink_feature(item.feature)


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
            

    def link_feature(self, feature):
        """ Link the object to the feature. """
        self.object.linked_leds.append(feature)

    def unlink_feature(self, feature):
        """ Remove a specific feature from the list. """
        self.object.linked_leds.pop(self.object.linked_leds.index(feature))

    def update_object(self):
        if self.name == None:
            print "Empty object tab! This should not have happened!"
            return
        self.object.tracked = self.ckb_track.isChecked()
        self.object.trace = self.ckb_trace.isChecked()