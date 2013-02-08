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
    --source 0 --outfile test.avi --size=320x200 --fps=30

"""

import cv2
#import os
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

    # frame buffers
    write_queue = multiprocessing.Queue( 16 ) # pipe to writer process
    newest_frame = None  # fresh from the frame source; to be processed/written
    still_frame = None   # frame shown in GUI, may be an older one
    hsv_frame = None     # converted into HSV colorspace for tracking

    ts_start = None

    paused = False


    def __init__( self, source, destination, fps, size, gui, serial = None ):

        # Setup frame grabber object, fills framebuffer
        self.grabber = Grabber( source, fps, size )

        # Setup writer if required, writes frames from buffer to video file.
        if destination:
            print str(multiprocessing.cpu_count()) + ' CPUs found'
            self.writer = multiprocessing.Process(
                        target = Writer,
                        args = ( destination,
                                self.grabber.fps,
                                self.grabber.size,
                                self.write_queue, ) )
            self.writer.start()
            self.check_writer()
        else:
            self.writer = None

        # tracker object finds LEDs in frames
        self.tracker = Tracker()

        # chatter handles serial communication
        self.chatter = Chatter(serial)

        # GUI other than Qt currently not available. We apologize for any
        # inconvinience. << NOT TRUE ANYMORE! HOORAY!
#        self.gui = GUI( self, gui, "Spotter", size )

        # histogram instance required to do... nothing for now?
#        self.hist = utils.HSVHist()


    def update( self ):
        # Get new frame
        if self.grabber.grab_next():
            self.newest_frame = self.grabber.framebuffer.pop()

            # Check if writer process is still alive
            # Otherwise might lose data without knowing!
            # Copy numpy array, otherwise queue references same object
            if not self.writer == None and self.check_writer():
                self.write_queue.put( self.newest_frame.copy() )
                time.sleep( 0.001 ) # required, or may crash?

            # Find and update position of tracked object
            self.hsv_frame = cv2.cvtColor( self.newest_frame, cv2.COLOR_BGR2HSV )
            self.tracker.trackLeds( self.hsv_frame, method = 'hsv_thresh' )

            # Calculate positions send to Serial if object linked to serial
            # if no point detected (guessed_pos == None)
            # output will be zeroed
            for o in self.tracker.oois:
                o.updatePosition()
                if o.analog_pos and self.chatter: # and o.guessed_pos
                    self.chatter.send_point2analog(o.guessed_pos)

            # run collision detections
            for r in self.tracker.rois:
                for o in self.tracker.oois:
                    collision = r.collision_check(o.guessed_pos)
                    if r.label == 'Trigger' and o.label == 'Subject':
                        if collision:
                            self.chatter.send_trigger_state(41, 0x07)
                        else:
                            self.chatter.send_trigger_state(41, 0x00)


                    if r.label == 'Sync_trig' and o.label == 'Sync':
                        if collision:
                            self.chatter.send_trigger_state(40, 0x07)
                        else:
                            self.chatter.send_trigger_state(40, 0x00)
#                        print collision
#                    if o.digital_collision_out and self.chatter:
#                        self.chatter.send_collision2digital(o.digital_ports)

            # freezes frame being shown, but not frame being processed/written
#            self.gui.update( self.newest_frame )

        else:
            print 'No new frame returned!!! What does it mean??? We are going to die! Eventually!!!'

        total_elapsed = ( time.clock() - self.grabber.ts_last_frame ) * 1000
        t = int( 1000/self.grabber.fps - total_elapsed ) - 1
        if t <= 0:
            log.info('Missed next frame by: ' + str( t * -1. ) + ' ms')
            t = 1

    def check_writer( self ):
        """ True if alive, otherwise causes script to terminate. """
        if not self.writer.is_alive():
            print('Writing to disk failed.')
            log.error('Writing to disk failed.')
            self.exitMain()
        else:
            return True


    def exitMain( self ):
        """ Graceful exit. Ha. Ha. Ha. Bottle of root beer anyone? """

        # closing grabber is straight forward, will release capture object
        if self.grabber:
            self.grabber.close()

        # tracker no longer has serial handle to take care of
        if self.tracker:
            self.tracker.close()

        # chatter HAS to close serial connection or all hell breaks loose!
        if self.chatter:
            self.chatter.close()

        # writer is a bit trickier, may have frames left to stow away
        if not self.writer == None and self.writer.is_alive():
            self.write_queue.put( 'terminate' )
            # gives the child process one second to finish up, will be
            # terminated otherwise
            self.writer.join( 1 )
            if self.writer.is_alive():
                main.writer.terminate()

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
            if not main.writer == None and main.check_writer():
                main.write_queue.put( main.newest_frame.copy() )
                time.sleep( 0.001 ) # required, or may crash?

            # Find and update position of tracked object
            main.hsv_frame = cv2.cvtColor( main.newest_frame, cv2.COLOR_BGR2HSV )
            main.tracker.trackLeds( main.hsv_frame, method = 'hsv_thresh' )
#            main.Object.updatePosition()

            # send position of tracked object to serial port
#            if not main.Object.guessed_pos is None:
#                main.tracker.chatter.send( main.Object.guessed_pos )

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
