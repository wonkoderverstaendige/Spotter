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
    
def drawCross( frame, x, y, size, color, gap = 7 ):
    #left    
    cv2.line(frame, (x - size - gap, y), (x - gap, y), color, 1)
    #right
    cv2.line(frame, (x + size + gap, y), (x + gap, y), color, 1)
    #up
    cv2.line(frame, (x, y - size - gap), (x, y - gap), color, 1)
    #down
    cv2.line(frame, (x, y + size + gap), (x, y + gap), color, 1)
    #return frame
        
        
    
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
        hsv_map = np.zeros((self.map_height, self.map_width, 3), np.uint8)
        hsv_map[:,:,0] = np.uint8(np.linspace(0, 180, self.map_width))
        hsv_map[:,:,1] = 255
        hsv_map[:,:,2] = 64
        self.Map = np.copy(hsv_map)
        
    def calcHist( self, frame ):
        self.frame = np.copy(frame)
        """ Calculate Hue histogram of given frame """
        hist_item = cv2.calcHist([self.frame], [0], None, [180], [0,179])
        if self.log:        
            hist_item = cv2.log(hist_item+1)
        cv2.normalize(hist_item, hist_item, 0, self.map_height, cv2.NORM_MINMAX)
        self.hist=np.copy(np.uint8(np.around(hist_item)))

    
    def overlayHistMap( self ):
        self.overlay = np.copy(self.Map)
        h, w = self.map_height, self.map_width
        
#         this is terribly inefficient and should be done with numpy functions!
        for pos, hbin in enumerate(self.hist):
            if hbin > 3:
                cv2.rectangle(self.overlay, (pos, h), (pos+1, h-hbin), (pos, 255, 128), -1)
                
        self.overlay = cv2.cvtColor(self.overlay, cv2.COLOR_HSV2BGR)
        

       