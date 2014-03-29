# -*- coding: utf-8 -*-
"""
Created on Sat Mar 29 18:52:52 2014
@author: <Ronny Eichler> ronny.eichler@gmail.com

PyQtGraph widget to draw video and ROIs onto QGraphicsView

Alternative backend to GLFrame
"""
import cv2

from lib.pyqtgraph import QtGui, QtCore  # ALL HAIL LUKE!
import lib.pyqtgraph as pg

from lib.ui.PGFrameUi import Ui_PGFrame

import numpy as np


class PGFrame(QtGui.QWidget, Ui_PGFrame):

    def __init__(self, *args, **kwargs):
        super(QtGui.QWidget, self).__init__(*args, **kwargs)
        self.setupUi(self)

        self.frame = None
        self.spotter = None
        self.draw_jobs = []

        # Central Video Frame
        self.gv_video.setBackground(None)
        self.vb = pg.ViewBox()
        self.gv_video.setCentralItem(self.vb)
        self.vb.setAspectLocked()
        self.img = pg.ImageItem()
        self.vb.addItem(self.img)
        self.vb.setRange(QtCore.QRectF(0, 0, 640, 360))

        # plot items for features and objects
        self.traces = dict()
        self.markers = dict()

    def update_world(self, spotter):
        if spotter is None:
            return

        if self.spotter is not spotter:
            self.spotter = spotter

        self.frame = self.spotter.newest_frame
        if self.frame is not None and self.frame.img is not None:
            shape = self.frame.img.shape
            self.img.setImage(cv2.transpose(self.frame.img), autoLevels=False)
            #self.gv_video.scaleToImage(self.img)

        # draw crosses and traces for objects
        for o in self.spotter.tracker.oois:
            if o.position is not None:
                #self.draw_jobs.append([self.drawCross, o.position, 8,
                #                  (1.0, 1.0, 1.0, 1.0), 7, True])
                if o.traced:
                    self.draw_jobs.append([self.draw_trace, o])

        self.populate_plot_items()
        self.process_draw_jobs()

    def process_draw_jobs(self):
        """ This puny piece of code is IMPORTANT! It handles all external
        drawing jobs! That looks really un-pythonic, by the way!
        j[0] is the reference to the drawing function
        (*j[1:]) expands the parameters for the drawing function to be called
        """
        while self.draw_jobs:
            j = self.draw_jobs.pop()
            draw_func = j[0]
            draw_func(*j[1:])

    def draw_trace(self, obj, color=(1.0, 1.0, 1.0, 1.0), num_points=100):  # array
        """ Draw trace of position given in array.

        TODO: Time vs. number of points into past
        """
        points = []
        for n in xrange(min(len(obj.pos_hist), num_points)):
            if obj.pos_hist[-n - 1] is not None:
                points.append([obj.pos_hist[-n - 1][0] * 1.0,
                               obj.pos_hist[-n - 1][1] * 1.0])
        self.traces[obj].setData(np.asarray(points))

    def populate_plot_items(self):
        # have a plot item for each drawing job
        # what a pain...
        for o in self.spotter.tracker.oois:
            if not o in self.traces:
                object_trace = pg.PlotDataItem()
                self.traces[o] = object_trace
                self.vb.addItem(object_trace)

        for f in self.spotter.tracker.leds:
            if not f in self.markers:
                feature_marker = pg.PlotDataItem()
                self.markers[f] = feature_marker
                self.vb.addItem(feature_marker)