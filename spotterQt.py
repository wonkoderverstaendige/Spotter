#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 15 21:14:43 2012
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
    -d --dims DIMS      Frame size [default: 640x360]
    -H --Headless       Run without interface
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

import sys
import os
import platform
import time
from PyQt4 import QtGui, QtCore
import logging

#configuration and templates
sys.path.append(DIR_TEMPLATES)
sys.path.append('./lib/configobj')
from configobj import ConfigObj, flatten_errors
from validate import Validator

#project libraries
sys.path.append('./lib')
from spotter import Spotter
import geometry as geom
import utilities as utils

#Qt user interface files
sys.path.append('./ui')
from mainUi import Ui_MainWindow
from GLFrame import GLFrame
import TabFeatures
import TabObjects
import TabRegions
import TabSerial
from SerialIndicator import SerialIndicator

#command line handling
sys.path.append('./lib/docopt')
from docopt import docopt


class Main(QtGui.QMainWindow):
    def __init__(self, source, destination, fps, size, gui, serial):
        QtGui.QMainWindow.__init__(self)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.center_window()

        # Exit Signals
        self.ui.actionE_xit.setShortcut('Ctrl+Q')
        self.ui.actionE_xit.setStatusTip('Exit Spotter')
        self.connect(self.ui.actionE_xit, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()'))

        # About window
        self.connect(self.ui.actionAbout, QtCore.SIGNAL('triggered()'), self.about)

        # Menubar items
        #   File
        self.connect(self.ui.actionFile, QtCore.SIGNAL('triggered()'), self.file_dialog_video)
        #   Configuration
        self.connect(self.ui.actionLoadConfig, QtCore.SIGNAL('triggered()'), self.load_config)
        self.connect(self.ui.actionSaveConfig, QtCore.SIGNAL('triggered()'), self.save_config)
        self.connect(self.ui.actionResetConfig, QtCore.SIGNAL('triggered()'), self.reset_config)

        # Toolbar items
        self.connect(self.ui.actionRecord, QtCore.SIGNAL('toggled(bool)'), self.record_video)

        # Spotter main class, handles Grabber, Writer, Tracker, Chatter
        self.spotter = Spotter(source, destination, fps, size, gui, serial)

        # OpenGL frame
        self.glframe = GLFrame()
        self.ui.frame_video.addWidget(self.glframe)
        self.glframe.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

        # handling mouse events by the tabs for selection of regions etc.
        self.glframe.sig_event.connect(self.mouse_event_to_tab)

        # Loading template list in folder
        default_path = os.path.join(os.path.abspath(DIR_TEMPLATES), DEFAULT_TEMPLATE)
        self.template_default = self.parse_config(default_path, True)
        #list_of_files = [f for f in os.listdir(DIR_TEMPLATES) if f.lower().endswith('ini')]
        #for f in list_of_files:
        #    if not f == DEFAULT_TEMPLATE:
        #        self.ui.combo_templates.addItem(f)
        #self.connect(self.ui.btn_feature_template, QtCore.SIGNAL('clicked()'), self.load_template)
        #self.connect(self.ui.btn_object_template, QtCore.SIGNAL('clicked()'), self.load_template)
        #self.connect(self.ui.btn_region_template, QtCore.SIGNAL('clicked()'), self.load_template)

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

        # Serial tab widget
        self.serial_tabs = []
        self.add_serial(self.spotter.chatter)

        # Serial/Arduino Connection status indicator
        self.arduino_indicator = SerialIndicator(self.spotter.chatter)
        self.ui.toolBar.addWidget(self.arduino_indicator)
        self.serial_timer = QtCore.QTimer(self)
        self.serial_timer.timeout.connect(self.serial_check)
        self.serial_timer.start(1000)

        # Starts main frame grabber loop
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.refresh()
        self.glframe.resizeFrame()
        self.timer.start(30)

    ###############################################################################
    ##  FRAME REFRESH
    ###############################################################################
    def refresh(self):
        rv = self.spotter.update()
        if rv is None:
            self.spotter.exitMain()
            self.close()
            return

        # Append Object tracking markers to the list of things that have
        # to be drawn onto the GL frame
        self.glframe.frame = self.spotter.newest_frame.img

        # draw crosses
        for l in self.spotter.tracker.leds:
            if l.pos_hist[-1] is not None and l.marker_visible:
                self.glframe.jobs.append([self.glframe.drawCross,
                                          l.pos_hist[-1], 14, l.lblcolor])

        # draw search windows if adaptive tracking is used:
        if self.spotter.tracker.adaptive_tracking:
            for l in self.spotter.tracker.leds:
                if l.adaptive_tracking and l.search_roi is not None:
                    self.glframe.jobs.append([self.glframe.drawBox,
                                              l.search_roi.points,
                                              (l.lblcolor[0],
                                               l.lblcolor[1],
                                               l.lblcolor[2],
                                               0.25)])

        # draw crosses and traces for objects
        for o in self.spotter.tracker.oois:
            if o.position is not None:
                self.glframe.jobs.append([self.glframe.drawCross,
                                          o.position, 8,
                                          (1.0, 1.0, 1.0, 1.0), 7, True])
                if o.traced:
                    points = []
                    for n in xrange(min(len(o.pos_hist), 100)):
                        if o.pos_hist[-n - 1] is not None:
                            points.append([o.pos_hist[-n - 1][0] * 1.0 / self.glframe.width,
                                           o.pos_hist[-n - 1][1] * 1.0 / self.glframe.height])
                    self.glframe.jobs.append([self.glframe.drawTrace, points])

        # draw shapes of active ROIs
        for r in self.spotter.tracker.rois:
            color = (r.normal_color[0], r.normal_color[1], r.normal_color[2], r.alpha)
            for s in r.shapes:
                if s.active:
                    if s.shape == "rectangle":
                        self.glframe.jobs.append([self.glframe.drawRect, s.points, color])
                    elif s.shape == "circle":
                        self.glframe.jobs.append([self.glframe.drawCircle, s.points, color])
                    elif s.shape == "line":
                        self.glframe.jobs.append([self.glframe.drawLine, s.points, color])

        self.glframe.updateWorld()
        self.update_current_tab()

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
                   <p>This application is under heavy development. Use on your own risk.
                   <p>Python %s -  PyQt4 version %s - on %s""" % (__version__,
                                                                  platform.python_version(), QtCore.QT_VERSION_STR,
                                                                  platform.system()))

    def center_window(self):
        """
        Centers main window on screen.
        Doesn't quite work on multi-monitor setups, as the whole screen-area is taken. But as long as the window ends
        up in a predictable position...
        """
        screen = QtGui.QDesktopWidget().screenGeometry()
        window_size = self.geometry()
        self.move((screen.width() - window_size.width()) / 2, (screen.height() - window_size.height()) / 2)

    def add_tab(self, tab_widget, new_tab_class, tab_equivalent, focus_new=True):
        """
        Add new tab with Widget newTabClass and switches to it. The
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

    def remove_tab(self, tab_widget, tab):
        """
        Removing is trickier, as it has to delete the features/objects
        from the tracker!
        """
        pass

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

    def file_dialog_video(self):
        """
        Open a video file. Should finish current spotter if any by closing
        it to allow all frames/settings to be saved properly. Then instantiate
        a new spotter.
        TODO: Open file dialog in a useful folder. E.g. store the last used one
        """
        # Windows 7 uses 'HOMEPATH' instead of 'HOME'
        path = os.getenv('HOME')
        if not path:
            path = os.getenv('HOMEPATH')
        filename = QtGui.QFileDialog.getOpenFileName(self, 'Open Video', path)
        print filename

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
    def parse_config(self, path, validate=True):
        """
        Template parsing and validation.
        """
        template = ConfigObj(path, file_error=True, stringify=True,
                             configspec=DIR_SPECIFICATION)
        if validate:
            validator = Validator()
            results = template.validate(validator)
            if not results is True:
                print "Template error in file ", path
                for (section_list, key, _) in flatten_errors(template, results):
                    if key is not None:
                        print 'The "%s" key in the section "%s" failed validation' % (key, ', '.join(section_list))
                    else:
                        print 'The following section was missing:%s ' % ', '.join(section_list)
                return None
        return template

    def load_config(self, filename=None, directory=DIR_TEMPLATES):
        """
        Opens file dialog to choose template file and starts parsing of it
        """
        if filename is None:
            filename = str(QtGui.QFileDialog.getOpenFileName(self, 'Open Template', directory))
        print "Opening template", filename
        template = self.parse_config(filename)
        if template is not None:
            for f_key, f_val in template['FEATURES'].items():
                self.add_feature(f_val, f_key, focus_new=False)
            for o_key, o_val in template['OBJECTS'].items():
                self.add_object(o_val, o_key, focus_new=False)
            for r_key, r_val in template['REGIONS'].items():
                self.add_region(r_val, r_key, shapes=template['SHAPES'], focus_new=False)

    def save_config(self, filename=None, directory=DIR_TEMPLATES):
        config = ConfigObj(indent_type='    ')
        if filename is None:
            filename = str(QtGui.QFileDialog.getSaveFileName(self, 'Save Template', directory))
            if len(filename):
                config.filename = filename
            else:
                return

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
        rng = (self.glframe.width, self.glframe.height)
        for r in self.spotter.tracker.rois:
            for s in r.shapes:
                if not s in shapelist:
                    shapelist.append(s)
        config['SHAPES'] = {}
        for s in shapelist:
            section = {'p1': geom.norm_points(s.points[0], rng),
                       'p2': geom.norm_points(s.points[1], rng),
                       'type': s.shape}
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

        config.write()

    def reset_config(self):
        pass

    ###############################################################################
    ##  FEATURES Tab Updates
    ###############################################################################
    def tab_features_switch(self, idx_tab=0):
        """
        Switch to selected tab or create a new tab if the selected tab is
        the last, which should be the "+" tab. Switching through the tabs with
        the mousewheel can cause to create a lot of tabs unfortunately.
        TODO: Mousewheel handling.
        """
        #        if idx_tab == self.ui.tab_features.count() - 1:
        #            self.add_feature()
        #        else:
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
            range_area = map(int, template['range_area'])
            fixed_pos = template.as_bool('fixed_pos')
            feature = self.spotter.tracker.addLED(label,
                                                  range_hue,
                                                  range_area,
                                                  fixed_pos)
        new_tab = self.add_tab(self.ui.tab_features, TabFeatures, feature, focus_new)
        self.feature_tabs.append(new_tab)

    ###############################################################################
    ##  OBJECTS Tab Updates
    ###############################################################################
    def tab_objects_switch(self, idx_tab=0):
        """
        Switch to selected tab or create a new tab if the selected tab is
        the last, which should be the "+" tab. Switching through the tabs with
        the mousewheel can cause to create a lot of tabs unfortunately.
        TODO: Mousewheel handling.
        """
        #        if idx_tab == self.ui.tab_objects.count() - 1:
        #            self.add_object()
        #        else:
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
        self.object_tabs.append(new_tab)

    ###############################################################################
    ##  REGIONS Tab Updates
    ###############################################################################
    def tab_regions_switch(self, idx_tab=0):
        """
        Switch to selected tab or create a new tab if the selected tab is
        the last, which should be the "+" tab. Switching through the tabs with
        the mousewheel can cause to create a lot of tabs unfortunately.
        TODO: Mousewheel handling.
        """
        #        if idx_tab == self.ui.tab_regions.count() - 1:
        #            self.add_region()
        #        else:
        self.ui.tab_regions.setCurrentIndex(idx_tab)

    def add_region(self, template=None, label=None, shapes=None, focus_new=True):
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
                points = geom.scale_points([shapes[s_key]['p1'],
                                            shapes[s_key]['p2']],
                                           (self.glframe.width,
                                            self.glframe.height))
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
def main(source, destination, fps, size, gui, serial):
    app = QtGui.QApplication([])
    window = Main(source, destination, fps, size, gui, serial)
    window.show()
    window.raise_()  # needed on OSX?

    sys.exit(app.exec_())


if __name__ == "__main__":                                  #
#############################################################

    # Command line parsing
    ARGDICT = docopt(__doc__, version=None)
    DEBUG = ARGDICT['--DEBUG']
    if DEBUG:
        print(ARGDICT)

    # Debug logging
    log = logging.getLogger('ledtrack')
    log_handle = logging.StreamHandler()  # logging.FileHandler('ledtrack.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    log_handle.setFormatter(formatter)
    log.addHandler(log_handle)
    if DEBUG:
        log.setLevel(logging.INFO)  # INFOERROR
    else:
        log.setLevel(logging.ERROR)  # INFOERROR

    # Frame size parameter string 'WIDTHxHEIGHT' to size tuple (WIDTH, HEIGHT)
    size = (0, 0) if not ARGDICT['--dims'] else tuple(ARGDICT['--dims'].split('x'))

    gui = 'Qt' if not ARGDICT['--Headless'] else ARGDICT['--Headless']

    # Qt main window which instantiates spotter class with all parameters
    main(source=ARGDICT['--source'],
         destination=utils.dst_file_name(ARGDICT['--outfile']),
         fps=ARGDICT['--fps'],
         size=size,
         gui=gui,
         serial=ARGDICT['--Serial'])
