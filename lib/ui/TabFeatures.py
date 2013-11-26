# -*- coding: utf-8 -*-
"""
Created on Sun Jan 13 14:19:24 2013
@author: <Ronny Eichler> ronny.eichler@gmail.com


"""
import logging

from PyQt4 import QtGui, QtCore
from tab_featuresUi import Ui_tab_features
import lib.utilities as utils
import math


class Tab(QtGui.QWidget, Ui_tab_features):

    label = None
    feature = None
    accept_events = False
    tab_type = "feature"
    current_range_hue = (None, None)

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

        self.update_color_space()

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

        self.update_color_space()

    def update_led(self):
        self.feature.range_hue = (self.spin_hue_min.value(), self.spin_hue_max.value())
        self.feature.range_sat = (self.spin_sat_min.value(), self.spin_sat_max.value())
        self.feature.range_val = (self.spin_val_min.value(), self.spin_val_max.value())
        self.feature.range_area = (self.spin_area_min.value(), self.spin_area_max.value())
        self.feature.detection_active = self.ckb_track.isChecked()
        self.feature.fixed_pos = self.ckb_fixed_pos.isChecked()
        self.feature.marker_visible = self.ckb_marker.isChecked()

    def update_color_space(self):
        """ Make the fancy rainbow color thingy. """

        # base string
        style_sheet = "background-color:qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0"

        if self.current_range_hue == self.feature.range_hue:
            return

        self.current_range_hue = self.feature.range_hue
        min_h = int(self.current_range_hue[0]*2)
        max_h = int(self.current_range_hue[1]*2)

        sv_inner = 255
        sv_outer = 80

        if min_h > max_h:
            min_h, max_h = max_h, min_h
            sv_outer, sv_inner = sv_inner, sv_outer

        epsilon = 0.0001

        stops_pos = [1.0/6*p for p in xrange(0, 7)]
        stops_hue = [(60*p) % 360 for p in xrange(0, 7)]
        stops_sv = [sv_outer]*len(stops_hue)

        stops = zip(stops_pos, stops_hue, stops_sv)

        # TODO: Check that min_h and max_h are not equal

        #print "Stop list:", stops
        if min_h in stops_hue:
            idx = stops_hue.index(min_h)
            stops.insert(idx+1, (stops_pos[idx]+epsilon, min_h, sv_inner))
            #print "min is stop!"
        else:
            idx = int(min_h/60+1)
            stops.insert(idx, (min_h/360., min_h, sv_outer))
            stops.insert(idx, (min_h/360.+epsilon, min_h, sv_inner))
            #print "min is not a stop!"

        if max_h in stops_hue:
            idx = stops_hue.index(max_h)
            stops.insert(idx+1, (stops_pos[idx]-epsilon, max_h, sv_inner))
            #print "max is stop!"
        else:
            idx = int(max_h/60+1) + (2 if min_h not in stops_hue else 1)
            stops.insert(idx, (max_h/360.-epsilon, max_h, sv_inner))
            stops.insert(idx+1, (max_h/360., max_h, sv_outer))
            #print "max is not a stop!"

        for idx, stop in enumerate(stops):
            if min_h < stop[1] < max_h:
                stops[idx] = (stop[0], stop[1], sv_inner)

        #print "Stop list:", stops

        for stop in stops:
            style_sheet += ", stop:{0[0]} hsva({0[1]}, {0[2]}, {0[2]}, 255)".format(stop)

        style_sheet += ");"
        #print style_sheet
        self.lbl_colorspace.setStyleSheet(style_sheet)

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
