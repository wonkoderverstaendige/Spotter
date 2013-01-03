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

import sys
from PyQt4 import QtGui, QtCore, QtOpenGL
from OpenGL.GL import *
#import numpy as np
import logging

#project libraries
sys.path.append('./lib')
from spotter import Spotter
import utils

#command line handling
sys.path.append('./lib/docopt')
from docopt import docopt


class GLFrame(QtOpenGL.QGLWidget):
    
    frame = None

    def __init__(self, *args):
        QtOpenGL.QGLWidget.__init__(self, *args)


    def updateWorld(self):
        self.updateGL()

        
    def initializeGL(self):
        glClearColor(0.0, 0.0, 0.0, 1.0)        
        glClearDepth(1.0)
        glMatrixMode(GL_PROJECTION)


    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        if self.frame != None:
            shape = self.frame.shape
            glDrawPixels(shape[1], shape[0], GL_RGB, GL_UNSIGNED_BYTE, self.frame.tostring()[::-1]) #self.width(), self.height()


    def resizeGL(self, width, height):
        glViewport(0, 0, width, height);
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()  



class MainWindow(QtGui.QMainWindow):
    def __init__(self, source, destination, fps, size, gui, serial, parent=None):
        QtGui.QMainWindow.__init__(self)
        self.setWindowTitle('Spotter')
#        self.setGeometry(300, 100, 750, 500) # size AND position in one go
        self.resize(720, 400)
        self.center()

        # Status bar
        self.statusBar().showMessage("Ready")
        
        # Actions
        exit = QtGui.QAction(QtGui.QIcon('icons/exit.png'), 'Exit', self)
        exit.setShortcut('Ctrl+Q')
        exit.setStatusTip('Exit Spotter')
        self.connect(exit, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()'))
        
        # Menu bar
        menubar = self.menuBar()
        file = menubar.addMenu("&File")
        file.addAction(exit)
        
        # Toolbar
        toolbar = self.addToolBar('Exit')
        toolbar.addAction(exit)

        # Spotter main class, handles Grabber, Writer, Tracker, Funker      
        self.spotter = Spotter(source, destination, fps, size, gui, serial)      
      
        # Central widget
        self.frame = GLFrame()
        self.setCentralWidget(self.frame)

        # Starts main frame grabber loop
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.refresh()
        self.timer.start(30)


    def refresh(self):
        self.spotter.update()
        self.frame.frame = self.spotter.newest_frame
        self.frame.updateWorld()
        

    def center(self):
        screen = QtGui.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)


    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, 
                                          'Exit confirmation',
                                          'Are you sure?',
                                          QtGui.QMessageBox.Yes,
                                          QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
            
            
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
            
    app = QtGui.QApplication([]) # sys.argv    
    main = MainWindow(source    = ARGDICT['--source'],
                    destination = utils.dst_file_name( ARGDICT['--outfile'] ),
                    fps         = ARGDICT['--fps'],
                    size        = size,
                    gui         = gui,
                    serial      = ARGDICT['--Serial'])
    main.show()
    sys.exit(app.exec_())