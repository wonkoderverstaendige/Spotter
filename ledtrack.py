# -*- coding: utf-8 -*-
"""
Created on Mon Jul 09 00:02:20 2012

@author: Ronny
"""

import cv, cv2, sys, argparse, time, threading

sys.path.append('./lib')
import grabber, writer

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

    def __init__( self, args ):
        
        self.grabber = grabber.Grabber(args)
        self.grabber.grab_first()
        args.fourcc = self.grabber.fourcc
        args.size = (self.grabber.width, self.grabber.height)
        
        self.writer = writer.Writer(args)
        
        cv2.namedWindow('preview', 1)




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
                cv2.imshow('preview', main.grabber.framebuffer[0])
        
        total_elapsed = (time.clock() - main.grabber.ts_last_frame) * 1000
        t = int(1000/main.grabber.fps - total_elapsed) - 1
        
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
