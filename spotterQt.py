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
from PyQt4 import QtGui, QtCore
import logging

#project libraries
sys.path.append('./lib')
from spotter import Spotter
import utils

#Qt user interface files
sys.path.append('./ui')
from GLFrame import GLFrame
from mainUi import Ui_MainWindow
import TabFeatures
import TabObjects

#command line handling
sys.path.append('./lib/docopt')
from docopt import docopt


class Main(QtGui.QMainWindow):

    led_templates = [['red', ( 160, 5 ), False],
                     ['blue', ( 105, 135 ), False],
                     ['green', ( 15, 90 ), True]]


    def __init__(self, source, destination, fps, size, gui, serial):
        QtGui.QMainWindow.__init__(self)
        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Exit Signals
        self.ui.actionE_xit.setShortcut('Ctrl+Q')
        self.ui.actionE_xit.setStatusTip('Exit Spotter') 
        self.connect(self.ui.actionE_xit, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()'))

        self.centerWindow()

        # Spotter main class, handles Grabber, Writer, Tracker, Funker      
        self.spotter = Spotter(source, destination, fps, size, gui, serial)
        
        # OpenGL frame        
        self.frame = GLFrame()
        self.ui.frame_video.addWidget(self.frame)
        self.frame.setSizePolicy( QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding )

        # Features tab widget
        self.feature_tabs = []
        self.connect(self.ui.tab_features, QtCore.SIGNAL('currentChanged(int)'), self.tab_features_switch)
        self.connect(self.ui.btn_new_feature_tab, QtCore.SIGNAL('clicked()'), self.add_feature)

        # Objects tab widget
        self.connect(self.ui.tab_objects, QtCore.SIGNAL('currentChanged(int)'), self.tab_objects_switch) 
        self.connect(self.ui.btn_new_object_tab, QtCore.SIGNAL('clicked()'), self.add_object)
        self.object_tabs = []

        # Starts main frame grabber loop
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.refresh()
        self.frame.resizeFrame()
        self.timer.start(30)
       

    def centerWindow(self):
        screen = QtGui.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)
 
    #Feature Tab List Updates
    def tab_features_switch(self, idx_tab = 0):
        if idx_tab == self.ui.tab_features.count() - 1:
            self.add_feature()
        else:
            self.ui.tab_features.setCurrentIndex(idx_tab)

    def add_feature(self):
        # TODO:
            #Example features, REMOVE   
        new_led = self.spotter.tracker.addLED(*self.led_templates[self.ui.tab_features.count()-2])
        new_tab = self.add_tab(self.ui.tab_features, TabFeatures, new_led)
        self.feature_tabs.append(new_tab)

            
    # Object Tab List Updates
    def tab_objects_switch(self, idx_tab = 0):
        if idx_tab == self.ui.tab_features.count() - 1:
            self.add_object()
        else:
            self.ui.tab_objects.setCurrentIndex(idx_tab)

    def add_object(self,):
        # TODO:
            #Example Object, REMOVE        
        new_object = self.spotter.tracker.addOOI(self.spotter.tracker.leds[1:3], "Subject")
        self.add_tab(self.ui.tab_objects, TabObjects, new_object)
        self.object_tabs.append(new_object)

        # TODO:
            #Example Object, REMOVE        

    def add_tab(self, tabwidget, newTabClass, tab_equivalent):
        """ Addd new tab with Widget newTabClass and switches to it. """
#        # create a unique label for the Tab
#        num_newLabel = tabwidget.count() - 1
#        lbl_list = []
#        for t in range(tabwidget.count()):
#            lbl_list.append(str(tabwidget.tabText(t)))
#        while ''.join([newTabClass.tab_lbl, str(num_newLabel)]) in lbl_list:
#            num_newLabel += 1

        # Add a new Tab of the class specific to the calling TabWidget
        new_tab = newTabClass.Tab(self, tab_equivalent ) #''.join([newTabClass.tab_lbl, str(num_newLabel)]), 
        tabwidget.insertTab(tabwidget.count() - 1, new_tab, new_tab.name)
        
        # switch to new tab            
        tabwidget.setCurrentIndex(tabwidget.count()-2)
        return new_tab


    def remove_tab(self, tabwidget, tab):
        """ Removing is trickier, as it has to delete the features/objects
        from the tracker!
        """
 
 
    def closeEvent(self, event):
        if NO_EXIT_CONFIRMATION:
            event.accept()
            return
        reply = QtGui.QMessageBox.question(self, 'Exit confirmation', 'Are you sure?', QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()       


    def refresh(self):
        self.spotter.update()
        self.frame.frame = self.spotter.newest_frame
        
        # Append Object tracking markers to the list of things that have 
        # to be drawn onto the GL frame
        for l in self.spotter.tracker.leds:
            if not l.pos_hist[-1] == None:
                self.frame.jobs.append([self.frame.drawCross, l.pos_hist[-1][0], l.pos_hist[-1][1], 20, l.lblcolor])
        
        for o in self.spotter.tracker.oois:
            if not o.guessed_pos == None:
                self.frame.jobs.append([self.frame.drawCross, o.guessed_pos[0], o.guessed_pos[1], 10, (1.0, 1.0, 1.0, 1.0)])

        self.frame.updateWorld()


def main(source, destination, fps, size, gui, serial):
    app = QtGui.QApplication([])
    window = Main(source, destination, fps, size, gui, serial)
    window.show()
    
    sys.exit(app.exec_())


            
#############################################################
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
        
    # no GUI, may later select GUI backend, i.e., Qt or cv2.highgui etc.
    gui = 'Qt' if not ARGDICT['--Headless'] else ARGDICT['--Headless']
            
    # Qt main window which instantiates spotter class with all parameters    
    main(source    = ARGDICT['--source'],
         destination = utils.dst_file_name( ARGDICT['--outfile'] ),
         fps         = ARGDICT['--fps'],
         size        = size,
         gui         = gui,
         serial      = ARGDICT['--Serial'])
