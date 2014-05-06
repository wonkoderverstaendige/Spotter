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
    _center = None
    _width = None
    _height = None
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
        if self.center is not None:
            self.center.x += dx
            self.center.y += dy
            self.update_representation()

    def move_to(self, point):
        """Move the shape to a new absolute position. """
        self.center = point
        self.update_representation()

    def scale_by(self, factor):
        self.width *= factor
        self.height *= factor
        self.update_representation()

    def scale_to(self, size):
        self.update_representation()
        raise NotImplementedError

    @property
    def radius(self):
        """Most shapes have no radius."""
        # TODO: Could return the radius of the bounding circle...
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
        """Middle point acting as reference point for within the shape."""
        return self._center

    @center.setter
    def center(self, point):
        self._center = point
        self.update_representation()

    @property
    def origin(self):
        if self.center is None:
            return None

        if self.angle is None or self.angle == 0:
            return geom.Point(self.center.x-self.width/2., self.center.y-self.width/2.)
        else:
            raise NotImplementedError

    @origin.setter
    def origin(self, point):
        if self.angle is None or self.angle == 0:
            self.center = geom.Point(point.x+self.width/2., point.y+self.height/2.)
        else:
            raise NotImplementedError

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
        return self.origin, self.size

    @bounding_box.setter
    def bounding_box(self, bb):
        self.size = bb[1]
        self.origin = bb[0]

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
        return self._minor * 2.0

    @property
    def width(self):
        return self._major * 2.0

    def check_collision(self, point):
        if not self.angle:
            return self.active and (point is not None)


class Rectangle(Shape):
    def __init__(self, *args, **kwargs):
        Shape.__init__(self, *args, **kwargs)
        self.log = logging.getLogger(__name__)
        self.shape = 'rectangle'

    def check_collision(self, point):
        if self.angle is None or self.angle == 0:
            in_x_interval = self.center - self.width/2. < point.x < self.center + self.width/2.
            in_y_interval = self.center - self.height/2. < point.y < self.center + self.height/2.
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