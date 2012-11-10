# -*- coding: utf-8 -*-
"""
Created on Wed Jul 11 09:28:37 2012
@author: <Ronny Eichler> ronny.eichler@gmail.com

Tracks colored spots in images or series of images

Usage:
    tracker.py --source SRC [--continuous -D -H]
    tracker.py -h | --help

Options:
    -h --help        Show this screen
    -s --source SRC  Source, path to file or integer device ID [default: 0]
    -c --continuous  Track spots over time, not frame by frame
    -D --DEBUG       Verbose debug output
    -H --Headless    No Interface

"""

import time, cv2, sys
import numpy as np
sys.path.append('./lib')
import funker, utils
sys.path.append('./lib/docopt')
from docopt import docopt



DEBUG = True

class LED:
    """ Each instance is a spot to track in the image. Holds histogram to do
    camshift with plus ROI/Mask"""

    hue_hist = None
    hue_range = None # np.array uint8 of (lowerBound, higherBound), red: 170,10
    min_sat = 150
    min_val = 90
    label = None
    roi = None
    fixed_pos = False
    pos_hist = None
    linked_to = None # physically linked to another LED?


    def __init__( self, label, hue_range, fixed_pos = False, linked_to = None ):
        self.label = label
        self.fixed_pos = fixed_pos
        self.hue_range = hue_range
        self.linked_to = None
        self.pos_hist = list()

    def updateHistogram( self, led_hist ):
        pass

    def gethistory( ):
        pass

    def updateHistory( self, coords):
        pass


class Mob:
    """ Mobile object LEDs are attached to, if any.
    """

    pos_hist = None
    guessed_pos = None
    leds = None
    label = None

    def __init__( self, led_list, label = 'trackme' ):
        self.pos_hist = list()
        self.leds = led_list
        self.label = label

    def updatePosition( self ):
        coords = []
        for l in self.leds:
            if not l.pos_hist[-1] is None:
                coords.append( l.pos_hist[-1] )

        # find !mean! coordinates
        self.pos_hist.append( utils.middle_point( coords ) )
        self.guessed_pos = utils.guessedPosition( self.pos_hist )


    def predictPositionFast( self, frame_idx ):
        pass
    
    def predictPositionAccurate( self, frame_idx ):
        pass


class Tracker:
    """ Performs tracking and returns positions of found LEDs """
    leds = list()
    min_sat = 50
    min_val = 50

    # frame buffer
    frame = None

    # mobile object, linked to LEDs
    ooi = None


    def __init__( self ):
#        self.leds = led_list
        self.funker = funker.Funker()


    def addLED( self, label, hue_range, fixed_pos = False, linked_to = None ):
        # TODO: More comprehensive LED types, including val/sat ranges etc.
        self.leds.append( LED( label, hue_range, fixed_pos, linked_to ) )


    def addObjectOfInterest( self, led_list, label = 'trackme' ):
        self.ooi = Mob( led_list, label )


    def trackLeds( self, frame, method = 'hsv_thresh' ):
        """ Intermediate method selecting tracking method and seperating those
            tracking methods from the frames stored in the instantiatd Tracker
        """
        if method == 'hsv_thresh':
            self.frame = frame
            coord_list = self.threshTrack( self.frame, self.leds )
            for i, l in enumerate( self.leds ):
                l.pos_hist.append( coord_list[i] )


    def threshTrack( self, hsv_frame, led_list ):
        """ Tracks LEDs from a list in a HSV frame by thresholding
            hue, saturation, followed by thresholding for each LEDs hue.
            Large enough contours will have coords returned, or None
        """
        coord_list = list()

        # dilate bright spots
#        kernel = np.ones( (3,3), 'uint8' )
#        # conversion to HSV before dilation causes artifacts
#        dilatedframe = cv2.cvtColor( self.frame, cv2.COLOR_BGR2HSV )

        for l in led_list:
            # if range[0] > range[1], i.e., color is red and wraps around,
            # invert range and perform NOT on result
            invert_range = False if not l.hue_range[0] > l.hue_range[1] else True

            # All colors except red
            if not invert_range:
                lowerBound = np.array( [l.hue_range[0], l.min_sat, l.min_val], np.uint8 )
                upperBound = np.array( [l.hue_range[1], 255, 255], np.uint8 )
                ranged_frame = cv2.inRange( hsv_frame, lowerBound, upperBound )

            # Red requires double thresholding!
            else:
                # min-180 (or, 255)
                lowerBound = np.array( [l.hue_range[0], l.min_sat, l.min_val], np.uint8 )
                upperBound = np.array( [179, 255, 253], np.uint8 )
                ranged_frame = cv2.inRange( hsv_frame, lowerBound, upperBound )
                # 0-max (or, 255)
                lowerBound = np.array( [0, l.min_sat, l.min_val], np.uint8 )
                upperBound = np.array( [l.hue_range[1], 255, 253], np.uint8 )
                redrange = cv2.inRange( hsv_frame, lowerBound, upperBound )
                # combine both ends for complete mask
                ranged_frame = cv2.bitwise_or( ranged_frame, redrange )

            # find largest contour
            ranged_frame = cv2.dilate( ranged_frame, np.ones( (3,3), 'uint8' ) )
            contour = self.findContour( ranged_frame, min_area = 5 )

            # finding centroids of best_cnt and draw a circle there
            if not contour == None:
                M = cv2.moments( contour )
                cx,cy = int( M['m10']/M['m00'] ), int( M['m01']/M['m00'] )
#                cv2.circle(ranged_frame,(cx,cy),5,255,-1)
                coord_list.append( tuple( [cx, cy] ) )
            else:
                # Couldn't find a good enough spot
                coord_list.append( None )

        # having a returnlist may be overly complicated, but makes it easier to
        # track LEDs in frames not part of sequence from the framesource for
        # fine tuning of parameters.
        return coord_list


    def findContour( self, frame, min_area = 5 ):
        """ Return contour with largest area. Returns None if no contour
            larger than min_area """
        contours, hierarchy = cv2.findContours( frame,
                                                cv2.RETR_LIST,
                                                cv2.CHAIN_APPROX_SIMPLE )
        largest_area = 0
        best_cnt = None
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > largest_area and area > min_area:
                largest_area = area
                best_cnt = cnt

        return best_cnt


    def camshiftTrack( self, hsv_frame, led_list ):
        """ camshifting shifty histograms
        """
        kernel = np.ones( (3,3), 'uint8' )
        dilatedframe = cv2.dilate( hsv_frame, kernel )
        h, s, v = cv2.split(dilatedframe)

        rv, st = cv2.threshold(s, self.min_sat, 1, cv2.THRESH_BINARY)

        ledpos = ( 100, 100 )
        return ledpos
        
    def close( self ):
        self.funker.close()



#############################################################
if __name__ == '__main__':                                  #
#############################################################

    # Parsing CLI arguments
    ARGDICT = docopt( __doc__, version=None )
    DEBUG = ARGDICT['--DEBUG']
    if DEBUG: print ARGDICT

    # Run in command line without user interface to slow things down
    GUI = not ARGDICT['--Headless']

    # Instantiate frame source to get something to write
    import grabber
    frame_source = grabber.Grabber( ARGDICT['--source'] )
    fps = frame_source.fps

    tracker = Tracker()

    tracker.addLED( 'red', ( 160, 5 ) )
    tracker.addLED( 'sync', ( 15, 90 ), fixed_pos = True )
    tracker.addLED( 'blue', ( 105, 135 ) )

    tracker.addObjectOfInterest( [tracker.leds[0],
                                  tracker.leds[2]],
                                  'MovingObject' )

    colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0)]

    # Main loop till EOF or Escape key pressed
    ts = time.clock()
    n = 0
    key = 0
    while frame_source.grab_next() and not ( key % 100 == 27 ):
        frame = frame_source.framebuffer.pop()

        tracker.frame = cv2.cvtColor( frame, cv2.COLOR_BGR2HSV )
        tracker.trackLeds( tracker.frame, method = 'hsv_thresh' )
        tracker.ooi.updatePosition()

        if not tracker.ooi.pos_hist[-1] == None:
#            tracker.funker.send(tracker.ooi.pos_hist[-1][0])
            tracker.funker.send(tracker.ooi.guessed_pos)

        for idx, led in enumerate( tracker.leds ):
            if not led.pos_hist[-1] == None:
                utils.drawCross( frame, led.pos_hist[-1], 5, colors[idx], gap = 3 )

#        if not ( tracker.leds[2].pos_hist[-1] == None or tracker.leds[0].pos_hist[-1] == None ):
#            utils.drawPointer( frame,
#                               tracker.leds[2].pos_hist[-1],
#                               tracker.leds[0].pos_hist[-1] )

        # 0.12ms for 10, 0.5ms for 100 points
        utils.drawTrace( frame, tracker.ooi.pos_hist, 255, 100 )


        if GUI:
            cv2.imshow( 'Tracker', frame )
            key = cv2.waitKey(1)

        n+=1

    # Exiting gracefully
    tt = time.clock() - ts
    t_fps = n*1.0/tt
    print 'Tracked ' + str(n) + ' frames in ' + str(tt) + 's, ' + str(t_fps) + ' fps'
    frame_source.close()
    sys.exit(0)
