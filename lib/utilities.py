# -*- coding: utf-8 -*-
"""
Created on Mon Jul 09 14:45:41 2012
@author: <Ronny Eichler> ronny.eichler@gmail.com

Helper functions.

"""
from sys import float_info
import numpy as np
import cv2
import math
#import time

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


def HSVpix2RGB( pixel ):
    """ Converts HSV color information of a single pixel to RGB """
    h, s, v = pixel
    S = s/255.0
    V = v/255.0
    H = h*2
    C = V * S;
    Hn = H/60.0
    
    X = C * (1 - abs((Hn % 2) -1))
    
    if 0 <= Hn and Hn < 1:
        RGB1 = (C, X, 0)
    elif 1 <= Hn and Hn < 2:
        RGB1 = (X, C, 0)
    elif 2 <= Hn and Hn < 3:
        RGB1 = (0, C, X)
    elif 3 <= Hn and Hn < 4:
        RGB1 = (0, X, C)
    elif 4 <= Hn and Hn < 5:
        RGB1 = (X, 0, C)
    elif 5 <= Hn and Hn < 6:
        RGB1 = (C, 0, X)
    else:
        print "Something went terribly wrong!"
        
    m = V - C
    return (RGB1[0]+m, RGB1[1]+m, RGB1[2]+m)


def mean_hue(range_hue):
    """ 
    Overly complicated formula to calculate the center color of the 
    HSV range, used for coloring of related labels etc.
    """
    if range_hue == None:
        return None
        
    if range_hue[0] <= range_hue[1]:
        mean_hue = sum(range_hue)/2
    else:
        center = ((180 - range_hue[0]) + range_hue[1])/2
        if range_hue[0] + center >= 180:
            mean_hue = range_hue[0] + center - 180
        else:
            mean_hue = range_hue[0] + center
    return mean_hue


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
    if destination == 'None':
        return None
    else:
        return destination

def binary_prefix(n_bytes):
    prefixes = {'0': 'B', '1': 'KiB', '2': 'MiB', '3': 'GiB', '4': 'TiB',
                '5': 'PiB', '6': 'EiB', '7': 'ZiB', '8': 'YiB'}
    
    for n in xrange(10):
        if (n_bytes/math.pow(2, 10*n) < 1000):
            num_str = '{0:.2f} ' + prefixes[str(n)]
            return num_str.format(n_bytes/math.pow(2, 10*n))
        
#    if n_bytes > math.pow(2, 60):
#        return '%d EiB'.format( % n_bytes/math.pow(2, 60)
#    if n_bytes > math.pow(2, 50):
#        return str(n_bytes/math.pow(2, 50)) + ' MiB'
#    if n_bytes > math.pow(2, 40):
#        return str(n_bytes/math.pow(2, 40)) + ' TiB'    
#    if n_bytes > math.pow(2, 30):
#        return str(n_bytes/math.pow(2, 30)) + ' GiB'
#    if n_bytes > math.pow(2, 20):
#        return str(n_bytes/math.pow(2, 20)) + ' MiB'
#    if n_bytes > math.pow(2, 10):
#        return str(n_bytes/math.pow(2, 10)) + ' KiB'

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
    binwidth = None

    def __init__( self, width = 180, height = 100, binwidth = 4 ):
        if not width == None:
            self.map_width = width

        if not height == None:
            self.map_height = height

        self.binwidth = binwidth

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
        """ Calculate Hue histogram """
        _,_,v = cv2.split( frame )
        lowerBound = np.array( [5], np.uint8 )
        upperBound = np.array( [254], np.uint8 )
        mask = cv2.inRange( frame, lowerBound, upperBound )

        self.frame = np.copy( frame )
        hist_item = cv2.calcHist([self.frame], [0], mask, [self.map_width/self.binwidth], [0,179])
        if self.log:
            hist_item = cv2.log( hist_item + 1)
        cv2.normalize( hist_item, hist_item, 0, self.map_height, cv2.NORM_MINMAX )
        self.hist = np.copy( np.uint8( np.around( hist_item ) ) )


    def overlayHistMap( self ):
        self.overlay = np.copy( self.Map )
        h, w = self.map_height, self.map_width
        ofs = self.binwidth

#         this is terribly inefficient and should be done with numpy functions!
        for pos, hbin in enumerate( self.hist ):
            if hbin > 1:
                cv2.rectangle( self.overlay, (ofs*pos, h), ( ofs*pos + (ofs-1), h-hbin ), ( ofs*pos, 255, 128 ), -1 )

        self.overlay = cv2.cvtColor( self.overlay, cv2.COLOR_HSV2BGR )
