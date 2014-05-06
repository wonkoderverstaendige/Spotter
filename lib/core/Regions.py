# -*- coding: utf-8 -*-
"""
Created on Tue Dec 04 21:41:19 2012
@author: <Ronny Eichler> ronny.eichler@gmail.com

Regions used by Tracker.
"""

import logging
import random
import Shapes
import Slots


class RegionOfInterest(object):
    """ Region in image registered objects are tested against.
    If tracked objects are occupying or intersecting, trigger their specific
    callbacks.
    """
    visible = True
    color = None
    alpha = .4
    highlighted = False

    strict_prefs_dealt = False

    normal_color = None
    active_color = None
    passive_color = None

    def __init__(self, shape_list=None, label=None, color=None, obj_list=None, magnetic_objects=None):
        self.log = logging.getLogger(__name__)
        self.label = label

        # Aesthetics
        self.update_color(color)
        self.set_passive_color()

        # slots linked to pins for physical output
        self.slots = []
        # reference to all objects spotter holds
        self.linked_objects = None  # aka slots?!
        self.oois = obj_list

        # The slots for these objects are trying to automatically link pins
        self.magnetic_objects = [] if magnetic_objects is None else magnetic_objects

        self.shapes = []
        # if initialized with starting set of shapes
        if shape_list:
            for shape in shape_list:
                self.add_shape(*shape)

        self.representation = None

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
        """Set color for region, used by all associated shapes. If no color
        give, will generate a random (most often ugly) on.
        """
        # Generate color if necessary
        self.normal_color = self.get_normal_color() if not color else self.normalize_color(color)
        self.passive_color = self.scale_color(self.normal_color, 150)
        self.active_color = self.scale_color(self.normal_color, 255)
        self.toggle_highlight()

    @property
    def linked_slots(self):
        """Return list of slots that are linked to a pin. """
        slots_to_update = []
        for slot in self.slots:
            if slot.pin:
                slots_to_update.append(slot)
        return slots_to_update

    def move(self, dx, dy):
        """Moves all shapes, aka the whole ROI, by (dx, dy) pixels. """
        for shape in self.shapes:
            shape.move_by(dx, dy)

    def add_shape(self, shape_type, *args, **kwargs):
        """Adds a new shape instance."""
        shape = Shapes.from_type(shape_type, parent=self, *args, **kwargs)
        if shape is not None:
            self.shapes.append(shape)
        return shape

    def remove_shape(self, shape):
        """Removes a shape. """
        try:
            self.shapes.remove(shape)
        except ValueError:
            self.log.error("Couldn't find shape for removal")

    def refresh_slot_list(self):
        """Gather all objects in list. Check done by name."""
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
        self.log.debug("Linked Object %s to %s" % (obj.label, self.label))
        if obj in self.oois:
            self.slots.append(Slots.Slot(label=obj.label, slot_type='digital',
                                         state=self.test_collision, state_idx=obj, ref=obj))

    def unlink_object(self, obj):
        for slot in self.slots:
            if slot.ref is obj:
                self.slots.remove(slot)
                self.log.debug("Removed object %s from slot list of %s" % (obj.label, self.label))

    def test_collision(self, obj):
        """ Test if point collides with any shapes of the ROI.
        """
        # TODO: Only checks of the point is within the bounding box of shapes?
        # TODO: Check if segment between most recent points in history CROSSES (i.e. add point2)

        collision = any([s.collision_check(obj.position) for s in self.shapes if s.active])
        self.toggle_highlight(self.highlighted or collision)
        return collision

    def toggle_highlight(self, state=None):
        """Toggle color to active set if region is highlighted by collision.
        """
        # TODO: Can be cleared up further
        self.highlighted = state if state is not None else self.highlighted

        if self.highlighted and self.normal_color != self.active_color:
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