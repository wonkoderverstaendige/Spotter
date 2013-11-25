# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'side_barUi.ui'
#
# Created: Mon Nov 25 22:32:41 2013
#      by: PyQt4 UI code generator 4.10.3
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

class Ui_side_bar(object):
    def setupUi(self, side_bar):
        side_bar.setObjectName(_fromUtf8("side_bar"))
        side_bar.resize(312, 377)
        side_bar.setMinimumSize(QtCore.QSize(260, 0))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(side_bar)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setMargin(0)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.tabs_main = QtGui.QTabWidget(side_bar)
        self.tabs_main.setTabShape(QtGui.QTabWidget.Triangular)
        self.tabs_main.setIconSize(QtCore.QSize(0, 0))
        self.tabs_main.setDocumentMode(True)
        self.tabs_main.setObjectName(_fromUtf8("tabs_main"))
        self.horizontalLayout_2.addWidget(self.tabs_main)

        self.retranslateUi(side_bar)
        self.tabs_main.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(side_bar)

    def retranslateUi(self, side_bar):
        side_bar.setWindowTitle(_translate("side_bar", "Form", None))

