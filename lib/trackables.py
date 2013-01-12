# -*- coding: utf-8 -*-
"""
Created on Tue Dec 04 21:41:19 2012
@author: <Ronny Eichler> ronny.eichler@gmail.com

Trackable object class.
"""

import geometry as geom
import cv2
import utils

class LED:
    """ Each instance is a spot to track in the image. Holds histogram to do
    camshift with plus ROI/Mask"""

    hue_hist = None
    hue_range = None # np.array uint8 of (lowerBound, higherBound), red: 170,10
    min_sat = 150
    min_val = 90
    label = None
#    pos_hist = list()
    pos_hist = None
#    pos_hist = []
    mean_hue = None    # mean color of range for labels/markers etc.
    lblcolor =  None


    def __init__( self, label, hue_range, fixed_pos = False, linked_to = None ):
        self.label = label
        self.fixed_pos = fixed_pos
        self.hue_range = hue_range
        self.linked_to = linked_to  # List of linked LEDs

        # overly complicated formula to calculate the center color of HSV range
        if hue_range[0] <= self.hue_range[1]:
            self.mean_hue = sum(hue_range)/2
        else:
            center = ((180 - hue_range[0]) + hue_range[1])/2
            if hue_range[0] + center >= 180:
                self.mean_hue = hue_range[0] + center - 180
            else:
                self.mean_hue = hue_range[0] + center
            
        self.lblcolor = utils.HSVpix2RGB((self.mean_hue, 255, 255))
        self.pos_hist = []

    def updateHistogram( self, led_hist ):
        pass

    def gethistory( ):
        pass

    def updateHistory( self, coords):
        pass


class OOI:
    """ Mobile object LEDs are attached to, if any."""

    # TODO: Use general "features" rather than LEDs specifically

    pos_hist = None # Has the "real" values
    guessed_pos = None # Holds currently guessed position, either from tracking
                       # or estimation
    leds = None
    label = None

    def __init__( self, leds, label = 'trackme' ):
        self.linked_leds = leds
        self.label = label
        self.pos_hist = []

    def updatePosition( self ):
        feature_coords = []
        for linked_led in self.linked_leds:
            if not linked_led.pos_hist[-1] == None:
                feature_coords.append( linked_led.pos_hist[-1] )

        # find !mean! coordinates
        self.pos_hist.append( geom.middle_point( feature_coords ) )
        self.guessed_pos = geom.guessedPosition( self.pos_hist )


    def predictPositionFast( self, frame_idx ):
        pass

    def predictPositionAccurate( self, frame_idx ):
        pass


class ROI:
    """ Region in image registered objects are tested against.
    If trackables are occupying or intersecting, trigger their specific
    callbacks.
    """
    def __init__(self, points, color ):
        self.points = points
        self.color = color
        self.visible = True

    def draw( self, frame ):
        if self.visible:
            cv2.FillPoly(frame, self.points, self.color )

    def move( self, x, y ):
        print "Moving to new position"

    def pointTest( self, point ):
        cv2.pointPolygonTest( self.points, point, measureDist = False)