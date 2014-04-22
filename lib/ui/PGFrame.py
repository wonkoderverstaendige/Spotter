# -*- coding: utf-8 -*-
"""
Created on Sat Mar 29 18:52:52 2014
@author: <Ronny Eichler> ronny.eichler@gmail.com

PyQtGraph widget to draw video and ROIs onto QGraphicsView

Alternative backend to GLFrame
"""
import cv2
from math import floor
import logging

from lib.pyqtgraph import QtGui, QtCore  # ALL HAIL LUKE!
import lib.pyqtgraph as pg

from lib.ui.PGFrameUi import Ui_PGFrame

import numpy as np


class PGFrameROI(QtCore.QObject):
    def __init__(self, parent, roi):
        QtCore.QObject.__init__(self)
        self.log = logging.getLogger(__name__)

        self.parent = parent
        self.roi = roi
        self.color = self.roi.color
        self.alpha = 255
        self.update_pen()

        self.shapes = dict()
        for shape in self.roi.shapes:
            self.add_shape(shape)

    def populate_shapes(self):
        for shape in self.roi.shapes:
            if not shape in self.shapes:
                self.add_shape(shape)

    def prune_shapes(self):
        for shape in self.shapes.keys():
            if not shape in self.roi.shapes:
                self.remove_shape(shape)

    def add_shape(self, shape):

        point, size = self.translate_points_to_pyqtgraph(shape)
        if shape.shape == 'circle':
            pg_roi = pg.CircleROI(point, size, pen=self.pen)
        elif shape.shape == 'rectangle':
            pg_roi = pg.RectROI(point, size, pen=self.pen)
        else:
            return None

        if pg_roi is not None:
            self.shapes[shape] = pg_roi
            if pg_roi is not None:
                pg_roi.sigRegionChanged.connect(self.shape_changed)
            self.parent.vb.addItem(pg_roi)
        return pg_roi

    def remove_shape(self, shape):
        self.parent.vb.removeItem(self.shapes[shape])
        del self.shapes[shape]

    def update(self):
        self.prune_shapes()
        self.populate_shapes()

        if self.color != self.roi.color:
            self.update_shape_colors()

        for spotter_shape, pg_roi in self.shapes.items():
            # show/hide shape is no longer active/inactive
            if spotter_shape.active:
                if pg_roi.currentPen is None:
                    pg_roi.setPen(self.pen)
            else:
                if pg_roi.currentPen is not None:
                    pg_roi.setPen(None)

            # if position of roi not the same as shape
            # Fixme: Rounding of coordinates causes stutter
            if spotter_shape.origin() != (pg_roi.pos()[0], pg_roi.pos()[1]):
                print 'not the same!', spotter_shape.origin(), (pg_roi.pos()[0], pg_roi.pos()[1])
                pg_roi.setPos(spotter_shape.origin())

            if self.roi.highlighted and self.roi.color != (80, 80, 80):
                print self.roi, self.roi.color, self.roi.highlighted

    @staticmethod
    def translate_points_to_spotter(roi, shape):
        # update position of the shape
        if shape.shape == 'circle':
            (w, h) = roi.size()
            p1 = map(floor, (roi.pos()[0]+w/2., roi.pos()[1]+w/2.))
            p2 = map(floor, (p1[0]+w/2., p1[1]))

        elif shape.shape == 'rectangle':
            (w, h) = roi.size()
            p1 = map(floor, (roi.pos()[0], roi.pos()[1]))
            p2 = map(floor, (p1[0]+w, p1[1]+h))
        else:
            raise NotImplementedError

        return [p1, p2]

    @staticmethod
    def translate_points_to_pyqtgraph(shape):
        # translate opencv coordinates into pyqtgraph coordinates
        # pyqtgraph ROIs take coordinates as a point + size bounding rect
        (x, y) = shape.points[0]
        (w, h) = (shape.width, shape.height)

        if shape.shape == 'circle':
            point = map(floor, (x-shape.radius, y-shape.radius))
            size = map(floor, (w, h))
        elif shape.shape == 'rectangle':
            point = map(floor, (x, y))
            size = map(floor, (w, h))
        else:
            raise NotImplementedError

        return point, size

    def shape_changed(self, calling_roi):
        # find moved pg_roi
        for spotter_shape, pg_roi in self.shapes.items():
            if pg_roi is calling_roi:
                moved_shape = spotter_shape
                break
        else:
            self.log.error("Moved ROI not found!")
            return

        points = self.translate_points_to_spotter(calling_roi, moved_shape)
        print 'Move to', points
        moved_shape.move_to(points=points)

    def update_shape_colors(self):
        self.color = self.roi.color
        self.update_pen(self.color)
        for spotter_shape, pg_roi in self.shapes.items():
            #if spotter_shape.active:
            pg_roi.setPen(self.pen)

    def update_pen(self, color=None, alpha=None):
        if color is not None:
            self.color = color

        if alpha is not None:
            self.alpha = alpha

        self.pen = pg.mkPen(pg.mkColor((self.color[0], self.color[1], self.color[2], self.alpha)))


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
                    self.draw_jobs.append([self.draw_marker, feature, 7, feature.lblcolor])

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
            if ref.pos_hist[-n - 1] is not None:
                # if we rotate the frame, height becomes width!
                # points.append([ref.pos_hist[-n - 1][0] * 1.0,
                #                self.frame.width-ref.pos_hist[-n - 1][1] * 1.0])
                points.append([ref.pos_hist[-n - 1][0] * 1.0, ref.pos_hist[-n - 1][1] * 1.0])

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
        if ref.pos_hist[-1] is not None:
            # if we rotate the frame, height becomes width!
            # ax, ay = ref.pos_hist[-1][0], self.frame.width-ref.pos_hist[-1][1]
            ax, ay = ref.pos_hist[-1][0], ref.pos_hist[-1][1]
            if angled:
                cross = [[ax-size, ay-size], [ax+size, ay+size], [ax, ay], [ax+size, ay-size], [ax-size, ay+size]]
            else:
                cross = [[ax-size, ay], [ax+size, ay], [ax, ay], [ax, ay-size], [ax, ay+size]]
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
        # [self.remove_roi(roi) for roi in [rk for rk in self.rois.keys() if not rk in self.spotter.tracker.rois]]
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
