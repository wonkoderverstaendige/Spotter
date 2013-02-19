#!/usr/bin/env python
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
    -S --Serial         Serial port to uC [default: None]
    -o --outfile DST    Path to video out file [default: None]
    -d --dims DIMS      Frame size [default: 320x200]
    -H --Headless       Run without interface
    -D --DEBUG          Verbose output

To do:
    - destination file name may consist of tokens to automatically create,
      i.e., %date%now%iterator3$fixedstring
    - track low res, but store full resolution
    - can never overwrite a file

#Example:
    --source 0 --dims 320x200 --outfile test.avi

"""

import cv2
import sys
import time
import multiprocessing
import logging

#project libraries
sys.path.append('./lib')
from grabber import Grabber
from writer import Writer
from tracker import Tracker
from chatter import Chatter
#from GUI import GUI
import utilities as utils


#command line handling
sys.path.append('./lib/docopt')
from docopt import docopt


class Spotter:

    # helper instances
    grabber = None
    writer = None
    tracker = None
    chatter = None

    # state variables
    record_to_file = True

    newest_frame = None  # fresh from the frame source; to be processed/written
    still_frame = None   # frame shown in GUI, may be an older one
    hsv_frame = None     # converted into HSV colorspace for tracking

    ts_start = None

    paused = False


    def __init__(self, source, destination, fps, size, gui, serial=None):
        # Setup frame grabber object, fills framebuffer
        self.grabber = Grabber(source, fps, size)

        # Writer writes frames from buffer to video file in a seperate process.
#        print str(multiprocessing.cpu_count()) + ' CPUs found'
        self.writer_queue = multiprocessing.Queue(16)
        self.writer_pipe, child_pipe = multiprocessing.Pipe()

        self.writer = multiprocessing.Process(
                    target = Writer,
                    args = (self.grabber.fps,
                            self.grabber.size,
                            self.writer_queue,
                            child_pipe,))
        self.writer.start()

        # tracker object finds LEDs in frames
        self.tracker = Tracker()

        # chatter handles serial communication
        self.chatter = Chatter(serial, auto=True)

        # GUI other than Qt currently not available. We apologize for any
        # inconvinience. << NOT TRUE ANYMORE! HOORAY!
#        self.gui = GUI( self, gui, "Spotter", size )

        # histogram instance required to do... nothing for now?
#        self.hist = utils.HSVHist()


    def update(self):
        # Get new frame
#        print "updating"
        if not self.paused and self.grabber.grab_next():
            self.newest_frame = self.grabber.framebuffer.pop()

            # Find and update position of tracked object
            self.hsv_frame = cv2.cvtColor( self.newest_frame, cv2.COLOR_BGR2HSV )
            self.tracker.trackLeds( self.hsv_frame, method = 'hsv_thresh' )

            slots = []
            # Update positions of all objects
            for o in self.tracker.oois:
                o.update_slots(self.chatter)
                o.update_state()
                slots.extend(o.linked_slots())
            for r in self.tracker.rois:
                r.update_slots(self.chatter)
                r.update_state()
                slots.extend(r.linked_slots())

            self.chatter.update_pins(slots)

            # Check if writer process is still alive
            # Otherwise might lose data without knowing!
            # Copy numpy array, otherwise queue references same object
#            print self.writer_pipe.recv()
            if self.check_writer():
                self.writer_pipe.send('alive')
                self.writer_queue.put(self.newest_frame.copy())
                # required, or may crash?
                time.sleep(0.001)

        else:
            print 'No new frame returned!!! What does it mean??? We are going to die! Eventually!!!'

        total_elapsed = ( time.clock() - self.grabber.ts_last_frame ) * 1000
        t = int( 1000/self.grabber.fps - total_elapsed ) - 1
        if t <= 0:
#            log.info('Missed next frame by: ' + str( t * -1. ) + ' ms')
            t = 1

    def toggle_video_recording(self, state):
        if state:
            self.writer_pipe.send('start')
        else:
            self.writer_pipe.send('stop')

    def check_writer(self):
        """ True if alive """
        return self.writer.is_alive()
        #check pipe!
#        if self.return_queue.is_
#        if not self.writer.is_alive():
#            print('Writing to disk failed.')
#            log.error('Writing to disk failed.')
#            self.exitMain()
#        else:
#            return True

    def exitMain( self ):
        """ Graceful exit. Ha. Ha. Ha. Bottle of root beer anyone? """
        # closing grabber is straight forward, will release capture object
        if self.grabber is not None:
            self.grabber.close()
        # tracker has no volatile things to handle either
        if self.tracker is not None:
            self.tracker.close()
        # chatter HAS to close serial connection or all hell breaks loose!
        if self.chatter is not None:
            self.chatter.close()
        # writer is a bit trickier, may have frames left to stow away
        if self.writer is not None and self.writer.is_alive():
            self.writer_pipe.send( 'terminate' )
            # gives the child process one second to finish up
            self.writer.join(1)
            # will be terminated otherwise
            if self.writer.is_alive():
                self.writer.terminate()

        try:
            fc = self.grabber.framecount
            tt = ( time.clock() - self.ts_start )
            log.info('Done! Grabbed ' + str( fc ) + ' frames in ' + str( tt ) + 's, with ' + str( fc / tt ) + ' fps')
        except:
            pass
        sys.exit( 0 )


#############################################################
if __name__ == "__main__":                                  #
#############################################################
#    pass
    # Command line parsing
    ARGDICT = docopt( __doc__, version=None )
    DEBUG   = ARGDICT['--DEBUG']
    if DEBUG: print( ARGDICT )

    # Debug logging
    log = logging.getLogger('ledtrack')
    loghdl = logging.StreamHandler()#logging.FileHandler('ledtrack.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s') #
    loghdl.setFormatter( formatter )
    log.addHandler( loghdl )
    if DEBUG:
        log.setLevel( logging.INFO ) #INFOERROR
    else:
        log.setLevel( logging.ERROR ) #INFOERROR

    # no GUI, may later select GUI backend, i.e., Qt or cv2.highgui etc.
    guistring = 'cv2.highgui' if not ARGDICT['--Headless'] else ARGDICT['--Headless']

    # Frame size parameter string 'WIDTHxHEIGHT' to size tupple (WIDTH, HEIGHT)
    size = (0, 0) if not ARGDICT['--dims'] else tuple( ARGDICT['--dims'].split('x') )

    # Instantiating main class ... no shit, Sherlock!
    main = Spotter( source      = ARGDICT['--source'],
                    destination = utils.dst_file_name( ARGDICT['--outfile'] ),
                    fps         = ARGDICT['--fps'],
                    size        = size,
                    gui         = guistring,
                    serial      = ARGDICT['--Serial'])

    # It's Math. 3rd grade Math. Wait time between frames, if any left
    log.debug( 'fps: ' + str(main.grabber.fps) )
    t = int(1000/main.grabber.fps)

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
            if not main.writer == None and main.check_writer():
                main.write_queue.put( main.newest_frame.copy() )
                time.sleep( 0.001 ) # required, or may crash?

            # Find and update position of tracked object
            main.hsv_frame = cv2.cvtColor( main.newest_frame, cv2.COLOR_BGR2HSV )
            main.tracker.trackLeds( main.hsv_frame, method = 'hsv_thresh' )
#            main.Object.updatePosition()

            # send position of tracked object to serial port
#            if not main.Object.position is None:
#                main.tracker.chatter.send( main.Object.position )

            # freezes frame being shown, but not frame being processed/written
            main.gui.update( main.newest_frame )

        else:
            print 'No new frame returned!!! What does it mean??? We are going to die! Eventually!!!'

        total_elapsed = ( time.clock() - main.grabber.ts_last_frame ) * 1000
        t = int( 1000/main.grabber.fps - total_elapsed ) - 1
        if t <= 0:
            log.info('Missed next frame by: ' + str( t * -1. ) + ' ms')
            t = 1
#        main.update()
        main.gui.onKey( cv2.waitKey(t) )

#    sys.exit(app.exec_())
