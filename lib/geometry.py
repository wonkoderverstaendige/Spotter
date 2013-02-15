# -*- coding: utf-8 -*-
"""
Created on Tue Dec 04 21:41:19 2012
@author: <Ronny Eichler> ronny.eichler@gmail.com

Geometry functions.
"""

import numpy as np
import math

class Point:
    def __init__(self,x,y):
        self.x = x
        self.y = y

def middle_point( coord_list ):
    """ Find center point of a list of not None coordinates. E.g. find center
        of group of LEDs to track. Returns None if no valid LEDs found,
        and position of single LED if only one valid, etc.
    """
    # TODO: Proper type checking, corner cases, None etc.
    if len( coord_list ) > 0:
        x = y = 0
        n = len( coord_list )
        for c in coord_list:
            x += c[0]
            y += c[1]
        return [x/n, y/n]
    else:
        return None


def scale_points(pts, rng):
    """ Scale points in list of given nromalized (0.0-1.0) points to a range
    i.e. 1.0 --> 640 etc.
    """
    try:
        is_list = len(pts[0]) > 1
    except: # Exception as inst
        pts = [pts]
        is_list = False

    outpts = []
    if type(rng[0]) == int and type(rng[1]) == int:
        for p in pts:
            outpts.append( [int(p[0]*rng[0]), int(p[1]*rng[1])] )
    else:
        for p in pts:
            outpts.append( [p[0]*rng[0], p[1]*rng[1]] )

    if is_list:
        return outpts
    else:
        return outpts[0]


def norm_points(pts, rng):
    """ Normalize points in a list of points by dividing by their range
    in the respective axis.
    """
    try:
        is_list = len(pts[0]) > 1
    except: # Exception as inst
        pts = [pts]
        is_list = False

    outpts = []
    for p in pts:
        outpts.append( [p[0]*1.0/rng[0], p[1]*1.0/rng[1]] )

    if is_list:
        return outpts
    else:
        return outpts[0]


def map_points(pt_list, range1, range2):
    """ Map points from range 1 to range 2. """
    npt = norm_points(pt_list, range1)
#    print ('normalized: ', npt)
    scpt = scale_points(npt, range2)
    return scpt


def scale(val, range1, range2):
    """
    Maps val of numerical range 1 to numerical range 2.
    """
    # normalize by range of range1, multiply by range of range2, offset
    return ((float(val) - range1[0]) / (range1[1] - range1[0])) * (range2[1] - range2[0]) + range2[0]


def extrapolateLinear( p1, p2 ):
    """
    Linear extrapolation of missing point
    """
    dx = p2[0] - p1[0]
    dy = p2[1] - p2[1]

    return( tuple([p2[0]+dx, p2[1]+dy]) )


def guessedPosition( pos_hist ):
    if len(pos_hist) >= 3:
        if not (pos_hist[-1] is None):
            return pos_hist[-1]
        elif not ( (pos_hist[-2] is None) or (pos_hist[-3] is None) ):
                return extrapolateLinear( pos_hist[-3], pos_hist[-2] )
        else:
            return None
    else:
        return None

def distance(p1, p2):
    return math.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)



# line segment intersection using vectors
# modified and taken from:
#    http://www.cs.mun.ca/~rod/2500/notes/numpy-arrays/numpy-arrays.html
def perp( a ) :
    b = np.empty_like(a)
    b[0] = -a[1]
    b[1] = a[0]
    return b

def seg_intersect(a1,a2, b1,b2) :
    da = a2-a1
    db = b2-b1
    dp = a1-b1
    dap = perp(da)
    denom = np.dot( dap, db)
    num = np.dot( dap, dp )
    if denom == 0.0:
        return None
    else:
        return (num / denom)*db + b1


# Improved point in polygon test which includes edge
# and vertex points
#http://geospatialpython.com/2011/08/point-in-polygon-2-on-line.html
def point_in_poly(point, poly):
    x = point[0]
    y = point[1]
    n = len(poly)

    # check if point is a vertex
    if (x,y) in poly: return True

    # check if point is on a boundary
    for i in range(n):
        p1 = None
        p2 = None
        if i==0:
            p1 = poly[0]
            p2 = poly[1]
        else:
            p1 = poly[i-1]
            p2 = poly[i]
        if p1[1]==p2[1] and p1[1]==y and x > min(p1[0], p2[0]) and x < max(p1[0], p2[0]):
            return True

    # check the actual polygon space
    inside = False

    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x,p1y = p2x,p2y

    return inside


if __name__ == "__main__":
    a = np.array( [0.0, 0.0] )
    b = np.array( [0.0, 1.0] )
    c = np.array( [1.0, 1.0] )
    d = np.array( [1.0, 0.0] )
    print seg_intersect( a,d, b,c)

    p1 = np.array( [2.0, 2.0] )
    p2 = np.array( [4.0, 3.0] )
    p3 = np.array( [6.0, 0.0] )
    p4 = np.array( [6.0, 3.0] )
    print seg_intersect( p1,p2, p3,p4)

    # Test a vertex for inclusion
    poly = [(-33.416032,-70.593016), (-33.415370,-70.589604),
    (-33.417340,-70.589046), (-33.417949,-70.592351),
    (-33.416032,-70.593016)]
    point = (-33.416032,-70.593016)
    print point_in_poly(point, poly)

    # test a boundary point for inclusion
    poly = [(1,1), (5,1), (5,5), (1,5), (1,1)]
    point = (3, 1)
    print point_in_poly(point, poly)
