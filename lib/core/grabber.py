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
    """Container class for frames. Holds additional metadata aside from the
    actual image information."""

    def __init__(self, index, img, source_type, timestamp=None):
        self.index = index
        self.img = img
        self.source_type = source_type
        if timestamp is None:
            self.timestamp = time.time()
        time_text = time.strftime("%d-%b-%y %H:%M:%S", time.localtime(self.timestamp))
        ms = "{0:03d}".format(int((self.timestamp-int(self.timestamp))*1000))
        self.time_text = ".".join([time_text, ms])

        # Add timestamp to image if from a live source
        if self.source_type == 'device':
            cv2.putText(img=self.img, text=self.time_text,
                        org=(3, 12), fontFace=cv2.FONT_HERSHEY_PLAIN, fontScale=0.8,
                        color=(255, 255, 255), thickness=1, lineType=cv2.CV_AA)


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

    def __init__(self, *args, **kwargs):
        """
        Frame Grabber

        :param source: Integer DeviceID or path to source file
        :param fps: Float, frames per second of replay/capture
        :param size: list of floats (width, height)
        """

        self.log = logging.getLogger(__name__)
        self.log.info('Open CV %s', cv2.__version__)

        if 'source' in kwargs:
            self.start(*args, **kwargs)

    def start(self, source, *args, **kwargs):
        # TODO: Handling of frame size|self.size_init and fps|self.fps_init is very awkward.

        if self.capture:
            self.close()

        if source is not None:
            try:
                source = int(source)
                self.source_type = 'device'
            except ValueError:
                if os.path.isfile(source):
                    self.source_type = 'file'
                else:
                    self.log.info('Source file %s does not exist.', source)
                    return

            # Creating capture handle object
            self.log.debug('Attempting to open %s "%s" as capture... ', self.source_type, source)
            try:
                self.capture = cv2.VideoCapture(source)
            except Exception as error:
                self.log.exception(error)
            finally:
                self.log.debug('Capture %s returned', str(self.capture))

            # Proper fps values only important if lower than what camera can provide or for video files
            if 'fps' in kwargs:
                self.fps_init = kwargs['fps']

            try:
                self.fps_init = float(self.fps_init if self.fps_init else 30.0)
            except (ValueError, TypeError):
                self.fps_init = 30.0

            # size given, to compare with size of first frame
            self.size_init = kwargs['size'] if 'size' in kwargs else None

            # if source_type is 'device': Otherwise does nothing
            if self.source_type == 'device':
                self.capture.set(cv2.cv.CV_CAP_PROP_FPS, float(self.fps_init))
                self.capture.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, float(self.size_init[0]))
                self.capture.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, float(self.size_init[1]))

    def grab(self):
        """Grabs a new frame from the source. Returns Frame instance with
        image and meta data."""
        if self.capture is None:
            return

        # Only really loops for first frame
        n_tries = 100 if self.frame_count < 1 else 1
        for trial in xrange(2, n_tries+2):
            rv, img = self.capture.read()
            if rv:
                self.frame_count += 1
                break
            time.sleep(0.01)
        else:
            self.log.error("Frame retrieval failed after %d" + (' tries' if n_tries-1 else ' try'), n_tries)
            return None

        # First frame?
        if self.frame_count == 1:
            self.size = tuple([int(self.capture.get(3)), int(self.capture.get(4))])
            self.fps = self.capture.get(5)
            self.fourcc = self.capture.get(6)
            self.log.info('First frame: %.2f fps, %dx%d, %s after %d'+(' tries' if trial-2 else ' try'),
                          self.fps, self.size[0], self.size[1], str(self.fourcc), trial-1)

        #self.log.debug('returning frame')
        return Frame(self.frame_count, img, self.source_type)

    def close(self):
        """Close and release frame source."""
        self.log.debug('Resetting grabber')
        self.size = self.fps = self.fourcc = None
        self.frame_count = 0
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
