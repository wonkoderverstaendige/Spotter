# -*- coding: utf-8 -*-
"""
Created on Mon Jul 09 00:07:34 2012

Handles grabbing successive frames from capture object and returns current
frames of requested type.

Capture object must be closed with Grabber.close() or main loop will not listen
to termination!

@author: Ronny
"""

import cv, cv2, time, os
from collections import deque

class Grabber:
    config = None
    capture = None
    fourcc = None
    fps = None
    framecount = 0
    ts_last_frame = None
    ts_first = None
    framebuffer = deque(maxlen=256)
    capture_is_file = False
    
    def __init__(self, args):
           
        self.config = args
        
        if self.config.infile and len(self.config.infile[0]) > 0:
            filepath = self.config.infile[0]
            print 'Attempting to open file ' + filepath + ' as capture... '
            if os.path.isfile(filepath):
                self.capture = cv2.VideoCapture(filepath)
                print 'File returned ' + str(self.capture)
                self.capture_is_file = True
            else:
                print "Input file not found!"
                self.capture = None
            
        elif self.config.camera >= 0:
            print 'Trying to open device #' + str(self.config.camera)
            self.capture = cv2.VideoCapture(self.config.camera)
            self.capture.set(cv.CV_CAP_PROP_FPS, 30.0)
            self.capture.set(cv.CV_CAP_PROP_FRAME_WIDTH, self.config.width[0])
            self.capture.set(cv.CV_CAP_PROP_FRAME_HEIGHT, self.config.height[0])
            print 'Camera returned ' + str(self.capture)
            

    def grab_first( self ):
        rv = False
        while not rv:   
            rv, img = self.capture.read()
            if rv:
                # get FOURCC code as Integer
                self.width = int(self.capture.get(3))
                self.height = int(self.capture.get(4))
                self.fps = int(self.capture.get(cv.CV_CAP_PROP_FPS))
                self.fourcc = self.capture.get(6)
        self.ts_first = time.clock()
    
    def grab_next( self ):
        rv, img = self.capture.read()
        if rv:
            self.framecount += 1
            self.ts_last_frame = time.clock()
            
        self.framebuffer.appendleft(img)
        return rv
        
    def close( self ):
        self.capture.release()
            
            
            
