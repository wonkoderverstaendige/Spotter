# -*- coding: utf-8 -*-
"""
Created on Tue Dec 04 21:41:19 2012
@author: <Ronny Eichler> ronny.eichler@gmail.com

Classes related to tracking.
"""

import math
import random
import lib.utilities as utils
import lib.geometry as geom


class Shape:
    """ Geometrical shape that comprise ROIs. ROIs can be made of several
    independent shapes like two rectangles on either end of the track etc.
    Not sure about the color parameter, I think it better if all shapes in a
    ROI have the same color, to keep them together as one ROI.
    points: list of points defining the shape. Two for rectangle and circle,
    """
    # TODO: n-polygon and collision detection
    def __init__(self, shape, points=None, label=None):
        self.active = True
        self.selected = False

        self.collision_check = None

        self.shape = shape.lower()
        self.label = label

        self.points = points
        if shape == 'circle':
            # normalize the point positions based on radius,
            # second point is always to the right of the center
            self.points = [points[0], (int(points[0][0]), points[0][1]+self.radius)]
            self.collision_check = self.collision_check_circle
        elif shape == 'rectangle':
            self.collision_check = self.collision_check_rectangle

    def move(self, dx, dy):
        """ Move the shape relative to current position. """
        for i, p in enumerate(self.points):
            self.points[i] = (p[0] + dx, p[1] + dy)

    def move_to(self, points):
        """ Move the shape to a new absolute position. """
        self.points = points

    @property
    def radius(self):
        """ Calculate the radius of the circle. """
        return geom.distance(self.points[0], self.points[1])

    def collision_check_circle(self, point):
        """ Circle points: center point, one point on the circle. Test for
        collision by comparing distance between center and point of object with
        radius.
        """
        distance = geom.distance(self.points[0], point)
        if self.active and (distance <= self.radius):
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
        return self.active and x_in_interval and y_in_interval


class Feature:
    """ General class holding a feature to be tracked with whatever tracking
    algorithm is appropriate.
    """

    def __init__(self):
        pass


class LED(Feature):
    """ Each instance is a spot defined by ranges in a color space. """

    def __init__(self, label, range_hue, range_sat, range_val, range_area, fixed_pos, linked_to, roi=None):
        Feature.__init__(self)
        self.label = label
        self.detection_active = True
        self.marker_visible = True

        # feature description ranges
        self.range_hue = range_hue
        self.range_sat = range_sat
        self.range_val = range_val
        self.range_area = range_area

        self.pos_hist = []

        # Restrict tracking to a search window?
        self.adaptive_tracking = (roi is not None)
        # if so, where and which window?
        self.fixed_pos = fixed_pos
        self.search_roi = roi
        # List of linked features, can be used for further constraints
        self.linked_to = linked_to

    @property
    def mean_hue(self):
        return utils.mean_hue(self.range_hue)

    @property
    def lblcolor(self):
        # mean color of range for labels/markers etc.
        return utils.HSVpix2RGB((self.mean_hue, 255, 255))

    @property
    def position(self):
        return self.pos_hist[-1] if len(self.pos_hist) else None


class Slot:
    def __init__(self, label, slot_type, state=None, state_idx=None, ref=None):

        # While nice, should be used for style, not for identity testing
        # FIXME: Use instance comparisons vs. label comparisons
        self.label = label

        # analog (dac) or digital
        self.type = slot_type

        # The physical device pin
        self.pin = None
        self.pin_pref = None

        # reference to output value
        self.state = state
        # index of output value if iterable
        # for example, the position could be x or y position
        # TODO: Unnecessary with proper use of @property decorators
        self.state_idx = state_idx
        self.ref = ref              # reference to object representing slot

    def attach_pin(self, pin):
        if self.pin and self.pin.slot:
            self.detach_pin()
        self.pin = pin
        self.pin.slot = self

    def detach_pin(self):
        self.pin.slot = None
        self.pin = None

    def __del__(self):
        print "Removing slot", self


class ObjectOfInterest:
    """
    Object Of Interest. Collection of features to be tracked together and
    report state and behavior, or trigger events upon conditions.
    """
    # TODO: Use general "features" rather than LEDs specifically

    linked_leds = None

    tracked = True
    traced = False

    position = None
    angle = None

    analog_pos = False
    analog_dir = False
    analog_spd = False

    slots = None

    def __init__(self, led_list, label, traced=False, tracked=True, magnetic_signals=None):
        self.linked_leds = led_list
        self.label = label
        self.traced = traced
        self.tracked = tracked
        self.pos_hist = []

        # the slots for these properties/signals are greedy for pins
        if magnetic_signals is None:
            self.magnetic_signals = []
        else:
            self.magnetic_signals = magnetic_signals

        # listed order important. First come, first serve
        self.slots = [Slot('x position', 'dac', self.last_pos, 0),
                      Slot('y position', 'dac', self.last_pos, 1),
                      Slot('direction', 'dac', self.direction),
                      Slot('speed', 'dac', self.speed)]

    def update_state(self):
        """
        Calculate position, direction and speed of object.

        Update feature search windows!
        """
        self.position = self._position()
        self.angle = self.direction()

        min_step = 25
        # go back max. n frames to find last position, else search full frame
        for p in range(0, min(len(self.pos_hist), 10)):
            if self.pos_hist[-p-1] is not None:
                uidx = (p+1) * min_step
                pos = map(int, self.pos_hist[-p-1])
                roi = [(pos[0]-uidx, pos[1]-uidx), (pos[0]+uidx, pos[1]+uidx)]
                break
        else:
            roi = [(0, 0), (2000, 2000)]

        for l in self.linked_leds:
            if l.fixed_pos:
                l.search_roi.move_to([(0, 259), (100, 359)])
            else:
                l.search_roi.move_to(roi)

    def update_slots(self, chatter):
        for slot in self.slots:
            for ms in self.magnetic_signals:
                # Check that pin preferences are set correctly
                if slot.label == ms[0]:
                    if not slot.pin_pref == ms[1]:
                        slot.pin_pref = ms[1]

            if (slot.pin_pref is not None) and (slot.pin is None):
                # If pin pref and not connected to pin
                pins = chatter.pins_for_slot(slot)
                for pin in pins:
                    if pin.id == slot.pin_pref:
                        slot.attach_pin(pin)

    def _position(self):
        """
        Calculate position from detected features linked to object.
        """
        # TODO: Now that I know about @property decorators...
        if self.tracked:
            feature_coords = []
            for feature in self.linked_leds:
                if feature.pos_hist[-1] is not None:
                    feature_coords.append(feature.pos_hist[-1])
            # find !mean! coordinates
            self.pos_hist.append(geom.middle_point(feature_coords))
            return geom.guessedPosition(self.pos_hist)
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
        # TODO: Allow for a calibration of the field of view of cameras
        if len(self.pos_hist) < 2:
            return None
        if self.pos_hist[-1] is not None and self.pos_hist[-2] is not None:
            return self.pos_hist[-2]-self.pos_hist[-1]
        return None

    def direction(self):
        """
        Calculate direction of the object.

        If one feature, direction is not None if speed > v_threshold in px/s
        If two features, calculate heading relative to normal of features.

        This assumes the alignment of features is constant.
        """
        # TODO: Direction based on movement if only one feature
        if not self.tracked:
            return None

        if self.linked_leds is None or len(self.linked_leds) < 2:
            return None

        feature_coords = []
        for feature in self.linked_leds:
            if len(feature.pos_hist) > 0 and feature.pos_hist[-1] is not None:
                feature_coords.append(feature.pos_hist[-1])

        if len(feature_coords) == 2:
            x1 = feature_coords[0][0]*1.0
            y1 = feature_coords[0][1]*1.0
            x2 = feature_coords[1][0]*1.0
            y2 = feature_coords[1][1]*1.0

            angle = math.degrees(math.atan2(x1 - x2, y2 - y1))
            return int(angle)

        return None

    @property
    def linked_slots(self):
        """ Return list of slots that are linked to a pin. """
        slots_to_update = []
        for s in self.slots:
            if s.pin:
                slots_to_update.append(s)
        return slots_to_update


class RegionOfInterest:
    """ Region in image registered objects are tested against.
    If trackables are occupying or intersecting, trigger their specific
    callbacks.
    """
    visible = True
    color = None
    alpha = .4
    highlighted = False

    strict_prefs_dealt = False

    linked_objects = None  # aka slots?!

    normal_color = None
    active_color = None
    passive_color = None

    def __init__(self, shape_list=None, label=None, color=None, obj_list=None, magnetic_objects=None):
        self.label = label

        # Aesthetics
        self.update_color(color)
        self.set_passive_color()

        # slots linked to pins for physical output
        self.slots = []
        # reference to all objects spotter holds
        self.oois = obj_list
        # The slots for these objects are trying to automatically link pins
        if magnetic_objects is None:
            self.magnetic_objects = []
        else:
            self.magnetic_objects = magnetic_objects

        # if initialized with starting set of shapes
        self.shapes = []
        if shape_list:
            for shape in shape_list:
                self.add_shape(*shape)

    def update_state(self):
        self.highlighted = False
        self.deal_pin_prefs()

    def deal_pin_prefs(self):
        for mo in self.magnetic_objects:
            for s in self.slots:
                if s.ref == mo[0]:
                    s.pin_pref = mo[1]

    def update_slots(self, chatter):
        for slot in self.slots:
            if (slot.pin_pref is not None) and (slot.pin is None):
                pins = chatter.pins_for_slot(slot)
                for p in pins:
                    if p.id == slot.pin_pref:
                        slot.attach_pin(p)

    def update_color(self, color=None):
        """ Set color for region, used by all associated shapes. If no color
        give, will generate a random (most often ugly) on.
        """
        if not color:
            # Generating color
            self.normal_color = self.get_normal_color()
        else:
            self.normal_color = self.normalize_color(color)
        self.passive_color = self.scale_color(self.normal_color, 150)
        self.active_color = self.scale_color(self.normal_color, 255)

    @property
    def linked_slots(self):
        """ Return list of slots that are linked to a pin. """
        slots_to_update = []
        for slot in self.slots:
            if slot.pin:
                slots_to_update.append(slot)
        return slots_to_update

    def move(self, dx, dy):
        """ Moves all shapes, aka the whole ROI, by delta pixels. """
        for shape in self.shapes:
            shape.move(dx, dy)

    def add_shape(self, shape_type, points, label):
        """ Adds a new shape. """
        shape = Shape(shape_type, points, label)
        self.shapes.append(shape)
        return shape

    def remove_shape(self, shape):
        """ Removes a shape. """
        try:
            self.shapes.remove(shape)
        except ValueError:
            print "Couldn't find shape for removal"

    def refresh_slot_list(self):
        """
        Gather all objects in list. Check done by name.
        """
        # TODO: By label is risky, could lead to collisions
        #if self.oois and len(self.slots) < len(self.oois):
        for o in self.oois:
            for slot in self.slots:
                if slot.ref is o:
                    break
            else:
                self.link_object(o)

        for slot in self.slots:
            if not slot.ref in self.oois:
                self.unlink_object(slot.ref)

    def link_object(self, obj):
        print "Linked Object", obj.label, "to", self
        if obj in self.oois:
            self.slots.append(Slot(label=obj.label, slot_type='digital', state=self.test_collision,
                                   state_idx=obj, ref=obj))

    def unlink_object(self, obj):
        for slot in self.slots:
            if slot.ref is obj:
                self.slots.remove(slot)
                print "Removed object", obj.label, "from slot list of", self.label

    def test_collision(self, obj):
        return self.check_shape_collision(obj.position)

    def check_shape_collision(self, point1, point2=None):
        """ Test if a line between start and end would somewhere collide with
        any shapes of this ROI. Simple AND values in the collision detection
        array on the line.
        """
        # TODO: Only checks of the point is within the bounding box of shapes?
        if point1 is not None:
            collision = False
            for s in self.shapes:
                if s.active and s.collision_check(point1):
                    self.highlighted = True
                    collision = True
                    break

            # no collisions detected for this region
            self.toggle_highlight()
            return collision
        else:
            return None

    def toggle_highlight(self):
        """ Toggle color to active set if region is highlighted by collision. """
        if self.highlighted:
            if self.normal_color != self.active_color:
                self.set_active_color()
        else:
            if self.normal_color != self.passive_color:
                self.set_passive_color()

    def set_active_color(self):
        self.color = self.active_color
        self.alpha = 0.8
        self.normal_color = self.normalize_color(self.color)

    def set_passive_color(self):
        self.color = self.passive_color
        self.alpha = 0.4
        self.normal_color = self.normalize_color(self.color)

    def get_normal_color(self):
        c1 = random.random()
        c2 = random.uniform(0, 1.0-c1)
        c3 = 1.0-c1-c2
        values = random.sample([c1, c2, c3], 3)
        return values[0], values[1], values[2], self.alpha

    @staticmethod
    def scale_color(color, max_val):
        if len(color) == 3:
            return int(color[0]*max_val), int(color[1]*max_val), int(color[2]*max_val)
        elif len(color) == 4:
            return int(color[0]*max_val), int(color[1]*max_val), int(color[2]*max_val), int(color[3]*max_val)

    @staticmethod
    def normalize_color(color):
        if len(color) == 3:
            return color[0]/255., color[1]/255., color[2]/255.
        elif len(color) == 4:
            return color[0]/255., color[1]/255., color[2]/255., color[3]/255.
