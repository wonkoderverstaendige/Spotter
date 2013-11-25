# -*- coding: utf-8 -*-
"""
Created on Sun Jan 13 14:19:24 2013
@author: <Ronny Eichler> ronny.eichler@gmail.com


"""
import logging

from PyQt4 import QtGui, QtCore
from tab_featuresUi import Ui_tab_features
import lib.utilities as utils


class Tab(QtGui.QWidget, Ui_tab_features):

    label = None
    feature = None
    accept_events = False
    tab_type = "feature"

    def __init__(self, feature_ref, label=None, *args, **kwargs):
        #super(QtGui.QWidget, self).__init__(parent)
        QtGui.QWidget.__init__(self)
        self.log = logging.getLogger(__name__)
        self.setupUi(self)
        self.feature = feature_ref

        assert 'spotter' in kwargs
        self.spotter = kwargs['spotter']

        if label is None:
            self.label = self.feature.label
        else:
            self.label = label

        self.combo_label.setEditText(self.label)

        # Set spin boxes to the value of the represented feature
        self.spin_hue_min.setValue(self.feature.range_hue[0])
        self.spin_hue_max.setValue(self.feature.range_hue[1])
        self.spin_sat_min.setValue(self.feature.range_sat[0])
        self.spin_sat_max.setValue(self.feature.range_sat[1])
        self.spin_val_min.setValue(self.feature.range_val[0])
        self.spin_val_max.setValue(self.feature.range_val[1])
        self.spin_area_min.setValue(self.feature.range_area[0])
        self.spin_area_max.setValue(self.feature.range_area[1])

        # Connect checkboxes
        self.ckb_track.setChecked(self.feature.detection_active)
        self.ckb_fixed_pos.setChecked(self.feature.fixed_pos)
        self.ckb_marker.setChecked(self.feature.marker_visible)

        # Connect spin boxes
        self.connect(self.spin_hue_min, QtCore.SIGNAL('valueChanged(int)'), self.update_led)
        self.connect(self.spin_hue_max, QtCore.SIGNAL('valueChanged(int)'), self.update_led)
        self.connect(self.spin_sat_min, QtCore.SIGNAL('valueChanged(int)'), self.update_led)
        self.connect(self.spin_sat_max, QtCore.SIGNAL('valueChanged(int)'), self.update_led)
        self.connect(self.spin_val_min, QtCore.SIGNAL('valueChanged(int)'), self.update_led)
        self.connect(self.spin_val_max, QtCore.SIGNAL('valueChanged(int)'), self.update_led)
        self.connect(self.spin_area_min, QtCore.SIGNAL('valueChanged(int)'), self.update_led)
        self.connect(self.spin_area_max, QtCore.SIGNAL('valueChanged(int)'), self.update_led)

        self.connect(self.ckb_track, QtCore.SIGNAL('stateChanged(int)'), self.update_led)
        self.connect(self.ckb_fixed_pos, QtCore.SIGNAL('stateChanged(int)'), self.update_led)
        self.connect(self.ckb_marker, QtCore.SIGNAL('stateChanged(int)'), self.update_led)

        self.connect(self.btn_pick_color, QtCore.SIGNAL('toggled(bool)'), self.pick_color)

        self.update()

    def update(self):
        if self.label is None:
            print "Empty tab! This should not have happened!"
            return

        if not self.label == self.feature.label:
            self.label = self.feature.label

        if self.feature.pos_hist and self.feature.pos_hist[-1]:
            self.lbl_x.setText(str(int(self.feature.pos_hist[-1][0])))
            self.lbl_y.setText(str(int(self.feature.pos_hist[-1][1])))
        else:
            self.lbl_x.setText('---')
            self.lbl_y.setText('---')

    def update_led(self):
        self.feature.range_hue = (self.spin_hue_min.value(), self.spin_hue_max.value())
        self.feature.range_sat = (self.spin_sat_min.value(), self.spin_sat_max.value())
        self.feature.range_val = (self.spin_val_min.value(), self.spin_val_max.value())
        self.feature.range_area = (self.spin_area_min.value(), self.spin_area_max.value())
        self.feature.detection_active = self.ckb_track.isChecked()
        self.feature.fixed_pos = self.ckb_fixed_pos.isChecked()
        self.feature.marker_visible = self.ckb_marker.isChecked()

    def pick_color(self, state):
        self.accept_events = state

    def process_event(self, event_type, event):
        #print event_type
        if event_type == 'mousePress':
            x = int(event.x())
            y = int(event.y())
            pixel = self.spotter.newest_frame.img[y, x, :]
            #print pixel
            print "[X,Y][B G R](H, S, V):", [x, y], pixel, utils.BGRpix2HSV(pixel)
