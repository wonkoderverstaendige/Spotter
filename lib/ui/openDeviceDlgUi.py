# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'openDeviceDlgUi.ui'
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

class Ui_DeviceDialog(object):
    def setupUi(self, DeviceDialog):
        DeviceDialog.setObjectName(_fromUtf8("DeviceDialog"))
        DeviceDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/LiveCam.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        DeviceDialog.setWindowIcon(icon)
        self.gridLayout = QtGui.QGridLayout(DeviceDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.ledit_device = QtGui.QLineEdit(DeviceDialog)
        self.ledit_device.setObjectName(_fromUtf8("ledit_device"))
        self.gridLayout.addWidget(self.ledit_device, 1, 1, 1, 1)
        self.lbl_device_source = QtGui.QLabel(DeviceDialog)
        self.lbl_device_source.setObjectName(_fromUtf8("lbl_device_source"))
        self.gridLayout.addWidget(self.lbl_device_source, 1, 0, 1, 1)
        self.lbl_video_size = QtGui.QLabel(DeviceDialog)
        self.lbl_video_size.setObjectName(_fromUtf8("lbl_video_size"))
        self.gridLayout.addWidget(self.lbl_video_size, 0, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.spin_width = QtGui.QSpinBox(DeviceDialog)
        self.spin_width.setMinimum(1)
        self.spin_width.setMaximum(4096)
        self.spin_width.setObjectName(_fromUtf8("spin_width"))
        self.horizontalLayout.addWidget(self.spin_width)
        self.label_3 = QtGui.QLabel(DeviceDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.horizontalLayout.addWidget(self.label_3)
        self.spin_height = QtGui.QSpinBox(DeviceDialog)
        self.spin_height.setMinimum(1)
        self.spin_height.setMaximum(4096)
        self.spin_height.setObjectName(_fromUtf8("spin_height"))
        self.horizontalLayout.addWidget(self.spin_height)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(DeviceDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 2, 1, 1, 1)

        self.retranslateUi(DeviceDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), DeviceDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), DeviceDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(DeviceDialog)

    def retranslateUi(self, DeviceDialog):
        DeviceDialog.setWindowTitle(_translate("DeviceDialog", "Open Device", None))
        self.lbl_device_source.setText(_translate("DeviceDialog", "Device ID/URL", None))
        self.lbl_video_size.setText(_translate("DeviceDialog", "Video size:", None))
        self.spin_width.setSuffix(_translate("DeviceDialog", "px", None))
        self.label_3.setText(_translate("DeviceDialog", "x", None))
        self.spin_height.setSuffix(_translate("DeviceDialog", "px", None))

import icons_rc
import images_rc
