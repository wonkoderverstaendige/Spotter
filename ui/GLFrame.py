# -*- coding: utf-8 -*-
"""
Created on Sat Jan 12 08:28:52 2013
@author: <Ronny Eichler> ronny.eichler@gmail.com

OpenGL widget to draw video and primites into a GL context
"""

from PyQt4 import QtGui, QtCore, QtOpenGL
from OpenGL.GL import *
import math
import numpy as np
import geometry as geom


class GLFrame(QtOpenGL.QGLWidget):

    frame = None
    width = 1
    height = 1
    m_x1 = -50
    m_x2 = -50
    m_y1 = -50
    m_y2 = -50
    pressed = False
    dragging = False
    aratio = None       # aspect ratio float = width/height
    jobs = None

    sig_event = QtCore.pyqtSignal(str, object)

    def __init__(self, *args):
        QtOpenGL.QGLWidget.__init__(self, *args)
        self.setMouseTracking(True)
        self.setCursor(QtGui.QCursor(QtCore.Qt.BlankCursor))
        self.resize_canvas()

        self.jobs = []
        self.spotter = None

    def update_world(self):
        if self.spotter is None:
            return

        self.frame = self.spotter.newest_frame.img
        if self.frame is None:
            return

        self.resize_canvas()

        # draw crosses
        for l in self.spotter.tracker.leds:
            if l.pos_hist[-1] is not None and l.marker_visible:
                self.jobs.append([self.drawCross, l.pos_hist[-1], 14, l.lblcolor])

        # draw search windows if adaptive tracking is used:
        if self.spotter.tracker.adaptive_tracking:
            for l in self.spotter.tracker.leds:
                if l.adaptive_tracking and l.search_roi is not None:
                    self.jobs.append([self.drawBox, l.search_roi.points,
                                      (l.lblcolor[0], l.lblcolor[1], l.lblcolor[2],0.25)])

        # draw crosses and traces for objects
        for o in self.spotter.tracker.oois:
            if o.position is not None:
                self.jobs.append([self.drawCross, o.position, 8,
                                  (1.0, 1.0, 1.0, 1.0), 7, True])
                if o.traced:
                    points = []
                    for n in xrange(min(len(o.pos_hist), 100)):
                        if o.pos_hist[-n - 1] is not None:
                            points.append([o.pos_hist[-n - 1][0] * 1.0 / self.width,
                                           o.pos_hist[-n - 1][1] * 1.0 / self.height])
                    self.jobs.append([self.drawTrace, points])

        # draw shapes of active ROIs
        for r in self.spotter.tracker.rois:
            color = (r.normal_color[0], r.normal_color[1], r.normal_color[2], r.alpha)
            for s in r.shapes:
                if s.active:
                    if s.shape == "rectangle":
                        self.jobs.append([self.drawRect, s.points, color])
                    elif s.shape == "circle":
                        self.jobs.append([self.drawCircle, s.points, color])
                    elif s.shape == "line":
                        self.jobs.append([self.drawLine, s.points, color])

        self.updateGL()

    def initializeGL(self):  # , width=1, height=1
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
        if self.frame is not None:
            shape = self.frame.shape
            glDrawPixels(shape[1], shape[0], GL_RGB, GL_UNSIGNED_BYTE, np.fliplr(self.frame).tostring()[::-1])

        color = (0.5, 0.5, 0.5, 0.5)
        if self.dragging:
            p1 = (self.m_x1, self.m_y1)
            p2 = (self.m_x2, self.m_y2)

            modifiers = QtGui.QApplication.keyboardModifiers()
            if modifiers == QtCore.Qt.ShiftModifier:
                radius = geom.distance(p1, p2)
                p2_c = (int(p1[0]), p1[1]+radius)
                self.drawCircle((p1, p2_c), color, 16)
            elif modifiers == QtCore.Qt.ControlModifier:
                self.drawLine((p1, p2), color)
            else:
                self.drawRect((p1, p2), color)
#        else:
        self.drawCross((self.m_x1, self.m_y1), 20, color)

        # Process job queue
        self.process_paint_jobs()

    def process_paint_jobs(self):
        """ This puny piece of code is IMPORTANT! It handles all external
        drawing jobs! That looks really un-pythonic, by the way!
        j[0] is the reference to the drawing function
        (*j[1:]) expands the parameters for the drawing function to be called
        """
        while self.jobs:
            j = self.jobs.pop()
            draw_func = j[0]
            draw_func(*j[1:])

    def resizeGL(self, width, height):
        """ Resize frame when widget is being resized. """
        self.width = width
        self.height = height
        self.aratio = width*1.0/height

        # scale coordinate system of viewport to frame size, or similarly
        # important sounding task I do not understand...
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)

        # DOESN'T WORK!!
#        glOrtho(0, width, height, 0, -1, 1)

        # Enable rational alpha blending
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Load identity matrix
        glLoadIdentity()

    def mouseMoveEvent(self, mouseEvent):
        if int(mouseEvent.buttons()) != QtCore.Qt.NoButton:
            # user is dragging
            self.sig_event.emit('mouseDrag', mouseEvent)
            if int(mouseEvent.buttons()) == QtCore.Qt.LeftButton:
                self.dragging = True
                self.m_x2 = mouseEvent.x()
                self.m_y2 = mouseEvent.y()
                return
        self.m_x1 = mouseEvent.x()
        self.m_y1 = mouseEvent.y()

    def mouseDoubleClickEvent(self, mouseEvent):
        self.sig_event.emit('mouseDoubleClick', mouseEvent)

    def mousePressEvent(self, mouseEvent):
        self.sig_event.emit('mousePress', mouseEvent)
        self.pressed = True
        self.m_x1 = mouseEvent.x()
        self.m_y1 = mouseEvent.y()

    def mouseReleaseEvent(self, mouseEvent):
        self.sig_event.emit('mouseRelease', mouseEvent)
        self.pressed = False
        self.dragging = False
        self.m_x1 = mouseEvent.x()
        self.m_y1 = mouseEvent.y()

    def drawLine(self, points, color):
        x1 = points[0][0]*1.0/self.width
        y1 = points[0][1]*1.0/self.height
        x2 = points[1][0]*1.0/self.width
        y2 = points[1][1]*1.0/self.height

        glColor(*color)
        glBegin(GL_LINES)
        glVertex(x1, y1, 0.0)
        glVertex(x2, y2, 0.0)
        glEnd()

    def drawCross(self, point, size, color, gap = 7, angled=False):
        """ Draw colored cross to mark tracked features """
        x = point[0]*1.0/self.width
        y = point[1]*1.0/self.height

        dx = size*.5/self.width
        dy = size*.5/self.height

        glColor(*color)
        if angled:
            # diagonal line 1
            glBegin(GL_LINES)
            glVertex(x-dx, y-dy, 0.0)
            glVertex(x+dx, y+dy, 0.0)
            glEnd()

            # diagonal line 2
            glBegin(GL_LINES)
            glVertex(x-dx, y+dy, 0.0)
            glVertex(x+dx, y-dy, 0.0)
            glEnd()

        else:
            # vertical line
            glBegin(GL_LINES)
            glVertex(x-dx, y, 0.0)
            glVertex(x+dx, y, 0.0)
            glEnd()

            # horizontal line
            glBegin(GL_LINES)
            glVertex(x, y+dy, 0.0)
            glVertex(x, y-dy, 0.0)
            glEnd()

        glFlush()
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


    def drawRect(self, points, color):  # x1, y1, x2, y2
        """ Draws a filled rectangle. """
        glColor(*color)
        glRectf(points[0][0]*1.0/self.width, points[0][1]*1.0/self.height, points[1][0]*1.0/self.width, points[1][1]*1.0/self.height)

    def drawBox(self, points, color):
        if points is None:
            return
        p1x = (points[0][0]*1.0)/self.width
        p1y = (points[0][1]*1.0)/self.height
        p2x = (points[1][0]*1.0)/self.width
        p2y = (points[1][1]*1.0)/self.height

        glBegin(GL_LINE_LOOP)
        glColor4f(*color)
        glVertex2f(p1x, p1y)
        glVertex2f(p2x, p1y)
        glVertex2f(p2x, p2y)
        glVertex2f(p1x, p2y)
        #glVertex2f(p1x, p1y)
        glEnd()

    def drawCircle(self, points, color, filled=True, num_segments=None):
        """ Quickly draw approximate circle. Algorithm from:
            http://slabode.exofire.net/circle_draw.shtml
        """
        (cx1, cy1), (cx2, cy2) = points
        cx1 *= 1.0/self.width
        cy1 *= 1.0/self.height
        cx2 *= 1.0/self.width
        cy2 *= 1.0/self.height
        dx = abs(cx1 - cx2)
        dy = abs(cy1 - cy2)
        r = dx if dx > dy else dy

        if num_segments is None:
            num_segments = int(math.pi*16.0*math.sqrt(r))

        if filled:
            glBegin(GL_TRIANGLE_FAN)
            glColor4f(*color)
            for i in xrange(0, num_segments):
                angle = i * math.pi * 2.0 / num_segments
                glVertex2f(cx1 + r/self.aratio * math.cos(angle), cy1 + r * math.sin(angle))
            glEnd()
        else:
            theta = 2 * math.pi / float(num_segments)
            c = math.cos(theta)  # pre-calculate cosine0
            s = math.sin(theta)  # and sine
            t = 0
            x = r  # we start at angle = 0
            y = 0

            glColor4f(*color)
            glBegin(GL_LINE_LOOP)
            for ii in xrange(num_segments):
                # Circle requires correction for aspect ratio
                glVertex2f((x/self.aratio + cx1), (y + cy1))    # output vertex
                t = x
                x = c * x - s * y
                y = s * t + c * y
            glEnd()

    def drawTrace(self, points, color=(1.0, 1.0, 1.0, 1.0)):  # array
        """ Draw trace of position given in array.
        TODO: Draw trace in immediate mode via vertex and color arrays
        """
        glEnableClientState(GL_VERTEX_ARRAY)
        glColor4f(*color)
        glVertexPointerf(points)
        glDrawArrays(GL_LINE_STRIP, 0, len(points))

    def resize_canvas(self):
        """
        Locks video frame widget size to raster size, won't show
        up at all otherwise.
        """
        if self.frame is None:
            width = 320
            height = 240
        else:
            width, height = self.frame.shape[1], self.frame.shape[0]

        if not (self.width == width and self.height == height):
            self.width = width
            self.height = height
            #self.setFixedSize(self.width, self.height)
            self.setMinimumSize(width, height)
            self.setMaximumSize(width, height)
