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
from PyQt4 import QtGui, QtCore
import numpy as np
import logging

#project libraries
from spotter import Spotter

#command line handling
sys.path.append('./lib/docopt')
from docopt import docopt

class Frame(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.hbox = QtGui.QHBoxLayout(self)
        self.lbl = QtGui.QLabel(self)
        self.hbox.addWidget(self.lbl)
        self.setLayout(self.hbox)    
    
    
#    def paintEvent(self, event):
#        paint = QtGui.QPainter()
#        paint.begin(self)
#        
#        color = QtGui.QColor(0, 0, 0)
#        color.setNamedColor('#d4d4d4')
#        paint.setPen(color)
#        
#        paint.setBrush(QtGui.QColor(0, 0, 0, 255))
#        paint.drawRect(0, 0, 640, 360)
#        
#        paint.end()
        
    def array2pixmap(self, nparray ):
        shape = nparray.shape
        a = nparray.astype(np.uint32)
        b = (255 << 24 | a[:,:,0] << 16 | a[:,:,1] << 8 | a[:,:,2]).flatten()
        im = QtGui.QImage(b, shape[0], shape[1], QtGui.QImage.Format_RGB32)
        return QtGui.QPixmap.fromImage(im)
        
    def testframe(self):
        a = np.random.randint(0,256,size=(1000,1000,3)).astype(np.uint32)
        self.lbl.setPixmap( self.array2pixmap(a) )
        
    def update( self, frame ):
        print "Update!"
        self.lbl.setPixmap( self.array2pixmap(frame) )
        

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self)
        self.setWindowTitle('Spotter')
#        self.setGeometry(300, 100, 750, 500) # size AND position in one go
        self.resize(700, 400)
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
        
        # Central widget
        self.frame = Frame()
        self.setCentralWidget(self.frame)

        self.spotter = Spotter()


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
            
            
    def nextView( self ):
        if self.viewMode == 0:
            self.viewMode = 0
        else:
            self.viewMode += 1


    def onKey( self, key ):
        if key>0:
            print key % 0x100

        if (key % 0x100 == 114):
            print "Make ROI"

        # <SPACE> to toggle video pause
        if ( key % 0x100 == 32 ):
            self.paused = not self.paused

        # <ESCAPE> to EXIT
        if ( key % 0x100 == 27 ):
            self.parent.exitMain()
            

if __name__ == "__main__":
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

    app = QtGui.QApplication([]) # sys.argv    
    main = MainWindow()
    main.show()
    main.frame.testframe()
    sys.exit(app.exec_())