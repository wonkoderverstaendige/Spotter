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
DIR_EXAMPLES = './media/vid'
DIR_CONFIG = './config'
DIR_TEMPLATES = './templates'
DIR_SPECIFICATION = './config/template_specification.ini'
DEFAULT_TEMPLATE = 'defaults.ini'

GUI_REFRESH_INTERVAL = 16
AUTOPAUSE_ON_LOAD = False

import sys
import os
import platform
import time
import logging

from lib.docopt import docopt
from lib.configobj import configobj, validate


try:
    from lib.pyqtgraph import QtGui, QtCore  # ALL HAIL LUKE!
    import lib.pyqtgraph as pg
except ImportError:
    pg = None
    from PyQt4 import QtGui, QtCore

from lib.core import Spotter
from lib.ui.mainUi import Ui_MainWindow
from lib.ui import GLFrame, PGFrame
from lib.ui import SerialIndicator, StatusBar, SideBar, openDeviceDlg

sys.path.append(DIR_TEMPLATES)
gl = None


class Main(QtGui.QMainWindow):
    __spotter_ref = None

    def __init__(self, app, *args, **kwargs):  # , source, destination, fps, size, gui, serial
        self.log = logging.getLogger(__name__)
        QtGui.QMainWindow.__init__(self)
        self.app = app

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Status Bar
        self.status_bar = StatusBar(self)
        self.statusBar().addWidget(self.status_bar)

        # Side bar
        self.side_bar = SideBar.SideBar(self)
        self.ui.frame_parameters.addWidget(self.side_bar)

        # Exit Signals
        self.ui.actionE_xit.setShortcut('Ctrl+Q')
        self.ui.actionE_xit.setStatusTip('Exit Spotter')
        self.connect(self.ui.actionE_xit, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()'))

        # About window
        self.connect(self.ui.actionAbout, QtCore.SIGNAL('triggered()'), self.about)

        # Persistent application settings
        # TODO: Needs command line option to reset everything
        self.settings = QtCore.QSettings()

        # Menu Bar items
        #   File
        self.connect(self.ui.actionFile, QtCore.SIGNAL('triggered()'), self.file_open_video)
        self.connect(self.ui.actionCamera, QtCore.SIGNAL('triggered()'), self.file_open_device)
        self.recent_files = self.settings.value("RecentFiles").toStringList()
        self.update_file_menu()

        #   Configuration
        self.connect(self.ui.actionLoadConfig, QtCore.SIGNAL('triggered()'), self.load_config)
        self.connect(self.ui.actionSaveConfig, QtCore.SIGNAL('triggered()'), self.save_config)
        self.connect(self.ui.actionRemoveTemplate, QtCore.SIGNAL('triggered()'),
                     self.side_bar.remove_all_tabs)
        self.connect(self.ui.action_clearRecentFiles, QtCore.SIGNAL('triggered()'), self.clear_recent_files)

        # Toolbar items
        self.connect(self.ui.actionRecord, QtCore.SIGNAL('toggled(bool)'), self.record_video)
        self.ui.actionPlay.toggled.connect(self.toggle_play)
        self.ui.actionPause.toggled.connect(self.toggle_pause)
        self.ui.actionRepeat.toggled.connect(self.toggle_repeat)
        # self.ui.actionFastForward.triggered.connect(self.fast_forward)
        # self.ui.actionRewind.triggered.connect(self.rewind)
        #self.connect(self.ui.actionSourceProperties, QtCore.SIGNAL('triggered()'),
        #             self.spotter.grabber.get_capture_properties)

        # Serial/Arduino Connection status indicator
        self.arduino_indicator = SerialIndicator()
        self.ui.toolBar.addWidget(self.arduino_indicator)

        # OpenGL frame
        if gl is not None:
            self.gl_frame = GLFrame(AA=True)
            self.ui.frame_video.addWidget(self.gl_frame)
            self.gl_frame.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
            # handling mouse events by the tabs for selection of regions etc.
            self.gl_frame.sig_event.connect(self.mouse_event_to_tab)
        else:
            self.gl_frame = None

        # PyQtGraph frame
        if pg is not None:
            self.pg_frame = PGFrame.PGFrame()
            self.ui.gridLayout_2.addWidget(self.pg_frame)
            #self.pg_frame.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        else:
            self.pg_frame = None

        # Video source timing scroll bar
        self.ui.scrollbar_t.valueChanged.connect(self.slider_changed)

        # Loading template list in folder
        default_path = os.path.join(os.path.abspath(DIR_CONFIG), DEFAULT_TEMPLATE)
        self.template_default = self.parse_config(default_path, True)
        #list_of_files = [f for f in os.listdir(DIR_TEMPLATES) if f.lower().endswith('ini')]

        # Main Window states
        self.resize(self.settings.value("MainWindow/Size", QtCore.QVariant(QtCore.QSize(600, 500))).toSize())
        self.move(self.settings.value("MainWindow/Position", QtCore.QVariant(QtCore.QPoint(0, 0))).toPoint())
        self.restoreState(self.settings.value("MainWindow/State").toByteArray())
        #self.center_window()
        self.connect(self.ui.actionOnTop, QtCore.SIGNAL('toggled(bool)'), self.toggle_window_on_top)

        self.playing = False
        self.paused = False
        self.repeat = False

        self.gui_refresh_offset = 0
        self.gui_refresh_interval = GUI_REFRESH_INTERVAL
        self.stopwatch = QtCore.QElapsedTimer()
        QtCore.QTimer.singleShot(0, self.initialize)  # fires when event loop starts

    ###############################################################################
    ##  SPOTTER CLASS INIT
    ###############################################################################
    def initialize(self, *args, **kwargs):
        # Spotter main class, handles Grabber, Writer, Tracker, Chatter
        self.__spotter_ref = Spotter(*args, **kwargs)

        # populate side bar now that spotter is here...
        self.side_bar.initialize(self.spotter)
        self.arduino_indicator.initialize(self.spotter.chatter)

        self.stopwatch.start()
        self.refresh()

    @property
    def spotter(self):
        return self.__spotter_ref

    ###############################################################################
    ##  FRAME REFRESH
    ###############################################################################
    def refresh(self):
        elapsed = self.stopwatch.restart()

        self.update_ui_elements()
        try:
            # TODO: I ain't got no clue as to why reducing the interval drastically improves the frame rate
            # TODO: Maybe the interval immediately resets the counter and starts it up?

            # Trigger grabbing and processing of new frame
            if self.playing:
                #self.log.debug("Updating spotter")
                if self.spotter.update() is None:
                    pass
            else:
                if not self.spotter.grabber.index == self.ui.scrollbar_t.value():
                    self.spotter.grabber.grab(self.ui.scrollbar_t.value())

            # Update the video frame display (either PG or GL frame, or both for testing)
            if self.playing and not self.paused:
                # Update GL frame
                if self.gl_frame is not None:
                    if not (self.gl_frame.width and self.gl_frame.height):
                        return
                    self.gl_frame.update_world(self.spotter)
                # Update PyQtGraph frame
                if self.pg_frame is not None:
                    self.pg_frame.update_world(self.spotter)

            # Update the currently open tab
            #self.log.debug("Updating side bar")
            self.side_bar.update_current_page()

            # Check if the refresh rate needs adjustment
            #self.log.debug("Updating GUI refresh rate")
            self.adjust_refresh_rate()

        finally:
            # Based on stopwatch, show GUI refresh rate
            #self.status_bar.update_fps(elapsed)
            # start timer to next refresh
            QtCore.QTimer.singleShot(self.gui_refresh_interval, self.refresh)

    def update_ui_elements(self):
        """Awkward helper method to check in some notorious misaligners...
        """
        if not self.spotter.grabber.capture:
            self.ui.scrollbar_t.setMaximum(1)
            self.ui.scrollbar_t.setEnabled(False)
            return
        else:
            if not self.ui.scrollbar_t.isEnabled():
                self.ui.scrollbar_t.setEnabled(True)

        num_frames = self.spotter.grabber.num_frames
        if not self.ui.scrollbar_t.maximum() == num_frames:
            self.ui.scrollbar_t.setMaximum(num_frames)
            self.ui.spin_index.setMaximum(num_frames)
            self.ui.lbl_num_frames.setText('/%s' % str(num_frames))

        index = self.spotter.grabber.index
        if not self.ui.scrollbar_t.value() == index or \
                not self.ui.spin_index.value() == index:
            self.ui.scrollbar_t.setValue(index)
            self.ui.spin_index.setValue(index)

        #self.ui.lbl.setText('Frame: %s/%s' % (str(self.spotter.grabber.index),
         #                                                       str(self.spotter.grabber.num_frames)))

    def adjust_refresh_rate(self, forced=None):
        """
        Change GUI refresh rate according to frame rate of video source, or keep at
        1000/GUI_REFRESH_INTERVAL Hz for cameras to not miss too many frames
        """
        # TODO: Allow adjusting for the video, too.
        self.gui_refresh_offset = self.ui.spin_offset.value()
        frame_dur = int(1000.0 / (self.spotter.grabber.fps if self.spotter.grabber.fps else 30))

        if forced is not None:
            self.gui_refresh_interval = forced
            return

        if self.spotter.source_type == 'file':
            if not self.ui.spin_offset.isEnabled():
                self.ui.spin_offset.setEnabled(True)
            try:
                interval = frame_dur + self.gui_refresh_offset
            except (ValueError, TypeError):
                interval = 0
            if interval < 0:
                interval = 0
                self.ui.spin_offset.setValue(interval - frame_dur)

            if frame_dur != 0 and self.gui_refresh_interval != interval:
                self.gui_refresh_interval = interval
                self.log.debug("Changed main loop update rate to match file. New: %d", self.gui_refresh_interval)
        else:
            if self.ui.spin_offset.isEnabled():
                self.ui.spin_offset.setEnabled(False)
            if self.gui_refresh_interval != GUI_REFRESH_INTERVAL:
                self.gui_refresh_interval = GUI_REFRESH_INTERVAL
                self.log.debug("Changed main loop update rate to be fast. New: %d", self.gui_refresh_interval)

    def toggle_play(self, state=None):
        """Start playback of video source sequence.
        """
        if self.spotter.grabber.capture:
            self.playing = self.ui.actionPlay.isChecked()
            if not self.playing:
                self.ui.actionPause.setChecked(False)
                self.ui.actionPause.setEnabled(False)
            else:
                self.ui.actionPause.setEnabled(True)
        else:
            self.ui.actionPlay.setChecked(False)
            self.ui.actionPause.setChecked(False)

    def toggle_pause(self):
        """Pause playback at current frame. Right now, there is not really a difference
        between not playing, and being paused.
        """
        self.paused = self.ui.actionPause.isChecked()

    def toggle_repeat(self):
        """Continuously loop over source sequence.
        """
        self.repeat = self.ui.actionRepeat.isChecked()
        if self.source is not None:
            self.source.repeat = self.repeat

    def record_video(self, state, filename=None):
        """ Control recording of grabbed video. """
        # TODO: Select output video file name.
        self.log.debug("Toggling writer recording state")
        if state:
            if filename is None:
                filename = QtGui.QFileDialog.getSaveFileName(self, 'Open Video', './recordings/')
                if len(filename):
                    self.spotter.start_writer(str(filename) + '.avi')
        else:
            self.spotter.stop_writer()

    def slider_changed(self):
        pass
        # should update video position here...

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
                   <p>Copyright &#169; 2012-2014 <a href=mailto:ronny.eichler@gmail.com>Ronny Eichler</a>.
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
        # TODO: Test on OSX
        if state:
            self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
            self.show()
        else:
            self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowStaysOnTopHint)
            self.show()

    def file_open_video(self, filename=None, path=DIR_EXAMPLES):
        """Open a video file.

        Actions calling this function are not providing
        arguments, so self.sender() has to be checked for the calling action
        if no arguments were given.
        """
        path = QtCore.QString(path)

        # If no filename given, this is may be supposed to open a recent file
        if filename is None:
            action = self.sender()
            if isinstance(action, QtGui.QAction):
                filename = action.data().toString()

        # If filename is still None, this was called by the Open File action
        if not len(filename) or filename is None:
            filename = QtGui.QFileDialog.getOpenFileName(self, 'Open Video', path,
                                                         self.tr('Video: *.avi *.mpg *.mp4 ;; All Files: (*.*)'))

        # If the user chose a file, this is finally not None...
        if len(filename):
            self.log.debug('Opening %s', str(filename))
            self.spotter.grabber.start(str(filename))

        self.ui.actionPlay.setChecked(True)
        # TODO: Force refresh with at least one new frame!
        self.ui.actionPause.setChecked(AUTOPAUSE_ON_LOAD)

        self.add_recent_file(filename)
        self.update_file_menu()
        self.setWindowTitle('Spotter - %s' % filename)
        self.ui.statusbar.showMessage('Opened %s' % filename, 2000)

    def file_open_device(self):
        """Open camera as frame source.
        """
        dialog = openDeviceDlg.OpenDeviceDlg()
        dialog.spin_width.setValue(640)
        dialog.spin_height.setValue(360)
        dialog.ledit_device.setText("0")
        if dialog.exec_():
            self.spotter.grabber.start(source=dialog.ledit_device.text(),
                                       size=(dialog.spin_width.value(),
                                             dialog.spin_height.value()))
        self.ui.actionPlay.setChecked(True)
        self.ui.actionPause.setChecked(AUTOPAUSE_ON_LOAD)

    @staticmethod
    def add_actions(target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def update_file_menu(self):
        """Update list of recently opened files in the File->Open menu.
        """
        # throw everything out and start over...
        self.ui.menu_Open.clear()
        self.add_actions(self.ui.menu_Open, [self.ui.actionFile, self.ui.actionCamera, None])

        current_file = QtCore.QFileInfo(QtCore.QString(self.spotter.grabber.source)).fileName() \
            if self.spotter is not None and self.spotter.grabber.source_type == 'file' else None

        # list of files to show in the menu, only append if file still exists!
        recent_files = []
        for fname in self.recent_files:
            if fname != current_file and QtCore.QFile.exists(fname):
                recent_files.append(fname)

        # Generate actions for each entry in the list and append to menu
        if recent_files:
            for i, fname in enumerate(recent_files):
                # TODO: Icons for the entries
                action = QtGui.QAction(QtGui.QIcon(":/icon.png"),
                                       "&%d %s" % (i + 1, QtCore.QFileInfo(fname).fileName()), self)
                action.setData(QtCore.QVariant(fname))
                self.connect(action, QtCore.SIGNAL("triggered()"), self.file_open_video)
                self.ui.menu_Open.addAction(action)
            # convenience action to remove all entries
            self.add_actions(self.ui.menu_Open, [None, self.ui.action_clearRecentFiles])

    def add_recent_file(self, fname):
        """Add file to the list of recently opened files.
         NB: self.recent_files is a QStringList, not a python list!
        """
        if fname is not None:
            if not self.recent_files.contains(fname):
                self.recent_files.prepend(QtCore.QString(fname))
                while self.recent_files.count() > 9:
                    self.recent_files.take_last()

    def clear_recent_files(self):
        """Remove all entries from the list of recently opened files.
        """
        self.recent_files.clear()
        self.update_file_menu()

    def store_settings(self):
        """Store window states and other settings.
        """
        settings = QtCore.QSettings()

        # Last opened file
        filename = QtCore.QVariant(QtCore.QString(self.spotter.grabber.source)) \
            if self.spotter.grabber.source_type == 'file' else QtCore.QVariant()
        settings.setValue("LastFile", filename)

        # recently opened files
        recent_files = QtCore.QVariant(self.recent_files) if self.recent_files else QtCore.QVariant()
        settings.setValue("RecentFiles", recent_files)

        # Main Window states
        settings.setValue("MainWindow/Size", QtCore.QVariant(self.size()))
        settings.setValue("MainWindow/Position", QtCore.QVariant(self.pos()))
        settings.setValue("MainWindow/State", QtCore.QVariant(self.saveState()))

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
            self.store_settings()
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
                        self.log.error('The "%s" key in the section "%s" failed validation', key,
                                       ', '.join(section_list))
                    else:
                        self.log.error('The following section was missing:%s ', ', '.join(section_list))
                return None
        return template

    def load_config(self, filename=None, path=DIR_TEMPLATES):
        """
        Opens file dialog to choose template file and starts parsing it
        """
        # TODO: Shouldn't load a template unless there is a capture?
        # Or simply disable relative templates?
        if self.spotter.grabber.capture is None:
            self.ui.statusbar.showMessage("No video source open! Can't load a template without in this version.", 3000)
            return
        path = QtCore.QString(path)
        if filename is None:
            filename = QtGui.QFileDialog.getOpenFileName(self, 'Open Template', path, self.tr('All Files: *.*'))
        if not len(filename):
            return None
        filename = str(filename)

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
        self.ui.statusbar.showMessage('Opened template %s' % filename, 2000)

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
    # identifiers for QSettings persistent application settings
    app.setOrganizationName('spotter_inc')
    app.setOrganizationDomain('spotter.sp')
    app.setApplicationName('Spotter')

    window = Main(app, *args, **kwargs)
    window.show()
    window.raise_()  # needed on OSX?

    sys.exit(app.exec_())


if __name__ == "__main__":  #
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
