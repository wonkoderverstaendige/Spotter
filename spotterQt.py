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
# ../Spotter_Tests/LisaCheeseMaze.avi
# media/vid/r52r2f107.avi

__version__ = 0.4

NO_EXIT_CONFIRMATION = True
DIR_TEMPLATES = './config'
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
import lib.geometry as geom
import lib.utilities as utils
from lib.ui.mainUi import Ui_MainWindow
from lib.ui import GLFrame
from lib.ui import TabFeatures, TabObjects, TabRegions, TabSerial
from lib.ui import SerialIndicator, StatusBar, SideBar
from lib.ui import MainTabPage

sys.path.append(DIR_TEMPLATES)


class Main(QtGui.QMainWindow):
    gui_fps = 20
    gui_refresh_offset = 0

    def __init__(self, *args, **kwargs):  # , source, destination, fps, size, gui, serial
        self.log = logging.getLogger(__name__)
        QtGui.QMainWindow.__init__(self)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.center_window()

        # Status Bar
        self.sbw = StatusBar(self)
        self.sbw.lbl_fps.setStyleSheet(' QLabel {color: red}')
        self.statusBar().addWidget(self.sbw)

        # Side bar widget
        self.side_bar = None
        #self.side_bar = SideBar.SideBar(self)
        #self.ui.frame_parameters.addWidget(self.side_bar)

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
        self.connect(self.ui.actionResetConfig, QtCore.SIGNAL('triggered()'), self.reset_config)

        # Toolbar items
        self.connect(self.ui.actionRecord, QtCore.SIGNAL('toggled(bool)'), self.record_video)

        # Spotter main class, handles Grabber, Writer, Tracker, Chatter
        self.spotter = Spotter(*args, **kwargs)

        # OpenGL frame
        self.gl_frame = GLFrame()
        self.ui.frame_video.addWidget(self.gl_frame)
        self.gl_frame.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

        # handling mouse events by the tabs for selection of regions etc.
        self.gl_frame.sig_event.connect(self.mouse_event_to_tab)

        # Loading template list in folder
        default_path = os.path.join(os.path.abspath(DIR_TEMPLATES), DEFAULT_TEMPLATE)
        self.template_default = self.parse_config(default_path, True)
        #list_of_files = [f for f in os.listdir(DIR_TEMPLATES) if f.lower().endswith('ini')]

        # Features tab widget
        self.feature_tabs = []
        self.connect(self.ui.tab_features, QtCore.SIGNAL('currentChanged(int)'), self.tab_features_switch)
        self.connect(self.ui.btn_new_feature_tab, QtCore.SIGNAL('clicked()'), self.add_feature)

        # Objects tab widget
        self.object_tabs = []
        self.connect(self.ui.tab_objects, QtCore.SIGNAL('currentChanged(int)'), self.tab_objects_switch)
        self.connect(self.ui.btn_new_object_tab, QtCore.SIGNAL('clicked()'), self.add_object)

        # Regions tab widget
        self.region_tabs = []
        self.connect(self.ui.tab_regions, QtCore.SIGNAL('currentChanged(int)'), self.tab_regions_switch)
        self.connect(self.ui.btn_new_region_tab, QtCore.SIGNAL('clicked()'), self.add_region)
        self.ui.tab_regions.tabCloseRequested.connect(self.remove_tab)

        # Serial tab widget
        self.serial_tabs = []
        self.add_serial(self.spotter.chatter)

        # Serial/Arduino Connection status indicator
        self.arduino_indicator = SerialIndicator(self.spotter.chatter)
        self.ui.toolBar.addWidget(self.arduino_indicator)
        self.serial_timer = QtCore.QTimer(self)
        self.serial_timer.timeout.connect(self.serial_check)
        self.serial_timer.start(1000)

        self.stopwatch = QtCore.QElapsedTimer()
        self.stopwatch.start()

        # Starts main frame grabber loop
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(GUI_REFRESH_INTERVAL)

    ###############################################################################
    ##  FRAME REFRESH
    ###############################################################################
    def refresh(self):
        t = self.stopwatch.restart()
        if t != 0:
            self.gui_fps = self.gui_fps*0.9 + 0.1*1000./t
            if self.gui_fps > 100:
                self.sbw.lbl_fps.setText('FPS: {:.0f}'.format(self.gui_fps))
            else:
                self.sbw.lbl_fps.setText('FPS: {:.1f}'.format(self.gui_fps))

        if self.spotter.update() is None:
            return

        if not (self.gl_frame.width and self.gl_frame.height):
            return

        # update the OpenGL frame
        self.gl_frame.update_world(self.spotter)

        # Update the currently open tab
        self.update_current_tab()

        # check if the refresh rate needs adjustment
        self.adjust_refresh_rate()

    def adjust_refresh_rate(self, forced=None):
        """
        Change GUI refresh rate according to frame rate of video source, or keep at
        1000/GUI_REFRESH_INTERVAL Hz for cameras to not miss too many frames
        """
        self.gui_refresh_offset = self.sbw.sb_offset.value()

        if forced:
            self.timer.setInterval(forced)
            return

        if self.spotter.source_type is not 'file':
            if self.sbw.sb_offset.isEnabled():
                self.sbw.sb_offset.setEnabled(False)
                self.sbw.sb_offset.setValue(0)
            if self.timer.interval() != GUI_REFRESH_INTERVAL:
                self.timer.setInterval(GUI_REFRESH_INTERVAL)
                #print "Changed main loop update rate to be fast. New: ", self.timer.interval()
        else:
            if not self.sbw.sb_offset.isEnabled():
                self.sbw.sb_offset.setEnabled(True)
            try:
                interval = int(1000.0/self.spotter.grabber.fps) + self.gui_refresh_offset
            except (ValueError, TypeError):
                interval = 0
            if interval < 0:
                interval = 1
                self.sbw.sb_offset.setValue(interval - int(1000.0/self.spotter.grabber.fps))

            if self.spotter.grabber.fps != 0 and self.timer.interval() != interval:
                self.timer.setInterval(interval)
                #print "Changed main loop update rate to match file. New: ", self.timer.interval()

    def record_video(self, state, filename=None):
        """
        Control recording of grabbed video.
        TODO: Select output video file name.
        """
        if state:
            self.spotter.start_writer()
        else:
            self.spotter.stop_writer()

    def mouse_event_to_tab(self, event_type, event):
        """
        Hand the mouse event to the active tab. Tabs may handle mouse events
        differently, and depending on internal states (e.g. selections)
        """
        current_tab = self.get_child_tab()
        if current_tab and current_tab.accept_events:
            current_tab.process_event(event_type, event)

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

    def add_tab(self, tab_widget, new_tab_class, tab_equivalent, focus_new=True):
        """
        Add new tab with Widget new_tab_class and switches to it. The
        tab_equivalent is the object that is being represented by the tab,
        for example an LED or Object.
        """
        new_tab = new_tab_class.Tab(self, tab_equivalent)
        tab_widget.insertTab(tab_widget.count() - 1, new_tab, new_tab.label)
        if focus_new:
            tab_widget.setCurrentIndex(tab_widget.count() - 2)
        else:
            tab_widget.setCurrentIndex(0)
        return new_tab

    def remove_tab(self, idx):
        """
        Removing is trickier, as it has to delete the features/objects
        from the tracker!
        """
        print "NOT removing tab", idx

    def get_top_tab_label(self):
        """ Return label of the top level tab. """
        return self.ui.tab_parameters.tabText(self.ui.tab_parameters.currentIndex())

    def get_child_tab(self):
        active_top_tab_label = self.get_top_tab_label()
        if active_top_tab_label == "Features" and (self.ui.tab_features.count() > 1):
            return self.ui.tab_features.widget(self.ui.tab_features.currentIndex())
        elif active_top_tab_label == "Objects" and (self.ui.tab_objects.count() > 1):
            return self.ui.tab_objects.widget(self.ui.tab_objects.currentIndex())
        elif active_top_tab_label == "ROIs" and (self.ui.tab_regions.count() > 1):
            return self.ui.tab_regions.widget(self.ui.tab_regions.currentIndex())
        elif active_top_tab_label == "Serial":
            return self.ui.tab_serial.widget(self.ui.tab_serial.currentIndex())
        else:
            return None

    def update_current_tab(self):
        """
        Currently visible tab is the only one that requires to be updated
        live when parameters of its associated object change, e.g. coordinates
        of tracked objects or LEDs. The rest should happen behind the scenes
        in the spotter sub-classes.
        """
        current_tab = self.get_child_tab()
        try:
            current_tab.update()
        except AttributeError:
            pass

    def update_all_tabs(self):
        """
        This is potentially very expensive! Best only trigger on 'large'
        event or introduce some selectivity, i.e. only update affected tabs as
        far as one can tell.
        """
        for tab_list in [self.feature_tabs, self.object_tabs, self.region_tabs]:
            for t in tab_list:
                t.update()

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
        self.spotter.grabber.start(source=0, size=(320, 180))

    def closeEvent(self, event):
        """
        Exiting the interface has to kill the spotter class and subclasses
        properly, especially the writer and serial handles, otherwise division
        by zero might be imminent.
        """
        if NO_EXIT_CONFIRMATION:
            reply = QtGui.QMessageBox.Yes
        else:
            reply = QtGui.QMessageBox.question(self,
                                               'Exiting...',
                                               'Are you sure?',
                                               QtGui.QMessageBox.Yes,
                                               QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            self.spotter.exitMain()
            event.accept()
        else:
            event.ignore()

    ###############################################################################
    ##  TEMPLATES handling
    ###############################################################################
    def parse_config(self, path, run_validate=True):
        """
        Template parsing and validation.
        """
        template = configobj.ConfigObj(path, file_error=True, stringify=True,
                                       configspec=DIR_SPECIFICATION)
        if run_validate:
            validator = validate.Validator()
            results = template.validate(validator)
            if not results is True:
                print "Template error in file ", path
                for (section_list, key, _) in configobj.flatten_errors(template, results):
                    if key is not None:
                        print 'The "%s" key in the section "%s" failed validation' % (key, ', '.join(section_list))
                    else:
                        print 'The following section was missing:%s ' % ', '.join(section_list)
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
                self.add_feature(f_val, f_key, focus_new=False)

            for o_key, o_val in template['OBJECTS'].items():
                self.add_object(o_val, o_key, focus_new=False)

            for r_key, r_val in template['REGIONS'].items():
                self.add_region(r_val, r_key,
                                shapes=template['SHAPES'],
                                abs_pos=abs_pos,
                                focus_new=False)

    def save_config(self, filename=None, directory=DIR_TEMPLATES):
        """
        Store a full set of configuration to file.
        """
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
                       'color': r.active_color}
            config['REGIONS'][str(r.label)] = section

        config['SERIAL'] = {}
        config['SERIAL']['auto'] = self.spotter.chatter.auto
        config['SERIAL']['last_port'] = self.spotter.chatter.serial_port

        # and finally
        config.write()

    def reset_config(self):
        """
        Remove everything from everything to start over!
        """
        pass
        # loop over all tabs, call their close methods and they will take over

    ###############################################################################
    ##  FEATURES Tab Updates
    ###############################################################################
    def tab_features_switch(self, idx_tab=0):
        """
        Switch to the tab page with index idx_tab.
        """
        self.ui.tab_features.setCurrentIndex(idx_tab)

    def add_feature(self, template=None, label=None, focus_new=True):
        """
        Create a feature from trackables and add a corresponding tab to
        the tab widget, which is linked to show and edit feature properties.
        TODO: Create new templates when running out by fitting them into
        the color space somehow.
        """
        if not template:
            key = self.template_default['FEATURES'].iterkeys().next()
            template = self.template_default['FEATURES'][key]
            label = 'LED_' + str(len(self.spotter.tracker.leds))

        if not template['type'].lower() == 'led':
            return
        else:
            range_hue = map(int, template['range_hue'])
            range_sat = map(int, template['range_sat'])
            range_val = map(int, template['range_val'])
            range_area = map(int, template['range_area'])
            fixed_pos = template.as_bool('fixed_pos')
            feature = self.spotter.tracker.addLED(label,
                                                  range_hue,
                                                  range_sat,
                                                  range_val,
                                                  range_area,
                                                  fixed_pos)
        new_tab = self.add_tab(self.ui.tab_features, TabFeatures, feature, focus_new)
        if self.side_bar is not None:
            self.side_bar.features_page.add_item(feature)
        self.feature_tabs.append(new_tab)

    ###############################################################################
    ##  OBJECTS Tab Updates
    ###############################################################################
    def tab_objects_switch(self, idx_tab=0):
        """
        Switch to the tab page with index idx_tab.
        """
        self.ui.tab_objects.setCurrentIndex(idx_tab)

    def add_object(self, template=None, label=None, focus_new=True):
        """
        Create a new object that will be linked to LEDs and/r ROIs to
        track and trigger events.
        TODO: Create new objects even when running out of templates for example
        by randomizing offsets.
        """
        if not template:
            key = self.template_default['OBJECTS'].iterkeys().next()
            template = self.template_default['OBJECTS'][key]
            label = 'Object_' + str(len(self.spotter.tracker.oois))

        features = []
        for n in xrange(min(len(self.spotter.tracker.leds), len(template['features']))):
            for l in self.spotter.tracker.leds:
                if template['features'][n] == l.label:
                    features.append(l)

        analog_out = template['analog_out']
        if analog_out:
            # Magnetic objects from collision list
            signal_names = template['analog_signal']
            pin_prefs = template['pin_pref']
            if pin_prefs is None:
                pin_prefs = []
            magnetic_signals = []
            if template['pin_pref_strict']:
                # If pin preference is strict but no/not enough pins given,
                # reject all/those without given pin preference
                if len(pin_prefs) == 0:
                    signal_names = []
            else:
                # if not strict but also not enough given, fill 'em up with -1
                # which sets those objects to being indifferent in their pin pref
                if len(pin_prefs) < len(signal_names):
                    pin_prefs[-(len(signal_names) - len(pin_prefs))] = -1

            # Reject all objects that still don't have a corresponding pin pref
            signal_names = signal_names[0:min(len(pin_prefs), len(signal_names))]

            # Those still in the race, assemble into
            # List of [object label, object, pin preference]
            for isig, sn in enumerate(signal_names):
            # Does an object with this name exist? If so, link its reference!
            #                obj = None
            #                for o in self.spotter.tracker.oois:
            #                    if o.label == on:
            #                        obj = o
                magnetic_signals.append([sn, pin_prefs[isig]])
        else:
            magnetic_signals = None

        trace = template['trace']
        track = template['track']
        object_ = self.spotter.tracker.addOOI(features,
                                              label,
                                              trace,
                                              track,
                                              magnetic_signals)

        if analog_out:
            if any(template['analog_signal']):
                if 'x position' in template['analog_signal']:
                    object_.analog_pos = True
                if 'y position' in template['analog_signal']:
                    object_.analog_pos = True
                if 'speed' in template['analog_signal']:
                    object_.analog_spd = True
                if 'direction' in template['analog_signal']:
                    object_.analog_dir = True

        new_tab = self.add_tab(self.ui.tab_objects, TabObjects, object_, focus_new)
        if self.side_bar is not None:
            self.side_bar.objects_page.add_item(object_)
        self.object_tabs.append(new_tab)

    ###############################################################################
    ##  REGIONS Tab Updates
    ###############################################################################
    def tab_regions_switch(self, idx_tab=0):
        """
        Switch to the tab page with index idx_tab.
        """
        self.ui.tab_regions.setCurrentIndex(idx_tab)

    def add_region(self, template=None, label=None, shapes=None, abs_pos=True, focus_new=True):
        """
        Create a new region of interest that will be that will be linked
        to Objects with conditions to trigger events.
        TODO: New regions created empty!
        """
        # Defaults if nothing else given
        if not template:
            key = self.template_default['REGIONS'].iterkeys().next()
            template = self.template_default['REGIONS'][key]
            label = 'ROI_' + str(len(self.spotter.tracker.rois))
        if not shapes:
            shapes = self.template_default['SHAPES']

        # extract shapes from shape templates
        shape_list = []
        for s_key in template['shapes']:
            if s_key in shapes:
                shape_type = shapes[s_key]['type']
                if abs_pos:
                    points = [shapes[s_key]['p1'], shapes[s_key]['p2']]
                else:
                    points = geom.scale_points([shapes[s_key]['p1'],
                                                shapes[s_key]['p2']],
                                               (self.gl_frame.width,
                                                self.gl_frame.height))
                shape_list.append([shape_type, points, s_key])

        # Magnetic objects from collision list
        obj_names = template['digital_collision']
        pin_prefs = template['pin_pref']
        if pin_prefs is None:
            pin_prefs = []
        magnetic_objects = []
        if template['pin_pref_strict']:
            # If pin preference is strict but no/not enough pins given,
            # reject all/those without given pin preference
            if len(pin_prefs) == 0:
                obj_names = []
        else:
            # if not strict but also not enough given, fill 'em up with -1
            # which sets those objects to being indifferent in their pin pref
            if len(pin_prefs) < len(obj_names):
                pin_prefs[-(len(obj_names) - len(pin_prefs))] = -1

        # Reject all objects that still don't have a corresponding pin pref
        obj_names = obj_names[0:min(len(pin_prefs), len(obj_names))]

        # Those still in the race, assemble into
        # List of [object label, object, pin preference]
        for io, on in enumerate(obj_names):
            # Does an object with this name exist? If so, link its reference!
            obj = None
            for o in self.spotter.tracker.oois:
                if o.label == on:
                    obj = o
            magnetic_objects.append([obj, pin_prefs[io]])

        color = template['color']

        region = self.spotter.tracker.addROI(shape_list,
                                             label,
                                             color,
                                             magnetic_objects)
        new_tab = self.add_tab(self.ui.tab_regions,
                               TabRegions,
                               region,
                               focus_new)
        self.region_tabs.append(new_tab)

    ###############################################################################
    ##  SERIAL Tab Updates
    ###############################################################################
    def serial_check(self):
        if self.spotter.chatter.is_open():
            self.spotter.chatter.read_all()

    def add_serial(self, serial_object, label=None):
        """
        Serial object tab. Probably an Arduino compatible board linked to it.
        """
        new_tab = self.add_tab(self.ui.tab_serial, TabSerial, serial_object)
        self.serial_tabs.append(new_tab)


#############################################################
def main(*args, **kwargs):
    app = QtGui.QApplication([])
    window = Main(*args, **kwargs)
    window.show()
    window.raise_()  # needed on OSX?

    sys.exit(app.exec_())


if __name__ == "__main__":                                  #
#############################################################

    # Command line parsing
    ARGDICT = docopt.docopt(__doc__, version=None)
    DEBUG = ARGDICT['--DEBUG']
    if DEBUG:
        print(ARGDICT)

    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # Debug logging
    #log = logging.getLogger('ledtrack')
    #log_handle = logging.StreamHandler()  # logging.FileHandler('ledtrack.log')
    #formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    #log_handle.setFormatter(formatter)
    #log.addHandler(log_handle)
    #if DEBUG:
    #    log.setLevel(logging.INFO)  # INFOERROR
    #else:
    #    log.setLevel(logging.ERROR)  # INFOERROR

    # Frame size parameter string 'WIDTHxHEIGHT' to size tuple (WIDTH, HEIGHT)
    size = (0, 0) if not ARGDICT['--dims'] else tuple(ARGDICT['--dims'].split('x'))

    main()

    # Qt main window which instantiates spotter class with all parameters
    #main(source=ARGDICT['--source'],
    #     destination=utils.dst_file_name(ARGDICT['--outfile']),
    #     fps=ARGDICT['--fps'],
    #     size=size,
    #     serial=ARGDICT['--Serial'])
