# -*- coding: utf-8 -*-
"""
Created on Mon Jul 09 00:07:34 2012
@author: <Ronny Eichler> ronny.eichler@gmail.com

Handles grabbing successive frames from source object and returns current
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

import logging
from framesources import CameraCapture, FileCapture, SocketCapture


class Grabber:
    fresh = True

    def __init__(self, *args, **kwargs):
        """
        Frame Grabber init. Also used to reset it when a new source is selected.

        :param source: Integer DeviceID or path to source file/URL
        :param fps: Float, frames per second of replay/source
        :param size: list of floats (width, height)
        """
        if self.fresh:
            self.log = logging.getLogger(__name__)
            self.available_sources_types = self.detect_src_types()
            self.fresh = False

        self.source = None
        self.source_type = None
        self.current_frame = None

        # Autostart with given source, else wait for external call to start
        if 'source' in kwargs:
            self.start(*args, **kwargs)

    def start(self, source, source_type, *args, **kwargs):
        """Initialize a source/capture with given type, if type is available.
        :param source: Path/device id for source.
        :param source_type: String of source type descriptor [camera, file socket]
        :param args:
        :param kwargs:
        """
        # If source object already exists, close it
        if self.source:
            self.close()

        try:
            self.log.debug('Starting with source %s', str(source))
            source = self.available_sources_types[source_type](source, *args, **kwargs)
            if source.capture is not None:
                self.source = source
                self.source_type = source_type
                return True
        except KeyError:
            self.log.error('Unsupported source type: %s', str(source_type).lower())

    def grab(self, *args, **kwargs):
        """Grabs a frame from the source."""
        if self.source is not None:
            return self.source.grab(*args, **kwargs)

    def next(self):
        """Return next frame in sequence."""
        if self.source is not None:
            return self.source.next()

    def rewind(self):
        """Jump to beginning of video sequence. Only supported by indexed sources."""
        if self.source is not None and self.source_indexed:
            self.source.rewind()

    def fast_forward(self):
        """Jump to end of video sequence. Only supported by indexed sources."""
        if self.source is not None and self.source_indexed:
            self.source.fast_forward()

    def seek(self, *args, **kwargs):
        """Set source to a specific position, either in time or in frame index. """
        if self.source is not None and self.source_indexed:
            self.source.seek(*args, **kwargs)

    @property
    def source_fps(self):
        return self.source.fps if self.source is not None else None

    @property
    def source_size(self):
        return self.source.size if self.source is not None else None

    @property
    def source_indexed(self):
        return self.source.indexed if self.source is not None else None

    @property
    def source_index(self):
        return self.source.index if self.source is not None else 0

    @property
    def source_num_frames(self):
        return self.source.num_frames if self.source is not None else 0

    def reset(self):
        """Ready for new source by resetting state variables and removing references."""
        self.log.debug('Resetting grabber, releasing capture')
        self.source.close()
        self.__init__()

    def close(self):
        """Close source."""
        self.log.debug('Closing grabber')
        if self.source is not None:
            self.source.close()
        self.source = None

    def detect_src_types(self):
        """Check which types of frame sources are available.

        In particular, OpenCV is expected to be available. ZMQ may or may not be there.
        """
        source_types = dict()

        # OpenCV there?
        try:
            import cv2
        except ImportError:
            cv2 = None
            self.log.info('OpenCV not imported.')
        else:
            self.log.info('Open CV: %s', cv2.__version__)
            source_types['camera'] = CameraCapture
            source_types['file'] = FileCapture

        # ZMQ there?
        try:
            import zmq
        except ImportError:
            zmq = None
            self.log.info('ZMQ not imported.')
        else:
            self.log.info('ZMQ: %s', zmq.zmq_version())
            source_types['socket'] = SocketCapture

        return source_types


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
