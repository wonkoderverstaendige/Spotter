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

import os
import logging
import time
import copy
import multiprocessing

import cv2
from lib.docopt import docopt
from lib.core import grabber, tracker, writer, chatter
from lib.configobj import configobj, validate

DIR_CONFIG = os.path.join(os.path.dirname(__file__), 'config')
SPEC_TEMPLATE = os.path.join(DIR_CONFIG, 'template_specification.ini')
DEFAULT_TEMPLATE = os.path.join(DIR_CONFIG, 'defaults.ini')
DIR_TEMPLATES = os.path.join(os.path.dirname(__file__), '../../templates')
PATH_TIMING_LOG = 'tracking_3LEDs.p'


class Spotter:

    # helper instances
    grabber = None
    writer = None
    tracker = None
    chatter = None

    # state variables
    record_to_file = True

    newest_frame = None  # fresh from the frame source; to be processed/written
    # FIXME: Can be removed?
    still_frame = None   # frame shown in GUI, may be an older one
    hsv_frame = None     # converted into HSV color space for tracking

    ts_start = None

    paused = False
    recording = False

    scale_resize = 1.0
    scale_tracking = 1.0

    def __init__(self, serial=None, *args, **kwargs):
        """

        :param source:
        :param dst:
        :param fps:
        :param size:
        :param serial:
        """
        self.log = logging.getLogger(__name__)
        self.log.info(str(multiprocessing.cpu_count()) + ' CPUs found')

        # Default template holds all defaults for creating new things (LEDs, ROIs, etc) from scratch
        self.log.debug('Loading default template...')
        default_path = os.path.join(os.path.abspath(DIR_CONFIG), DEFAULT_TEMPLATE)
        self.template_default = self.load_template(default_path)

        # Setup frame grabber object, fills frame buffer
        self.log.debug('Instantiating grabber...')
        self.grabber = grabber.Grabber(*args, **kwargs)

        # Writer writes frames from buffer to video file in a separate process.
        self.log.debug('Instantiating writer...')
        self.writer_queue = multiprocessing.Queue(16)
        self.writer_pipe, child_pipe = multiprocessing.Pipe()
        self.writer = multiprocessing.Process(target=writer.Writer,
                                              args=(self.grabber.source_fps, self.grabber.source_size,
                                                    self.writer_queue, child_pipe,))
        self.log.debug('Starting writer...')
        self.writer.start()
        self.writer_pipe.send('started!')

        # Tracker object finds features in frames
        self.log.debug('Instantiating tracker...')
        self.tracker = tracker.Tracker(self, adaptive_tracking=True)

        # Chatter handles serial communication with arduino
        self.log.debug('Instantiating chatter...')
        self.chatter = chatter.Chatter(serial, auto=True)

    def update(self, grab_new=True):
        loop_start = time.time()
        # FIXME: Stalls if buffer runs full, e.g. when writer crashes/closes
        # send heart-beat to writer
        self.writer_pipe.send(['alive'])

        # Get new frame
        new_frame = self.grabber.next() if grab_new else None
        if new_frame:
            self.newest_frame = new_frame

            # resize frame if necessary
            # TODO: This should be handled by the grabber, which then could return the proper corrected frame dimensions
            if self.scale_resize < 1.0:
                new_frame.img = cv2.resize(new_frame.img, (0, 0), fx=self.scale_resize,
                                           fy=self.scale_resize, interpolation=cv2.INTER_LINEAR)

            # Find and update position of tracked object
            self.tracker.track_feature(new_frame, method='hsv_thresh',
                                       scale=self.scale_tracking*self.scale_resize)

            slots = []
            messages = []
            # Update positions of all objects
            for o in self.tracker.oois:
                o.update_slots(self.chatter)
                o.update_state()
                slots.extend(o.linked_slots)
                messages.append('\t'.join([new_frame.time_text,
                                           #str(self.newest_frame.tickstamp),
                                           str(o.label),
                                           str(o.position)]))

            for l in self.tracker.features:
                messages.append('\t'.join([new_frame.time_text,
                                           #str(self.newest_frame.tickstamp),
                                           str(l.label),
                                           str(l.position)]))

            # Check Object-Region collisions
            for r in self.tracker.rois:
                r.update_slots(self.chatter)
                r.update_state()
                slots.extend(r.linked_slots)
            self.chatter.update_pins(slots)

            # Check on writer process to prevent data loss
            if self.check_writer():
                if self.recording:
                    self.writer_pipe.send(['record'])
                    item = (copy.deepcopy(new_frame),
                            copy.deepcopy(messages))
                    self.writer_queue.put(item)
#               time.sleep(0.001)  # required, or may crash?

        print (time.time() - loop_start) * 1000
        return self.newest_frame

    @property
    def source_type(self):
        return self.newest_frame.source_type if self.newest_frame else None

    def check_writer(self):
        """ True if alive """
        return self.writer.is_alive()

    def start_writer(self, filename=None):
        # FIXME: replace img.shape with Frame object properties height and width
        size = (self.newest_frame.img.shape[1], self.newest_frame.img.shape[0])
        self.writer_pipe.send(['start', size, filename])
        self.recording = True

    def stop_writer(self):
        self.writer_pipe.send(['stop'])
        self.recording = False

    def exit(self):
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
            self.writer_pipe.send(['terminate'])
            # gives the child process one second to finish up
            self.writer.join(1)
            # will be terminated otherwise
            if self.writer.is_alive():
                self.writer.terminate()

    def load_template(self, filename, validation=True):
        """Load and validate template file.
        """
        self.log.debug("Opening template %s", filename)

        template = configobj.ConfigObj(filename, file_error=True, stringify=True,
                                       configspec=SPEC_TEMPLATE)
        if validation:
            assert self.validate_template(template)

        return template

    def apply_template(self, template):
        """Create components defined in template and return their references so they may
        be linked with their representations in the GUI.
        """
        return self.tracker.add_from_template(template)

    def save_template(self, filename):
        """Save current state of spotter and all the sub-components as a template.
        """

        template = configobj.ConfigObj(indent_type='    ')
        template.filename = filename

        # General options and comment
        template['TEMPLATE'] = {}
        template['TEMPLATE']['name'] = filename
        template['TEMPLATE']['date'] = '_'.join(map(str, time.localtime())[0:3])
        template['TEMPLATE']['description'] = 'A new template.'
        template['TEMPLATE']['absolute_positions'] = True
        template['TEMPLATE']['resolution'] = self.grabber.source_size

        # FEATURES
        template['FEATURES'] = {}
        for f in self.tracker.features:
            section = {'type': 'LED',
                       'range_hue': f.range_hue,
                       'range_sat': f.range_sat,
                       'range_val': f.range_val,
                       'range_area': f.range_area,
                       'fixed_pos': f.fixed_pos}
            template['FEATURES'][str(f.label)] = section

        # OBJECTS
        template['OBJECTS'] = {}
        for o in self.tracker.oois:
            features = [f.label for f in o.linked_features]
            analog_out = len(o.magnetic_signals) > 0
            section = {'features': features,
                       'analog_out': analog_out}
            if analog_out:
                section['analog_signal'] = [s[0] for s in o.magnetic_signals]
                section['pin_pref'] = [s[1] for s in o.magnetic_signals]
            section['trace'] = o.traced
            template['OBJECTS'][str(o.label)] = section

        # SHAPES
        shape_list = []
        #rng = (self.gl_frame.width, self.gl_frame.height)
        for r in self.tracker.rois:
            for s in r.shapes:
                if not s in shape_list:
                    shape_list.append(s)
        template['SHAPES'] = {}
        for s in shape_list:
            section = {'p2': s.points[1],
                       'p1': s.points[0],
                       'type': s.shape}
            # if one would store the points normalized instead of absolute
            # But that would require setting the flag in TEMPLATES section
            #section = {'p1': geom.norm_points(s.points[0], rng),
            #           'p2': geom.norm_points(s.points[1], rng),
            #           'type': s.shape}
            template['SHAPES'][str(s.label)] = section

        # REGIONS OF INTEREST
        template['REGIONS'] = {}
        for r in self.tracker.rois:
            mo = r.magnetic_objects
            section = {'shapes': [s.label for s in r.shapes],
                       'digital_out': True,
                       'digital_collision': [o[0].label for o in mo],
                       'pin_pref': [o[1] for o in mo],
                       'color': r.active_color[0:3]}
            template['REGIONS'][str(r.label)] = section

        template['SERIAL'] = {}
        template['SERIAL']['auto'] = self.chatter.auto
        template['SERIAL']['last_port'] = self.chatter.serial_port

        # and finally
        template.write()

    def validate_template(self, template):
        """Template parsing and validation.
        """
        validator = validate.Validator()
        results = template.validate(validator)
        if not results is True:
            self.log.error('Template error!')
            for (section_list, key, _) in configobj.flatten_errors(template, results):
                if key is not None:
                    self.log.error('The "%s" key in the section "%s" failed validation', key,
                                   ', '.join(section_list))
                else:
                    self.log.error('The following section was missing:%s ', ', '.join(section_list))
            return None
        else:
            return template

#############################################################
if __name__ == "__main__":                                  #
#############################################################
    pass
#    # Command line parsing
#    arg_dict = docopt( __doc__, version=None )
#    DEBUG   = arg_dict['--DEBUG']
#    if DEBUG: print( arg_dict )
#
#    # Debug logging
#    log = logging.getLogger('ledtrack')
#    loghdl = logging.StreamHandler()#logging.FileHandler('ledtrack.log')
#    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s') #
#    loghdl.setFormatter(formatter)
#    log.addHandler(loghdl)
#    if DEBUG:
#        log.setLevel( logging.INFO ) #INFOERROR
#    else:
#        log.setLevel( logging.ERROR ) #INFOERROR
#
#    # no GUI, may later select GUI backend, i.e., Qt or cv2.highgui etc.
#    guistring = 'cv2.highgui' if not arg_dict['--Headless'] else arg_dict['--Headless']
#
#    # Frame size parameter string 'WIDTHxHEIGHT' to size tupple (WIDTH, HEIGHT)
#    size = (0, 0) if not arg_dict['--dims'] else tuple( arg_dict['--dims'].split('x') )
#
#    # Instantiating main class ... no shit, Sherlock!
#    main = Spotter( source      = arg_dict['--source'],
#                    destination = utils.dst_file_name( arg_dict['--outfile'] ),
#                    fps         = arg_dict['--fps'],
#                    size        = size,
#                    gui         = guistring,
#                    serial      = arg_dict['--Serial'])
#
#    # It's Math. 3rd grade Math. Wait time between frames, if any left
#    log.debug( 'fps: ' + str(main.grabber.fps) )
#    t = int(1000/main.grabber.fps)
#
#    # Main loop, runs until EOF or <ESCAPE> key pressed
#    log.debug( 'starting main loop' )
#    main.ts_start = time.clock()
#
#    while True:
#
#        # Get new frame
#        if main.grabber.grab_next():
#            main.newest_frame = main.grabber.framebuffer.pop()
#
#            # Check if writer process is still alive
#            # Otherwise might lose data without knowing!
#            # Copy numpy array, otherwise queue references same object
#            # like frame that will be worked on
#            if not main.writer == None and main.check_writer():
#                main.write_queue.put( main.newest_frame.copy() )
#                time.sleep( 0.001 ) # required, or may crash?
#
#            # Find and update position of tracked object
#            main.hsv_frame = cv2.cvtColor( main.newest_frame, cv2.COLOR_BGR2HSV )
#            main.tracker.trackLeds( main.hsv_frame, method = 'hsv_thresh' )
##            main.Object.updatePosition()
#
#            # send position of tracked object to serial port
##            if not main.Object.position is None:
##                main.tracker.chatter.send( main.Object.position )
#
#            # freezes frame being shown, but not frame being processed/written
#            main.gui.update( main.newest_frame )
#
#        else:
#            print 'No new frame returned!!! What does it mean??? We are going to die! Eventually!!!'
#
#        total_elapsed = ( time.clock() - main.grabber.ts_last_frame ) * 1000
#        t = int( 1000/main.grabber.fps - total_elapsed ) - 1
#        if t <= 0:
#            log.info('Missed next frame by: ' + str( t * -1. ) + ' ms')
#            t = 1
##        main.update()
#        main.gui.onKey( cv2.waitKey(t) )
#
##    sys.exit(app.exec_())
