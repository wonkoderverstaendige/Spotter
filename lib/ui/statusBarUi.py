# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'statusBarUi.ui'
#
# Created: Wed Nov 27 04:47:40 2013
#      by: PyQt4 UI code generator 4.9.6
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
        statusBar.resize(960, 40)
        self.horizontalLayout_2 = QtGui.QHBoxLayout(statusBar)
        self.horizontalLayout_2.setMargin(0)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.lbl_fps = QtGui.QLabel(statusBar)
        self.lbl_fps.setMinimumSize(QtCore.QSize(55, 0))
        self.lbl_fps.setFrameShape(QtGui.QFrame.NoFrame)
        self.lbl_fps.setObjectName(_fromUtf8("lbl_fps"))
        self.horizontalLayout_2.addWidget(self.lbl_fps)
        self.sb_offset = QtGui.QSpinBox(statusBar)
        self.sb_offset.setFocusPolicy(QtCore.Qt.NoFocus)
        self.sb_offset.setFrame(False)
        self.sb_offset.setButtonSymbols(QtGui.QAbstractSpinBox.PlusMinus)
        self.sb_offset.setAccelerated(True)
        self.sb_offset.setMinimum(-99)
        self.sb_offset.setMaximum(999)
        self.sb_offset.setProperty("value", -10)
        self.sb_offset.setObjectName(_fromUtf8("sb_offset"))
        self.horizontalLayout_2.addWidget(self.sb_offset)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)

        self.retranslateUi(statusBar)
        QtCore.QMetaObject.connectSlotsByName(statusBar)

    def retranslateUi(self, statusBar):
        statusBar.setWindowTitle(_translate("statusBar", "Form", None))
        self.lbl_fps.setToolTip(_translate("statusBar", "Interface refresh rate, NOT the acquisition rate if grabbing from a camera.", None))
        self.lbl_fps.setText(_translate("statusBar", "FPS: 100.0", None))
        self.sb_offset.setToolTip(_translate("statusBar", "Bias GUI refresh interval", None))
        self.sb_offset.setSuffix(_translate("statusBar", " ms", None))

