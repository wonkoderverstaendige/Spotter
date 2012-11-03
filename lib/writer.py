# -*- coding: utf-8 -*-
"""
Created on Mon Jul 09 00:29:00 2012
@author: <Ronny Eichler> ronny.eichler@gmail.com

Wrapper for VideoWriter, can either work as seperate thread fed by frame buffer
or being provided one frame a time.

Usage:
    writer.py --outfile DST --dims DIMS --fps FPS [--source SRC --codec CODEC -DH]
    writer.py -h | --help

Options:
    -h --help         Show this screen
    -c --codec CODEC  FOURCC letter code [default: XVID]
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

import cv, cv2, os, sys #time,
sys.path.append('./lib')
import utils
from docopt import docopt

DEBUG = True

class Writer:
    codecs = ( ('XVID'), ('DIVX'), ('IYUV') )
    destination = None
    writer = None
    size = None
    alive = True

    def __init__( self, dst, fps, size, codec='DIVX' ):

        # check if output file exists
        self.destination = utils.dst_file_name( dst )
        if os.path.isfile( self.destination ):
            print 'Destination file exists. Exiting.'
            sys.exit(0)

        # Video Writer takes tuple of INTS, not FLOATS!
        self.size = tuple( int(i) for i in size )

        # Explode the string into characters as required by archaic VideoWriter
        cc = list( codec )

        # Proper fps values only important if lower than what camera can provide,
        # or for video files, which are limited by CPU speed and 1ms min of waitKey()
        try:
            fps = float( 29.97 if not fps else fps )
        except ValueError:
            fps = 29.97

        # VideoWriter object
        if DEBUG: print 'Writer Init - fps: ' + str( fps ) + '; size: ' + str( size ) + ';'
        self.writer = cv2.VideoWriter(
                        self.destination,
                        cv.CV_FOURCC( cc[0], cc[1], cc[2], cc[3] ),
                        fps,
                        self.size, 1 )
        if DEBUG: print str( self.writer ) + ' destination: ' + self.destination


    def write( self, frame ):
        self.writer.write( frame )


    def write_thread( self, fb, ev ):
        """ When woken, writes frames from framebuffer until only nleaves number of
        frames left. If _alive flag set to false, flushes all remaining frames from
        buffer and deletes capture object to allow proper exit"""

        minimum_frames = 1
        mini_fb = list()

        while self.alive or len( fb ) > 0:
            # waiting for wake up signal from main loop
            ev.wait()

            # main loop shutting down
            if not self.alive:
                if DEBUG: print 'Flushing buffer to file...'
                minimum_frames = 0

            # flush frames to file. Writing to disk may take time and block
            # parent thread, fb content moved to temporary list and then written.
            mini_fb = list( fb.pop() for i in range( len(fb) - minimum_frames ) )
            while len(mini_fb):
                self.writer.write( mini_fb.pop() )

        #if not self.alive, close:
        self.close()


    def close( self ):
        print 'Closing Writer'
        del( self.writer )


if __name__ == '__main__':

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
    frame_source.grab_first()
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
        if GUI: cv2.imshow( 'Main', frame_source.framebuffer[0] )
        main.write( frame_source.framebuffer.pop() )
        if GUI: key = cv2.waitKey(1)

    # Exiting gracefully
    main.close()
    frame_source.close()
    if DEBUG: print 'Wrote ' + str( frame_source.framecount ) + ' frames.'
    sys.exit(0)