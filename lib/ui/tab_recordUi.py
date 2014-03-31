# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'tab_recordUi.ui'
#
# Created: Mon Mar 31 18:33:38 2014
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

class Ui_tab_record(object):
    def setupUi(self, tab_record):
        tab_record.setObjectName(_fromUtf8("tab_record"))
        tab_record.resize(245, 449)
        self.gridLayout = QtGui.QGridLayout(tab_record)
        self.gridLayout.setMargin(0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setSpacing(1)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.toolBox = QtGui.QToolBox(tab_record)
        self.toolBox.setFrameShape(QtGui.QFrame.NoFrame)
        self.toolBox.setFrameShadow(QtGui.QFrame.Plain)
        self.toolBox.setLineWidth(0)
        self.toolBox.setObjectName(_fromUtf8("toolBox"))
        self.page_record = QtGui.QWidget()
        self.page_record.setGeometry(QtCore.QRect(0, 0, 243, 426))
        self.page_record.setObjectName(_fromUtf8("page_record"))
        self.gridLayout_6 = QtGui.QGridLayout(self.page_record)
        self.gridLayout_6.setMargin(0)
        self.gridLayout_6.setSpacing(0)
        self.gridLayout_6.setObjectName(_fromUtf8("gridLayout_6"))
        self.toolBox.addItem(self.page_record, _fromUtf8(""))
        self.gridLayout_2.addWidget(self.toolBox, 0, 0, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_2, 0, 0, 1, 1)

        self.retranslateUi(tab_record)
        self.toolBox.setCurrentIndex(0)
        self.toolBox.layout().setSpacing(0)
        QtCore.QMetaObject.connectSlotsByName(tab_record)

    def retranslateUi(self, tab_record):
        tab_record.setWindowTitle(_translate("tab_record", "Form", None))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_record), _translate("tab_record", "Recording parameters", None))

import images_rc
