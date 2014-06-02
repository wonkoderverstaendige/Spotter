# -*- coding: utf-8 -*-
"""
Created on Sat Mar 29 18:52:52 2014
@author: <Ronny Eichler> ronny.eichler@gmail.com

ROIs/Shapes to be drawn using the PGFrame backend
"""

import logging

from lib.pyqtgraph import QtGui, QtCore  # ALL HAIL LUKE!
import lib.pyqtgraph as pg
import lib.geometry as geom


class PGFrameROI(QtCore.QObject):
    def __init__(self, parent, roi):
        QtCore.QObject.__init__(self)
        self.log = logging.getLogger(__name__)

        self.parent = parent
        self.roi = roi
        self.color = self.roi.color
        self.alpha = 255
        self.pen = None
        self.update_pen()

        self.supported_shapes = {'circle': PGFrameCircle,
                                 'rectangle': PGFrameRectangle}
        self.shapes = dict()
        self.populate_shapes()

    def populate_shapes(self):
        for shape in self.roi.shapes:
            if not shape in self.shapes:
                self.add_shape(shape)

    def prune_shapes(self):
        for shape in self.shapes.keys():
            if not shape in self.roi.shapes:
                self.remove_shape(shape)

    def add_shape(self, shape):
        try:
            pgf_shape = self.supported_shapes[shape.shape.lower()](self, shape)
        except KeyError:
            raise NotImplementedError
        else:
            if pgf_shape is not None:
                self.shapes[shape] = pgf_shape
                self.parent.vb.addItem(pgf_shape.pg_roi)
            return pgf_shape

    def remove_shape(self, shape):
        self.parent.vb.removeItem(self.shapes[shape].pg_roi)
        del self.shapes[shape]

    def update(self):
        self.prune_shapes()
        self.populate_shapes()

        if self.color != self.roi.color:
            self.update_shape_colors()

        for spotter_shape, pg_shape in self.shapes.items():
            # show/hide shape is no longer active/inactive
            if spotter_shape.active:
                if pg_shape.pg_roi.currentPen is None:
                    pg_shape.pg_roi.setPen(self.pen)
            else:
                if pg_shape.pg_roi.currentPen is not None:
                    pg_shape.pg_roi.setPen(None)

            # if position of roi not the same as shape
            # Fixme: Rounding of coordinates causes stutter
            if spotter_shape.origin != geom.Point(pg_shape.pg_roi.pos()[0], pg_shape.pg_roi.pos()[1]):
                print 'not the same!', spotter_shape.origin, (pg_shape.pg_roi.pos()[0], pg_shape.pg_roi.pos()[1])
                pg_shape.pg_roi.setPos((spotter_shape.origin.x, spotter_shape.origin.y))

            if self.roi.highlighted and self.roi.color != (80, 80, 80):
                print self.roi, self.roi.color, self.roi.highlighted

    def update_shape_colors(self):
        self.color = self.roi.color
        self.update_pen(self.color)
        for spotter_shape, pg_roi in self.shapes.items():
            #if spotter_shape.active:
            pg_roi.set_pen(self.pen)

    def update_pen(self, color=None, alpha=None):
        if color is not None:
            self.color = color

        if alpha is not None:
            self.alpha = alpha

        self.pen = pg.mkPen(pg.mkColor((self.color[0], self.color[1], self.color[2], self.alpha)))


class PGFrameShape(QtCore.QObject):
    def __init__(self, parent_roi, shape):
        QtCore.QObject.__init__(self)
        self.parent_roi = parent_roi
        self.shape = shape
        self._origin, self._size = self.shape.bounding_box
        self._origin = self._origin if self._origin is not None and self._origin.is_valid() else geom.Point(50, 100)

    def set_pen(self, pen):
        self.pg_roi.setPen(pen)

    @staticmethod
    def translate_points_to_spotter(self):
        raise NotImplementedError

    @staticmethod
    def translate_points_to_pyqtgraph(self):
        # translate opencv coordinates into pyqtgraph coordinates
        # pyqtgraph ROIs take coordinates as a point + size bounding rect
        raise NotImplementedError

    @property
    def pos(self):
        return self.pg_roi.pos()

    @pos.setter
    def pos(self, pos):
        self.pg_roi.setPos(pos)

    @property
    def x(self):
        return self.pos[0]

    @property
    def y(self):
        return self.pos[1]

    @property
    def size(self):
        return self.pg_roi.size()

    @size.setter
    def size(self, size):
        self.pg_roi.setSize(size)

    @property
    def width(self):
        return self.size[0]

    @property
    def height(self):
        return self.size[1]


class PGFrameRectangle(PGFrameShape):
    def __init__(self, parent_roi, shape):
        PGFrameShape.__init__(self, parent_roi, shape)
        self.pg_roi = pg.RectROI((self._origin.x, self._origin.y), self._size, pen=parent_roi.pen)
        self.pg_roi.addRotateHandle([1, 0], [0.5, 0.5])
        self.pg_roi.sigRegionChanged.connect(self.shape.representation_moved_to)

    # def translate_points_to_pyqtgraph(self):
    #     (x, y) = shape.points[0]
    #     (w, h) = (shape.width, shape.height)
    #     point = map(floor, (x, y))
    #     size = map(floor, (w, h))
    #     return point, size
    #
    # def translate_points_to_spotter(self):
    #     (w, h) = self.shape.width, self.shape.height
    #     p1 = self.shape.center.x, self.shape.center.y
    #     p2 = map(floor, (p1[0]+w, p1[1]+h))
    #     return point, size


class PGFrameCircle(PGFrameShape):
    def __init__(self, parent_roi, shape):
        PGFrameShape.__init__(self, parent_roi, shape)
        self.pg_roi = pg.CircleROI((self._origin.x, self._origin.y), self._size, pen=parent_roi.pen)
        self.pg_roi.sigRegionChanged.connect(self.shape.representation_moved_to)

    # def translate_points_to_pyqtgraph(self):
    #     (x, y) = shape.points[0]
    #     (w, h) = (shape.width, shape.height)
    #     point = map(floor, (x-shape.radius, y-shape.radius))
    #     size = map(floor, (w, h))
    #     return point, size
    #
    # def translate_points_to_spotter(self):
    #     (w, h) = self.shape.width, self.shape.height
    #     p1 = self.shape.center.x+w/2., self.center.x+w/2.
    #     p2 = p1[0]+w/2., p1[1]
    #
