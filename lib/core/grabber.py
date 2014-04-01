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
import struct
import numpy as np
from collections import deque
from lib.docopt import docopt

try:
    import zmq
except ImportError:
    zmq = None

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
            self.tickstamp = int((1000 * cv2.getTickCount()) / cv2.getTickFrequency())
        time_text = time.strftime("%d-%b-%y %H:%M:%S", time.localtime(self.timestamp))
        ms = "{0:03d}".format(int((self.timestamp - int(self.timestamp)) * 1000))
        self.time_text = ".".join([time_text, ms])

        # Add timestamp to image if from a live source
        if self.source_type == 'device':
            cv2.putText(img=self.img, text=self.time_text,
                        org=(3, 12), fontFace=cv2.FONT_HERSHEY_PLAIN, fontScale=0.8,
                        color=(255, 255, 255), thickness=1, lineType=cv2.CV_AA)

    @property
    def width(self):
        return self.img.shape[0]

    @property
    def height(self):
        return self.img.shape[1]

    @property
    def shape(self):
        return self.width, self.height


class Grabber:

    ts_last_frame = None  # Timestamp of most recent frame
    ts_first = None  # Timestamp of first frame, BUGGY!
    #    buffer = deque(maxlen=256)
    log = None

    def __init__(self, *args, **kwargs):
        """
        Frame Grabber

        :param source: Integer DeviceID or path to source file/URL
        :param fps: Float, frames per second of replay/capture
        :param size: list of floats (width, height)
        """
        if self.log is None:
            self.log = logging.getLogger(__name__)
            self.log.info('Open CV %s', cv2.__version__)
            if zmq is None:
                self.log.info('ZMQ not imported.')
            else:
                self.log.info(zmq.zmq_version())

        self.fourcc = kwargs['fourcc'] if 'fourcc' in kwargs else None

        self.capture = None
        self.capture_type = None

        self.source = None
        self.source_type = None

        self.size = None
        self.size_init = None

        self.fps = None
        self.fps_init = None

        self.frame_count = 0
        self._frame_ptr = None

        self.current_frame = None
        self.repeat = False

        if 'source' in kwargs:
            self.start(*args, **kwargs)

    def start(self, source, source_type=None, fps=None, size=None, *args, **kwargs):
        # TODO: Handling of frame size|self.size_init and fps|self.fps_init is very awkward.
        # TODO: Specify source type as argument, less type checking

        if source is None:
            return

        # if capture object already exists, must be closed first to be sure no
        # hanging files/sockets are floating around...
        if self.capture:
            self.close()

        # Figure out what type source was requested
        try:
            self.open_device(int(source))
        except ValueError:
            # not a device number... maybe a file?
            if os.path.isfile(source):
                self.open_file(source)
            else:
                self.log.debug('Source %s not an existing file. Maybe socket?', source)
                if zmq is not None:
                    self.open_socket(source)

    def open_device(self, source, *args, **kwargs):
        self.log.debug('Attempting to open device "%s" as capture... ', source)
        self.open_opencv(source, 'device', *args, **kwargs)
        if self.fps_init is not None:
            self.log.debug("Setting fps of capture: {0}".format(float(self.fps_init)))
            self.capture.set(cv2.cv.CV_CAP_PROP_FPS, float(self.fps_init))
        if self.size_init is not None:
            self.log.debug("Setting frame size of capture: {0[0]}x{0[1]}".format(self.size_init))
            self.width = float(self.size_init[0])
            self.height = float(self.size_init[1])

    def open_file(self, source, *args, **kwargs):
        self.log.debug('Attempting to open file "%s" as capture... ', source)
        self.open_opencv(source, 'file', *args, **kwargs)

    def open_opencv(self, source, source_type, *args, **kwargs):
        """Source handled by opencv.
        """
        try:
            self.capture = cv2.VideoCapture(source)
        except Exception as error:
            self.log.exception(error)
            return

        assert self.capture.isOpened()
        self.log.debug('Capture %s returned', str(self.capture))
        self.source = source
        self.source_type = source_type
        self.capture_type = 'opencv'

        # Proper fps values only important if lower than what camera can provide or for video files
        if 'fps' in kwargs:
            self.fps_init = kwargs['fps']
        try:
            self.fps_init = float(self.fps_init if self.fps_init else 30.0)
        except (ValueError, TypeError):
            self.fps_init = 30.0

        # initial size given, can be used to compare with size of first frame
        self.size_init = kwargs['size'] if 'size' in kwargs else None

        # Show caller everything worked out
        return self.capture

    def open_socket(self, source):
        context = zmq.Context()
        self.log.info("Connecting to frame server...")
        self.capture = context.socket(zmq.REQ)
        self.capture.connect("tcp://localhost:5555")
        self.source_type = 'socket'
        self.capture_type = 'zmq'
        self.log.debug('Opened ZMQ socket')

    def grab_opencv(self, index=None):
        """Grab a frame from an opencv-source, either video file or a camera."""
        # Only really loops for first frame
        n_tries = 10 if self.frame_count < 1 else 1
        for trial in xrange(2, n_tries + 2):
            rv, img = self.capture.read()
            if rv:
                self.frame_count += 1
                break
            time.sleep(0.01)
        else:
            self.log.error("Frame retrieval failed after %d" + (' tries' if n_tries - 1 else ' try'), n_tries)
            self.close()
            return None

        # First frame?
        if self.frame_count == 1:
            self.size = tuple([int(self.capture.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)),
                               int(self.capture.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))])
            self.fps = self.capture.get(cv2.cv.CV_CAP_PROP_FPS)
            # There seems to be an issue with V4L where above property always returns a NaN
            try:
                int(self.fps)
            except ValueError:
                self.fps = 30.0
            self.fourcc = self.capture.get(cv2.cv.CV_CAP_PROP_FOURCC)
            self.log.info('First frame: %.2f fps, %dx%d, %s after %d' + (' tries' if trial - 2 else ' try'),
                          self.fps, self.size[0], self.size[1], str(self.fourcc), trial - 1)

        # TODO: Should use self.index, not self.frame_count
        return Frame(self.frame_count, img, self.source_type)

    def grab_zmq(self, index=None):
        """Grab a frame from a ZMQ socket.

        If index is given, request a specific frame, rather than any new one.
        """
        try:
            # Send request for new frame (any message will do here)
            if index is None:
                self.capture.send(__name__, zmq.NOBLOCK)
            else:
                self.capture.send(index, zmq.NOBLOCK)  # request specific frame number

            # Receive frame
            img = np.fromstring(self.capture.recv(), np.uint8)
            shape = (600, 800, 3)  # (960, 1280, 3)
            img = np.reshape(img, shape)
            self.frame_count += 1
            if index is not None:
                self._frame_ptr = index
        except zmq.ZMQError:
            return None
        except ValueError:
            return None

        # First frame?
        if self.frame_count == 1:
            self.size = img.shape
            self.fps = 60.0
            self.fourcc = None
            self.log.info('First ZMQ frame: %s fps, %dx%d, %s',
                          str(self.fps), self.size[0], self.size[1], str(self.fourcc))

        # TODO: Should use self.index, not self.frame_count
        return Frame(self.frame_count, img, self.source_type)

    def grab(self, index=0):
        """Grabs a new frame from the source. Returns Frame instance with
        image and meta data."""
        if self.capture is None:
            return

        #self.log.debug("Grabbing frame")
        if self.capture_type == "opencv":
            return self.grab_opencv()

        if self.capture_type == "zmq":
            return self.grab_zmq()

    def next(self):
        """Return next frame in sequence.
        """
        return self.grab(self.index + 1)

    def rewind(self):
        """Jump to beginning of video sequence. Only supported by indexed sources.
        """
        self.log.debug('Rewinding to first frame of video source')
        self.index = 0

    def fast_forward(self):
        """Jump to end of video sequence. Only supported by indexed sources.
        """
        self.log.debug('Jumping to last frame of video source')
        self.index = self.num_frames - 1

    def __getitem__(self, index):
        """Return a specific frame in the frame sequence. Only works if the source
        supports indexing (e.g. video file with intact index).
        """
        # TODO: Buffering, handling
        return self.grab(index)

    def get_capture_properties(self):
        if not self.capture_type == "opencv":
            return
        #base_string = 'CV_CAP_PROP_'
        properties = ['POS_MSEC', 'POS_FRAMES', 'POS_AVI_RATIO', 'FRAME_WIDTH', 'FRAME_HEIGHT',
                      'FPS', 'FOURCC', 'FRAME_COUNT', 'FORMAT', 'MODE', 'BRIGHTNESS', 'CONTRAST',
                      'SATURATION', 'HUE', 'GAIN', 'EXPOSURE', 'CONVERT_RGB', 'WHITE_BALANCE']
        if self.capture is not None:
            self.log.info("++++++++++++++++++++++")
            for idx, prop in enumerate(properties):
                self.log.info(prop + ": %s", str(self.capture.get(idx)))
            self.log.info("++++++++++++++++++++++")
            print struct.unpack('4c', struct.pack('f', self.capture.get(6)))

    def set_capture_properties(self):
        pass

    @property
    def num_frames(self):
        """Total number of frames in video. Only works for indexed sources.
        """
        if self.capture is not None:
            return int(self.capture.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))

    @property
    def index(self):
        """Position in video in absolute number of frames.

        Only available for indexed sources?
        """
        if self.capture is not None:
            return int(self.capture.get(cv2.cv.CV_CAP_PROP_POS_FRAMES))

    @index.setter
    def index(self, index):
        """Move position pointer in video to position in absolute number of frames. Only works for
        indexed sources.
        """
        index = int(index)
        if index < 0:
            index = 0
        if index >= self.num_frames:
            if self.repeat:
                index = 0
            else:
                index = self.num_frames - 1

        # if the current pointer is not the same as requested, update and seek in video file
        # (not sure about performance of the seeking, I'll avoid doing it all the time)
        # NB! Potential death trap thanks to float<>int conversions!??
        if self.capture is not None:
            if self.index != index:
                self.capture.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, float(index))

    @property
    def pos_time(self):
        """Position in video in milliseconds. Unreliable if frame rate set during encoding not the
        same as frame rate of acquisition. Requires external synchronization markers.
        """
        if self.capture is not None:
            return self.capture.get(cv2.cv.CV_CAP_PROP_POS_MSEC)

    @property
    def width(self):
        """ Width of the _source_ frames. As frames may be rescaled, this can differ from the
        properties of the frames emitted by the grabber.
        """
        if self.capture is not None:
            return self.capture.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)

    @width.setter
    def width(self, width):
        """Set capture property 'width' of capture object, if available.

        :param width:float
        """
        if self.capture is None:
            return

        if self.capture_type == 'opencv':
            self.capture.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, width)
        elif self.capture_type == 'zmq':
            # TODO: Send command to frame server
            pass

    @property
    def height(self):
        """ Height of the _source_ frames. As frames may be rescaled, this can differ from the
        properties of the frames emitted by the grabber.
        """
        if self.capture is not None:
            return self.capture.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)

    @height.setter
    def height(self, height):
        """Set capture property 'height' of capture object, if available.

        :param height:float
        """
        if self.capture is None:
            return
        if self.capture_type == 'opencv':
            self.capture.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, height)
        elif self.capture_type == 'zmq':
            # TODO: Send command to frame server
            pass

    def close(self):
        """Close and release frame source/capture object."""
        self.log.debug('Resetting grabber, releasing capture')
        if self.capture:
            try:
                self.capture.release()
                self.log.DEBUG("Capture %s released", str(self.capture))
            except BaseException, error:
                self.log.error("Capture %s release exception: [%s]", self.capture, error)
        # reset all other stuff
        self.__init__()


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
