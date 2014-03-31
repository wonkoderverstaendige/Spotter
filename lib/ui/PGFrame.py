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
        self.rois = dict()

    def update_world(self, spotter):
        """Core refresh procedure for the PyQtGraph based video frame. Draws video and updates
        all things that have to be drawn, like traces and markers.
        """
        if spotter is None:
            return

        if self.spotter is not spotter:
            self.spotter = spotter

        # video frame
        self.frame = self.spotter.newest_frame
        if self.frame is not None and self.frame.img is not None:
            shape = self.frame.img.shape
            # The viewbox coordinate system and color layering is rather different from OpenCV
            #self.img.setImage(cv2.flip(cv2.transpose(cv2.cvtColor(self.frame.img, code=cv2.COLOR_BGR2RGB)), flipCode=1),
            #                  autoLevels=False)
            #self.img.setImage(cv2.cvtColor(self.frame.img, code=cv2.COLOR_BGR2RGB), autoLevels=False)
            #self.img.setImage(cv2.flip(self.frame.img, flipCode=-1), autoLevels=False)
            self.img.setImage(cv2.transpose(cv2.cvtColor(self.frame.img, code=cv2.COLOR_BGR2RGB)), autoLevels=False)
            #self.gv_video.scaleToImage(self.img)

        # draw crosses and traces for objects
        for o in self.spotter.tracker.oois:
            self.draw_jobs.append([self.draw_cross, o, 3, (1.0, 1.0, 1.0, 1.0), 7, True])
            if o.traced:
                self.draw_jobs.append([self.draw_trace, o])

        # draw crosses for features
        for l in self.spotter.tracker.leds:
            if len(l.pos_hist):
                if l.marker_visible:
                    self.draw_jobs.append([self.draw_cross, l, 7, l.lblcolor])

        self.populate_markers()
        self.populate_rois()
        self.populate_traces()

        self.process_draw_jobs()

    def process_draw_jobs(self):
        """ This puny piece of code is IMPORTANT! It handles all external
        drawing jobs! That looks really un-pythonic, by the way!
        job[0] is the reference to the drawing function
        (*job[1:]) expands the parameters for the drawing function to be called
        """
        while self.draw_jobs:
            job = self.draw_jobs.pop()
            job[0](*job[1:])

    def draw_trace(self, ref, color=(1.0, 1.0, 1.0, 1.0), num_points=100):
        """ Draw trace of position of the object given as reference ref.
        TODO: Time vs. number of points into past
        """
        points = []
        for n in xrange(min(len(ref.pos_hist), num_points)):
            if ref.pos_hist[-n - 1] is not None:
                points.append([ref.pos_hist[-n - 1][0] * 1.0,
                               ref.pos_hist[-n - 1][1] * 1.0])

        self.traces[ref].setData(np.asarray(points))

    def draw_cross(self, ref, size, color, gap=7, angled=False):
        """Draw marker (cross) of most recent position of referenced feature or object.
        """
        # TODO: When not visible, don't plot!
        if ref.pos_hist[-1] is not None:
            ax, ay = ref.pos_hist[-1][0], ref.pos_hist[-1][1]
            if angled:
                cross = [[ax-size, ay-size], [ax+size, ay+size], [ax, ay], [ax+size, ay-size], [ax-size, ay+size]]
            else:
                cross = [[ax-size, ay], [ax+size, ay], [ax, ay], [ax, ay-size], [ax, ay+size]]
            self.markers[ref].setPen((color[0]*255, color[1]*255, color[2]*255))
            self.markers[ref].setData(np.asarray(cross))
        else:
            self.markers[ref].setData((np.nan, np.nan))

    ### TRACES
    def populate_traces(self):
        self.prune_traces()
        for o in self.spotter.tracker.oois:
            if not o in self.traces:
                self.add_trace(o)

    def prune_traces(self):
        """Remove orphaned trace plot items.
        """
        orphaned = []
        for tk in self.traces.keys():
            if tk not in self.spotter.tracker.oois:
                orphaned.append(tk)
        for tk in orphaned:
            self.remove_trace(tk)

    def add_trace(self, tk):
        """Add trace plot item
        """
        self.traces[tk] = pg.PlotDataItem()
        self.vb.addItem(self.traces[tk])

    def remove_trace(self, tk):
        """Remove trace plot item
        """
        self.vb.removeItem(self.traces[tk])
        del self.traces[tk]

    ### MARKERS
    def populate_markers(self):
        """For PyQtGraph each marker or trace needs its own plot item that has to be
         handled continuously.
        """
        self.prune_markers()
        for o in self.spotter.tracker.oois:
            if not o in self.markers:
                self.add_marker(o)

        for f in self.spotter.tracker.leds:
            if not f in self.markers:
                self.add_marker(f)

    def prune_markers(self):
        """Remove orphaned markers from view.
        """
        orphaned = []
        for mk in self.markers.keys():
            if mk not in self.spotter.tracker.oois and mk not in self.spotter.tracker.leds:
                orphaned.append(mk)
        for mk in orphaned:
            self.remove_marker(mk)

    def add_marker(self, mk):
        """Add marker plot item to viewbox
        """
        self.markers[mk] = pg.PlotDataItem()
        self.vb.addItem(self.markers[mk])

    def remove_marker(self, mk):
        """Remove marker from viewbox
        """
        self.vb.removeItem(self.markers[mk])
        del self.markers[mk]

    #### ROIS
    def populate_rois(self):
        """Represent shapes of ROIs as PyQtGraph ROIs. This allows nicer UX and later
        more sophisticated interactions with the data.
        """
        self.prune_rois()
        for roi in self.spotter.tracker.rois:
            if roi not in self.rois:
                self.add_roi(roi)

    def prune_rois(self):
        """Brute force check for orphaned ROIs and remove if necessary.
        """
        orphaned = []
        for rk in self.rois.keys():
            if not rk in self.spotter.tracker.rois:
                orphaned.append(rk)
        for roi in orphaned:
            self.remove_roi(roi)

    def add_roi(self, rk):
        """Add ROI plot item
        """
        roi_shapes = []
        for s in rk.shapes:
            if s.shape == 'circle':
                pg_roi = pg.CircleROI((s.points[0][1], s.points[0][0]), (s.radius, s.radius), pen=pg.mkPen(rk.color))
            elif s.shape == 'rectangle':
                pg_roi = pg.RectROI((s.points[0][1], s.points[0][0]), (s.height, s.width), pen=pg.mkPen(rk.color))
            else:
                pg_roi = None
            if pg_roi is not None:
                roi_shapes.append(pg_roi)
                self.vb.addItem(pg_roi)
        self.rois[rk] = roi_shapes

    def remove_roi(self, roi):
        """Remove ROI (and all its shapes) from the roi dictionary and the plot.
        """
        if roi in self.rois:
            for shape in self.rois[roi]:
                self.remove_shape(shape)
            del self.rois[roi]

    def remove_shape(self, shape):
        """Remove a single shape from the plot.
        """
        self.vb.removeItem(shape)
