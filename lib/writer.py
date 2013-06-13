# -*- coding: utf-8 -*-
"""
Created on Mon Jul 09 00:29:00 2012
@author: <Ronny Eichler> ronny.eichler@gmail.com

Wrapper for VideoWriter, can either work as seperate thread fed by frame buffer
or being provided one frame a time.

Usage:
    writer.py --outfile DST [options]
    writer.py -h | --help

Options:
    -h --help         Show this screen
    -c --codec CODEC  FOURCC letter code [default: IYUV]
    -f --fps FPS      Fps for camera and video
    -o --outfile DST  Path to video out file [default: None]
    -s --source SRC   Source, path to file or integer device ID [default: 0]
    -d --dims DIMS    Frame size [default: 320x200]
    -H --Headless     No Interface
    -D --DEBUG        Verbose debug output
"""

# TODO:
#    - check if codec on list of known working ones.
#    - if destination exists, offer file name change

import cv2
import cv2.cv as cv
import os
import sys
import time
import logging

#project libraries
sys.path.append('./lib')
import utilities as utils

#command line handling
sys.path.append('./lib/docopt')
from docopt import docopt

DEBUG = True
OVERWRITE = False
 #seconds till writer process times out after having received last alive packet
TIMEOUT = 10

class Writer:
    codecs = ( ('XVID'), ('DIVX'), ('IYUV') )
    destination = None
    writer = None
    logger = None
    size = None
    alive = True
    recording = False
    ts_last = time.clock()

    def __init__( self, fps, size, queue, pipe, codec='XVID' ):
        self.queue = queue
        self.pipe = pipe

        self.fps = fps
        # Video Writer takes tuple of INTS, not FLOATS!
        self.size = tuple(int(i) for i in size)

        # Explode the string into characters as required by archaic VideoWriter
        self.codec = codec
        self.cc = list(codec)
        self.printflush(codec)

        # Only important if lower than what camera can provide, or for videos
        try:
            fps = float( 29.97 if not fps else fps )
        except ValueError:
            fps = 29.97

        self.loop()

    def start(self, dst=None):
        # check if output file exists
        dst = self.time_string() + '.avi'
        destination = utils.dst_file_name(dst)
        if os.path.isfile(destination) and not OVERWRITE:
            self.printflush('Destination file exists, stopped.', True)
            return
        self.destination = destination
        self.printflush(self.destination)

        # VideoWriter object
        self.printflush('Writer Init - fps: ' + str(self.fps) + '; size: ' + str(self.size) + ';')

        self.writer = cv2.VideoWriter(
                        self.destination,
                        cv.CV_FOURCC(self.cc[0], self.cc[1], self.cc[2], self.cc[3]),
                        self.fps,
                        self.size, 1 )

        self.logger = logging.getLogger(destination)
        loghandler = logging.FileHandler(''.join([destination, '.log']))#logging.StreamHandler()
#        formatter = logging.Formatter('%(asctime)-15s %(levelname)-8s %(message)s') #%(name)-5s %(levelname)-8s IP: %(ip)-15s User: %(user)-8s %(message)s
#        loghandler.setFormatter(formatter)
        self.logger.addHandler(loghandler)
        self.logger.setLevel(logging.INFO)

        self.printflush(str(self.writer) + ' destination: ' + self.destination)
        self.recording = True

    def printflush(self, string, override = False):
        """ Prints a string and flushes the buffered output, so that prints
        in this sub-process show up in the parent process terminal output."""
        if DEBUG or override:
            print string
            sys.stdout.flush()

    def stop(self):
#        self.printflush("STOP METHOD")
        self.destination = None
        self.logger = None

        if self.recording:
            self.close()
        self.recording = False

    def write(self, item):
        frame = item[0]
        messages = item[1]

        for m in messages:
            self.logger.info(m)
        self.writer.write(frame.img)

    def loop(self):
        """
        Writes frames from the queue. If alive flag set to
        false, deletes capture object to allow proper exit
        """
        while 42 and self.alive:
            # Process should terminate if not being talked to for a while
            if time.clock() - self.ts_last > TIMEOUT:
                self.printflush("Terminating unattended Writer process!")
                self.close()
                sys.exit(0)

            try:
                new_pipe_msg = self.pipe.poll()
            except:
                new_pipe_msg = False

            if new_pipe_msg:
                # any command in the pipe will keep the process alive
                cmd = self.pipe.recv()
                self.ts_last = time.clock()
                if cmd == 'terminate':
                    self.printflush('Writer received termination signal')
                    # don't close yet, first empty buffer!
                    self.alive = False
                elif cmd == 'stop':
                    self.printflush('Writer received stop signal')
                    self.stop()
                elif cmd == 'start':
                    self.printflush('Writer received start signal')
                    self.start()
                elif cmd == 'alive':
                    pass

            while not self.queue.empty():
                item = self.queue.get()
#                self.printflush("removed item")
                if self.writer is not None and self.recording:
                    self.write(item)

            # refresh time to keep CPU utilization down
            time.sleep(0.01)
        # Close writer upon termination signal
        if not self.alive:
            self.close()

    def time_string(self):
        return time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
#        return '_'.join(map(str, time.localtime())[0:6])

    def close(self):
        print 'Closing Writer'
        if self.writer is not None:
            del(self.writer)
            self.writer = None



#############################################################
if __name__ == '__main__':                                  #
#############################################################

    # Parsing CLI arguments
    ARGDICT = docopt( __doc__, version=None )
    DEBUG = ARGDICT['--DEBUG']
    if DEBUG: print( ARGDICT )

    # Width and height; WWWxHHH to tuple of floats; cv2 set requires floats
    size = (0, 0) if not ARGDICT['--dims'] else tuple( ARGDICT['--dims'].split('x') )

    # Codec should be four character code (FOURCC)
    codec = ARGDICT['--codec'].upper()
    if codec:
        if not len(codec) == 4:
            print 'Codec must be four letter code. E.g. "XVID".'
            sys.exit(0)
        else:
            if DEBUG: print 'Using codec FOURCC ' + codec

    # Run in command line without user interface to slow things down
    GUI = not ARGDICT['--Headless']

    # Instantiate frame source to get something to write
    import grabber
    frame_source = grabber.Grabber( ARGDICT['--source'] )
    fps = 30.0 if not ARGDICT['--fps'] else frame_source.fps

    if DEBUG: print str( fps ) + ':' + str( size )

    # Instantiate main video writer class
    main = Writer( destination = ARGDICT['--outfile'],
                   fps = fps,
                   size = frame_source.size,
                   codec = codec )

    # Main loop till EOF or Escape key pressed
    key = 0
    while frame_source.grab_next() and not ( key % 100 == 27 ):
        if GUI: cv2.imshow( 'Writer', frame_source.framebuffer[0] )
        main.write( frame_source.framebuffer.pop() )
        if GUI: key = cv2.waitKey(1)

    # Exiting gracefully
    main.close()
    frame_source.close()
    if DEBUG: print 'Wrote ' + str( frame_source.framecount ) + ' frames.'
    sys.exit(0)