# -*- coding: utf-8 -*-
"""
Created on Tue Dec 04 21:41:19 2012
@author: <Ronny Eichler> ronny.eichler@gmail.com

Trackable object class.
"""

import geometry as geom
import random
import cv2
import utilities as utils

class Shape:
    """ Geometrical shape that comprise ROIs. ROIs can be made of several
    independent shapes like two rectangles on either end of the track etc.
    Not sure about the color parameter, I think it better if all shapes in a
    ROI have the same color, to keep them together as one ROI.
    points: list of points defining the shape. Two for rectangle and circle,
    TODO: n-poly
    """
    active = True
    selected = False

    collision_check = None

    def __init__(self, shape, points, label):
        self.shape = shape
        self.points = points
        self.label = label

        if shape == 'Circle':
            dx = abs(points[0][0] - points[1][0])
            dy = abs(points[0][1] - points[1][1])
            self.radius = max(dx, dy)
            self.collision_check = self.collision_check_circle
        elif shape == 'Rectangle':
            self.collision_check = self.collision_check_rectangle


    def collision_check_circle(self, point):
        """ Circle points: center point, one point on the circle. Test for
        collision by comparing distance between center and point of object with
        radius.
        """
        if self.active and (geom.distance(self.points[0], point) <= self.radius):
            return True
        else:
            return False

    def collision_check_rectangle(self, point):
        """ Circle points: center point, one point on the circle. Test for
        collision by comparing distance between center and point of object with
        radius.
        """
        x_in_interval = (point[0] > min(self.points[0][0], self.points[1][0])) and\
                        (point[0] < max(self.points[0][0], self.points[1][0]))

        y_in_interval = (point[1] > min(self.points[0][1], self.points[1][1])) and\
                        (point[1] < max(self.points[0][1], self.points[1][1]))
        if self.active and x_in_interval and y_in_interval:
            return True
        else:
            return False

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

    pos_hist = None    # Has the "real" values
    guessed_pos = None # Holds currently guessed position, either from tracking
                       # or estimation
    linked_leds = None

    tracked = True
    traced = False

    analog_pos_out = False

    def __init__( self, led_list, label, traced = False ):
        self.linked_leds = led_list
        self.label = label
        self.traced = traced
        self.pos_hist = []

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
    color = None
    alpha = .7
    
    linked_objects = None

    def __init__(self, shape_list = None, label = None, color = None ):
        if not color:
            self.normal_color = self.get_normal_color()
        else:
            self.normal_color = self.normalize_color(color)

        self.passive_color = self.scale_color(self.normal_color, 200)
        self.active_color = self.scale_color(self.normal_color, 255)

        self.set_passive_color()

        self.label = label
        self.shapes = []
        # if the ROI is initialized with a set of shapes to begin with:
        if shape_list:
            for shape in shape_list:
                self.add_shape(*shape[1], label = shape[0])

    def move( self, x, y ):
        print "Moving whole ROI to new position"

    def add_shape(self, shape_type, points, label):
        shape = Shape(shape_type, points, label)
        self.shapes.append(shape)
        return shape

    def remove_shape(self, shape):
        print 'not really removing shape'

    def assemble_collision_array(self):
        for s in self.shapes:
            pass

    def collision_check(self, point1, point2 = None):
        """ Test if a line between start and end would somewhere collide with
        any shapes of this ROI. Simple AND values in the collision detection
        array on the line.
        TODO: Right now the test only checks of the point is within the bounding
        box of the shapes!!!
        TODO: I think there is the corner case missing in which no shape
        receives a valid signal in a while after just triggering, leaving the
        shape in it's active color
        """
#        self.set_passive_color()
        if point1 == None:
            return None

        for s in self.shapes:
            if s.active and s.collision_check(point1):
                self.set_active_color()
                return True

        # no collisions detected for this region
        if self.normal_color != self.passive_color:
            self.set_passive_color()
        return False


    def set_active_color(self):
        self.color = self.active_color
        self.alpha = 0.8
        self.normal_color = self.normalize_color(self.color)

    def set_passive_color(self):
        self.color = self.passive_color
        self.alpha = 0.6
        self.normal_color = self.normalize_color(self.color)


    def get_normal_color(self):
        c1 = random.random()
        c2 = random.uniform(0, 1.0-c1)
        c3 = 1.0-c1-c2
        vals = random.sample([c1, c2, c3], 3)
        return (vals[0], vals[1], vals[2], self.alpha)

    def scale_color(self, color, max_val):
        if len(color) == 3:
            return (int(color[0]*max_val), int(color[1]*max_val), int(color[2]*max_val))
        elif len(color) == 4:
            return (int(color[0]*max_val), int(color[1]*max_val), int(color[2]*max_val), int(color[3]*max_val))

    def normalize_color(self, color):
        if len(color) == 3:
            return (color[0]/255., color[1]/255., color[2]/255.)
        elif len(color) == 4:
            return (color[0]/255., color[1]/255., color[2]/255., color[3]/255.)
