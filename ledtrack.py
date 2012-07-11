# -*- coding: utf-8 -*-
"""
Created on Mon Jul 09 00:02:20 2012

@author: Ronny
"""

import cv2, sys, argparse, time, threading

sys.path.append('./lib')
import grabber, writer, tracker, utils

# Parse command line arguments:
parser = argparse.ArgumentParser(description = 'track colored LEDs and sync signal from live camera feed or recorded video file')
parser.add_argument('-c', '--camera', type=int, default=0, help='Camera ID (V4L default: 0, WMF default: 0)')
parser.add_argument('-i', '--infile', nargs = 1, help='Path to videop file')
parser.add_argument('-o', '--outfile', help='Path to output video file path/name')
parser.add_argument('-d', '--display', default=1, type=int, help='Live preview, default: 1')
parser.add_argument('-t', '--threshold', type=int, nargs=3, help='HSV threshold [0, 0, 30]', default=[0, 80, 60])
parser.add_argument('-iw', '--width', nargs=1, type=float, help='width of image in pixel, default:auto', default=0)
parser.add_argument('-ih', '--height', nargs=1, type=float, help='height of image in pixel, default:auto', default=0)
parser.add_argument('-fps', '--fps', nargs=1, help='frames per second, changes video playback or camera polling interval', default='auto')

ARGUMENTS = parser.parse_args()

for (key, value) in vars(ARGUMENTS).items():
    print 'I: "%s" is set to "%s"' % ( key, value )
    
class Main(object):
    paused = False
    windowName = 'Capture'
    viewMode = 0
    current_frame = None
    show_frame = None
    selection = None
    drag_start = None
    
    
    def __init__( self, args ):
        
        self.grabber = grabber.Grabber(args)
        self.grabber.grab_first()
        args.fourcc = self.grabber.fourcc
        args.size = (self.grabber.width, self.grabber.height)
        
        self.writer = writer.Writer(args)
        
        self.tracker = tracker.Tracker()
        
        if args.display:
            cv2.namedWindow(self.windowName)
            cv2.setMouseCallback(self.windowName, self.onMouse)
            
        self.hist = utils.HSVHist()


    def onMouse( self, event, x, y, flags, param ):
        """ 
        Mouse interactions with Main window:
            - Left mouse button gives pixel data under cursor
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
                    self.track_window = self.selection
                    print self.track_window

        if self.drag_start:
            xmin = min(x, self.drag_start[0])
            ymin = min(y, self.drag_start[1])
            xmax = max(x, self.drag_start[0])
            ymax = max(y, self.drag_start[1])
            
            if xmax - xmin < 2 and ymax - ymin < 2:
                self.selection = None
            else:
                self.selection = (xmin, ymin, xmax - xmin, ymax - ymin)
                
        if event == cv2.EVENT_RBUTTONDOWN:
            self.nextView()
            
    def nextView( self ):
        pass
    
    def update_frame( self ):
        if self.viewMode == 0:
            self.show_frame = self.current_frame
            
    def show( self ):
        cv2.imshow(self.windowName, self.show_frame)
        
    def updateHist( self ):
        self.hist.calcHist( self.hsv_frame )
        self.hist.overlayHistMap()
        cv2.imshow('histogram', self.hist.overlay)






if __name__ == "__main__":
    main = Main( ARGUMENTS )

    # seperate video writer thread
    frame_event = threading.Event()
    writer_thread = threading.Thread(target = main.writer.write_thread, args = (main.grabber.framebuffer, frame_event, ))
    writer_thread.start()

    print 'fps: ' + str(main.grabber.fps)
    if main.grabber.fps and main.grabber.fps > 0:
        t = int(1000/main.grabber.fps)
    else:
        t = 33
        
    ts_start = time.clock()
    while True:
        if main.grabber.grab_next():
            frame_event.set()
            frame_event.clear()
            
            if not main.paused:
                main.current_frame = main.grabber.framebuffer[0]
                main.hsv_frame = cv2.cvtColor(main.current_frame, cv2.COLOR_BGR2HSV)
                main.update_frame()
                main.show()
                main.updateHist()
        
        total_elapsed = (time.clock() - main.grabber.ts_last_frame) * 1000
        t = int(1000/main.grabber.fps - total_elapsed) - 1
        if t <= 0:
            print 'Missed next frame by: ' + str(t*-1.) + ' ms'
            t = 1        
        
        key = cv2.waitKey(t)
        
        if ( key % 0x100 == 32 ):
            main.paused = not main.paused
        
        # escape key closes windows/exits
        if ( key % 0x100 == 27 ):
            print 'Exiting...'            
            cv2.destroyAllWindows()
            # wake up threads to let them stop themselves
            main.writer._alive = False
            frame_event.set()
            
            main.grabber.close()
            main.writer.close()
            
            fc = main.grabber.framecount
            tt = (time.clock() - ts_start)
            print 'Done! Grabbed ' + str(fc) + ' frames in ' + str(tt) + 's, with ' + str(fc/tt) + ' fps'
            sys.exit(0)
