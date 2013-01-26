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
    -d --dims DIMS      Frame size [default: 320x200]
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

NO_EXIT_CONFIRMATION = True

import sys
import os
import platform
from PyQt4 import QtGui, QtCore
import logging

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

#command line handling
sys.path.append('./lib/docopt')
from docopt import docopt


__version__ = 0.1

class Main(QtGui.QMainWindow):
    
    feature_templates = dict( default = [(0, 1), True],
                              redLED = [( 160, 5 ), False],
                              blueLED = [( 105, 135 ), False],
                              greenLED = [( 15, 90 ), True] )
                              
    object_templates = dict( default = [[], True],
                             Subject = [['redLED', 'blueLED'], True],
                             Sync    = [['greenLED'], False] )

    shape_templates = dict( LeftSensor   = ['Rectangle', [(0.20, 0.00), (0.30, 1.00)]],
                            CenterSensor = ['Rectangle', [(0.45, 0.20), (0.55, 0.80)]],
                            RightSensor  = ['Rectangle', [(0.70, 0.00), (0.80, 1.00)]] )

    region_templates = dict( default = [[]],
                             LeftReward  = [['LeftSensor']],
                             Trigger     = [['CenterSensor']],
                             RightReward = [['RightSensor']] )
                        
    full_templates = dict( LinearTrack =  [feature_templates, object_templates, region_templates] )

    def __init__(self, source, destination, fps, size, gui, serial):
        QtGui.QMainWindow.__init__(self)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Exit Signals
        self.ui.actionE_xit.setShortcut('Ctrl+Q')
        self.ui.actionE_xit.setStatusTip('Exit Spotter')
        self.connect(self.ui.actionE_xit, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()'))

        self.centerWindow()

        # About window
        self.connect(self.ui.actionAbout, QtCore.SIGNAL('triggered()'), self.about)

        # Menubar items
        self.connect(self.ui.actionFile, QtCore.SIGNAL('triggered()'), self.openFile)

        # Spotter main class, handles Grabber, Writer, Tracker, Chatter
        self.spotter = Spotter(source, destination, fps, size, gui, serial)

        # OpenGL frame
        self.glframe = GLFrame()
        self.ui.frame_video.addWidget(self.glframe)
        self.glframe.setSizePolicy( QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding )

        # handling mouse events by the tabs for selection of regions etc.
        self.glframe.sig_event.connect(self.mouse_event_to_tab)


        # Loading debugging/example templates
        for t in self.full_templates:        
            self.ui.combo_templates.addItem(t)
        
        self.connect(self.ui.btn_load_template, QtCore.SIGNAL('clicked()'), self.load_templates)
        self.connect(self.ui.btn_feature_template, QtCore.SIGNAL('clicked()'), self.load_templates)
        self.connect(self.ui.btn_object_template, QtCore.SIGNAL('clicked()'), self.load_templates)
        self.connect(self.ui.btn_region_template, QtCore.SIGNAL('clicked()'), self.load_templates)

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


        # Starts main frame grabber loop
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.refresh()
        self.glframe.resizeFrame()
        self.timer.start(30)
        
        self.serial_timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.serial_check)
        self.serial_timer.start(10)

    def serial_check(self):
        if self.spotter.chatter.is_open():
#            print("buffer in: " + str(self.spotter.chatter.bytes_available()) + 
#                   "; buffer out: " + str(len(self.spotter.chatter.inst_buffer)))
            self.spotter.chatter.read_all()

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
               <p>This application can and will be used for funs.
               <p>Python %s -  PyQt4 version %s - on %s""" % (__version__,
                platform.python_version(), QtCore.QT_VERSION_STR, platform.system()))


    def centerWindow(self):
        """ Centers main window on screen."""
        screen = QtGui.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)


    def load_templates(self):
        """ 
        Loads and creates all LEDs and Objects from templates. This will
        probably be the place later the standard set of features/objects/ROIs
        etc. will be handled on startup.
        TODO: Add Object templates
        """
        active_top_tab_label = self.get_top_tab_label()
        if active_top_tab_label == "Settings":
            templates_list = self.full_templates[str(self.ui.combo_templates.currentText())]
            for f_key in templates_list[0]:
                if not f_key == 'default':
                    self.add_feature(self.feature_templates[f_key], f_key)
            for o_key in templates_list[1]:
                if not o_key == 'default':
                    self.add_object(self.object_templates[o_key], o_key)
            for r_key in templates_list[2]:
                if not r_key == 'default':
                    self.add_region(self.region_templates[r_key], r_key)

        elif active_top_tab_label == "Features":
            for f_key in self.feature_templates:
                if not f_key == 'default':
                    self.add_feature(self.feature_templates[f_key], f_key)

        elif active_top_tab_label == "Objects":
            for o_key in self.object_templates:
                if not o_key == 'default':
                    self.add_object(self.object_templates[o_key], o_key)

        elif active_top_tab_label == "ROIs":
            for r_key in self.region_templates:
                if not r_key == 'default':
                    self.add_region(self.region_templates[r_key], r_key)

        elif active_top_tab_label == "SerialOut":
            return "Serial"


    #Feature Tab List Updates
    def tab_features_switch(self, idx_tab = 0):
        """ 
        Switch to selected tab or create a new tab if the selected tab is
        the last, which should be the "+" tab. Switching through the tabs with
        the mousewheel can cause to create a lot of tabs unfortunately.
        TODO: Mousewheel handling.
        """
        if idx_tab == self.ui.tab_features.count() - 1:
            self.add_feature()
        else:
            self.ui.tab_features.setCurrentIndex(idx_tab)


    def add_feature(self, template = None, label = None):
        """ 
        Create a feature from trackables and add a corresponding tab to
        the tab widget, which is linked to show and edit feature properties.
        TODO: Create new templates when running out by fitting them into
        the colorspace somehow.
        """
        if not template:
            template = self.feature_templates['default']
            label = 'LED_'+str(len(self.spotter.tracker.leds))
        feature = self.spotter.tracker.addLED(label, *template)
        new_tab = self.add_tab(self.ui.tab_features, TabFeatures, feature)
        self.feature_tabs.append(new_tab)


    # Object Tab List Updates
    def tab_objects_switch(self, idx_tab = 0):
        """ 
        Switch to selected tab or create a new tab if the selected tab is
        the last, which should be the "+" tab. Switching through the tabs with
        the mousewheel can cause to create a lot of tabs unfortunately.
        TODO: Mousewheel handling.
        """
        if idx_tab == self.ui.tab_objects.count() - 1:
            self.add_object()
        else:
            self.ui.tab_objects.setCurrentIndex(idx_tab)


    def add_object(self, template = None, label = None):
        """ 
        Create a new object that will be linked to LEDs and/r ROIs to
        track and trigger events.
        TODO: Create new objects even when running out of templates for example
        by randomizing offsets.
        """
        if not template:
            template = self.object_templates['default']
            # list of features, if enough in list of features so far
        if not label:
            label = 'Object_' + str(len(self.spotter.tracker.oois))

        features = []
        for n in xrange(min(len(self.spotter.tracker.leds), len(template[0]))):
            for l in self.spotter.tracker.leds:
                if template[0][n] == l.label:
                    features.append(l)

        _object = self.spotter.tracker.addOOI(features, label, template[1])
        new_tab = self.add_tab(self.ui.tab_objects, TabObjects, _object)
        self.object_tabs.append(new_tab)


    # Regions Tab List Updates
    def tab_regions_switch(self, idx_tab = 0):
        """ 
        Switch to selected tab or create a new tab if the selected tab is
        the last, which should be the "+" tab. Switching through the tabs with
        the mousewheel can cause to create a lot of tabs unfortunately.
        TODO: Mousewheel handling.
        """
        if idx_tab == self.ui.tab_regions.count() - 1:
            self.add_region()
        else:
            self.ui.tab_regions.setCurrentIndex(idx_tab)


    def add_region(self, template = None, label = None):
        """ 
        Create a new region of interest that will be that will be linked
        to Objects with conditions to trigger events.
        TODO: New regions created empty!
        """
        if not template:
            template = self.region_templates['default']
        if not label:
            label =  'ROI_' + str(len(self.spotter.tracker.rois))
        
        shape_list = []
        shape_keys = template[0]
        for sk in shape_keys:
            if not sk == "default":
                shape_template = self.shape_templates[sk]
                shape_template[1] = geom.scale_points(shape_template[1],
                                                     (self.glframe.width, 
                                                      self.glframe.height) )
                shape_list.append([sk, shape_template])
        
        region = self.spotter.tracker.addROI(shape_list, label)
        new_tab = self.add_tab(self.ui.tab_regions, TabRegions, region)
        self.region_tabs.append(new_tab)


    def add_serial(self, serial_object, label = None):
        """ 
        Serial object tab. Probably an Arduino Mega 2560.
        """
        new_tab = self.add_tab(self.ui.tab_serial, TabSerial, serial_object)
        self.serial_tabs.append(new_tab)


    def add_tab(self, tabwidget, newTabClass, tab_equivalent):
        """ 
        Add new tab with Widget newTabClass and switches to it. The
        tab_equivalent is the object that is being represented by the tab,
        for example an LED or Object.
        """
        new_tab = newTabClass.Tab(self, tab_equivalent)
        tabwidget.insertTab(tabwidget.count() - 1, new_tab, new_tab.label)
        tabwidget.setCurrentIndex(tabwidget.count()-2)
        return new_tab


    def remove_tab(self, tabwidget, tab):
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

        elif active_top_tab_label == "SerialOut":
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


    def openFile(self):
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


    def refresh(self):
        self.spotter.update()
        self.glframe.frame = self.spotter.newest_frame

        # Append Object tracking markers to the list of things that have
        # to be drawn onto the GL frame
        for l in self.spotter.tracker.leds:
            if not l.pos_hist[-1] == None and l.marker_visible:
                self.glframe.jobs.append([self.glframe.drawCross, l.pos_hist[-1], 14, l.lblcolor])

        for o in self.spotter.tracker.oois:
            if not o.guessed_pos == None:
                self.glframe.jobs.append([self.glframe.drawCross, o.guessed_pos, 8, (1.0, 1.0, 1.0, 1.0), 7, True])
                if o.traced:
                    points = []
                    for n in xrange(min(len(o.pos_hist), 100)):
                        if not o.pos_hist[-n-1] == None:
                            points.append([o.pos_hist[-n-1][0]*1.0/self.glframe.width, o.pos_hist[-n-1][1]*1.0/self.glframe.height])
                    self.glframe.jobs.append([self.glframe.drawTrace, points])

        for r in self.spotter.tracker.rois:
            color = (r.normal_color[0], r.normal_color[1], r.normal_color[2], r.alpha)
            for s in r.shapes:
                if s.active:
                    if s.shape == "Rectangle":
                        self.glframe.jobs.append([self.glframe.drawRect, s.points, color])
                    elif s.shape == "Circle":
                        self.glframe.jobs.append([self.glframe.drawCircle, s.points, color])
                    elif s.shape == "Line":
                        self.glframe.jobs.append([self.glframe.drawLine, s.points, color])
        self.glframe.updateWorld()

        self.update_current_tab()


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
                                               'Exit confirmation', 
                                               'Are you sure?', 
                                               QtGui.QMessageBox.Yes, 
                                               QtGui.QMessageBox.No )
        if reply == QtGui.QMessageBox.Yes:
            self.spotter.exitMain()
            event.accept()
        else:
            event.ignore()


#############################################################
def main(source, destination, fps, size, gui, serial):
    app = QtGui.QApplication([])
    window = Main(source, destination, fps, size, gui, serial)
    window.show()
    window.raise_() # needed on OSX?

    sys.exit(app.exec_())

if __name__ == "__main__":                                  #
#############################################################

    # Command line parsing
    ARGDICT = docopt( __doc__, version=None )
    DEBUG   = ARGDICT['--DEBUG']
    if DEBUG: print( ARGDICT )

    # Debug logging
    log = logging.getLogger('ledtrack')
    loghdl = logging.StreamHandler()#logging.FileHandler('ledtrack.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s') #
    loghdl.setFormatter( formatter )
    log.addHandler( loghdl )
    if DEBUG:
        log.setLevel( logging.INFO ) #INFOERROR
    else:
        log.setLevel( logging.ERROR ) #INFOERROR

    # Frame size parameter string 'WIDTHxHEIGHT' to size tupple (WIDTH, HEIGHT)
    size = (0, 0) if not ARGDICT['--dims'] else tuple( ARGDICT['--dims'].split('x') )

    gui = 'Qt' if not ARGDICT['--Headless'] else ARGDICT['--Headless']

    # Qt main window which instantiates spotter class with all parameters
    main(source    = ARGDICT['--source'],
         destination = utils.dst_file_name( ARGDICT['--outfile'] ),
         fps         = ARGDICT['--fps'],
         size        = size,
         gui         = gui,
         serial      = ARGDICT['--Serial'])
