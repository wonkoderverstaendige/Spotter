# -*- coding: utf-8 -*-
"""
Created on Tue Dec 04 21:41:19 2012
@author: <Ronny Eichler> ronny.eichler@gmail.com

Trackable object class.
"""

import geometry as geom
import random
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
        self.shape = shape.lower()
        self.points = points
        self.label = label

        if shape == 'circle':
            dx = abs(points[0][0] - points[1][0])
            dy = abs(points[0][1] - points[1][1])
            self.radius = max(dx, dy)
            self.collision_check = self.collision_check_circle
        elif shape == 'rectangle':
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

    def move(self, dx, dy):
        for i, p in enumerate(self.points):
            self.points[i] = (p[0] + dx, p[1] + dy)

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
    range_area = None

    label = None
    pos_hist = None
    mean_hue = None    # mean color of range for labels/markers etc.
    lblcolor =  None

    def __init__( self, label, range_hue, range_area, fixed_pos, linked_to ):
        self.label = label
        self.fixed_pos = fixed_pos
        self.detection_active = True
        self.marker_visible = True

        self.range_hue = range_hue
        self.range_sat = (150, 255)
        self.range_val = (90, 255)
        self.range_area = range_area
        self.linked_to = linked_to  # List of linked features, used as constraint

        self.mean_hue = utils.mean_hue(self.range_hue)
        self.lblcolor = utils.HSVpix2RGB((self.mean_hue, 255, 255))
        self.pos_hist = []

    def updateHistogram( self, led_hist ):
        pass

    def gethistory( ):
        pass

    def updateHistory( self, coords):
        pass


class Slot:
    def __init__(self, label, _type, state_ref=None, state_ref_idx=None):
        self.label = label
        self.type = _type
        self.pin = None
        self.state = state_ref
        self.state_idx = state_ref_idx

    def attach_pin(self, pin):
        if self.pin and self.pin.slot:
            self.detach_pin()
        self.pin = pin
        self.pin.slot = self

    def detach_pin(self):
        self.pin.slot = None
        self.pin = None


class OOI:
    """
    Object Of Interest. Collection of features to be tracked together and
    report state and behavior, or trigger events upon conditions.
    """

    # TODO: Use general "features" rather than LEDs specifically

    linked_leds = None

    tracked = True
    traced = False

    position = None

    lookahead_roi = None # region pos will likely be in next frame, limit search
                         # of all linked features to this mask

    analog_pos = False
    analog_dir = False
    analog_spd = False

    slots = None

    def __init__( self, led_list, label, traced = False, tracked = True ):
        self.linked_leds = led_list
        self.label = label
        self.traced = traced
        self.tracked = tracked
        self.pos_hist = []

        # listed order important. First come, first serve
        self.slots = [Slot('x position', 'dac', self.last_pos, 0),
                      Slot('y position', 'dac', self.last_pos, 1),
                      Slot('direction', 'dac', self.direction),
                      Slot('speed', 'dac', self.speed)]

    def update_state(self):
        """
        Calculate position, direction and speed of object. Based on these,
        try to predict a region to look for the object in the next frame.
        """
        self.position = self._position()
        self.lookahead_roi = None

    def _position(self):
        """ Calculate position from detected features linked to object. """
        if self.tracked:
            feature_coords = []
            for feature in self.linked_leds:
                if not feature.pos_hist[-1] == None:
                    feature_coords.append( feature.pos_hist[-1] )

            # find !mean! coordinates
            self.pos_hist.append( geom.middle_point( feature_coords ) )
            return geom.guessedPosition( self.pos_hist )
        else:
            return None

    def last_pos(self, *args):
        """
        Return last position. Helper to pass reference, rather than value,
        to slot_state.
        """
        return self.position

    def speed(self, *args):
        """Return movement speed in pixel/s."""
        return None

    def direction(self, *args):
        """
        Calculate direction of the object.

        If one feature, direction is not None if speed > v_threshold in px/s
        If multiple features, calculate peak movement direction relative to
        normal of features. This assumes the alignment of features is constant.
        """
        return None

    def linked_slots(self):
        """ Return list of slots that are linked to a pin. """
        slots_to_update = []
        for s in self.slots:
            if s.pin:
                slots_to_update.append(s)
        return slots_to_update

#    def predictPositionFast(self, frame_idx):
#        pass
#
#    def predictPositionAccurate(self, frame_idx):
#        pass


class ROI:
    """ Region in image registered objects are tested against.
    If trackables are occupying or intersecting, trigger their specific
    callbacks.
    """
    visible = True
    color = None
    alpha = .6

    linked_objects = None # aka slots!

    def __init__(self, shape_list=None, label=None, color=None, obj_list=None ):
        self.label = label
        if not color:
            self.normal_color = self.get_normal_color()
        else:
            self.normal_color = self.normalize_color(color)
        self.passive_color = self.scale_color(self.normal_color, 200)
        self.active_color = self.scale_color(self.normal_color, 255)
        self.set_passive_color()

        # slots linked to pins for physical output
        self.slots = []

        # reference to all objects spotter holds
        self.oois = obj_list

        # if initialized with starting set of shapes
        self.shapes = []
        if shape_list:
            for shape in shape_list:
                self.add_shape(*shape)

    def update_state(self):
        pass

    def linked_slots(self):
        """ Return list of slots that are linked to a pin. """
        slots_to_update = []
        for s in self.slots:
            if s.pin:
                slots_to_update.append(s)
        return slots_to_update

    def move( self, dx, dy ):
        """ Moves all shapes, aka the whole ROI, by delta pixels. """
        for s in self.shapes:
            s.move(dx, dy)

    def add_shape(self, shape_type, points, label):
        """ Adds a new shape. """
        shape = Shape(shape_type, points, label)
        self.shapes.append(shape)
        return shape

    def remove_shape(self, shape):
        """ Removes a shape. """
        self.shapes.pop(self.shapes.index(shape))

    def refresh_slot_list(self):
        """
        Gather all objects in list. Check done by name.
        TODO: By label is risky, could lead to collisions
        """
        if self.oois and len(self.slots) < len(self.oois):
            for o in self.oois:
                for s in self.slots:
                    if s.label == o.label:
                        break
                else:
                    self.link_object(o)

    def link_object(self, obj):
        if obj in self.oois:
            self.slots.append(Slot(obj.label, 'digital',
                                   self.test_collision,
                                   self.oois.index(obj)))

    def unlink_object(self, obj):
        for s in self.slots:
            if s.label == obj.label:
                self.slots.pop(self.slots.find(s))
                print "removed object ", obj.label, " from slot list of ", self.label

    def test_collision(self, obj_idx):
        return self.collision_check(self.oois[obj_idx].position)

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
