# -*- coding: utf-8 -*-
"""
Created on Mon Jul 09 00:02:20 2012
@author: <Ronny Eichler> ronny.eichler@gmail.com

Track position LEDs and sync signal from camera or video file.

Usage:
    spotter.py --source SRC [--outfile DST] [options]
    spotter.py -h | --help

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
import grabber, writer, tracker, utils
sys.path.append('./lib/docopt')
from docopt import docopt


global DEBUG

# Debug logging
log = logging.getLogger('ledtrack')
loghdl = logging.StreamHandler()#logging.FileHandler('ledtrack.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s') #
loghdl.setFormatter( formatter )
log.addHandler( loghdl )
log.setLevel( logging.ERROR ) #INFOERROR


class Spotter(object):

    # helper instances
    grabber = None
    writer_process = None

    # state variables
    paused = False
    selection = None
    drag_start = None
    record_to_file = True
    viewMode = 0
    nviewModes = 1

    # frame buffers
    queue = multiprocessing.Queue( 16 ) # pipe to writer process
    newest_frame = None  # fresh from the frame source; to be processed/written
    still_frame = None   # frame shown in GUI, may be an older one
    hsv_frame = None     # converted into HSV colorspace for tracking
    gui_frame = None     # still_frame + Menu side bar + overlays

    windowName = 'Spotter'
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
        self.tracker.addLED( 'red', ( 160, 5 ) )
        self.tracker.addLED( 'sync', ( 15, 90 ), fixed_pos = True )
        self.tracker.addLED( 'blue', ( 105, 135 ) )

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
            if not self.gui_frame == None:
                self.drag_start = (x, y)

        if event == cv2.EVENT_LBUTTONUP:
                self.drag_start = None

                if self.selection == None:
                    pixel = self.gui_frame[y, x]
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


    def buildGui( self ):
        """ Assembles GUI by taking a still frame and adding additional space
            for GUI elements and markers
        """
        # still frame selection
        # 0: normal RGB from raw source
        # 1: dense overlay of debugging information
        if self.viewMode == 0:
            self.gui_frame = self.still_frame.copy()
            # overlay information onto stillframe
            self.overlay()

        elif self.viewMode == 1:
            pass
        elif self.viewMode == 2:
            pass
#            self.show_frame = cv2.bitwise_and( self.current_frame, self.current_frame, mask = self.tracker.mask )


    def nextView( self ):
        self.viewMode += 1
        if self.viewMode > self.nviewModes:
            self.viewMode = 0


    def overlay( self ):
        """ Writes information into still frame of GUI, like crosses on tracked
            spots or textual information and ROI borders
        """
        colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0)]
        for i, l in enumerate(self.tracker.leds):
            coords = l.pos_hist[-1]
            if not coords == None:
                # TODO: HSV_to_RGB conversion function
                utils.drawCross( self.gui_frame, coords, 5, colors[i], gap = 3 )


    def show( self ):
        cv2.imshow( self.windowName, self.gui_frame )


    def updateHist( self ):
        self.hist.hueHist( self.hsv_frame )
        self.hist.overlayHistMap()
        cv2.imshow( 'histogram', self.hist.overlay )


    def check_writer( self ):
        """ True if alive, otherwise causes script to terminate. """
        if not self.writer_process.is_alive():
            print('Writing to disk failed.')
            log.error('Writing to disk failed.')
            self.exitMain()
        else:
            return True


    def exitMain( self ):
        """ Graceful exit. """

        # closing grabber is straight forward, will release capture object
        if self.grabber:
            self.grabber.close()

        # writer is a bit trickier, may have frames left to write away
        if self.writer_process and self.writer_process.is_alive():
            self.queue.put( 'terminate' )
            # gives the child process one second to finish up, will be
            # terminated otherwise
            self.writer_process.join( 1 )
            if self.writer_process.is_alive(): main.writer_process.terminate()

        fc = self.grabber.framecount
        tt = ( time.clock() - self.ts_start )
        log.info('Done! Grabbed ' + str( fc ) + ' frames in ' + str( tt ) + 's, with ' + str( fc / tt ) + ' fps')
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
    main = Spotter( source      = ARGDICT['--source'],
                    destination = utils.dst_file_name( ARGDICT['--outfile'] ),
                    fps         = ARGDICT['--fps'],
                    size        = size,
                    gui         = gui )

    # It's Math. 3rd grade Math. Wait time between frames, if any left
    log.debug( 'fps: ' + str( main.grabber.fps ) )
    t = int( 1000/main.grabber.fps )

    # Main loop, runs until EOF or <ESCAPE> key pressed
    log.debug( 'starting main loop' )
    main.ts_start = time.clock()


    while True:

        # Get new frame
        if main.grabber.grab_next():
            main.newest_frame = main.grabber.framebuffer.pop()

            # Check if writer process is still alive
            # Otherwise might lose data without knowing!
            # Copy numpy array, otherwise queue references same object
            # like frame that will be worked on
            if main.check_writer():
                main.queue.put( main.newest_frame.copy() )
                time.sleep( 0.001 )

            main.hsv_frame = cv2.cvtColor( main.newest_frame, cv2.COLOR_BGR2HSV )
            main.tracker.trackLeds( main.hsv_frame )

            # freezes frame being shown, but not frame being processed/written
            if not main.paused:
                main.still_frame = main.newest_frame.copy()

            main.buildGui()
            main.show()
#            main.updateHist()

        else:
            print 'No new frame returned!!! What does it mean??? We are going to die! Eventually!'

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

