# -*- coding: utf-8 -*-
"""
Created on Tue Dec 04 21:41:19 2012
@author: <Ronny Eichler> ronny.eichler@gmail.com

Geometry functions.
"""

import math


class Point(object):
    """Single point in 2D plane."""
    def __init__(self, x=None, y=None):
        self._x, self._y = x, y

    def __eq__(self, point):
        """Points considered same if distance less than a pixel, allowing for some
        floating point tolerance.
        """
        return distance(self, point) <= 1.0

    def __ne__(self, point):
        return not self.__eq__(point)

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, x):
        self._x = x

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, y):
        self._y = y

    def is_valid(self):
        return None not in (self._x, self._y)


class PointArray(object):
    """List of points."""
    def __init__(self):
        self._x = []
        self._y = []

    def __getitem__(self, index):
        try:
            return Point(self._x[index], self._y[index])
        except IndexError:
            return None

    def __len__(self):
        return len(self._x)

    def append(self, point):
        self._x.append(point.x if point is not None else None)
        self._y.append(point.y if point is not None else None)

    def last(self):
        """Return last point, valid or not."""
        return self[-1]

    def last_valid(self):
        """Return last valid point and position of point in history."""
        n = min(len(self), 10)
        for step in range(n):
            if all([self._x[-step-1], self._y[-step-1]]):
                point = self[-step-1]
                assert point.is_valid()
                return point, step
        else:
            return None, None

    def clear(self):
        self._x = []
        self._y = []


def distance(p1, p2):
    """Euclidean distance between two points in 2D plane"""
    if all([p1 and p1.is_valid(), p2 and p2.is_valid()]):
        return math.sqrt((p1.x-p2.x)**2 + (p1.y-p2.y)**2)


def middle_point(point_list):
    """Find center point of a list of points.

    Returns None if no valid LEDs found, and position of single LED if only one valid, etc.
    """
    point_list = [point for point in point_list if point is not None and point.is_valid()]
    n = len(point_list)
    x = sum([1.0/n * point.x for point in point_list]) if n else None
    y = sum([1.0/n * point.y for point in point_list]) if n else None
    return Point(x, y)


# def scale_points(pts, rng):
#     """ Scale points in list of given normalized (0.0-1.0) points to a range
#     i.e. 1.0 --> 640 etc.
#     """
#     try:
#         is_list = len(pts[0]) > 1
#     except:  # Exception as inst
#         pts = [pts]
#         is_list = False
#
#     outpts = []
#     if type(rng[0]) == int and type(rng[1]) == int:
#         for p in pts:
#             outpts.append([int(p[0]*rng[0]), int(p[1]*rng[1])])
#     else:
#         for p in pts:
#             outpts.append([p[0]*rng[0], p[1]*rng[1]])
#
#     if is_list:
#         return outpts
#     else:
#         return outpts[0]
#
#
# def norm_points(pts, rng):
#     """ Normalize points in a list of points by dividing by their range
#     in the respective axis.
#     """
#     try:
#         is_list = len(pts[0]) > 1
#     except: # Exception as inst
#         pts = [pts]
#         is_list = False
#
#     outpts = []
#     for p in pts:
#         outpts.append( [p[0]*1.0/rng[0], p[1]*1.0/rng[1]] )
#
#     if is_list:
#         return outpts
#     else:
#         return outpts[0]


# def map_points(pt_list, range1, range2):
#     """ Map points from range 1 to range 2. """
#     npt = norm_points(pt_list, range1)
# #    print ('normalized: ', npt)
#     scpt = scale_points(npt, range2)
#     return scpt
#
#
# def scale(val, range1, range2):
#     """
#     Maps val of numerical range 1 to numerical range 2.
#     """
#     # normalize by range of range1, multiply by range of range2, offset
#     return ((float(val) - range1[0]) / (range1[1] - range1[0])) * (range2[1] - range2[0]) + range2[0]
#
#
# def extrapolateLinear(p1, p2):
#     """
#     Linear extrapolation of missing point
#     """
#     dx = p2[0] - p1[0]
#     dy = p2[1] - p2[1]
#
#     return tuple([p2[0]+dx, p2[1]+dy])


# def guessedPosition(pos_hist):
#     if len(pos_hist) >= 3:
#         if not (pos_hist[-1] is None):
#             return pos_hist[-1]
#         elif not ((pos_hist[-2] is None) or (pos_hist[-3] is None)):
#                 return extrapolateLinear(pos_hist[-3], pos_hist[-2])
#         else:
#             return None
#     else:
#         return None


# def perp(a):
#     """Line segment intersection using vectors. Modified and taken from:
#     http://www.cs.mun.ca/~rod/2500/notes/numpy-arrays/numpy-arrays.html
#     """
#     b = np.empty_like(a)
#     b[0] = -a[1]
#     b[1] = a[0]
#     return b
#
# def seg_intersect(a1, a2, b1, b2):
#     da = a2-a1
#     db = b2-b1
#     dp = a1-b1
#     dap = perp(da)
#     denom = np.dot( dap, db)
#     num = np.dot(dap, dp)
#     if denom == 0.0:
#         return None
#     else:
#         return (num / denom)*db + b1
#
#
# def point_in_polygon(point, poly):
#     """Improved point in polygon test which includes edge and vertex points
#     From: http://geospatialpython.com/2011/08/point-in-polygon-2-on-line.html
#     """
#     debug = True
#     x, y = point.x, point.y
#
#     # check if point is a vertex
#     if (x, y) in poly:
#         if debug:
#             print "Point is a vertex"
#         return True
#
#     # check if point is on a boundary
#     for i in range(1, len(poly)+1):
#         p1 = poly[i-1]
#         p2 = poly[i]
#         if p1.y == p2.y and p1.y == y and min(p1.x, p2.x) < x < max(p1.x, p2.x):
#             if debug:
#                 print "Point is on boundary"
#             return True
#
#     # check the actual polygon space
#     inside = False
#     p1x, p1y = poly[0]
#     for i in range(len(poly)+1):
#         p2x, p2y = poly[i % len(poly)]
#         if y > min(p1y, p2y):
#             if y <= max(p1y, p2y):
#                 if x <= max(p1x, p2x):
#                     if p1y != p2y:
#                         xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
#                     if p1x == p2x or x <= xints:
#                         inside = not inside
#         p1x, p1y = p2x, p2y
#
#     return inside


if __name__ == "__main__":
    pass
    #a = np.array( [0.0, 0.0] )
    #b = np.array( [0.0, 1.0] )
    #c = np.array( [1.0, 1.0] )
    #d = np.array( [1.0, 0.0] )
    #print seg_intersect( a,d, b,c)
    #
    #p1 = np.array( [2.0, 2.0] )
    #p2 = np.array( [4.0, 3.0] )
    #p3 = np.array( [6.0, 0.0] )
    #p4 = np.array( [6.0, 3.0] )
    #print seg_intersect( p1,p2, p3,p4)
    #
    ## Test a vertex for inclusion
    #poly = [(-33.416032,-70.593016), (-33.415370,-70.589604),
    #(-33.417340,-70.589046), (-33.417949,-70.592351),
    #(-33.416032,-70.593016)]
    #point = (-33.416032,-70.593016)
    #print point_in_poly(point, poly)
    #
    ## test a boundary point for inclusion
    #poly = [(1,1), (5,1), (5,5), (1,5), (1,1)]
    #point = (3, 1)
    #print point_in_poly(point, poly)
