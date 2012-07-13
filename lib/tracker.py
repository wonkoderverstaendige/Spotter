# -*- coding: utf-8 -*-
"""
Created on Wed Jul 11 09:28:37 2012

@author: Ronny

"""
import time, cv2
import numpy as np

class LED:
    """ Each instance is a spot to track in the image. Holds histogram to do
    camshift with plus ROI/Mask"""
    
    hue_hist = None
    min_sat = 150
    min_val = 90
    label = None
    roi = None
    fixed_pos = False
    pos_hist = []
    
    def __init__( self, led_hist, label ):
        pass

    def updateFeature( self, led_hist ):
        pass
    
class Tracker:
    """ Performs tracking and returns positions of found LEDs """
    leds = []
    min_sat = 200
    min_val = 150
    
    frame = None
    
    def __init__( self, leds = [] ):
        self.leds = leds

    def preprocess( self, hsv_img ):
        # split
        h, s, v = cv2.split(hsv_img)

        #threshold
        rv, st = cv2.threshold(s, self.min_sat, 1, cv2.THRESH_BINARY)
        cstart = time.clock()         
        rv, vt = cv2.threshold(v, self.min_val, 1, cv2.THRESH_BINARY)
        print (time.clock() - cstart)*1000
        self.mask = cv2.max( st, vt )
        self.frame = cv2.bitwise_and( hsv_img, hsv_img, mask = self.mask )

        return self.mask, self.frame

    def addLED( self, label, min_sat, min_val, hist ):
        self.leds.append(LED(hist, label))
        print self.leds

    def camshift(self, led, frame ):
        print 'camshifting shifty figures'
        
    def sumTrack( self, BGRframe ):
        # this may be the simplest and fastest way UNDER IDEAL CONDITIONS!!
        
        # TODO: test area, refuse if too small, too far apart
        #       mask RGB image with mask from hsv thresholding!
        #       dilate + smooth image
        #       'None ' if not found!
   
        kernel = np.ones((3,3),'uint8')
        BGRframe = cv2.dilate(BGRframe, kernel)

        B, G, R = cv2.split(BGRframe)
        RG = R>G
        RB = R>B
        GB = G>B
        
        G[ RG & ~GB ] = 0
        B[ RB & GB ] = 0
        R[ ~RG & ~RB ] = 0
        
        Bx = B.sum(1).argmax()
        Gx = G.sum(1).argmax()
        Rx = R.sum(1).argmax()
        
        Ry = R.sum(0).argmax()
        Gy = G.sum(0).argmax()
        By = B.sum(0).argmax()
        
        ledcoords = [(Ry, Rx), (Gy, Gx), (By, Bx)]

        return ledcoords
        
        #print Bx
        
    def threshTrack( self, led ):
        pass