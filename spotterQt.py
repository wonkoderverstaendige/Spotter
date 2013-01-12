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
import math
#import numpy as np
import logging

#project libraries
sys.path.append('./lib')
from spotter import Spotter
import utils

#Qt user interface files
sys.path.append('./ui')
from mainUi import Ui_MainWindow

#command line handling
sys.path.append('./lib/docopt')
from docopt import docopt


class GLFrame(QtOpenGL.QGLWidget):
    
    frame = None
    width = None
    height = None
    m_x1 = -1
    m_x2 = -1
    m_y1 = -1
    m_y2 = -1
    pressed = False
    dragging = False
    aratio = None       # aspect ratio float = width/height

    def __init__(self, *args):
        QtOpenGL.QGLWidget.__init__(self, *args)
        self.setMouseTracking(True)
        self.cursor = "Cross"


    def updateWorld(self):
        self.updateGL()


    def initializeGL(self, width = 20, height = 20):
        """ Initialization of the GL frame. 
        TODO: glOrtho should set to size of the frame which would allow
        using absolute coordinates in range/domain of original frame
        """
        glClearColor(0.0, 0.0, 0.0, 1.0)        
        glClearDepth(1.0)
        glOrtho(0, 1, 1, 0, -1, 1)
        glMatrixMode(GL_PROJECTION)


    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Draw the numpy array onto the GL frame, stringify first
        # NB: Currently flips the frame.
        if self.frame != None:
            shape = self.frame.shape
            glDrawPixels(shape[1], shape[0], GL_RGB, GL_UNSIGNED_BYTE, self.frame.tostring()[::-1])

        color = (0.5, 0.5, 0.5, 0.5)
        if self.dragging:
            x1 = self.m_x1/float(self.width)
            y1 = self.m_y1/float(self.height)
            x2 = self.m_x2/float(self.width)
            y2 = self.m_y2/float(self.height)
            
            modifiers = QtGui.QApplication.keyboardModifiers()
            if modifiers == QtCore.Qt.ShiftModifier:
                dx = x2-x1
                dy = y2-y1
                r = dx if abs(dx)>abs(dy) else dy
                
                self.drawCircle(x1, y1, r, color, 16)
            elif modifiers == QtCore.Qt.ControlModifier:
                print('Control+Click')
            else:
                self.drawRect(x1, y1, x2, y2, color)
        else:
            self.drawCross(self.m_x1, self.m_y1, 20, color)


    def resizeGL(self, width, height):
        """ Resize frame when widget resized """
        self.width = width
        self.height = height
        self.aratio = width*1.0/height
        
        # scale coordinate system of viewport to frame size, or similarly
        # important sounding task I do not understand...
        glViewport(0, 0, width, height)
        
        # DOESN't WORK!!
#        glOrtho(0, width, height, 0, -1, 1)
        glMatrixMode(GL_PROJECTION)
        
        # Enable rational alpha blending
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Load identity matrix
        glLoadIdentity()


    def drawCross(self, x, y, size, color, gap = 7):
        """ Draw colored cross to mark tracked features """
        x = x*1.0/self.width
        y = y*1.0/self.height
        dx = size*.5/self.width
        dy = size*.5/self.height
        glColor(*color)
        glBegin(GL_LINES)
        
        # vertical line
        glVertex( x-dx, y, 0.0)
        glVertex( x+dx, y, 0.0)
        glEnd()

        # horizontal line
        glColor(*color)
        glBegin(GL_LINES)
        glVertex( x, y+dy, 0.0)
        glVertex( x, y-dy, 0.0)
        glEnd()


#        glColor4f(0.0, 0.0, 1.0, 0.5)
#        glRectf(-.5, -.5, .5, .5)
#        glColor3f(1.0, 0.0, 0.0)
#        glBegin(GL_LINES)
#        glVertex3f(0, 0, 0)
#        glVertex3f(20, 20, 0)
#        glEnd()        
        
#        glColor(0.0, 1.0, 0.0)
#        glBegin(GL_LINES)
#        glVertex( 0, 0, 0)
#        glVertex( 0, 1, 0)
#        glEnd()
#        glColor(0.0, 0.0, 1.0)
#        glBegin(GL_LINES)
#        glVertex( 0, 0, 0)
#        glVertex( 0, 0, 1)
#        glEnd()

#        glFlush()


    def drawRect(self, x1, y1, x2, y2, color):
        glColor(*color)
        glRectf(x1, y1, x2, y2)


    def drawCircle(self, cx, cy, r, color, num_segments):
        """ Quickly draw approximate circle. Algorithm from:
            http://slabode.exofire.net/circle_draw.shtml    
        """
        theta = 2 * math.pi / float(num_segments)
        c = math.cos(theta) # pre-calculate cosine
        s = math.sin(theta) # and sine
        t = 0
        x = r # we start at angle = 0 
        y = 0
        
        glColor(*color)
        glBegin(GL_LINE_LOOP)
        for ii in range(num_segments):
            # Circle requires correction for aspect ratio
            glVertex2f((x/self.aratio + cx), (y + cy))    # output vertex
            t = x
            x = c * x - s * y
            y = s * t + c * y
        glEnd()            

        
    def drawTail(self, array):
        """ Draw trace of position given in array.
        TODO: Draw trace in immediate mode via vertex and color arrays
        """
#         # Second Spiral using "array immediate mode" (i.e. Vertex Arrays)
#        glEnableClientState(GL_VERTEX_ARRAY)
#        spiral_array = []
#        radius = 0.8
#        x = radius*math.sin(0)
#        y = radius*math.cos(0)
#        glColor(1.0, 0.0, 0.0)
#        for deg in xrange(820):
#            spiral_array.append([x, y])
#            rad = math.radians(deg)
#            radius -= 0.001
#            x = radius*math.sin(rad)
#            y = radius*math.cos(rad)
#        glVertexPointerf(spiral_array)
#        glDrawArrays(GL_LINE_STRIP, 0, len(spiral_array))


    def resizeFrame(self):
        if self.frame != None:
            self.framesize = self.frame.shape
            self.setMinimumSize(self.frame.shape[1], self.frame.shape[0])
            self.setMaximumSize(self.frame.shape[1], self.frame.shape[0])  
#            self.setMinimumSize(self.framesize[1], self.framesize[0])
#            self.setMaximumSize(self.framesize[1], self.framesize[0]) 

    def mouseMoveEvent(self, e):
#        if int(mouseEvent.buttons()) != QtCore.Qt.NoButton :
#            # user is dragging
#            delta_x = mouseEvent.x() - self.oldx
#            delta_y = self.oldy - mouseEvent.y()
#            if int(mouseEvent.buttons()) & QtCore.Qt.LeftButton :
#                if int(mouseEvent.buttons()) & QtCore.Qt.MidButton :
#                    pass                    
##                    print delta_x
#                else:
#                    pass
##                    print delta_y
#            elif int(mouseEvent.buttons()) & QtCore.Qt.MidButton :
#            self.update()
        if self.pressed:        
            if (abs(e.x() - self.m_x1) + abs(e.y() - self.m_y1)) > 2:
                self.dragging = True
                self.m_x2 = e.x()
                self.m_y2 = e.y()
        else:
            self.m_x1 = e.x()
            self.m_y1 = e.y()
            

    def mouseDoubleClickEvent(self, mouseEvent):
        print "double click"

        
    def mousePressEvent(self, e):
        self.pressed = True
        self.m_x1 = e.x()
        self.m_y1 = e.y()


    def mouseReleaseEvent(self, e):
        self.pressed = False
        self.dragging = False
        self.m_x1 = e.x()
        self.m_y1 = e.y()



class Main(QtGui.QMainWindow):
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
        self.ui.horizontalLayout_3.addWidget(self.frame)
        self.frame.setSizePolicy( QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding )
        self.connect(self.ui.horizontalLayout_3, QtCore.SIGNAL('mouseMoveEvent()'), self.coords)         
        

        # Tab widget
        self.tabs = self.ui.tabWidget
        self.connect(self.ui.tabWidget, QtCore.SIGNAL('currentChanged(int)'), self.tabUpdate)        


        # Starts main frame grabber loop
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.refresh()
        self.frame.resizeFrame()
        self.timer.start(30)
        
        
    def coords(self):
        self.ui.statusbar.showMessage("coords")

    def centerWindow(self):
        screen = QtGui.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)
 
    def tabUpdate(self, tab):
        if tab == self.ui.tabWidget.count() - 1:
            self.ui.tabWidget.insertTab(tab, QtGui.QWidget(), str(self.ui.tabWidget.count()))
#            self.ui.tabWidget.
            self.ui.tabWidget.setCurrentIndex(self.ui.tabWidget.count()-2)
        else:
            self.ui.tabWidget.setCurrentIndex(tab)
 
    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, 'Exit confirmation', 'Are you sure?', QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()       


    def refresh(self):
        self.spotter.update()
        self.frame.frame = self.spotter.newest_frame
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
