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
import numpy as np
import logging

#project libraries
sys.path.append('./lib')
from spotter import Spotter
import utils

#command line handling
sys.path.append('./lib/docopt')
from docopt import docopt


class GLFrame(QtOpenGL.QGLWidget):

    def __init__(self, *args):
        QtOpenGL.QGLWidget.__init__(self, *args)
        
        self.frame = None
#        self.angle = 0.0

    def updateWorld(self):
#        self.frame = self.detector.frame()
#        self.angle = self.angle + 5.0
        self.updateGL()
        
    def initializeGL(self):
        glClearColor(1.0, 1.0, 1.0, 1.0)        
        glClearDepth(1.0)
        glMatrixMode(GL_PROJECTION)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        if self.frame != None:
            shape = self.frame.shape
            glDrawPixels(shape[1], shape[0], GL_RGB, GL_UNSIGNED_BYTE, self.frame.tostring()[::-1]) #self.width(), self.height()

#        glRotatef(self.angle, 0.0, 1.0, 0.0)
#
#        glColor(0.1, 0.5, 0.8)
#        glBegin(OpenGL.GL.GL_TRIANGLES)
#        glVertex3f( 0.0, 0.5, 0.0) 
#        glVertex3f(-0.5,-0.5, 0.0)
#        glVertex3f( 0.5,-0.5, 0.0)
#        glEnd()

    def resizeGL(self, width, height):
        glViewport(0, 0, width, height);
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()  

    def numpy2qimage(self, array):
    	if np.ndim(array) == 2:
    		return self.gray2qimage(array)
    	elif np.ndim(array) == 3:
    		return self.rgb2qimage(array)
    	raise ValueError("can only convert 2D or 3D arrays")
    
    def gray2qimage(gray):
    	"""Convert the 2D numpy array `gray` into a 8-bit QImage with a gray
    	colormap.  The first dimension represents the vertical image axis."""
    	if len(gray.shape) != 2:
    		raise ValueError("gray2QImage can only convert 2D arrays")
    
    	gray = np.require(gray, np.uint8, 'C')
    
    	h, w = gray.shape
    
    	result = QtGui.QImage(gray.data, w, h, QtGui.QImage.Format_Indexed8)
    	result.ndarray = gray
    	for i in range(256):
    		result.setColor(i, QtGui.QColor(i, i, i).rgb())
    	return result
    
    def rgb2qimage(self, rgb):
    	"""Convert the 3D numpy array `rgb` into a 32-bit QImage.  `rgb` must
    	have three dimensions with the vertical, horizontal and RGB image axes."""
    	if len(rgb.shape) != 3:
    		raise ValueError("rgb2QImage can expects the first (or last) dimension to contain exactly three (R,G,B) channels")
    	if rgb.shape[2] != 3:
    		raise ValueError("rgb2QImage can only convert 3D arrays")
    
    	h, w, channels = rgb.shape
    
    	# Qt expects 32bit BGRA data for color images:
    	bgra = np.empty((h, w, 4), np.uint8, 'C')
    	bgra[...,0] = rgb[...,2]
    	bgra[...,1] = rgb[...,1]
    	bgra[...,2] = rgb[...,0]
    	bgra[...,3].fill(255)
    
    	result = QtGui.QImage(bgra.data, w, h, QtGui.QImage.Format_RGB32)
    	result.ndarray = bgra
    	return result                             

        
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
#        print frame
#        pixmap = self.array2pixmap(frame)
        pixmap2 = QtGui.QPixmap.fromImage(self.rgb2qimage(frame))
        self.lbl.setPixmap( pixmap2 )







class MainWindow(QtGui.QMainWindow):
    def __init__(self, source, destination, fps, size, gui, serial, parent=None):
        QtGui.QMainWindow.__init__(self)
        self.setWindowTitle('Spotter')
#        self.setGeometry(300, 100, 750, 500) # size AND position in one go
        self.resize(640, 360)
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
#        self.frame = Frame()
        self.frame = GLFrame()
        self.setCentralWidget(self.frame)

        self.spotter = Spotter(source, destination, fps, size, gui, serial)
        
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.refresh()
        self.timer.start(5)


    def refresh(self):
        self.spotter.update()
#        self.frame.update(self.spotter.newest_frame.copy())
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
            print "Closing!"
            event.accept()
        else:
            print "Not closing after all!"
            event.ignore()
            

            

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
#    main.frame.testframe()
    sys.exit(app.exec_())