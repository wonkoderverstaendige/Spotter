# -*- coding: utf-8 -*-
"""
Created on Mon Jul 09 00:07:34 2012
@author: <Ronny Eichler> ronny.eichler@gmail.com

Handles grabbing successive frames from capture object and returns current
frames of requested type.
Capture object must be closed with Grabber.close() or script will not terminate!

Usage: 
    grabber.py --source SRC [--dims DIMS --fps FPS -D]
    grabber.py -h | --help

Options:
    -h --help          Show this screen
    -f --fps=<FPS>     Fps for camera and video
    -s --source=<SRC>  Source, path to file or integer device ID [default: 0]
    -d --dims=<DIMS>   Frame size [default: 320x200]
    -D --DEBUG         Verbose debug output

"""


import cv, cv2, time, os, sys
sys.path.append('./lib')
from docopt import docopt
from collections import deque

DEBUG = True

class Grabber:
    capture = None          # Capture object to frame source
    fourcc = None           # Source frame coding
    fps = None              # Current source fps, may differ from CLI parameter
    framecount = 0          # Frames received so far
    ts_last_frame = None    # Timestamp of most recent frame
    ts_first = None         # Timestamp of first frame, BUGGY!
    source_type = None      # File, stream, device; changes behavior of GUI
    framebuffer = deque(maxlen=256)
    
    def __init__( self, source, fps=0, size=[0, 0] ):
        """ source - Integer DeviceID or path to source file
            fps    - Float, frames per second of replay/capture
            size   - lsit of floats (width, height)
        """

        # Integer: Devide ID. Else, grabber will use as path and look for file
        try:
            source = int( source )
            self.source_type = 'device'
            if DEBUG: print 'Source type: device.'
        except ValueError:
            self.source_type = 'file'
            if not os.path.isfile( source ):
                print 'Unable to open source file!'
                sys.exit(0)
       
        # Creating capture handle object
        if DEBUG: print 'Attempting to open source "' + str( source ) + '" of type ' + self.source_type +  ' as capture... '
        try:                
            self.capture = cv2.VideoCapture( source )
        except:
            print 'Unable to open Capture!'
        if DEBUG: print str( self.capture ) + ' returned.'
        
        # Proper fps values only important if lower than what camera can provide,
        # or for video files, which are limited by CPU speed and 1ms min of waitKey()
        try:
            fps = float( 0 if not fps else fps ) 
        except ValueError:
            fps = 0.0
        
        # if source_type is 'device': Otherwise does nothing
        self.capture.set( cv.CV_CAP_PROP_FPS, float(fps) )
        self.capture.set( cv.CV_CAP_PROP_FRAME_WIDTH, float(size[0]) )
        self.capture.set( cv.CV_CAP_PROP_FRAME_HEIGHT, float(size[1]) )
           
        # Grab first frame, don't append to framebuffer
        self.grab_first()


    def grab_first( self ):
        """ Grabs first fram to get source image parameters. """
        rv = False
        while not rv:   
            rv, img = self.capture.read()
       
        # get source parameters
        self.width  = int( self.capture.get(3) )
        self.height = int( self.capture.get(4) )
        self.fps    = int( self.capture.get(5) )
        self.fourcc = self.capture.get(6)
    
    
    def grab_next( self ):
        """Grabs a new frame from the source and appends it to framebuffer."""
        rv, img = self.capture.read()
        if rv:
            # time of first 'real' frame            
            if self.framecount == 0: self.ts_first = time.clock()
            self.framecount += 1
            self.ts_last_frame = time.clock()
            self.framebuffer.appendleft(img)
        return rv
        
        
    def close( self ):
        self.capture.release()



if __name__ == "__main__":
    
    # Parsing arguments    
    ARGDICT = docopt(__doc__, version=None)
    DEBUG = ARGDICT['--DEBUG']
    if DEBUG: print( ARGDICT )

    # Width and height; WWWxHHH to tuple of floats; cv2 property set requires floats
    if not ARGDICT['--dims']:
        size = [0.0, 0.0]
    else:
        size = ARGDICT['--dims'].split('x')
        for i,s in enumerate(size):
            size[i] = float(s)
        
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
    ts_start = time.clock()
    while True:
        if main.grab_next():
            cv2.imshow( 'Main', main.framebuffer.pop() )
        else:
            main.close()
            cv2.destroyAllWindows()
            sys.exit( 0 )    

        if ( cv2.waitKey( t ) % 0x100 == 27 ):
            main.close()
            cv2.destroyAllWindows()
            sys.exit( 0 )