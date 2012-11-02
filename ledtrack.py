# -*- coding: utf-8 -*-
"""
Created on Mon Jul 09 00:02:20 2012
@author: <Ronny Eichler> ronny.eichler@gmail.com

Track position LEDs and sync signal from camera or video file.

Usage: 
    ledtrack.py --source SRC [--outfile OUT] [options]
    ledtrack.py -h | --help
    
Options:
    -h --help           Show this screen
    -f --fps FPS        Fps for camera and video
    -s --source SRC     Path to file or device ID [default: 0]
    -o --outfile OUT    Path to video out file [default: None]
    -d --dims DIMS      Frame size [default: 320x200]
    -H --Headless       Run without interface
    -D --DEBUG          Verbose output

To do:
    - destination file name may consist of tokens to automatically create,
      i.e., %date%now%iterator3$fixedstring
    - track low res, but store full resolution
    - can never overwrite a file

"""
#Example:
#    docopt:
#        --source 0 --outfile test.avi --size=320x200 --fps=30


import cv2, os, sys, time, threading

sys.path.append('./lib')
from docopt import docopt
import grabber, writer, tracker, utils

global DEBUG

class Main(object):
    grabber = None
    writer = None
    
    paused = False
    windowName = 'Capture'
    viewMode = 0
    nviewModes = 1
    current_frame = None
    hsv_frame = None
    show_frame = None
    selection = None
    drag_start = None
    record_to_file = True
    
    
    def __init__( self, source, destination, fps, size, gui='cv2.highgui' ):
        
        # Setup frame grab object, fills framebuffer        
        self.grabber = grabber.Grabber( source, fps, size )
        
        # Setup writer if required, writes frames from buffer to video file.    
        if destination:
            # instantiate video writer object
            self.writer = writer.Writer( destination, fps, size )
        
        # tracker object finds LEDs in frames
        self.tracker = tracker.Tracker()
        
        # Only OpenCV's HighGui is currently used as user interface
        if gui=='cv2.highgui':
            cv2.namedWindow( self.windowName )
            cv2.setMouseCallback( self.windowName, self.onMouse )
            
        # histogram instance required to do... what, again?
        self.hist = utils.HSVHist()


    def onMouse( self, event, x, y, flags, param ):
        """ 
        Mouse interactions with Main window:
            - Left mouse click gives pixel data under cursor
            - Left mouse drag selects rectangle
            
            - Right mouse button switches view mode
        """
        if event == cv2.EVENT_LBUTTONDOWN:
            if not self.current_frame == None:
                self.drag_start = (x, y)
                
        if event == cv2.EVENT_LBUTTONUP:
                self.drag_start = None
                
                if self.selection == None:
                    pixel = self.current_frame[y, x]
                    print "[X,Y][B G R](H, S, V):", [x, y], pixel, utils.BGRpix2HSV(pixel)
                else:
                    #self.track_window = self.selection
                    print self.selection    #self.track_window

        if self.drag_start:
            xmin = min( x, self.drag_start[0] )
            ymin = min( y, self.drag_start[1] )
            xmax = max( x, self.drag_start[0] )
            ymax = max( y, self.drag_start[1] )
            
            if xmax - xmin < 2 and ymax - ymin < 2:
                self.selection = None
            else:
                self.selection = ( xmin, ymin, xmax - xmin, ymax - ymin )
                
        if event == cv2.EVENT_RBUTTONDOWN:
            self.nextView()
            
    def nextView( self ):
        self.viewMode += 1
        if self.viewMode > self.nviewModes:
            self.viewMode = 0
    
    def update_frame( self ):

#        utils.drawCross( self.current_frame, 100, 100, 10, (100, 255, 255) )
        if self.viewMode == 0:
            self.show_frame = self.current_frame
            ledcoords = self.tracker.sumTrack( self.show_frame )
            colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0)]
            for cf, coord in enumerate(ledcoords):
                utils.drawCross( self.show_frame, coord[0], coord[1], 5, colors[cf], gap = 3 )
                
        elif self.viewMode == 1:
            self.show_frame = cv2.bitwise_and( self.current_frame, self.current_frame, mask = self.tracker.mask )
            
    def show( self ):
        cv2.imshow( self.windowName, self.show_frame )
        
    def updateHist( self ):
        self.hist.calcHist( self.hsv_frame )
        self.hist.overlayHistMap()
        cv2.imshow( 'histogram', self.hist.overlay )
        
    def trackLeds( self ):
        self.tracker.sumTrack( self.current_frame )






if __name__ == "__main__":

    # Command line parsing    
    ARGDICT = docopt( __doc__, version=None )
    DEBUG   = ARGDICT['--DEBUG']
    if DEBUG: print( ARGDICT )

    # no GUI, may later select GUI backend, i.e., Qt or cv2.highgui etc.
    gui = 'cv2.highgui' if not ARGDICT['--Headless'] else ARGDICT['--Headless']
     
    # Frame size parameter string 'WIDTHxHEIGHT' to size list [WIDTH, HEIGHT]
    size = [0, 0] if not ARGDICT['--dims'] else list( ARGDICT['--dims'].split('x') )
        
    # Instantiating main class ... no shit, Sherlock!
    main = Main( source      = ARGDICT['--source'],
                 destination = utils.dst_file_name( ARGDICT['--outfile'] ),
                 fps         = ARGDICT['--fps'], 
                 size        = size, 
                 gui         = gui )


    # Event for Thread wake-up, required even if no writer Thread present
    frame_event = threading.Event()
    # seperate video writer thread if Writer Instantiated
    if main.writer:    
        writer_thread = threading.Thread( target = main.writer.write_thread, args = ( main.grabber.framebuffer, frame_event, ) )
        writer_thread.start()

    # It's Math. 3rd grade Math.
    if DEBUG: print 'fps: ' + str( main.grabber.fps )
    if main.grabber.fps > 0.0:
        t = int( 1000/main.grabber.fps )
    else:
        t = 33
        
    ts_start = time.clock()
    while True:
        if main.grabber.grab_next():
            frame_event.set()
            frame_event.clear()
            
            if not main.paused:
                main.current_frame = main.grabber.framebuffer[0]
                main.hsv_frame = cv2.cvtColor( main.current_frame, cv2.COLOR_BGR2HSV )
                #main.trackLeds()
                main.update_frame()
                main.show()
                main.updateHist()

        total_elapsed = ( time.clock() - main.grabber.ts_last_frame ) * 1000
        t = int( 1000/main.grabber.fps - total_elapsed ) - 1
        if t <= 0:
            if DEBUG: print 'Missed next frame by: ' + str( t * -1. ) + ' ms'
            t = 1        
        
        key = cv2.waitKey(t)
        
        if ( key % 0x100 == 32 ):
            main.paused = not main.paused
        
        # escape key closes windows/exits
        if ( key % 0x100 == 27 ):
            if DEBUG: print 'Exiting...'            
            
            # wake up threads to let them stop themselves
            if main.record_to_file:            
                main.writer._alive = False
                frame_event.set()
                #main.writer.close()
            
            main.grabber.close()

            cv2.destroyAllWindows()
            
            fc = main.grabber.framecount
            tt = ( time.clock() - ts_start )
            print 'Done! Grabbed ' + str( fc ) + ' frames in ' + str( tt ) + 's, with ' + str( fc / tt ) + ' fps'
            sys.exit( 0 )
