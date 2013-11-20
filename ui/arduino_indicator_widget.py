# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'arduino_indicator_widget.ui'
#
# Created: Wed Nov 20 22:14:15 2013
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
        indicator.setWindowTitle(_translate("indicator", "Form", None))
        self.actionArduino.setText(_translate("indicator", "Arduino", None))

import icons_rc
