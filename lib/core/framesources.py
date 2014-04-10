# -*- coding: utf-8 -*-
"""
Created on 4/10/14 12:32 AM 2013
@author: <'Ronny Eichler'> ronny.eichler@gmail.com


Collection of frame sources.
"""

import logging
import time
import cv2
from collections import deque


class Frame(object):
    """Container class for frames. Holds additional metadata aside from the
    actual image information."""

    def __init__(self, index, img, source_type, timestamp=None, tickstamp=None):
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
        return self.img.shape


class FrameSource(object):
    """General purpose class for frame sources."""
    def __init__(self, *args, **kwargs):
        self.source = None
        self.capture = None

        self.time_last_frame = None  # Timestamp of most recent frame
        self.time_first_frame = None  # Timestamp of first frame, BUGGY!
        self.tick_last_frame = None
        self.tick_first_frame = None

        self.indexed = False
        self.frame_count = 0

        self.buffer = None
        self.buffered = False

        self._size = None
        self.size_init = None

        self._fps = None
        self.fps_init = None

        self.frame_count = 0
        self._frame_ptr = None

        self._fourcc = None

    def open(self, *args, **kwargs):
        pass

    def first_frame(self):
        """Some housekeeping of properties when grabbing the first frame of a source."""
        pass

    def close(self):
        """Close and release frame source/capture object."""
        self.capture = None

    def next(self):
        """Return next frame in sequence."""

    def grab(self, index=None):
        """Grabs a new frame from the source. Returns Frame instance with
        image and meta data."""
        pass

    def seek(self, index=None, milliseconds=None):
        pass

    def fast_forward(self):
        pass

    def rewind(self):
        pass

    @property
    def index(self):
        return self._frame_ptr

    @property
    def fps(self):
        return self._fps

    @property
    def size(self):
        return self._size

    @property
    def num_frames(self):
        """Return number of total frames of video source. Not supported by non-indexed sources."""
        return None

    @property
    def fourcc(self):
        return self._fourcc

    def __getitem__(self, index):
        """Return a specific frame in the frame sequence. Only works if the source
        supports indexing (e.g. video file with intact index).
        """
        return self.grab(index)

    def capture_properties(self):
        pass

###############################################################################
#                                   CAMERA                                    #
###############################################################################
class CameraCapture(FrameSource):
    def __init__(self, source, *args, **kwargs):
        super(CameraCapture, self).__init__()
        self.log = logging.getLogger(__name__)
        self.log.debug('Attempting to open camera interface "%s"... ', source)

        try:
            self.capture = cv2.VideoCapture(int(source))
        except ValueError as error:
            self.log.exception(error)
            return

        assert self.capture.isOpened()

        self.log.debug('Camera capture %s returned', str(self.capture))
        self.source = source
        self.indexed = False
        self.buffered = False

        # Proper fps values only important if lower than what camera can provide
        if 'fps' in kwargs:
            self.fps_init = kwargs['fps']
        try:
            self.fps_init = float(self.fps_init if self.fps_init else 30.0)
        except (ValueError, TypeError):
            self.fps_init = 30.0
        if self.fps_init is not None:
            self.log.debug("Pretending to set camera fps: {0}".format(float(self.fps_init)))
            self.capture.set(cv2.cv.CV_CAP_PROP_FPS, float(self.fps_init))
            self._fps = self.fps_init

        # initial size given, can be used to compare with size of first frame
        self.size_init = kwargs['size'] if 'size' in kwargs else None
        if self.size_init is not None:
            self.log.debug("Setting frame size of camera capture: {0[0]}x{0[1]}".format(self.size_init))
            self.width = float(self.size_init[0])
            self.height = float(self.size_init[1])

    def grab(self, index=None):
        """Grabs a frame from a camera via OpenCV."""
        # First frame?
        if self.frame_count == 0:
            rv, img = self.first_frame()
        else:
            rv, img = self.capture.read()

        if not rv:
            return None

        frame = Frame(self.index, img, str(self))
        self.frame_count += 1
        return frame

    def first_frame(self):
        """Some housekeeping of properties when grabbing the first frame from the camera."""
        for trial in xrange(10):
            # GET A NEW FRAME!
            rv, img = self.capture.read()
            if rv:
                break
            time.sleep(0.01)
        else:
            self.log.error("Failed to retrieve first frame.")
            self.close()
            return False, None

        self.log.info('First frame: %.2f fps, %dx%d, %s', self.fps, self.width, self.height, str(self.fourcc))
        return rv, img

    def next(self):
        """Return next frame from the camera."""
        return self.grab()

    @property
    def fps(self):
        # TODO: WTF? cv2.cv.CV_CAP_PROP_FPS is not implemented for V4L2?!
        return self._fps

    @property
    def size(self):
        return tuple([int(self.width), int(self.height)])

    @property
    def width(self):
        """ Width of the _source_ frames. As frames may be rescaled, this can differ from the
        properties of the frames emitted by the grabber.
        :rtype : float
        """
        if self.capture is not None:
            return self.capture.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)

    @width.setter
    def width(self, width):
        """Set capture property 'width'. Support of resolutions depends on device.
        :param width:float
        """
        self.log.debug('Setting requested frame width to: %f' % width)
        self.capture.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, width)

    @property
    def height(self):
        """ Height of the _source_ frames. As frames may be rescaled, this can differ from the
        properties of the frames emitted by the grabber.
        :rtype : float
        """
        return self.capture.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)

    @height.setter
    def height(self, height):
        """Set capture property 'height'. Support for resolutions depends on device.
        :param height:float
        """
        self.log.debug('Set frame height to: %f' % height)
        self.capture.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, height)

    def rewind(self):
        """Not supported by cameras. For now."""
        self.log.debug('Rewinding to first frame of video source')
        self.index = 0

    def fast_forward(self):
        """Not supported by cameras. For more details see 'Time machine proposal IV'."""
        self.log.debug("Device can't fast forward.")
        pass

    @property
    def num_frames(self):
        """Not supported by cameras. No guaranteed return type."""
        return self.capture.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)

    @property
    def fourcc(self):
        # TODO: WTF? self.capture.get(cv2.cv.CV_CAP_PROP_FOURCC) not implemented for V4L2?
        return '????'

    @property
    def index(self):
        """Number of frames acquired so far."""
        if self.capture is not None:
            return self.frame_count

    @index.setter
    def index(self, idx):
        """Not supported for cameras. For now."""
        # TODO: Fancy feature: If recording, could try to open video file at position. However,
        # FFMPEG seems to write file index only after closing the writer?
        return

    @property
    def pos_time(self):
        """Position in video in milliseconds. Unreliable if frame rate set during encoding not the
        same as frame rate of acquisition. Requires external synchronization markers.

        May not be supported by cameras.
        """
        # TODO: I could try to give the elapsed time since capture was opened.
        if self.capture is not None:
            return self.capture.get(cv2.cv.CV_CAP_PROP_POS_MSEC)

    def close(self):
        self.log.debug('Closing %s', str(self))
        if self.capture:
            try:
                self.capture.release()
                self.log.DEBUG("Capture %s released", str(self.capture))
            except BaseException, error:
                self.log.error("Capture %s release exception: [%s]", self.capture, error)
                self.capture = None


###############################################################################
#                                   FILE                                      #
###############################################################################
class FileCapture(FrameSource):
    def __init__(self, filename, *args, **kwargs):
        super(FileCapture, self).__init__()
        self.log = logging.getLogger(__name__)
        self.log.debug('Attempting to open file "%s"... ', filename)

        try:
            self.capture = cv2.VideoCapture(filename)
        except ValueError as error:
            self.log.exception(error)
            return

        assert self.capture.isOpened()

        self.log.debug('File capture %s returned', str(self.capture))
        self.source = filename
        self.indexed = True
        self.buffered = True

        # initial FPS given
        if 'fps' in kwargs:
            self.fps_init = kwargs['fps']
        try:
            self.fps_init = float(self.fps_init if self.fps_init else 30.0)
        except (ValueError, TypeError):
            self.fps_init = 30.0

        # initial size given
        self.size_init = kwargs['size'] if 'size' in kwargs else None

    def grab(self, index=None):
        """Grabs a frame from a file via OpenCV."""
        if index is not None:
            self.index = index

        # First frame?
        if self.frame_count == 0:
            rv, img = self.first_frame()
        else:
            rv, img = self.capture.read()

        if not rv:
            return None

        frame = Frame(self.index, img, str(self))
        self.frame_count += 1
        return frame

    def first_frame(self):
        """Some housekeeping of properties when grabbing the first frame of the file."""
        for trial in xrange(10):
            # GET A NEW FRAME!
            rv, img = self.capture.read()
            if rv:
                break
            time.sleep(0.01)
        else:
            self.log.error("Failed to retrieve first frame.")
            self.close()
            return False, None

        self.log.info('First frame: %.2f fps, %dx%d, %s', self.fps, self.width, self.height, str(self.fourcc))
        return rv, img

    def next(self):
        """Return next frame in file."""
        return self.grab()

    @property
    def fps(self):
        return self.capture.get(cv2.cv.CV_CAP_PROP_FPS)

    @property
    def size(self):
        return tuple([int(self.width), int(self.height)])

    @property
    def width(self):
        """ Width of the _source_ frames. As frames may be rescaled, this can differ from the
        properties of the frames emitted by the grabber.
        :rtype : float
        """
        if self.capture is not None:
            return self.capture.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)

    @width.setter
    def width(self, width):
        """Not available for video files."""
        return

    @property
    def height(self):
        """ Height of the _source_ frames. As frames may be rescaled, this can differ from the
        properties of the frames emitted by the grabber.
        :rtype : float
        """
        return self.capture.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)

    @height.setter
    def height(self, height):
        """Not available for video files."""
        return

    def rewind(self):
        """Jumps to beginning of file."""
        self.log.debug('Rewinding to first frame of video source')
        self.index = 0

    def fast_forward(self):
        """Jumps to last frame."""
        self.log.debug("Jumping to last frame")
        self.index = self.num_frames - 1

    @property
    def num_frames(self):
        """Number of frames in the file. Requires intact frame index.

        FFMPEG can repair frame/time indices.
        """
        return self.capture.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)

    @property
    def fourcc(self):
        return self.capture.get(cv2.cv.CV_CAP_PROP_FOURCC)

    @property
    def index(self):
        """Position in video in absolute number of frames.

        Returns None for non-indexed sources.
        """
        if self.capture is not None:
            return int(self.capture.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)) if self.indexed else self.frame_count

    @index.setter
    def index(self, idx):
        """Move position pointer in video to position in absolute number of frames."""
        if self.capture is None or not self.indexed:
            return

        idx = int(idx)
        if idx < 0:
            idx = 0
        if idx >= self.num_frames:
            idx = self.num_frames - 1

        # if the current pointer is not the same as requested, update and seek in video file
        # (not sure about performance of the seeking, I'll avoid doing it all the time)
        # NB! Potential death trap thanks to float<>int conversions!??
        if self.index != idx:
            self.capture.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, float(idx))

    @property
    def pos_time(self):
        """Position in video in milliseconds. Unreliable if frame rate set during encoding not the
        same as frame rate of acquisition. Requires external synchronization markers.
        """
        if self.capture is not None:
            return self.capture.get(cv2.cv.CV_CAP_PROP_POS_MSEC)

    @pos_time.setter
    def pos_time(self, milliseconds):
        """Jump to time position in video file. Unreliable for variable acquisition frame rates."""
        if self.capture is not None:
            self.capture.set(cv2.cv.CV_CAP_PROP_POS_MSEC, milliseconds)

    def close(self):
        self.log.debug('Closing %s', str(self))
        if self.capture:
            try:
                self.capture.release()
                self.log.DEBUG("Capture %s released", str(self.capture))
            except BaseException, error:
                self.log.error("Capture %s release exception: [%s]", self.capture, error)
                self.capture = None


###############################################################################
#                                  SOCKET                                     #
###############################################################################
class SocketCapture(FrameSource):
    def __init__(self, source, *args, **kwargs):
        super(SocketCapture, self).__init__()

