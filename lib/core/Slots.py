# -*- coding: utf-8 -*-
"""
Created on Tue Dec 04 21:41:19 2012
@author: <Ronny Eichler> ronny.eichler@gmail.com

The awkward and awful slots class. Dear lord, I have to
get rid of these.
"""

import logging


class Slot:
    def __init__(self, label, slot_type, state=None, state_idx=None, ref=None):
        self.log = logging.getLogger(__name__)

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
        self.log("Removing slot %s" % str(self))