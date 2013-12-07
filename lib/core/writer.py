# -*- coding: utf-8 -*-
"""
Created on Mon Jul 09 00:29:00 2012
@author: <Ronny Eichler> ronny.eichler@gmail.com

Wrapper for VideoWriter, can either work as separate thread fed by frame buffer
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
import os
import sys
import time
import logging

from lib import utilities as utils
from lib.docopt import docopt

OVERWRITE = False
#seconds till writer process times out after having received last alive packet
STILL_ALIVE_TIMEOUT = 10


class Writer:
    codecs = ('XVID', 'DIVX', 'IYUV')
    destination = None
    writer = None
    size = None
    alive = True
    recording = False
    ts_last = time.clock()
    video_logger = None

    def __init__(self, fps=None, size=None, queue=None, pipe=None, *args, **kwargs):
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.log = logging.getLogger(__name__)
        self.queue = queue
        self.pipe = pipe

        # Only important if lower than what camera can provide, or for videos
        try:
            fps = float(29.97 if not fps else fps)
        except ValueError:
            fps = 29.97
        self.fps = fps

        # Video Writer takes tuple of INTs for size, not floats!
        try:
            self.size = tuple(int(i) for i in size)
        except TypeError:
            pass

        self.codec = kwargs['codec'] if 'codec' in kwargs else self.codecs[0]
        self.log.info('Starting loop with size %s', str(size))
        self.loop()

    def start(self, parameters):  # dst=None, size=None
        if len(parameters) >= 1:
            size = parameters[1]
            if size is None:
                self.log.error('Video size not specified, writer would fail.')
                return
        self.size = size

        if len(parameters) >= 2:
            dst = parameters[2]

        # check if output file exists
        if dst is None:
            dst = 'recordings/' + utils.time_string() + '.avi'

        destination = utils.dst_file_name(dst)
        if os.path.isfile(destination) and not OVERWRITE:
            self.log.error('Destination file %s exists.', destination)
            return
        self.destination = destination

        self.log.info('Start recording: %s fps, %s, %s', str(self.fps), str(self.size), self.destination)

        # VideoWriter object
        cc = list(self.codec)
        self.writer = cv2.VideoWriter(filename=self.destination, fourcc=cv2.cv.CV_FOURCC(cc[0], cc[1], cc[2], cc[3]),
                                      fps=self.fps, frameSize=self.size, isColor=True)

        self.video_logger = logging.getLogger(destination)
        self.video_logger.handlers = []
        self.video_logger.addHandler(logging.FileHandler(''.join([destination, '.log'])))
        self.video_logger.setLevel(logging.INFO)
        self.video_logger.propagate = False

        self.video_logger.info('Start recording: %s fps, %s, %s, %s',
                               str(self.fps), str(self.size), self.codec, self.destination)

        self.log.debug('Recording running...')
        self.recording = True

    def stop(self):
        self.destination = None
        if self.video_logger is not None:
            for handle in self.video_logger.handlers:
                self.log.debug("Flushing video logger file handle of %s", str(handle))
                handle.flush()
                if isinstance(handle, logging.FileHandler):
                    self.log.debug("Closing video logger file handle of %s", str(handle))
                    handle.close()
            self.video_logger = None

        if self.recording:
            self.close()
        self.recording = False

    def write(self, item):
        # TODO: Error handling of frame existence/content
        frame = item[0]
        messages = item[1]

        try:
            assert self.size == (frame.img.shape[1], frame.img.shape[0])
        except AssertionError:
            self.log.error('Frame size not correct!')
            self.log.debug('Frame shape: %s, expected: %s', str(frame.img.shape), str(self.size))
            self.stop()

        for m in messages:
            self.video_logger.info(m)
        self.writer.write(frame.img)

    def loop(self):
        """Writes frames from the queue. If alive flag set to
        false, deletes capture object to allow proper exit
        """
        # FIXME: The interface initialization can take longer than the timeout on the writer!
        while 42 and self.alive:
            # Process should terminate if not being talked to for a while
            #self.log.debug("Alive signal timeout: %s", str(time.clock() - self.ts_last))
            if time.clock() - self.ts_last > STILL_ALIVE_TIMEOUT:
                self.log.error("Alive signal timed out")
                self.close()
                sys.exit(0)

            try:
                new_pipe_msg = self.pipe.poll()
            except Exception, error:
                self.log.error(error)
                new_pipe_msg = False

            if new_pipe_msg:
                # any command in the pipe will keep the process alive
                full_message = self.pipe.recv()
                cmd = full_message[0]
                if len(full_message) > 1:
                    msg = full_message[:]
                else:
                    msg = None
                self.ts_last = time.clock()
                if cmd == 'terminate':
                    self.log.debug('Writer received termination signal')
                    # don't close yet, first empty buffer!
                    self.alive = False
                elif cmd == 'stop':
                    self.log.debug('Writer received stop signal')
                    self.stop()
                elif cmd == 'start':
                    self.log.debug('Writer received start signal with parameters: %s', str(msg))
                    self.start(msg)
                elif cmd == 'alive':
                    pass

            while not self.queue.empty():
                item = self.queue.get()

                if self.writer and self.recording:
                    self.write(item)

            # refresh time to keep CPU utilization down
            time.sleep(0.01)

        # Close writer upon termination signal
        if not self.alive:
            self.close()

    def close(self):
        self.log.debug('Closing writer')
        if self.writer is not None:
            del self.writer
            self.writer = None


#############################################################
if __name__ == '__main__':                                  #
#############################################################
    pass
    ## Parsing CLI arguments
    #arg_dict = docopt( __doc__, version=None )
    #DEBUG = arg_dict['--DEBUG']
    #if DEBUG: print( arg_dict )
    #
    ## Width and height; WWWxHHH to tuple of floats; cv2 set requires floats
    #size = (0, 0) if not arg_dict['--dims'] else tuple( arg_dict['--dims'].split('x') )
    #
    ## Codec should be four character code (FOURCC)
    #codec = arg_dict['--codec'].upper()
    #if codec:
    #    if not len(codec) == 4:
    #        print 'Codec must be four letter code. E.g. "XVID".'
    #        sys.exit(0)
    #    else:
    #        if DEBUG: print 'Using codec FOURCC ' + codec
    #
    ## Run in command line without user interface to slow things down
    #GUI = not arg_dict['--Headless']
    #
    ## Instantiate frame source to get something to write
    #import grabber
    #frame_source = grabber.Grabber( arg_dict['--source'] )
    #fps = 30.0 if not arg_dict['--fps'] else frame_source.fps
    #
    #if DEBUG: print str( fps ) + ':' + str( size )
    #
    ## Instantiate main video writer class
    #main = Writer( destination = arg_dict['--outfile'],
    #               fps = fps,
    #               size = frame_source.size,
    #               codec = codec )
    #
    ## Main loop till EOF or Escape key pressed
    #key = 0
    #while frame_source.grab_next() and not ( key % 100 == 27 ):
    #    if GUI: cv2.imshow( 'Writer', frame_source.framebuffer[0] )
    #    main.write( frame_source.framebuffer.pop() )
    #    if GUI: key = cv2.waitKey(1)
    #
    ## Exiting gracefully
    #main.close()
    #frame_source.close()
    #if DEBUG: print 'Wrote ' + str( frame_source.framecount ) + ' frames.'
    #sys.exit(0)
