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

    label = None
    accept_events = False
    tab_type = "object"

    def __init__(self, parent, object_handle, label = None):
        self.object = object_handle
        self.parent = parent

        self.all_features = self.parent.spotter.tracker.leds
        self.all_regions = self.parent.spotter.tracker.oois

        if label == None:
            self.label = self.object.label
        else:
            self.label = label
            self.object.label  = label
        super(QtGui.QWidget, self).__init__(parent)
        self.setupUi(self)

        self.connect(self.tree_link_features, QtCore.SIGNAL('itemChanged(QTreeWidgetItem *, int)'), self.feature_item_changed)

        self.connect(self.ckb_track, QtCore.SIGNAL('stateChanged(int)'), self.update_object)
        self.connect(self.ckb_trace, QtCore.SIGNAL('stateChanged(int)'), self.update_object)
        self.connect(self.ckb_analog_pos, QtCore.SIGNAL('stateChanged(int)'), self.update_object)

        self.update()

    def update(self):
        if self.label == None:
            print "empty tab"
            return

        self.refresh_feature_list()
        self.refresh_pin_list()

        if not self.ckb_trace.isChecked() == self.object.traced:
            self.ckb_trace.setChecked(self.object.traced)

        if not self.ckb_track.isChecked() == self.object.tracked:
            self.ckb_track.setChecked(self.object.tracked)

        if not self.ckb_analog_pos.isChecked() == self.object.analog_pos:
            self.ckb_analog_pos.setChecked(self.object.analog_pos)

        if self.object.guessed_pos:
            self.lbl_x.setText(str(self.object.guessed_pos[0]))
            self.lbl_y.setText(str(self.object.guessed_pos[1]))
        else:
            self.lbl_x.setText('---')
            self.lbl_y.setText('---')

    def update_object(self):
        if self.label == None:
            print "Empty object tab! This should not have happened!"
            return
        self.object.tracked = self.ckb_track.isChecked()
        self.object.traced = self.ckb_trace.isChecked()
        self.object.analog_pos = self.ckb_analog_pos.isChecked()
        self.combo_analog_signal.setEnabled(self.ckb_analog_pos.isChecked())

    def process_event(self, event):
        pass


###############################################################################
## FEATURE LIST
###############################################################################
    def refresh_feature_list(self):
        """
        Compare the content of the list of all available features with the
        current content of the feature tree/list widget. If anything is there
        that shouldn't be, remove it, if something is missing, add it.
        """
        remove = []
        listed = []
        for n in xrange(self.tree_link_features.topLevelItemCount()):
            if not self.tree_link_features.topLevelItem(n).feature in self.all_features:
                remove.append(self.tree_link_features.topLevelItem(n))
            else:
                listed.append(self.tree_link_features.topLevelItem(n).feature)

        map(self.remove_feature, [f for f in remove])
        map(self.add_feature, [f for f in self.all_features if f not in listed])

    def feature_item_changed(self, item, column):
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
        if not item.feature.label == item.text(0):
            item.feature.label = item.text(0)

    def add_feature(self, f):
        """ Add feature to feature list. """
        feature_item = QtGui.QTreeWidgetItem([f.label])
        feature_item.feature = f
        if feature_item.feature in self.object.linked_leds:
            feature_item.setCheckState(0,QtCore.Qt.Checked)
        else:
            feature_item.setCheckState(0,QtCore.Qt.Unchecked)
        self.tree_link_features.addTopLevelItem(feature_item)
        feature_item.setFlags(feature_item.flags() | QtCore.Qt.ItemIsEditable)

    def remove_feature(self, f):
        """ Remove feature from feature list. """
        self.tree_link_features.removeItemWidget(f)

    def link_feature(self, feature):
        """ Link the object to the feature. """
        self.object.linked_leds.append(feature)

    def unlink_feature(self, feature):
        """ Remove a specific feature from the list. """
        self.object.linked_leds.pop(self.object.linked_leds.index(feature))


###############################################################################
## PIN LIST
###############################################################################
    def refresh_pin_list(self):
        pins = self.parent.spotter.chatter.pins()
        if pins:
            pins = pins['dac']
        if self.parent.spotter.chatter.is_open() and pins:
            if not self.tree_link_spi_dac.topLevelItemCount() == pins.n:
                self.add_pin(self.tree_link_spi_dac.topLevelItemCount())
        else:
            while not self.tree_link_spi_dac.topLevelItemCount() == 0:
                self.remove_pin()

    def add_pin(self, pin):
        """
        Add a new digital out pin to the list of pins.
        """
        pin_item = QtGui.QTreeWidgetItem([str(pin)])
#        pin_item.pin = self.region.add_shape(shape_type, shape_points, shape_type)
        pin_item.setCheckState(0, QtCore.Qt.Unchecked)
        self.tree_link_spi_dac.addTopLevelItem(pin_item)
        self.tree_link_spi_dac.setCurrentItem(pin_item)
#        pin_item.setFlags(pin_item.flags() | QtCore.Qt.ItemIsEditable)

    def remove_pin(self):
        """ Remove a pin from the list of available digital out pins """
        print "removing pins"
        self.tree_link_spi_dac.takeTopLevelItem(0)
