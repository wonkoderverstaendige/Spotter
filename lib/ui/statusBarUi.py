# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'statusBarUi.ui'
#
# Created: Tue Apr  1 02:59:50 2014
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

class Ui_statusBar(object):
    def setupUi(self, statusBar):
        statusBar.setObjectName(_fromUtf8("statusBar"))
        statusBar.resize(1282, 40)
        self.horizontalLayout_2 = QtGui.QHBoxLayout(statusBar)
        self.horizontalLayout_2.setMargin(0)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)

        self.retranslateUi(statusBar)
        QtCore.QMetaObject.connectSlotsByName(statusBar)

    def retranslateUi(self, statusBar):
        statusBar.setWindowTitle(_translate("statusBar", "Form", None))

