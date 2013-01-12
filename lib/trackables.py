# -*- coding: utf-8 -*-
"""
Created on Tue Dec 04 21:41:19 2012
@author: <Ronny Eichler> ronny.eichler@gmail.com

Trackable object class.
"""

import geometry as geom
import cv2

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


class LED:
    """ Each instance is a spot to track in the image. Holds histogram to do
    camshift with plus ROI/Mask"""

    hue_hist = None
    hue_range = None # np.array uint8 of (lowerBound, higherBound), red: 170,10
    min_sat = 150
    min_val = 90
    label = None
    pos_hist = None


    def __init__( self, label, hue_range, fixed_pos = False, linked_to = None ):
        self.label = label
        self.fixed_pos = fixed_pos
        self.hue_range = hue_range
        self.linked_to = linked_to  # List of linked LEDs
        self.pos_hist = list()

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

    def __init__( self, led_list, label = 'trackme' ):
        self.pos_hist = list()
        self.leds = led_list
        self.label = label

    def updatePosition( self ):
        coords = []
        for l in self.leds:
            if not l.pos_hist[-1] is None:
                coords.append( l.pos_hist[-1] )

        # find !mean! coordinates
        self.pos_hist.append( geom.middle_point( coords ) )
        self.guessed_pos = geom.guessedPosition( self.pos_hist )


    def predictPositionFast( self, frame_idx ):
        pass

    def predictPositionAccurate( self, frame_idx ):
        pass
