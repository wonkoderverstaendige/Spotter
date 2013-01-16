# -*- coding: utf-8 -*-
"""
Created on Tue Dec 04 21:41:19 2012
@author: <Ronny Eichler> ronny.eichler@gmail.com

Trackable object class.
"""

import geometry as geom
import random
import cv2
import utils

class Shape:
    """ Geometrical shape that comprise ROIs. ROIs can be made of several
    independent shapes like two rectangles on either end of the track etc.
    Not sure about the color parameter, I think it better if all shapes in a
    ROI have the same color, to keep them together as one ROI.
    points: list of points defining the shape. Three for triangle, two for
    rectangle, circle has only point plus radius, etc.
    """
    active = True    
    selected = False
    
    def __init__(self, shape, points, color = None, label = 'shape'):
        self.shape = shape
        self.points = points
        self.label = label
#        self.color = color
#        self.draw_instruction = self.build_draw_instruction()
#        
#    def build_draw_instruction(self, color = None):
#        pass
        
    def shape_to_array(self):
        """ Return shape as numpy array for overlaying into the total
        collision detection array. """
        pass


class LED:
    """ Each instance is a spot to track in the image. Holds histogram to do
    camshift with plus ROI/Mask"""

    hue_hist = None
    range_hue = None # np.array uint8 of (lowerBound, higherBound), red: 170,10
    range_sat = None
    range_val = None
    label = None
    pos_hist = None
    mean_hue = None    # mean color of range for labels/markers etc.
    lblcolor =  None

    def __init__( self, label, range_hue, fixed_pos = False, linked_to = None ):
        self.label = label
        self.fixed_pos = fixed_pos
        self.detection_active = True
        self.marker_visible = True

        self.range_hue = range_hue
        self.range_sat = (150, 255)
        self.range_val = (90, 255)
        self.linked_to = linked_to  # List of linked LEDs

        # overly complicated formula to calculate the center color of HSV range
        if range_hue[0] <= self.range_hue[1]:
            self.mean_hue = sum(range_hue)/2
        else:
            center = ((180 - range_hue[0]) + range_hue[1])/2
            if range_hue[0] + center >= 180:
                self.mean_hue = range_hue[0] + center - 180
            else:
                self.mean_hue = range_hue[0] + center

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
    linked_leds = None
    label = None
    
    tracked = True
    traced = False
    
    def __init__( self, leds, label = 'trackme', traced = False ):
        self.linked_leds = leds
        self.label = label
        self.pos_hist = []
        self.traced = traced

    def updatePosition( self ):
        if self.tracked:
            feature_coords = []
            for linked_led in self.linked_leds:
                if not linked_led.pos_hist[-1] == None:
                    feature_coords.append( linked_led.pos_hist[-1] )
    
            # find !mean! coordinates
            self.pos_hist.append( geom.middle_point( feature_coords ) )
            self.guessed_pos = geom.guessedPosition( self.pos_hist )
        else:
            self.guessed_pos = None

    def predictPositionFast( self, frame_idx ):
        pass

    def predictPositionAccurate( self, frame_idx ):
        pass


class ROI:
    """ Region in image registered objects are tested against.
    If trackables are occupying or intersecting, trigger their specific
    callbacks.
    """
    visible = True
    
    def __init__(self, color = None, label = 'ROI', shapes = None ):
        if not color:
            self.color = self.random_color()
        else:
            self.color = color
        self.color_normal = self.normalize_color(self.color)
        self.label = label
        self.shapes = []
        # if the ROI is initialized with a set of shapes to begin with:
        if shapes:
            for s in shapes:
                self.add_shape(s)

#    def draw( self, frame ):
#        if any(self.points):
#            if self.visible:
#                cv2.FillPoly(frame, self.points, self.color )

    def move( self, x, y ):
        print "Moving whole ROI to new position"
        
    def add_shape(self, shape_type, points, *args):
        shape = Shape(shape_type, points)
        self.shapes.append(shape)
        return shape
    
#    def update_draw_jobs(self):
#        jobs = []
#        for s in self.shapes:
#            jobs.append(s.draw_instruction)
#        return []

    def remove_shape(self, shape):
        print 'not really removing shape'
        
    def assemble_collision_array(self):
        for s in self.shapes:
            pass

    def test_collision(self, start, end):
        """ Test if a line between start and end would somewhere collide with
        any shapes of this ROI. Simple AND values in the collision detection
        array on the line.
        """
        return

    def random_color(self):
        c1 = random.randrange(200)
        c2 = random.randrange(200-c1)
        c3 = 200-c1-c2
        return random.sample([c1, c2, c3], 3)
        
    def normalize_color(self, color):
        return (color[0]/255., color[1]/255., color[2]/255.)