# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'arduino_indicator_widget.ui'
#
# Created: Thu Apr 04 05:48:35 2013
#      by: PyQt4 UI code generator 4.9.5
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_indicator(object):
    def setupUi(self, indicator):
        indicator.setObjectName(_fromUtf8("indicator"))
        indicator.resize(94, 33)
        self.gridLayout_2 = QtGui.QGridLayout(indicator)
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setContentsMargins(-1, 0, -1, 0)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setContentsMargins(0, -1, 0, -1)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lbl_indicator = QtGui.QLabel(indicator)
        self.lbl_indicator.setText(_fromUtf8(""))
        self.lbl_indicator.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_indicator.setObjectName(_fromUtf8("lbl_indicator"))
        self.gridLayout.addWidget(self.lbl_indicator, 0, 0, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.actionArduino = QtGui.QAction(indicator)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/arduino.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionArduino.setIcon(icon)
        self.actionArduino.setObjectName(_fromUtf8("actionArduino"))

        self.retranslateUi(indicator)
        QtCore.QMetaObject.connectSlotsByName(indicator)

    def retranslateUi(self, indicator):
        indicator.setWindowTitle(QtGui.QApplication.translate("indicator", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.actionArduino.setText(QtGui.QApplication.translate("indicator", "Arduino", None, QtGui.QApplication.UnicodeUTF8))

import icons_rc
