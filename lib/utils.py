# -*- coding: utf-8 -*-
"""
Created on Mon Jul 09 14:45:41 2012

@author: Ronny
"""
from sys import float_info
import numpy as np
import cv2, time


def BGRpix2HSV( pixel ):
    """ Converts BGR color information of a single pixel to HSV """
    B = pixel[0]/255.
    G = pixel[1]/255.
    R = pixel[2]/255.

    V = max(R, G, B)

    # This requires some corner case handling when V or S get 0 to avoid
    # div by Zeros, will be rounded away upon return again
    if V < 2*float_info.epsilon:
        S = float_info.epsilon
    else:
        S = (V-min(R, G, B))/V
        if S < 2*float_info.epsilon:
            S = float_info.epsilon

    if V == R:
        H = 60 * (G-B)/S
    elif V == G:
        H = 120 + 60 * (B-R)/S
    elif V == B:
        H = 240 + 60 * (R-G)/S

    if H < 0:
        H += 360

    H /= 2.
    S *= 255.
    V *= 255.

    return int(H), int(S), int(V)

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



def drawPointer( frame, p1, p2, color=(255, 255, 255), length = 50):
    """ draws line prependicular to midpoint of line section between p1 and p2"""
    # TODO: - scale line by length

    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]

    ldx = dy
    ldy = -dx

    line_start = ( int(p1[0] + .5 * dx), int(p1[1] + .5 * dy) )
    line_end = (line_start[0] + ldx, line_start[1] + ldy)

    cv2.line(frame, line_start, line_end, color )


def drawTrace( frame, history, color, N ):
    N = min( N, len(history) )
    if N >= 2:
        for n in range(N-1, 0, -1):
            col = int( color/N * (N-n) )
            if history[-(n+1)] is None:
                continue
            elif history[-n] is None:
                n+=1
                continue
            else:
                cv2.line(frame,
                         tuple(history[-n]),
                         tuple(history[-(n+1)]),
                         [col, col, col],
                         1 )



def drawCross( frame, coords, size, color, gap = 7 ):
    """ Draws cross into BGR frame.
    ( frame = BGR image, coords = tuple(2 ints), size=int, color=tuple(3 ints), gap = int )
    """
    x, y = coords
    #left
    cv2.line(frame, (x - size - gap, y), (x - gap, y), color, 1)
    #right
    cv2.line(frame, (x + size + gap, y), (x + gap, y), color, 1)
    #up
    cv2.line(frame, (x, y - size - gap), (x, y - gap), color, 1)
    #down
    cv2.line(frame, (x, y + size + gap), (x, y + gap), color, 1)


def dst_file_name( destination ):
    """ Allows to automatically generate the output file name from tokens:
        %date-FORMAT        FORMAT as YYYYMMDDhhmmss
        %iterator           If file with base till this point exists, iterate
        $fixedString        $Animal52
    """
    # TODO: Destination file name generation
    return destination


class HSVHist:
    """ Calculate and show HSV histogram for the current frame shown
    in the main window. Clicking equally returns pixel information.
    From: http://www.pirobot.org/blog/0016/"""
    map_width = None
    map_height = None
    Map = None
    hist = None
    overlay = None
    frame = None
    log = True

    def __init__( self, width = 180, height = 100 ):
        if not width == None:
            self.map_width = width

        if not height == None:
            self.map_height = height

        self.createMap()


    def createMap( self ):
        """ Creates a HSV map with given size, best to give multiples of 180
            width
            height"""
        hsv_map = np.zeros( ( self.map_height, self.map_width, 3 ), np.uint8 )
        hsv_map[:,:,0] = np.uint8( np.linspace( 0, 180, self.map_width ) )
        hsv_map[:,:,1] = 255
        hsv_map[:,:,2] = 64
        self.Map = np.copy(hsv_map)

    def hueHist( self, frame ):
        self.frame = np.copy( frame )
        """ Calculate Hue histogram of given frame """
        hist_item = cv2.calcHist([self.frame], [0], None, [180], [0,179])
        if self.log:
            hist_item = cv2.log( hist_item + 1)
        cv2.normalize( hist_item, hist_item, 0, self.map_height, cv2.NORM_MINMAX )
        self.hist = np.copy( np.uint8( np.around( hist_item ) ) )


    def overlayHistMap( self ):
        self.overlay = np.copy( self.Map )
        h, w = self.map_height, self.map_width

#         this is terribly inefficient and should be done with numpy functions!
        for pos, hbin in enumerate( self.hist ):
            if hbin > 3:
                cv2.rectangle( self.overlay, (pos, h), ( pos + 1, h-hbin ), ( pos, 255, 128 ), -1 )

        self.overlay = cv2.cvtColor( self.overlay, cv2.COLOR_HSV2BGR )
