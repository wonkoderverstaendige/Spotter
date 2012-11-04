# -*- coding: utf-8 -*-
"""
Created on Mon Jul 09 00:02:20 2012
@author: <Ronny Eichler> ronny.eichler@gmail.com

Track position LEDs and sync signal from camera or video file.

Usage:
    ledtrack.py --source SRC [--outfile DST] [options]
    ledtrack.py -h | --help

Options:
    -h --help           Show this screen
    -f --fps FPS        Fps for camera and video
    -s --source SRC     Path to file or device ID [default: 0]
    -o --outfile DST    Path to video out file [default: None]
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


import cv2, os, sys, time, multiprocessing, logging

sys.path.append('./lib')
from docopt import docopt
import grabber, writer, tracker, utils

global DEBUG

# Debug logging
log = logging.getLogger('ledtrack')
loghdl = logging.StreamHandler()#logging.FileHandler('ledtrack.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s') #
loghdl.setFormatter( formatter )
log.addHandler( loghdl )
log.setLevel( logging.INFO ) #INFOERROR


class Main(object):
    grabber = None
    writer_process = None
    queue = multiprocessing.Queue( 16 )

    paused = False
    windowName = 'Capture'
    viewMode = 0
    nviewModes = 1
    last_frame = None
    current_frame = None
    hsv_frame = None
    show_frame = None
    selection = None
    drag_start = None
    record_to_file = True
    ts_start = None


    def __init__( self, source, destination, fps, size, gui='cv2.highgui' ):

        # Setup frame grab object, fills framebuffer
        self.grabber = grabber.Grabber( source, fps, size )

        # Setup writer if required, writes frames from buffer to video file.
        if destination:
            print str(multiprocessing.cpu_count()) + ' CPUs found'
            self.writer_process = multiprocessing.Process(
                        target = writer.Writer,
                        args = ( destination,
                                self.grabber.fps,
                                self.grabber.size,
                                self.queue, ) )
            self.writer_process.start()
            self.check_writer()

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

        #if not self.alive, close:
#        if not self.writer.alive: self.writer.close()

    def check_writer( self ):
        if not self.writer_process.is_alive():
            print 'Writing to disk failed.'
            self.exitMain()
        else:
            return True

    def exitMain( self ):
        if self.grabber:
            self.grabber.close()
        if self.writer_process and self.writer_process.is_alive():
            self.queue.put( 'terminate' )
            self.writer_process.join( 1 )
            if self.writer_process.is_alive(): main.writer_process.terminate()

        fc = self.grabber.framecount
        tt = ( time.clock() - self.ts_start )
        print 'Done! Grabbed ' + str( fc ) + ' frames in ' + str( tt ) + 's, with ' + str( fc / tt ) + ' fps'
        sys.exit( 0 )



#############################################################
if __name__ == "__main__":                                  #
#############################################################

    # Command line parsing
    ARGDICT = docopt( __doc__, version=None )
    DEBUG   = ARGDICT['--DEBUG']
    if DEBUG: print( ARGDICT )

    # no GUI, may later select GUI backend, i.e., Qt or cv2.highgui etc.
    gui = 'cv2.highgui' if not ARGDICT['--Headless'] else ARGDICT['--Headless']

    # Frame size parameter string 'WIDTHxHEIGHT' to size tupple (WIDTH, HEIGHT)
    size = (0, 0) if not ARGDICT['--dims'] else tuple( ARGDICT['--dims'].split('x') )

    # Instantiating main class ... no shit, Sherlock!
    main = Main( source      = ARGDICT['--source'],
                 destination = utils.dst_file_name( ARGDICT['--outfile'] ),
                 fps         = ARGDICT['--fps'],
                 size        = size,
                 gui         = gui )

    # It's Math. 3rd grade Math.
    if DEBUG: print 'fps: ' + str( main.grabber.fps )
    t = int( 1000/main.grabber.fps )

    log.info('starting main loop')

    main.ts_start = time.clock()
    while True:
        # Get new frame
        if main.grabber.grab_next():
            main.last_frame = main.grabber.framebuffer.pop()
            # Check if writer process is still alive
            # Otherwise might lose data without knowing!
            if main.check_writer():
                # Copy numoy array, otherwise queue references same object
                # like frame that will be worked on
                main.queue.put( main.last_frame.copy() )
                time.sleep( 0.001 )

            # pauses interface but should let tracking/writing continue
            if not main.paused:
                main.current_frame = main.last_frame.copy()
                main.hsv_frame = cv2.cvtColor( main.current_frame, cv2.COLOR_BGR2HSV )
                #main.trackLeds()
                main.update_frame()
                main.show()
                main.updateHist()

        total_elapsed = ( time.clock() - main.grabber.ts_last_frame ) * 1000
        t = int( 1000/main.grabber.fps - total_elapsed ) - 1
        if t <= 0:
            log.info('Missed next frame by: ' + str( t * -1. ) + ' ms')
            t = 1

        key = cv2.waitKey(t)

        # Pause video with <SPACE>
        main.paused = not main.paused if ( key % 0x100 == 32 ) else main.paused

        # <ESCAPE> to EXIT
        if ( key % 0x100 == 27 ):
            main.exitMain()

