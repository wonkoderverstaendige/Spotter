# -*- coding: utf-8 -*-
"""
Created on Tue Dec 04 21:41:19 2012
@author: <Ronny Eichler> ronny.eichler@gmail.com

Objects of interest.
"""


import math
import logging
import lib.geometry as geom
from Slots import Slot


class ObjectOfInterest:
    """Object Of Interest. Collection of features to be tracked together and
    report state and behavior, or trigger events upon conditions.
    """
    def __init__(self, feature_list, label, traced=False, tracked=True, magnetic_signals=None):
        self.log = logging.getLogger(__name__)

        self.linked_features = feature_list
        self.label = label
        self.traced = traced
        self.tracked = tracked
        self.pos_hist = geom.PointArray()

        # the slots for these properties/signals are greedy for pins
        self.magnetic_signals = [] if magnetic_signals is None else magnetic_signals

        self.analog_pos = False
        self.analog_dir = False
        self.analog_spd = False

        # listed order important. First come, first serve
        self.slots = [Slot('x position', 'dac', self.x),
                      Slot('y position', 'dac', self.y),
                      Slot('direction', 'dac', self.direction),
                      Slot('speed', 'dac', self.speed)]

    def update_state(self):

        # Calculate position from detected features
        if self.tracked:
            self.pos_hist.append(geom.middle_point([f.pos_hist.last() for f in self.linked_features]))

        # calculate window to search for linked features in the next frame
        self.update_search_window()

    def update_search_window(self):

        # go back max. n frames to find last position
        min_step = 50
        point, steps = self.pos_hist.last_valid()
        if point and point.is_valid():
            # search window size increases with steps it took to find a valid point in history
            new_pos = geom.Point(point.x, point.y)
            inc = (2*steps+1) * min_step
            new_size = (inc, inc)
        else:
            # search full frame
            new_pos = geom.Point(0, 0)
            new_size = (2000, 2000)

        # FIXME: Updating search window is completely botched
        # FIXME: Search window not linked to feature, but object position. So features
        # far from the objects detected center will not fall into the search region
        # TODO: Visual feedback on search window position and size
        for l in self.linked_features:
            if l.adaptive_tracking is not None:
                if l.fixed_pos:
                    # FIXME: Movable feature ROIs
                    l.search_roi.center = geom.Point(0, 259)
                    l.search_roi.size = (100, 100)
                else:
                    l.search_roi.center = new_pos
                    l.search_roi.size = new_size

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

    @property
    def position(self):
        """Return last position."""
        return self.pos_hist.last()

    @property
    def position_guessed(self):
        """Get position based on history. Could allow for fancy filtering etc."""
        raise NotImplementedError
        #return geom.guessedPosition(self.pos_hist)

    def x(self):
        """ Helper method to provide chatter with function reference for slot updates"""
        return self.position.x if self.position.is_valid() else None

    def y(self):
        """ Helper method to provide chatter with function reference for slot updates"""
        return self.position.x if self.position.is_valid() else None

    def speed(self, *args):
        """Return movement speed in pixel/s."""
        # FIXME: Hardcoded magic number crap
        # TODO: Allow for a calibration of the field of view of cameras
        try:
            return geom.distance(self.pos_hist[-2], self.pos_hist[-1])*30.0 if len(self.pos_hist) >= 2 else None
        except TypeError:
            return None

    def direction(self):
        """
        Calculate direction of the object.

        If two features, calculate heading relative to normal of features.
        This assumes the alignment of features is constant.
        """
        # TODO: Direction based on movement if only one feature
        # TODO: Calculate angle when having multiple features
        # TODO: If one feature, direction is None if speed < v_threshold in px/s

        if any([not self.tracked, self.linked_features is None, len(self.linked_features) < 2]):
            return None

        points = [f.pos_hist.last() for f in self.linked_features]
        points = [c for c in points if c.is_valid()]

        # FIXME: Indices correct order? i.e. x2-x1 or x1-x2?
        if len(points) == 2:
            dx = float(points[0].x - points[1].x)
            dy = float(points[1].y - points[0].y)
            return int(math.degrees(math.atan2(dx, dy)))
        else:
            return None

    @property
    def linked_slots(self):
        """ Return list of slots that are linked to a pin. """
        return [slot for slot in self.slots if slot.pin]
