# -*- coding: utf-8 -*-
"""
Track position LEDs and sync signal from camera or video file.

Usage: 
    ledtrack.py --camera=<DEVID> [--outfile=<OUTPATH>] [-s=<SIZE> -f=<FPS> -Bvh]
    ledtrack.py --infile=<INPATH> [-Bvh]
    
Options:
    -h, --help              Show this screen
    -v, --version           Show version
    -i, --infile=<INPATH>   Path to source video file
    -c, --camera=<DEVID>    Camera ID [default: 0]
    -o, --outfile=<OUTPUT>  Path to video out file
    -s, --size=<SIZE>       Frame size [default: 320x200]
    -B, --Blind             Run without interface

Created on Mon Jul 09 00:02:20 2012
@author: Ronny
-iw 160 -ih 120 -o test.avi -i media/r52r2f117.avi -fps 30

"""
#-i ./media/r52r2f117,.avi
import cv2, sys, argparse, time, threading
from docopt import docopt

sys.path.append('./lib')
import grabber, writer, tracker, utils

# Parse command line arguments:
parser = argparse.ArgumentParser(description = 'track colored LEDs and sync signal from live camera feed or recorded video file')
parser.add_argument('-c', '--camera', type=int, default=0, help='Camera ID (V4L default: 0, WMF default: 0)')
parser.add_argument('-i', '--infile', type = str, nargs = 1, help='Path to videop file')
parser.add_argument('-o', '--outfile', type = str, nargs = 1, help='Path to output video file path/name')
parser.add_argument('-d', '--display', default=1, type=int, help='Live preview, default: 1')
parser.add_argument('-t', '--threshold', type=int, nargs=3, help='HSV threshold [0, 0, 30]', default=[0, 80, 60])
parser.add_argument('-iw', '--width', nargs=1, type=float, help='width of image in pixel, default:auto', default=0)
parser.add_argument('-ih', '--height', nargs=1, type=float, help='height of image in pixel, default:auto', default=0)
parser.add_argument('-fps', '--fps', nargs=1, help='frames per second, changes video playback or camera polling interval', default='auto')


VERSION = 0.01

#ARGUMENTS = parser.parse_args()
#for (key, value) in vars(ARGUMENTS).items():
#    print 'I: "%s" is set to "%s"' % ( key, value )
    
class Main(object):
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
    
    
    def __init__( self, args ):
        
        self.grabber = grabber.Grabber(args)
        self.grabber.grab_first()
        args.fourcc = self.grabber.fourcc
        args.size = (self.grabber.width, self.grabber.height)
        
        """ Setup VideoWriter if required """        
        if self.grabber.capture_is_file:
            self.record_to_file = False
            self.writer = None
            print 'NOT recording, source is file.'
        else:
            if args.outfile and len(args.outfile[0]) > 0:
                self.writer = writer.Writer(args)
                print 'Recording video to file:' + args.outfile[0]
            else:
                self.record_to_file = False
                self.writer = None
                print 'NOT recording to file, no proper destination given.'
        
        self.tracker = tracker.Tracker()
        
        if args.display:
            cv2.namedWindow( self.windowName )
            cv2.setMouseCallback( self.windowName, self.onMouse )
            
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
    ARGUMENTS = docopt(__doc__, version=VERSION)
    print(ARGUMENTS)
    main = Main( ARGUMENTS )

    # seperate video writer thread
    frame_event = threading.Event()
    if main.record_to_file:    
        writer_thread = threading.Thread( target = main.writer.write_thread, args = ( main.grabber.framebuffer, frame_event, ) )
        writer_thread.start()

    print 'fps: ' + str( main.grabber.fps )
    if main.grabber.fps and main.grabber.fps > 0:
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
            print 'Missed next frame by: ' + str( t * -1. ) + ' ms'
            t = 1        
        
        key = cv2.waitKey(t)
        
        if ( key % 0x100 == 32 ):
            main.paused = not main.paused
        
        # escape key closes windows/exits
        if ( key % 0x100 == 27 ):
            print 'Exiting...'            
            
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
