# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'PGFrameUi.ui'
#
# Created: Mon Mar 31 03:02:18 2014
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_PGFrame(object):
    def setupUi(self, PGFrame):
        PGFrame.setObjectName(_fromUtf8("PGFrame"))
        PGFrame.resize(400, 295)
        self.gridLayout = QtGui.QGridLayout(PGFrame)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.gv_video = GraphicsView(PGFrame)
        self.gv_video.setObjectName(_fromUtf8("gv_video"))
        self.gridLayout.addWidget(self.gv_video, 0, 0, 1, 1)

        self.retranslateUi(PGFrame)
        QtCore.QMetaObject.connectSlotsByName(PGFrame)

    def retranslateUi(self, PGFrame):
        PGFrame.setWindowTitle(_translate("PGFrame", "Form", None))

from lib.pyqtgraph import GraphicsView
