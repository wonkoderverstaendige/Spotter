#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 11 09:28:37 2012
@author: <Ronny Eichler> ronny.eichler@gmail.com

Tracks colored spots in images or series of images

Usage:
    tracker.py --source SRC [options]
    tracker.py -h | --help

Options:
    -h --help        Show this screen
    -s --source SRC  Source, path to file or integer device ID [default: 0]
    -S --Serial      Serial port to uC [default: None]
    -c --continuous  Track spots over time, not frame by frame
    -D --DEBUG       Verbose debug output
    -H --Headless    No Interface

"""

import cv2
import logging
import time
import sys
import numpy as np

import lib.utilities as utils
import lib.geometry as geom
import trackables as trkbl
from lib.docopt import docopt

DEBUG = True


class Tracker:
    """ Performs tracking and returns positions of found LEDs """
    frame = None
    scale = 1.0

    def __init__(self, parent, adaptive_tracking=False):
        self.log = logging.getLogger(__name__)

        self.parent = parent
        self.oois = []
        self.rois = []
        self.features = []
        self.adaptive_tracking = adaptive_tracking

    def add_feature(self, label, template):
        # range_hue, range_sat, range_val, range_area, fixed_pos=False, linked_to=None):

        range_hue = map(int, template['range_hue'])
        range_sat = map(int, template['range_sat'])
        range_val = map(int, template['range_val'])
        range_area = map(int, template['range_area'])
        fixed_pos = template.as_bool('fixed_pos')
        linked_to = None

        roi = trkbl.Shape('rectangle', None, None)

        feature = trkbl.LED(label, range_hue, range_sat, range_val, range_area, fixed_pos, linked_to, roi)
        self.features.append(feature)
        self.log.debug("Added feature %s", feature)
        return feature

    def remove_feature(self, feature):
        try:
            self.log.debug("Removing feature %s", feature)
            self.features.remove(feature)
            for o in self.oois:
                if feature in o.linked_leds:
                    o.linked_leds.remove(feature)
        except ValueError:
            self.log.error("Feature to be removed not found")

    def add_ooi(self, label, template):
        # feature_list, label, traced=False, tracked=True, magnetic_signals=None):

        # generate list of all features linked to this object
        linked_features = []
        for n in xrange(min(len(self.features), len(template['features']))):
            for l in self.features:
                if template['features'][n] == l.label:
                    linked_features.append(l)

        # Super awkward handling of pin assignment preferences. Holy moly. Unreadable.
        analog_out = template['analog_out']
        if analog_out:
            # Magnetic objects from collision list
            signal_names = template['analog_signal']
            pin_prefs = template['pin_pref']
            if pin_prefs is None:
                pin_prefs = []
            magnetic_signals = []
            if template['pin_pref_strict']:
                # If pin preference is strict but no/not enough pins given,
                # reject all/those without given pin preference
                if len(pin_prefs) == 0:
                    signal_names = []
            else:
                # if not strict but also not enough given, fill 'em up with -1
                # which sets those objects to being indifferent in their pin pref
                if len(pin_prefs) < len(signal_names):
                    pin_prefs[-(len(signal_names) - len(pin_prefs))] = -1

            # Reject all objects that still don't have a corresponding pin pref
            signal_names = signal_names[0:min(len(pin_prefs), len(signal_names))]

            # Those still in the race, assemble into
            # List of [object label, object, pin preference]
            for i, sig in enumerate(signal_names):
                # Does an object with this name exist? If so, link its reference!
                #                obj = None
                #                for o in self.spotter.tracker.oois:
                #                    if o.label == on:
                #                        obj = o
                magnetic_signals.append([sig, pin_prefs[i]])
        else:
            magnetic_signals = None

        traced = template['trace']
        tracked = template['track']

        ooi = trkbl.ObjectOfInterest(linked_features, label, traced, tracked, magnetic_signals)

        if analog_out and any(template['analog_signal']):
            ooi.analog_pos = 'x position' in template['analog_signal']
            ooi.analog_pos = 'y position' in template['analog_signal']
            ooi.analog_spd = 'speed' in template['analog_signal']
            ooi.analog_dir = 'direction' in template['analog_signal']

        self.oois.append(ooi)
        self.log.debug("Added object %s", ooi)
        return ooi

    def remove_ooi(self, ooi):
        try:
            self.oois.remove(ooi)
            for roi in self.rois:
                roi.refresh_slot_list()
        except ValueError:
            self.log.error("Object to be removed not found")

    def add_roi(self, label, template, shapes, absolute_positions=True):
        # shape_list, label, color=None, magnetic_objects=None
        # extract shapes from shape templates
        shape_list = []
        points = None
        for s_key in template['shapes']:
            if s_key in shapes:
                shape_type = shapes[s_key]['type']
                if absolute_positions:
                    points = [shapes[s_key]['p1'], shapes[s_key]['p2']]
                else:
                    if self.parent.newest_frame is not None:
                        frame_size = self.parent.newest_frame.shape
                        points = geom.scale_points([shapes[s_key]['p1'], shapes[s_key]['p2']],
                                                   (frame_size[0], frame_size[1]))
                if points is not None:
                    shape_list.append([shape_type, points, s_key])

        # Magnetic objects from collision list
        obj_names = template['digital_collision']
        pin_prefs = template['pin_pref']
        if pin_prefs is None:
            pin_prefs = []
        magnetic_objects = []
        if template['pin_pref_strict']:
            # If pin preference is strict but no/not enough pins given,
            # reject all/those without given pin preference
            if len(pin_prefs) == 0:
                obj_names = []
        else:
            # if not strict but also not enough given, fill 'em up with -1
            # which sets those objects to being indifferent in their pin pref
            if len(pin_prefs) < len(obj_names):
                pin_prefs[-(len(obj_names) - len(pin_prefs))] = -1

        # Reject all objects that still don't have a corresponding pin pref
        obj_names = obj_names[0:min(len(pin_prefs), len(obj_names))]

        # Those still in the race, assemble into
        # List of [object label, object, pin preference]
        for io, on in enumerate(obj_names):
            # Does an object with this name exist? If so, link its reference!
            obj = None
            for o in self.oois:
                if o.label == on:
                    obj = o
            magnetic_objects.append([obj, pin_prefs[io]])
        color = template['color']
        roi = trkbl.RegionOfInterest(shape_list, label, color, self.oois, magnetic_objects)
        self.rois.append(roi)
        self.log.debug("Added region %s", roi)
        return roi

    def remove_roi(self, roi):
        try:
            del roi.shapes[:]
            self.rois.remove(roi)
        except ValueError:
            self.log.error("Region to be removed not found")

    def add_from_template(self, template):

        # Add features
        features = []
        for feature_label, feature_template in template['FEATURES'].items():
            features.append(self.add_feature(label=feature_label,
                                             template=feature_template))
            #self.side_bar.add_feature(f_val, f_key, focus_new=False)

        # Add objects of interest
        objects_ = []
        for ooi_label, ooi_template in template['OBJECTS'].items():
            objects_.append(self.add_ooi(label=ooi_label,
                                         template=ooi_template))
            #self.side_bar.add_object(o_val, o_key, focus_new=False)

        # Add regions of interest
        regions = []
        shapes = template['SHAPES']
        abs_pos = template['TEMPLATE']['absolute_positions']
        for region_label, region_template in template['REGIONS'].items():
            regions.append(self.add_roi(label=region_label,
                                        template=region_template,
                                        shapes=shapes,
                                        absolute_positions=abs_pos))
            # self.side_bar.add_region(r_val, r_key, shapes=template['SHAPES'], abs_pos=abs_pos, focus_new=False)

        return features, objects_, regions

    def track_feature(self, frame, method='hsv_thresh', scale=1.0):
        """Intermediate method selecting tracking method and separating those
        tracking methods from the frames stored in the instantiated Tracker

        :param:scale
            Resize frame before tracking, computation decreases scale^2.
        """
        self.scale = scale * 1.0  # float
        if self.scale > 1.0:
            self.scale = 1.0

        #        # conversion to HSV before dilation causes artifacts!
        # dilate bright spots
        #        kernel = np.ones((3,3), 'uint8')
        if method == 'hsv_thresh':
            if self.scale >= 1.0:
                self.frame = cv2.cvtColor(frame.img, cv2.COLOR_BGR2HSV)
            else:
                # TODO: Performance impact of INTER_LINEAR vs. INTER_NEAREST?
                self.frame = cv2.cvtColor(cv2.resize(frame.img, (0, 0), fx=self.scale, fy=self.scale, interpolation=cv2.INTER_NEAREST),
                                          cv2.COLOR_BGR2HSV)

            for feature in self.features:
                if feature.detection_active:
                    self.track_thresholds(self.frame, feature)
                else:
                    feature.pos_hist.append(None)

    def track_thresholds(self, hsv_frame, feature):
        """Tracks LEDs from a list in a HSV frame by thresholding
        hue, saturation, followed by thresholding for each LEDs hue.
        Large enough contours will have coordinates returned, or None
        """
        r_hue = feature.range_hue
        r_sat = feature.range_sat
        r_val = feature.range_val
        r_area = (feature.range_area[0] * self.scale ** 2, feature.range_area[1] * self.scale ** 2)

        # determine array slices if adaptive tracking is used
        if (feature.adaptive_tracking and self.adaptive_tracking) and feature.search_roi is not None and feature.search_roi.points is not None:
            (ax, ay), (bx, by) = feature.search_roi.points
            ax *= self.scale
            bx *= self.scale
            ay *= self.scale
            by *= self.scale
            h, w = hsv_frame.shape[0:2]

            # check if box is too far left or right:
            # Esther says to do it the stoopid way
            if ax < 0:
                ax = 0
            if bx >= w - 1:
                bx = w - 1

            if ay < 0:
                ay = 0
            if by >= h - 1:
                by = h - 1

            frame = hsv_frame[ay:by, ax:bx, :]
            frame_offset = True
        else:
            frame_offset = False
            frame = hsv_frame

        # if range[0] > range[1], i.e., color is red and wraps around
        invert_range = False if not r_hue[0] > r_hue[1] else True

        # All colors except red
        if not invert_range:
            lower_bound = np.array([r_hue[0], r_sat[0], r_val[0]], np.uint8)
            upper_bound = np.array([r_hue[1], r_sat[1], r_val[1]], np.uint8)
            ranged_frame = cv2.inRange(frame, lower_bound, upper_bound)

        # Red hue requires double thresholding due to wraparound in hue domain
        else:
            # min-180 (or, 255)
            lower_bound = np.array([r_hue[0], r_sat[0], r_val[0]], np.uint8)
            upper_bound = np.array([179, r_sat[1], r_val[1]], np.uint8)
            ranged_frame = cv2.inRange(frame, lower_bound, upper_bound)
            # 0-max (or, 255)
            lower_bound = np.array([0, r_sat[0], r_val[0]], np.uint8)
            upper_bound = np.array([r_hue[1], r_sat[1], r_val[1]], np.uint8)
            red_range = cv2.inRange(frame, lower_bound, upper_bound)
            # combine both ends for complete mask
            ranged_frame = cv2.bitwise_or(ranged_frame, red_range)

        # find largest contour that is >= than minimum area
        ranged_frame = cv2.dilate(ranged_frame, np.ones((3, 3), np.uint8))
        contour_area, contour = self.find_contour(ranged_frame, r_area)

        # find centroids of the contour returned
        if contour is not None:
            moments = cv2.moments(contour.astype(int))
            cx = moments['m10'] / moments['m00']
            cy = moments['m01'] / moments['m00']
            if frame_offset:
                cx += ax
                cy += ay
            feature.pos_hist.append((cx / self.scale, cy / self.scale))
        else:
            # Couldn't find a good enough spot
            feature.pos_hist.append(None)

    @staticmethod
    def find_contour(frame, range_area):
        """
        Return contour with largest area. Returns None if no contour within
        admissible range_area is found.
        """
        contours, hierarchy = cv2.findContours(frame, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        largest_area = 0
        best_cnt = None
        min_area = range_area[0]
        max_area = range_area[1]
        for cnt in contours:
            area = cv2.contourArea(cnt.astype(int))
            if area > largest_area and area >= min_area:
                if max_area == 0 or area < range_area[1]:
                    largest_area = area
                    best_cnt = cnt
        return largest_area, best_cnt

    def close(self):
        """ Nothing to do here. """
        self.log.debug('Closing tracker')

#############################################################
if __name__ == '__main__':  #
    #############################################################
    pass
    ## Parsing CLI arguments
    #arg_dict = docopt( __doc__, version=None )
    #DEBUG = arg_dict['--DEBUG']
    #if DEBUG: print arg_dict
    #
    ## Run in command line without user interface to slow things down
    #GUI = not arg_dict['--Headless']
    #
    ## Instantiate frame source to get something to write
    #import grabber
    #frame_source = grabber.Grabber( arg_dict['--source'] )
    #fps = frame_source.fps
    #
    #tracker = Tracker( arg_dict['--Serial'] )
    #
    #tracker.add_feature( 'red', ( 160, 5 ) )
    #tracker.add_feature( 'sync', ( 15, 90 ), fixed_pos = True )
    #tracker.add_feature( 'blue', ( 105, 135 ) )
    #
    #tracker.addObjectOfInterest( [tracker.features[0],
    #                              tracker.features[2]],
    #                              'MovingObject' )
    #
    #colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0)]
    #
    ## Main loop till EOF or Escape key pressed
    #ts = time.clock()
    #n = 0
    #key = 0
    #while frame_source.grab_next() and not ( key % 100 == 27 ):
    #    frame = frame_source.framebuffer.pop()
    #
    #    # tracker works with HSV frames, not BGR
    #    tracker.frame = cv2.cvtColor( frame, cv2.COLOR_BGR2HSV )
    #    tracker.trackLeds( tracker.frame, method = 'hsv_thresh' )
    #    tracker.ooi.updatePosition()
    #
    #    if not tracker.ooi.pos_hist[-1] == None:
    #        tracker.chatter.send(tracker.ooi.position)
    #
    #    for idx, led in enumerate( tracker.features ):
    #        if not led.pos_hist[-1] == None:
    #            utils.drawCross( frame, led.pos_hist[-1], 5, colors[idx], gap = 3 )
    #
    #    # 0.12ms for 10, 0.5ms to draw 100 points
    #    utils.drawTrace( frame, tracker.ooi.pos_hist, 255, 100 )
    #
    #    # draw ROIs
    #    for r in tracker.rois:
    #        r.draw( frame )
    #
    #    if GUI:
    #        cv2.imshow( 'Tracker', frame )
    #        key = cv2.waitKey(1)
    #
    #    n += 1
    #
    ## Exiting gracefully
    #tt = time.clock() - ts
    #t_fps = n*1.0/tt
    #print 'Tracked ' + str(n) + ' frames in ' + str(tt) + 's, ' + str(t_fps) + ' fps'
    #frame_source.close()
    #sys.exit(0)
