# -*- coding: utf-8 -*-
"""
Created on Wed Dec 05 02:19:40 2012
@author: <Ronny Eichler> ronny.eichler@gmail.com

GUI and event handling
"""

import cv2
import sys
import numpy as np

#project libraries
sys.path.append('./lib')
import utilities as utils

class GUI:
    gui_frame = None     # still_frame + Menu side bar + overlays
    windowName = None

    # state variables
    paused = False
    viewMode = 0
    drag_start = False

    # Var
    parent = None

    # frame objects
    still_frame = None

    def __init__( self, main, gui, windowname, size ):
        self.size = size
        self.windowName = windowname
        self.parent = main

        # Only OpenCV's HighGui is currently used as user interface
        if gui=='cv2.highgui':
            cv2.namedWindow( self.windowName )
            cv2.setMouseCallback( self.windowName, self.onMouse )


#    def registerView( self, frameObject ):
#        self.viewModeFrames.append( frameObject )


    def update( self, frame ):

        if not self.paused:
            self.still_frame = frame.copy()

        if not self.still_frame == None:
            self.buildGui()
            self.show()


    def show(self):
        cv2.imshow( self.windowName, self.gui_frame )


    def onMouse( self, event, x, y, flags, param ):
        """
        Mouse interactions with Main window:
            - Left mouse click gives pixel data under cursor
            - Left mouse drag selects rectangle

            - Right mouse button switches view mode
        """
        if event == cv2.EVENT_LBUTTONDOWN:
            if not self.gui_frame == None:
                self.drag_start = (x, y)

        if event == cv2.EVENT_LBUTTONUP:
                self.drag_start = None

                if self.selection == None:
                    pixel = self.gui_frame[y, x]
                    print "[X,Y][B G R](H, S, V):", [x, y], pixel, utils.BGRpix2HSV(pixel)
                else:
                    #self.track_window = self.selection
                    print self.selection    #self.track_window

        if self.drag_start:
            xmin = min( x, self.drag_start[0] )
            ymin = min( y, self.drag_start[1] )
            xmax = max( x, self.drag_start[0] )
            ymax = max( y, self.drag_start[1] )

            if xmax - xmin < 2 and ymax - ymin < 2:
                self.selection = None
            else:
                self.selection = ( xmin, ymin, xmax - xmin, ymax - ymin )

        if event == cv2.EVENT_RBUTTONDOWN:
            pass
#            self.nextView()


    def nextView( self ):
        if self.viewMode == 0:
            self.viewMode = 0
        else:
            self.viewMode += 1

    def onKey( self, key ):
        if key>0:
            print key % 0x100

        if (key % 0x100 == 114):
            print "Make ROI"

        # <SPACE> to toggle video pause
        if ( key % 0x100 == 32 ):
            self.paused = not self.paused

        # <ESCAPE> to EXIT
        if ( key % 0x100 == 27 ):
            self.parent.exit()


    def updateHist( self ):
        self.hist.hueHist( self.hsv_frame )
        self.hist.overlayHistMap()
        cv2.imshow( 'histogram', self.hist.overlay )


    def overlay( self ):
        """ Writes information into still frame of GUI, like crosses on tracked
            spots or textual information and ROI borders
        """
        colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0)]
        for i, l in enumerate( self.parent.tracker.leds ):
            coords = l.pos_hist[-1]
            if not coords == None:
                # TODO: HSV_to_RGB conversion function
                utils.drawCross( self.gui_frame, coords, 5, colors[i], gap = 3 )

        for o in self.parent.tracker.oois:
            utils.drawTrace( self.gui_frame, o.pos_hist, 255, 100 )


    def buildGui( self ):
        """ Assembles GUI by taking a still frame and adding additional space
            for GUI elements and markers
        """
        # still frame selection
        # 0: normal RGB from raw source
        # 1: dense overlay of debugging information
        if self.viewMode == 0:
            self.gui_frame = self.still_frame.copy()
            # overlay information onto stillframe
            self.overlay()
#            self.show_frame = cv2.bitwise_and( self.current_frame, self.current_frame, mask = self.tracker.mask )
