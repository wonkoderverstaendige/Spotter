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
    min_sat = 100
    min_val = 100
    
    
    def __init__( self, leds = [] ):
        self.leds = leds

    def preprocess( self, hsv_img ):
        # split
        h, s, v = cv2.split(hsv_img)
        print h, s, v
        
        #threshold
        rv, st = cv2.threshold(s, min_sat, 1, cv2.THRESH_BINARY_INV)
        rv, vt = cv2.threshold(s, min_val, 1, cv2.THRESH_BINARY_INV)
        self.mask = st and vt
        
        print self.mask
        

    def addLED( self, label, min_sat, min_val, hist ):
        self.leds.append(LED(hist, label))
        print self.leds

    def camshift(self, led, frame ):
        print 'camshifting shifty figures'