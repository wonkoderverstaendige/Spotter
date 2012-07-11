# -*- coding: utf-8 -*-
"""
Created on Wed Jul 11 09:28:37 2012

@author: Ronny

"""
import time, cv2

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
        rv, vt = cv2.threshold(v, self.min_val, 1, cv2.THRESH_BINARY)

        self.mask = cv2.max( st, vt )
        self.frame = cv2.bitwise_and( hsv_img, hsv_img, mask = self.mask )

        return self.mask, self.frame

    def addLED( self, label, min_sat, min_val, hist ):
        self.leds.append(LED(hist, label))
        print self.leds

    def camshift(self, led, frame ):
        print 'camshifting shifty figures'
        
    def threshTrack( self, led ):
        pass