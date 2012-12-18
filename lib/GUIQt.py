# -*- coding: utf-8 -*-
"""
Created on Sat Dec 15 21:14:43 2012

@author: wonko
"""

import sys
from PyQt4 import QtGui, QtCore

class Frame(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
    
    def paintEvent(self, event):
        paint = QtGui.QPainter()
        paint.begin(self)
        
        color = QtGui.QColor(0, 0, 0)
        color.setNamedColor('#d4d4d4')
        paint.setPen(color)
        
        paint.setBrush(QtGui.QColor(0, 0, 0, 255))
        paint.drawRect(0, 0, 640, 360)
        
        paint.end()

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
        textEdit = QtGui.QTextEdit()
        frame = Frame()
        self.setCentralWidget(frame)


    def center(self):
        screen = QtGui.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)
                     
    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, 
                                          'Exit confirmation?',
                                          'Are you sure?',
                                          QtGui.QMessageBox.Yes,
                                          QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
            
            
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    main = MainWindow()
    main.show()    
    sys.exit(app.exec_())