# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'serialIndicatorUi.ui'
#
# Created: Mon Nov 25 22:32:42 2013
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
        indicator.resize(564, 129)
        self.gridLayout_2 = QtGui.QGridLayout(indicator)
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setContentsMargins(-1, 0, -1, 0)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem, 0, 0, 1, 1)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setContentsMargins(0, -1, 0, -1)
        self.gridLayout.setHorizontalSpacing(5)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lbl_icon = QtGui.QLabel(indicator)
        self.lbl_icon.setText(_fromUtf8(""))
        self.lbl_icon.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_icon.setObjectName(_fromUtf8("lbl_icon"))
        self.gridLayout.addWidget(self.lbl_icon, 0, 1, 1, 1)
        self.lbl_warning = QtGui.QLabel(indicator)
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.lbl_warning.setFont(font)
        self.lbl_warning.setText(_fromUtf8(""))
        self.lbl_warning.setObjectName(_fromUtf8("lbl_warning"))
        self.gridLayout.addWidget(self.lbl_warning, 0, 0, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 2, 1, 1)
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
