# -*- coding: utf-8 -*-
"""
Created on Tue Dec 04 21:41:19 2012
@author: <Ronny Eichler> ronny.eichler@gmail.com

Shapes used for description of ROIs
"""

import logging
import lib.geometry as geom


def from_type(shape_type, *args, **kwargs):
    shapes = {'circle': Circle,
              'ellipse': Ellipse,
              'rectangle': Rectangle,
              'polygon': Polygon}

    try:
        return shapes[shape_type.lower()](*args, **kwargs)
    except KeyError:
        raise NotImplementedError


class Shape(object):
    """Geometrical shape that comprises ROIs. ROIs can be made of several
    independent shapes like two rectangles on either end of the track etc.
    """
    _origin = geom.Point(100, 100)
    _width = 100
    _height = 50
    _angle = None

    def __init__(self, parent, label, representation=None):
        self.parent = parent
        self.label = label
        self.active = True
        self.representation = representation
        self.shape = 'generic'
        self.dirty = False

    def move_by(self, dx, dy):
        """Move the shape relative to current position. """
        if self.origin is not None:
            self.origin.x += dx
            self.origin.y += dy
            self.update_representation()

    def move_to(self, point):
        """Move the shape to a new absolute position. """
        self.origin = point
        self.update_representation()

    def scale_by(self, factor):
        raise NotImplementedError
        self.width *= factor
        self.height *= factor
        self.update_representation()

    def scale_to(self, size):
        raise NotImplementedError
        self.update_representation()

    def representation_moved_to(self, representation):
        pos = representation.pos()
        self.origin = geom.Point(pos.x(), pos.y())

    @property
    def radius(self):
        """Most shapes have no radius."""
        # TODO: Could return the radius of the bounding circle...
        raise NotImplementedError
        return None

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, width):
        self._width = width
        self.update_representation()

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, height):
        self._height = height
        self.update_representation()

    @property
    def center(self):
        if self.angle is None or self.angle == 0:
            return geom.Point(self.origin.x+self.width/2., self.origin.y+self.height/2.)
        else:
            raise NotImplementedError

    @center.setter
    def center(self, point):
        raise NotImplementedError
        self.update_representation()

    @property
    def origin(self):
        return self._origin

    @origin.setter
    def origin(self, point):
        self._origin = point
        self.update_representation()

    @property
    def size(self):
        return self.width, self.height

    @size.setter
    def size(self, size):
        self.width, self.height = size[0], size[1]

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, angle):
        self._angle = angle
        self.update_representation()

    @property
    def bounding_box(self):
        if self.angle is None or self.angle == 0:
            return self.origin, self.size
        else:
            raise NotImplementedError

    @bounding_box.setter
    def bounding_box(self, bb):
        self.origin = bb[0]
        self.size = bb[1]

    def check_collision(self, point):
        return False

    def update_representation(self):
        if self.representation is not None:
            self.representation.update()


class Circle(Shape):
    _radius = 100

    def __init__(self, *args, **kwargs):
        Shape.__init__(self, *args, **kwargs)
        self.log = logging.getLogger(__name__)
        self.shape = 'circle'

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, radius):
        self._radius = radius

    @property
    def width(self):
        return 2.0 * self.radius

    @width.setter
    def width(self, width):
        self.radius = width / 2.0

    @property
    def height(self):
        return 2.0 * self.radius

    @height.setter
    def height(self, height):
        self.radius = height / 2.0

    def check_collision(self, point):
        # Compare distance center to point, must be > radius
        return self.active and (geom.distance(self.center, point) <= self.radius)


class Ellipse(Shape):
    _major = 100
    _minor = 50

    def __init__(self, *args, **kwargs):
        Shape.__init__(self, *args, **kwargs)
        self.log = logging.getLogger(__name__)
        self.shape = 'ellipse'

    @property
    def height(self):
        if not self.angle:
            return self._minor * 2.0
        else:
            raise NotImplementedError


    @property
    def width(self):
        if not self.angle:
            return self._major * 2.0
        else:
            raise NotImplementedError

    def check_collision(self, point):
        if not self.angle:
            return self.active and (point is not None)
        else:
            raise NotImplementedError


class Rectangle(Shape):
    def __init__(self, *args, **kwargs):
        Shape.__init__(self, *args, **kwargs)
        self.log = logging.getLogger(__name__)
        self.shape = 'rectangle'

    def check_collision(self, point):
        if self.angle is None or self.angle == 0:
            in_x_interval = self.origin.x < point.x < self.origin.x + self.width
            in_y_interval = self.origin.y < point.y < self.origin.y + self.height
            return self.active and in_x_interval and in_y_interval
        else:
            # complicated
            raise NotImplementedError


class Polygon(Shape):
    # TODO: n-polygon and collision detection
    def __init__(self, *args, **kwargs):
        Shape.__init__(self, *args, **kwargs)
        self.log = logging.getLogger(__name__)
        self.shape = 'polygon'

    @property
    def center(self):
        raise NotImplementedError

    def check_collision(self, point):
        raise NotImplementedError
        # geom.point_in_polygon(self.points[0], point)