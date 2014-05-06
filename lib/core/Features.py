# -*- coding: utf-8 -*-
"""
Created on Tue Dec 04 21:41:19 2012
@author: <Ronny Eichler> ronny.eichler@gmail.com

Features used by Tracker.
"""

import logging
import lib.utilities as utils
import lib.geometry as geom


class Feature(object):
    """ General class holding a feature to be tracked with whatever tracking
    algorithm is appropriate.
    """
    def __init__(self):
        pass


class LED(Feature):
    """ Each instance is a spot defined by ranges in a color space. """
    def __init__(self, label, range_hue, range_sat, range_val, range_area, fixed_pos, linked_to, roi=None):
        Feature.__init__(self)
        self.log = logging.getLogger(__name__)
        self.label = label
        self.detection_active = True
        self.marker_visible = True

        # feature description ranges
        self.range_hue = range_hue
        self.range_sat = range_sat
        self.range_val = range_val
        self.range_area = range_area

        self.pos_hist = geom.PointArray()

        # Restrict tracking to a search window?
        self.adaptive_tracking = roi is not None
        self.fixed_pos = fixed_pos
        self.search_roi = roi

        # List of linked features, can be used for further constraints
        self.linked_to = linked_to

    @property
    def mean_hue(self):
        return utils.mean_hue(self.range_hue)

    @property
    def lbl_color(self):
        # mean color of range for labels/markers etc.
        return utils.HSVpix2RGB((self.mean_hue, 255, 255))

    @property
    def position(self):
        return self.pos_hist.last()