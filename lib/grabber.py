# -*- coding: utf-8 -*-
"""
Created on Mon Jul 09 00:07:34 2012
@author: <Ronny Eichler> ronny.eichler@gmail.com

Handles grabbing successive frames from capture object and returns current
frames of requested type.
Capture object must be closed with Grabber.close() or script will not terminate!

Usage:
    grabber.py --source SRC [--dims DIMS] [options]
    grabber.py -h | --help

Options:
    -h --help        Show this screen
    -f --fps FPS     Fps for camera and video
    -s --source SRC  Source, path to file or integer device ID [default: 0]
    -S --Serial      Serial port to uC [default: None]
    -d --dims DIMS   Frame size [default: 320x200]
    -D --DEBUG       Verbose debug output

"""

import cv2
import cv2.cv as cv
import time
import os
import sys
from collections import deque

#project libraries
sys.path.append('./lib')

#command line handling
sys.path.append('./lib/docopt')
from docopt import docopt


DEBUG = True

class Grabber:
    capture = None          # Capture object to frame source
    fourcc = None           # Source frame coding

    fps_init = None         # Current source fps, may differ from CLI parameter
    fps = None

    size_init = None
    size = None

    framecount = 0          # Frames received so far
    ts_last_frame = None    # Timestamp of most recent frame
    ts_first = None         # Timestamp of first frame, BUGGY!
    source_type = None      # File, stream, device; changes behavior of GUI
    framebuffer = deque( maxlen=256 )

    def __init__( self, source, fps=0, size=(0, 0) ):
        """ source - Integer DeviceID or path to source file
            fps    - Float, frames per second of replay/capture
            size   - list of floats (width, height)
        """

        # Integer: Devide ID. Else, grabber will use as path and look for file
        try:
            source = int( source )
            self.source_type = 'device'
        except ValueError:
            self.source_type = 'file'
            if not os.path.isfile( source ):
                print 'Source file ' + source + ' does not exist.'
                sys.exit(0)

        # Creating capture handle object
        if DEBUG: print 'Attempting to open source "' + str( source ) + '" of type ' + self.source_type +  ' as capture... '
        try:
            self.capture = cv2.VideoCapture( source )
        except:
            print '!!! Unable to open VideoCapture!'
        if DEBUG: print '   --> ' + str( self.capture ) + ' returned.'

        # Proper fps values only important if lower than what camera can provide,
        # or for video files, which are limited by CPU speed/1ms min of waitKey()
        try:
            self.fps_init = float( 29.97 if not fps else fps )
        except ValueError:
            self.fps_init = 29.97

        # size given, to compare with size of first frame
        self.size_init = size

        # if source_type is 'device': Otherwise does nothing
        if not self.source_type == 'file':
            cv2.C
            self.capture.set( cv.CV_CAP_PROP_FPS, float( self.fps_init ) )
            self.capture.set( cv.CV_CAP_PROP_FRAME_WIDTH, float(self.size_init[0]) )
            self.capture.set( cv.CV_CAP_PROP_FRAME_HEIGHT, float(self.size_init[1]) )

        # Grab first frame, don't append to framebuffer
        # TODO: Thats nasty for video file, losing first frame! I.e. transcoding
        # would be lossy!
        self.grab_first()


    def grab_first( self ):
        """ Grabs first frame to get source image parameters. """
        # Possibly eternal loop until first frame returned
        rv = False
        while not rv:
            rv, img = self.capture.read()

        # get source parameters
        self.size = tuple( [int( self.capture.get(3) ), int( self.capture.get(4) )] )
        self.fps = int( self.capture.get(5) )
        self.fourcc = self.capture.get(6)

        if DEBUG: print 'First frame grab - fps: ' + str(self.fps) + '; size: ' + str(self.size) + ';'


    def grab_next( self ):
        """Grabs a new frame from the source and appends it to framebuffer."""
        rv, img = self.capture.read()
        if rv:
            # time of first 'real' frame
            if self.framecount == 0:
                self.ts_first = time.clock()

            self.framecount += 1
            self.ts_last_frame = time.clock()
            self.framebuffer.appendleft(img)
        return rv


    def close( self ):
        if DEBUG: print 'Closing Grabber'
        self.capture.release()


##########################
if __name__ == "__main__":

    # Parsing arguments
    ARGDICT = docopt(__doc__, version=None)
    DEBUG = ARGDICT['--DEBUG']
    if DEBUG: print( ARGDICT )

    # Width and height; WWWxHHH to tuple of ints; cv2 set requires floats
    size = (0, 0) if not ARGDICT['--dims'] else tuple( ARGDICT['--dims'].split('x') )


    # instantiate main class
    main = Grabber( source = ARGDICT['--source'],
                    fps    = ARGDICT['--fps'],
                    size   = size )

    # Requirements for main loop
    if DEBUG: print 'fps: ' + str( main.fps )
    if main.fps:
        t = int( 1000/main.fps )
    else:
        t = 1

    # Main loop
    key = 0
    while True:
        if not main.grab_next() or ( key % 0x100 == 27 ):
            main.close()
            cv2.destroyAllWindows()
            sys.exit( 0 )
        else:
            cv2.imshow( 'Grabber', main.framebuffer.pop() )
            key = cv2.waitKey( t )
