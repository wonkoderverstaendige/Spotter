# -*- coding: utf-8 -*-
"""
Created on Mon Jul 09 00:07:34 2012
@author: <Ronny Eichler> ronny.eichler@gmail.com

Handles grabbing successive frames from capture object and returns current
frames of requested type.
Capture object must be closed with Grabber.close() or script will not terminate!

Usage:
    grabber.py --source SRC [--dims DIMS] [options]
    grabber.py -h | --help

Options:
    -h --help        Show this screen
    -f --fps FPS     Fps for camera and video
    -s --source SRC  Source, path to file or integer device ID [default: 0]
    -S --Serial      Serial port to uC [default: None]
    -d --dims DIMS   Frame size [default: 320x200]
    -D --DEBUG       Verbose debug output
"""

import cv2
import logging
import time
import os
import sys
from collections import deque
from lib.docopt import docopt

DEBUG = True

class Frame:
    """Container class for frames. Holds additional meta data aside from the
    actual image information."""

    def __init__(self, index, img, source_type, timestamp):
        self.index = index
        self.img = img
        self.source_type = source_type
        self.timestamp = timestamp


class Grabber:
    capture = None          # Capture object to frame source
    fourcc = None           # Source frame coding

    fps_init = None         # Current source fps, may differ from CLI parameter
    fps = None

    size_init = None
    size = None

    frame_count = -1         # Frames received so far

    ts_last_frame = None    # Timestamp of most recent frame
    ts_first = None         # Timestamp of first frame, BUGGY!
    source_type = None      # File, stream, device; changes behavior of GUI
#    framebuffer = deque( maxlen=256 )

    def __init__(self, source, fps=0, size=(0, 0)):
        """
        Frame Grabber

        :param source: Integer DeviceID or path to source file
        :param fps: Float, frames per second of replay/capture
        :param size: list of floats (width, height)
        """
        # Integer: Device ID. Else, grabber will use as path and look for file

        self.log = logging.getLogger(__name__)
        self.log.info('Open CV %s', cv2.__version__)

        if source is not None:
            try:
                source = int(source)
                self.source_type = 'device'
            except ValueError:
                if os.path.isfile(source):
                    self.source_type = 'file'
                else:
                    self.log.info('Source file %s does not exist.', source)
                    source = None

        if source:
            # Creating capture handle object
            self.log.debug('Attempting to open %s "%s" as capture... ', self.source_type, source)
            try:
                self.capture = cv2.VideoCapture(source)
            except Exception as error:
                self.log.exception(error)
            finally:
                self.log.debug('Capture %s returned', str(self.capture))

            # Proper fps values only important if lower than what camera can provide,
            # or for video files, which are limited by CPU speed/1ms min of waitKey()
            try:
                self.fps_init = float(29.97 if not fps else fps)
            except ValueError:
                self.fps_init = 29.97

            # size given, to compare with size of first frame
            self.size_init = size

            # if source_type is 'device': Otherwise does nothing
            if self.source_type != 'file':
                self.capture.set(cv2.cv.CV_CAP_PROP_FPS, float(self.fps_init))
                self.capture.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, float(self.size_init[0]))
                self.capture.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, float(self.size_init[1]))

            # Grab first frame, don't append to framebuffer
            # TODO: That's nasty for video file, losing first frame! I.e. transcoding
            self.grab_first()

    def grab_first(self):
        """ Grabs first frame to get source image parameters. """
        # Possibly eternal loop until first frame returned
        for n in xrange(100):
            rv, img = self.capture.read()
            if rv:
                print "Tries before getting first frame:", n+1
                time.sleep(0.02)
                break
        else:
            print "Frame retrieval failed!"
            return None

        # get source parameters
        self.size = tuple([int(self.capture.get(3)), int(self.capture.get(4))])
        self.fps = self.capture.get(5)
        self.fourcc = self.capture.get(6)

        if DEBUG:
            print 'First frame grab - fps: ' + str(self.fps) + '; size: ' + str(self.size) + ';'

    def grab_next(self):
        """Grabs a new frame from the source and appends it to framebuffer."""
        if self.capture:
            rv, img = self.capture.read()
            if rv:
                self.ts_last_frame = time.time()
                # time of first 'real' frame
                if self.frame_count == 0:
                    self.ts_first = time.time()
                self.frame_count += 1

                return Frame(index=self.frame_count,
                             img=img,
                             source_type=self.source_type,
                             timestamp=time.time())
    #            self.framebuffer.appendleft(frame)

    def close(self):
        self.log.debug('Closing grabber')
        if self.capture:
            self.capture.release()


##########################
if __name__ == "__main__":
    pass
    ## Parsing arguments
    #arg_dict = docopt(__doc__, version=None)
    #DEBUG = arg_dict['--DEBUG']
    #if DEBUG:
    #    print(arg_dict)
    #
    ## Width and height; WWWxHHH to tuple of ints; cv2 set requires floats
    #size = (0, 0) if not arg_dict['--dims'] else tuple(arg_dict['--dims'].split('x'))
    #
    ## instantiate main class
    #main = Grabber(source=arg_dict['--source'],
    #               fps=arg_dict['--fps'],
    #               size=size)
    #
    ## Requirements for main loop
    #if DEBUG: print 'fps: ' + str(main.fps)
    #if main.fps:
    #    t = int(1000/main.fps)
    #else:
    #    t = 1
    #
    ## Main loop
    #key = 0
    #while True:
    #    if not main.grab_next() or (key % 0x100 == 27):
    #        main.close()
    #        cv2.destroyAllWindows()
    #        sys.exit(0)
    #    else:
    #        cv2.imshow('Grabber', main.framebuffer.pop())
    #        key = cv2.waitKey(t)
