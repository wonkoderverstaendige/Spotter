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

    def __init__(self, adaptive_tracking=False):

        self.log = logging.getLogger(__name__)

        self.oois = []
        self.rois = []
        self.leds = []
        self.adaptive_tracking = adaptive_tracking

    def addLED(self, label, range_hue, range_sat, range_val, range_area, fixed_pos=False, linked_to=None):
        if self.adaptive_tracking:
            roi = trkbl.Shape('rectangle', None, None)
        else:
            roi = trkbl.Shape('rectangle', None, None)
        led = trkbl.LED(label, range_hue, range_sat, range_val, range_area, fixed_pos, linked_to, roi)
        self.leds.append(led)
        return led

    def addOOI(self, led_list, label, traced=False, tracked=True, magnetic_signals=None):
        ooi = trkbl.OOI(led_list, label, traced, tracked, magnetic_signals)
        self.oois.append(ooi)
        return ooi

    def addROI(self, shape_list, label, color=None, magnetic_objects=None):
        roi = trkbl.ROI(shape_list, label, color, self.oois, magnetic_objects)
        self.rois.append(roi)
        return roi

    def track_feature(self, frame, method='hsv_thresh', scale=1.0):
        """
        Intermediate method selecting tracking method and separating those
        tracking methods from the frames stored in the instantiated Tracker

        :param:scale
            Resize frame before tracking, computation decreases scale^2.
        """
        self.scale = scale*1.0  # float
        if self.scale > 1.0:
            self.scale = 1.0

#        # conversion to HSV before dilation causes artifacts!
        # dilate bright spots
#        kernel = np.ones((3,3), 'uint8')
        if method == 'hsv_thresh':
            if self.scale >= 1.0:
                self.frame = cv2.cvtColor(frame.img, cv2.COLOR_BGR2HSV)
            else:
                self.frame = cv2.cvtColor(cv2.resize(frame.img, (0, 0), fx=self.scale, fy=self.scale,
                                                     interpolation=cv2.INTER_LINEAR), cv2.COLOR_BGR2HSV)

            for led in self.leds:
                if led.detection_active:
                    self.track_thresholds(self.frame, led)
                else:
                    led.pos_hist.append(None)

    def track_thresholds(self, hsv_frame, l):
        """
        Tracks LEDs from a list in a HSV frame by thresholding
        hue, saturation, followed by thresholding for each LEDs hue.
        Large enough contours will have coordinates returned, or None
        """
        r_hue = l.range_hue
        r_sat = l.range_sat
        r_val = l.range_val
        r_area = (l.range_area[0]*self.scale**2, l.range_area[1]*self.scale**2)

        # determine array slices if adaptive tracking is used
        if (l.adaptive_tracking and self.adaptive_tracking) \
           and l.search_roi is not None and l.search_roi.points is not None:
            (ax, ay), (bx, by) = l.search_roi.points
            ax *= self.scale
            bx *= self.scale
            ay *= self.scale
            by *= self.scale
            h, w = hsv_frame.shape[0:2]

            # check if box is too far left or right:
            # Esther says to do it the stoopid way
            if ax < 0:
                ax = 0
            if bx >= w-1:
                bx = w-1

            if ay < 0:
                ay = 0
            if by >= h-1:
                by = h-1

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
            cx = moments['m10']/moments['m00']
            cy = moments['m01']/moments['m00']
            if frame_offset:
                cx += ax
                cy += ay
            l.pos_hist.append((cx/self.scale, cy/self.scale))
        else:
            # Couldn't find a good enough spot
            l.pos_hist.append(None)

    @staticmethod
    def find_contour(frame, range_area):
        """
        Return contour with largest area. Returns None if no contour within
        admissible range_area is found.
        """
        contours, hierarchy = cv2.findContours(frame,
                                               cv2.RETR_LIST,
                                               cv2.CHAIN_APPROX_SIMPLE)
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
if __name__ == '__main__':                                  #
#############################################################
    pass
    ## Parsing CLI arguments
    #ARGDICT = docopt( __doc__, version=None )
    #DEBUG = ARGDICT['--DEBUG']
    #if DEBUG: print ARGDICT
    #
    ## Run in command line without user interface to slow things down
    #GUI = not ARGDICT['--Headless']
    #
    ## Instantiate frame source to get something to write
    #import grabber
    #frame_source = grabber.Grabber( ARGDICT['--source'] )
    #fps = frame_source.fps
    #
    #tracker = Tracker( ARGDICT['--Serial'] )
    #
    #tracker.addLED( 'red', ( 160, 5 ) )
    #tracker.addLED( 'sync', ( 15, 90 ), fixed_pos = True )
    #tracker.addLED( 'blue', ( 105, 135 ) )
    #
    #tracker.addObjectOfInterest( [tracker.leds[0],
    #                              tracker.leds[2]],
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
    #    for idx, led in enumerate( tracker.leds ):
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
