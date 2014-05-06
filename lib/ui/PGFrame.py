# -*- coding: utf-8 -*-
"""
Created on Sat Mar 29 18:52:52 2014
@author: <Ronny Eichler> ronny.eichler@gmail.com

PyQtGraph widget to draw video and ROIs onto QGraphicsView

Alternative backend to GLFrame
"""
import cv2
import logging

from lib.pyqtgraph import QtGui, QtCore  # ALL HAIL LUKE!
import lib.pyqtgraph as pg

from lib.ui.PGFrameUi import Ui_PGFrame
from lib.ui.PGFrameROI import PGFrameROI

import numpy as np


class PGFrame(QtGui.QWidget, Ui_PGFrame):

    def __init__(self, *args, **kwargs):
        super(QtGui.QWidget, self).__init__(*args, **kwargs)
        self.log = logging.getLogger(__name__)
        self.setupUi(self)

        self.frame = None
        self.spotter = None
        self.draw_jobs = []

        # Central Video Frame
        self.gv_video.setBackground(None)
        self.vb = pg.ViewBox(invertY=True)
        # self.vb.setMouseEnabled(False, False)
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
            #self.img.setImage(np.rot90(cv2.cvtColor(self.frame.img, code=cv2.COLOR_BGR2RGB), 3), autoLevels=False)
            #self.img.setImage(cv2.flip(self.frame.img, flipCode=-1), autoLevels=False)
            self.img.setImage(cv2.transpose(cv2.cvtColor(self.frame.img, code=cv2.COLOR_BGR2RGB)), autoLevels=False)
            #self.gv_video.scaleToImage(self.img)

        self.update_rois()
        self.update_markers()
        self.update_traces()

        # draw crosses and traces for objects
        for ooi in self.spotter.tracker.oois:
            self.draw_jobs.append([self.draw_marker, ooi, 3, (1.0, 1.0, 1.0, 1.0), 7, True])
            if ooi.traced:
                self.draw_jobs.append([self.draw_trace, ooi])

        # draw crosses for features
        for feature in self.spotter.tracker.features:
            if len(feature.pos_hist):
                if feature.marker_visible:
                    self.draw_jobs.append([self.draw_marker, feature, 7, feature.lbl_color])

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

    ### TRACES
    def update_traces(self):
        self.prune_traces()
        self.populate_traces()

    def populate_traces(self):
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

    def draw_trace(self, ref, color=(1.0, 1.0, 1.0, 1.0), num_points=100):
        """ Draw trace of position of the object given as reference ref.
        TODO: Time vs. number of points into past
        """
        if self.frame is None:
            return

        points = []
        for n in xrange(min(len(ref.pos_hist), num_points)):
            p = ref.pos_hist[-n-1]
            if p is not None and p.is_valid():
                points.append([ref.pos_hist[-n-1].x, ref.pos_hist[-n-1].y])

        self.traces[ref].setData(np.asarray(points))

    ### MARKERS
    def update_markers(self):
        self.prune_markers()
        self.populate_markers()

    def populate_markers(self):
        """For PyQtGraph each marker or trace needs its own plot item that has to be
         handled continuously.
        """
        for o in self.spotter.tracker.oois:
            if not o in self.markers:
                self.add_marker(o)

        for f in self.spotter.tracker.features:
            if not f in self.markers:
                self.add_marker(f)

    def prune_markers(self):
        """Remove orphaned markers from view.
        """
        orphaned = []
        for mk in self.markers.keys():
            if mk not in self.spotter.tracker.oois and mk not in self.spotter.tracker.features:
                orphaned.append(mk)
        for mk in orphaned:
            self.remove_marker(mk)

    def add_marker(self, mk):
        """Add marker plot item to ViewBox
        """
        self.markers[mk] = pg.PlotDataItem()
        self.vb.addItem(self.markers[mk])

    def remove_marker(self, mk):
        """Remove marker from ViewBox
        """
        self.vb.removeItem(self.markers[mk])
        del self.markers[mk]

    def draw_marker(self, ref, size, color, gap=7, angled=False):
        """Draw marker (cross) of most recent position of referenced feature or object.
        """
        # TODO: When not visible, don't plot!
        if self.frame is None:
            return

        p = ref.pos_hist.last()
        if p is not None and p.is_valid():
            x, y = p.x, p.y
            if angled:
                cross = [[x-size, y-size], [x+size, y+size], [x, y], [x+size, y-size], [x-size, y+size]]
            else:
                cross = [[x-size, y], [x+size, y], [x, y], [x, y-size], [x, y+size]]
            self.markers[ref].setPen((color[0]*255, color[1]*255, color[2]*255))
            self.markers[ref].setData(np.asarray(cross))
        else:
            self.markers[ref].setPen(None)

    #### ROIS
    def update_rois(self):
        self.prune_rois()
        self.populate_rois()
        for spotter_roi, pgf_roi in self.rois.items():
            pgf_roi.update()

    def populate_rois(self):
        """Represent shapes of ROIs as PyQtGraph ROIs. This allows nicer UX and later
        more sophisticated interactions with the data.
        """
        for roi in self.spotter.tracker.rois:
            if roi not in self.rois:
                self.add_roi(roi)

    def prune_rois(self):
        """Brute force check for orphaned ROIs and remove if necessary.
        """
        orphaned = [rk for rk in self.rois.keys() if not rk in self.spotter.tracker.rois]
        for roi in orphaned:
            self.remove_roi(roi)

    def add_roi(self, roi):
        """Add ROI. """
        self.rois[roi] = PGFrameROI(self, roi)
        self.log.debug('Added %s' % roi.label)

    def remove_roi(self, roi):
        """Remove ROI (and all its shapes) from the roi dictionary and the plot.
        """
        try:
            del self.rois[roi]
            self.log.debug('Removed %s' % roi.label)
        except KeyError:
            self.log.error("Couldn't remove ROI %s: Not found." % roi)

    def remove_shape(self, shape):
        """Remove a single shape from the plot.
        """
        self.vb.removeItem(shape)
