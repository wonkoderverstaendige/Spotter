#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 15 21:14:43 2012
@author: <Ronny Eichler> ronny.eichler@gmail.com

Track position LEDs and sync signal from camera or video file.

Usage:
    spotterQt.py [--source SRC --outfile DST] [options]
    spotterQt.py -h | --help

Options:
    -h --help           Show this screen
    -f --fps FPS        Fps for camera and video
    -s --source SRC     Path to file or device ID [default: 0]
    -S --Serial         Serial port to uC [default: None]
    -o --outfile DST    Path to video out file [default: None]
    -d --dims DIMS      Frame size [default: 640x360]
    -D --DEBUG          Verbose output

To do:
    - destination file name may consist of tokens to automatically create,
      i.e., %date%now%iterator3$fixedstring
    - track low res, but store full resolution
    - can never overwrite a file

#Example:
    --source 0 --outfile test.avi --size=320x200 --fps=30

"""

__version__ = 0.45

NO_EXIT_CONFIRMATION = True
DIR_CONFIG = './config'
DIR_TEMPLATES = './templates'
DIR_SPECIFICATION = './config/template_specification.ini'
DEFAULT_TEMPLATE = 'defaults.ini'

GUI_REFRESH_INTERVAL = 10

import sys
import os
import platform
import time
import logging

from lib.docopt import docopt
from lib.configobj import configobj, validate

from PyQt4 import QtGui, QtCore
from lib.core import Spotter
from lib.ui.mainUi import Ui_MainWindow
from lib.ui import GLFrame
from lib.ui import SerialIndicator, StatusBar, SideBar

sys.path.append(DIR_TEMPLATES)


class Main(QtGui.QMainWindow):
    gui_refresh_offset = 0

    __spotter_ref = None

    def __init__(self, *args, **kwargs):  # , source, destination, fps, size, gui, serial
        self.log = logging.getLogger(__name__)
        QtGui.QMainWindow.__init__(self)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Spotter main class, handles Grabber, Writer, Tracker, Chatter
        self.__spotter_ref = Spotter(*args, **kwargs)

        # Status Bar
        self.status_bar = StatusBar(self)
        self.statusBar().addWidget(self.status_bar)

        # Side bar widget
        self.side_bar = SideBar.SideBar(self)
        self.ui.frame_parameters.addWidget(self.side_bar)

        # Exit Signals
        self.ui.actionE_xit.setShortcut('Ctrl+Q')
        self.ui.actionE_xit.setStatusTip('Exit Spotter')
        self.connect(self.ui.actionE_xit, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()'))

        # About window
        self.connect(self.ui.actionAbout, QtCore.SIGNAL('triggered()'), self.about)

        # Menu Bar items
        #   File
        self.connect(self.ui.actionFile, QtCore.SIGNAL('triggered()'), self.file_open_video)
        self.connect(self.ui.actionCamera, QtCore.SIGNAL('triggered()'), self.file_open_device)
        #   Configuration
        self.connect(self.ui.actionLoadConfig, QtCore.SIGNAL('triggered()'), self.load_config)
        self.connect(self.ui.actionSaveConfig, QtCore.SIGNAL('triggered()'), self.save_config)
        self.connect(self.ui.actionRemoveTemplate, QtCore.SIGNAL('triggered()'),
                     self.side_bar.remove_all_tabs)

        # Toolbar items
        self.connect(self.ui.actionRecord, QtCore.SIGNAL('toggled(bool)'), self.record_video)
        self.connect(self.ui.actionSourceProperties, QtCore.SIGNAL('triggered()'),
                     self.spotter.grabber.get_capture_properties)
        # Serial/Arduino Connection status indicator
        self.arduino_indicator = SerialIndicator(self.spotter.chatter)
        self.ui.toolBar.addWidget(self.arduino_indicator)

        # OpenGL frame
        self.gl_frame = GLFrame(AA=True)
        self.ui.frame_video.addWidget(self.gl_frame)
        self.gl_frame.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

        # handling mouse events by the tabs for selection of regions etc.
        self.gl_frame.sig_event.connect(self.mouse_event_to_tab)

        # Loading template list in folder
        default_path = os.path.join(os.path.abspath(DIR_CONFIG), DEFAULT_TEMPLATE)
        self.template_default = self.parse_config(default_path, True)
        #list_of_files = [f for f in os.listdir(DIR_TEMPLATES) if f.lower().endswith('ini')]

        # Main Window states
        self.center_window()
        self.connect(self.ui.actionOnTop, QtCore.SIGNAL('toggled(bool)'), self.toggle_window_on_top)

        # Starts main frame grabber loop
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(GUI_REFRESH_INTERVAL)

        self.stopwatch = QtCore.QElapsedTimer()
        self.stopwatch.start()

    @property
    def spotter(self):
        return self.__spotter_ref

    ###############################################################################
    ##  FRAME REFRESH
    ###############################################################################
    def refresh(self):
        # TODO: I ain't got no clue as to why reducing the interval drastically improves the frame rate
        # TODO: Maybe the interval immediately resets the counter and starts it up?
        elapsed = self.stopwatch.restart()

        #self.log.debug("Updating spotter")
        if self.spotter.update() is None:
            pass
            #return

        # update the OpenGL frame
        #self.log.debug("Updating GL")
        if not (self.gl_frame.width and self.gl_frame.height):
            return
        self.gl_frame.update_world(self.spotter)

        # Update the currently open tab
        #self.log.debug("Updating side bar")
        self.side_bar.update_current_page()

        # check if the refresh rate needs adjustment
        #self.log.debug("Updating GUI refresh rate")
        self.adjust_refresh_rate()

        # based on stopwatch, show GUI refresh rate
        #self.log.debug("Updating GUI refresh rate display")
        self.status_bar.update_fps(elapsed)

    def adjust_refresh_rate(self, forced=None):
        """
        Change GUI refresh rate according to frame rate of video source, or keep at
        1000/GUI_REFRESH_INTERVAL Hz for cameras to not miss too many frames
        """
        self.gui_refresh_offset = self.status_bar.sb_offset.value()

        if forced is not None:
            self.timer.setInterval(forced)
            return

        if self.spotter.source_type == 'file':
            if not self.status_bar.sb_offset.isEnabled():
                self.status_bar.sb_offset.setEnabled(True)
            try:
                interval = int(1000.0/self.spotter.grabber.fps) + self.gui_refresh_offset
            except (ValueError, TypeError):
                interval = 0
            if interval < 0:
                interval = 1
                self.status_bar.sb_offset.setValue(interval - int(1000.0/self.spotter.grabber.fps))

            if self.spotter.grabber.fps != 0 and self.timer.interval() != interval:
                self.timer.setInterval(interval)
                self.log.debug("Changed main loop update rate to match file. New: %d", self.timer.interval())
        else:
            if self.status_bar.sb_offset.isEnabled():
                self.status_bar.sb_offset.setEnabled(False)
                #self.status_bar.sb_offset.setValue(0)
            if self.timer.interval() != GUI_REFRESH_INTERVAL:
                self.timer.setInterval(GUI_REFRESH_INTERVAL)
                self.log.debug("Changed main loop update rate to be fast. New: %d", self.timer.interval())

    def record_video(self, state, filename=None):
        """ Control recording of grabbed video. """
        # TODO: Select output video file name.
        self.log.debug("Toggling writer recording state")
        if state:
            if filename is None:
                filename = QtGui.QFileDialog.getSaveFileName(self, 'Open Video', './recordings/')
                if len(filename):
                    self.spotter.start_writer(str(filename)+'.avi')
        else:
            self.spotter.stop_writer()

    def mouse_event_to_tab(self, event_type, event):
        """
        Hand the mouse event to the active tab. Tabs may handle mouse events
        differently, and depending on internal states (e.g. selections)
        """
        current_tab = self.side_bar.get_child_page()
        if current_tab:
            try:
                if current_tab.accept_events:
                    current_tab.process_event(event_type, event)
            except AttributeError:
                pass

    def about(self):
        """ About message box. Credits. Links. Jokes. """
        QtGui.QMessageBox.about(self, "About",
                                """<b>Spotter</b> v%s
                   <p>Copyright &#169; 2012-2013 <a href=mailto:ronny.eichler@gmail.com>Ronny Eichler</a>.
                   <p>This application is under heavy development. Use at your own risk.
                   <p>Python %s -  PyQt4 version %s - on %s""" % (__version__,
                                                                  platform.python_version(), QtCore.QT_VERSION_STR,
                                                                  platform.system()))

    def center_window(self):
        """
        Centers main window on screen.
        Doesn't quite work on multi-monitor setups, as the whole screen-area is taken.
        But as long as the window ends up in a predictable position...
        """
        screen = QtGui.QDesktopWidget().screenGeometry()
        window_size = self.geometry()
        self.move((screen.width() - window_size.width()) / 2, (screen.height() - window_size.height()) / 2)

    def toggle_window_on_top(self, state):
        """ Have main window stay on top. According to the setWindowFlags
        documentation, the window will hide after changing flags, requiring
        either a .show() or a .raise(). These may have different behaviors on
        different platforms!"""
        # TODO: Test on Linux, OSX, Win8
        if state:
            self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
            self.show()
        else:
            self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowStaysOnTopHint)
            self.show()

    def file_open_video(self):
        """
        Open a video file. Should finish current spotter if any by closing
        it to allow all frames/settings to be saved properly. Then instantiate
        a new spotter.
        TODO: Open file dialog in a useful folder. E.g. store the last used one
        """
        # Windows 7 uses 'HOMEPATH' instead of 'HOME'
        #path = os.getenv('HOME')
        #if not path:
        #    path = os.getenv('HOMEPATH')
        filename = QtGui.QFileDialog.getOpenFileName(self, 'Open Video', './recordings')  # path
        if len(filename):
            self.log.debug('File dialog given %s', str(filename))
            self.spotter.grabber.start(str(filename))

    def file_open_device(self):
        """ Open camera as frame source """
        self.spotter.grabber.start(source=0, size=(640, 360))

    def closeEvent(self, event):
        """
        Exiting the interface has to kill the spotter class and subclasses
        properly, especially the writer and serial handles, otherwise division
        by zero might be imminent.
        """
        if NO_EXIT_CONFIRMATION:
            reply = QtGui.QMessageBox.Yes
        else:
            reply = QtGui.QMessageBox.question(self, 'Exiting...', 'Are you sure?',
                                               QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            self.spotter.exit()
            event.accept()
        else:
            event.ignore()

    ###############################################################################
    ##  TEMPLATES handling
    ###############################################################################
    def parse_config(self, path, run_validate=True):
        """ Template parsing and validation. """
        template = configobj.ConfigObj(path, file_error=True, stringify=True,
                                       configspec=DIR_SPECIFICATION)
        if run_validate:
            validator = validate.Validator()
            results = template.validate(validator)
            if not results is True:
                self.log.error("Template error in file %s", path)
                for (section_list, key, _) in configobj.flatten_errors(template, results):
                    if key is not None:
                        self.log.error('The "%s" key in the section "%s" failed validation', key, ', '.join(section_list))
                    else:
                        self.log.error('The following section was missing:%s ', ', '.join(section_list))
                return None
        return template

    def load_config(self, filename=None, directory=DIR_TEMPLATES):
        """
        Opens file dialog to choose template file and starts parsing it
        """
        if filename is None:
            filename = str(QtGui.QFileDialog.getOpenFileName(self, 'Open Template', directory))
        if not len(filename):
            return None

        self.log.debug("Opening template %s", filename)
        template = self.parse_config(filename)
        if template is not None:
            abs_pos = template['TEMPLATE']['absolute_positions']

            for f_key, f_val in template['FEATURES'].items():
                self.side_bar.add_feature(f_val, f_key, focus_new=False)

            for o_key, o_val in template['OBJECTS'].items():
                self.side_bar.add_object(o_val, o_key, focus_new=False)

            for r_key, r_val in template['REGIONS'].items():
                self.side_bar.add_region(r_val, r_key,
                                         shapes=template['SHAPES'],
                                         abs_pos=abs_pos,
                                         focus_new=False)

    def save_config(self, filename=None, directory=DIR_TEMPLATES):
        """ Store a full set of configuration to file. """
        config = configobj.ConfigObj(indent_type='    ')

        if filename is None:
            filename = str(QtGui.QFileDialog.getSaveFileName(self, 'Save Template', directory))
        if not len(filename):
            return
        config.filename = filename

        # General options and comment
        config['TEMPLATE'] = {}
        config['TEMPLATE']['name'] = filename
        config['TEMPLATE']['date'] = '_'.join(map(str, time.localtime())[0:3])
        config['TEMPLATE']['description'] = 'new template'
        config['TEMPLATE']['absolute_positions'] = True
        config['TEMPLATE']['resolution'] = self.spotter.grabber.size

        # Features
        config['FEATURES'] = {}
        for f in self.spotter.tracker.leds:
            section = {'type': 'LED',
                       'range_hue': f.range_hue,
                       'range_sat': f.range_sat,
                       'range_val': f.range_val,
                       'range_area': f.range_area,
                       'fixed_pos': f.fixed_pos}
            config['FEATURES'][str(f.label)] = section

        # Objects
        config['OBJECTS'] = {}
        for o in self.spotter.tracker.oois:
            features = [f.label for f in o.linked_leds]
            analog_out = len(o.magnetic_signals) > 0
            section = {'features': features,
                       'analog_out': analog_out}
            if analog_out:
                section['analog_signal'] = [s[0] for s in o.magnetic_signals]
                section['pin_pref'] = [s[1] for s in o.magnetic_signals]
            section['trace'] = o.traced
            config['OBJECTS'][str(o.label)] = section

        # Shapes
        shapelist = []
        #rng = (self.gl_frame.width, self.gl_frame.height)
        for r in self.spotter.tracker.rois:
            for s in r.shapes:
                if not s in shapelist:
                    shapelist.append(s)
        config['SHAPES'] = {}
        for s in shapelist:
            section = {'p1': s.points[0],
                       'p2': s.points[1],
                       'type': s.shape}
            # if one would store the points normalized instead of absolute
            # But that would require setting the flag in TEMPLATES section
            #section = {'p1': geom.norm_points(s.points[0], rng),
            #           'p2': geom.norm_points(s.points[1], rng),
            #           'type': s.shape}
            config['SHAPES'][str(s.label)] = section

        # Regions
        config['REGIONS'] = {}
        for r in self.spotter.tracker.rois:
            mo = r.magnetic_objects
            section = {'shapes': [s.label for s in r.shapes],
                       'digital_out': True,
                       'digital_collision': [o[0].label for o in mo],
                       'pin_pref': [o[1] for o in mo],
                       'color': r.active_color[0:3]}
            config['REGIONS'][str(r.label)] = section

        config['SERIAL'] = {}
        config['SERIAL']['auto'] = self.spotter.chatter.auto
        config['SERIAL']['last_port'] = self.spotter.chatter.serial_port

        # and finally
        config.write()


#############################################################
def main(*args, **kwargs):
    app = QtGui.QApplication([])
    window = Main(*args, **kwargs)
    window.show()
    window.raise_()  # needed on OSX?

    sys.exit(app.exec_())


if __name__ == "__main__":                                  #
#############################################################
    # TODO: Recover full command-line functionality
    # TODO: Add config file for general settings
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Command line parsing
    arg_dict = docopt.docopt(__doc__, version=None)
    DEBUG = arg_dict['--DEBUG']
    if DEBUG:
        print(arg_dict)

    # Frame size parameter string 'WIDTHxHEIGHT' to size tuple (WIDTH, HEIGHT)
    size = (640, 360) if not arg_dict['--dims'] else tuple(arg_dict['--dims'].split('x'))

    main(source=arg_dict['--source'], size=size)

    # Qt main window which instantiates spotter class with all parameters
    #main(source=arg_dict['--source'],
    #     destination=utils.dst_file_name(arg_dict['--outfile']),
    #     fps=arg_dict['--fps'],
    #     size=size,
    #     serial=arg_dict['--Serial'])
