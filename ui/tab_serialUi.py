# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'tab_serialUi.ui'
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

class Ui_tab_serial(object):
    def setupUi(self, tab_serial):
        tab_serial.setObjectName(_fromUtf8("tab_serial"))
        tab_serial.resize(241, 324)
        self.gridLayout = QtGui.QGridLayout(tab_serial)
        self.gridLayout.setMargin(0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setSpacing(1)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.toolBox = QtGui.QToolBox(tab_serial)
        self.toolBox.setFrameShape(QtGui.QFrame.NoFrame)
        self.toolBox.setFrameShadow(QtGui.QFrame.Plain)
        self.toolBox.setLineWidth(0)
        self.toolBox.setObjectName(_fromUtf8("toolBox"))
        self.page_serial_connection = QtGui.QWidget()
        self.page_serial_connection.setGeometry(QtCore.QRect(0, 0, 239, 280))
        self.page_serial_connection.setObjectName(_fromUtf8("page_serial_connection"))
        self.gridLayout_6 = QtGui.QGridLayout(self.page_serial_connection)
        self.gridLayout_6.setMargin(0)
        self.gridLayout_6.setSpacing(0)
        self.gridLayout_6.setObjectName(_fromUtf8("gridLayout_6"))
        self.gridLayout_3 = QtGui.QGridLayout()
        self.gridLayout_3.setSpacing(0)
        self.gridLayout_3.setContentsMargins(0, -1, -1, -1)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_3.addItem(spacerItem, 6, 1, 1, 1)
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.lbl_serial_port = QtGui.QLabel(self.page_serial_connection)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lbl_serial_port.sizePolicy().hasHeightForWidth())
        self.lbl_serial_port.setSizePolicy(sizePolicy)
        self.lbl_serial_port.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_serial_port.setObjectName(_fromUtf8("lbl_serial_port"))
        self.verticalLayout_2.addWidget(self.lbl_serial_port)
        self.btn_serial_refresh = QtGui.QPushButton(self.page_serial_connection)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_serial_refresh.sizePolicy().hasHeightForWidth())
        self.btn_serial_refresh.setSizePolicy(sizePolicy)
        self.btn_serial_refresh.setObjectName(_fromUtf8("btn_serial_refresh"))
        self.verticalLayout_2.addWidget(self.btn_serial_refresh)
        self.gridLayout_3.addLayout(self.verticalLayout_2, 3, 1, 1, 1)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.combo_serialports = QtGui.QComboBox(self.page_serial_connection)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.combo_serialports.sizePolicy().hasHeightForWidth())
        self.combo_serialports.setSizePolicy(sizePolicy)
        self.combo_serialports.setEditable(True)
        self.combo_serialports.setInsertPolicy(QtGui.QComboBox.InsertAtTop)
        self.combo_serialports.setDuplicatesEnabled(False)
        self.combo_serialports.setObjectName(_fromUtf8("combo_serialports"))
        self.verticalLayout.addWidget(self.combo_serialports)
        self.btn_serial_connect = QtGui.QPushButton(self.page_serial_connection)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_serial_connect.sizePolicy().hasHeightForWidth())
        self.btn_serial_connect.setSizePolicy(sizePolicy)
        self.btn_serial_connect.setCheckable(False)
        self.btn_serial_connect.setObjectName(_fromUtf8("btn_serial_connect"))
        self.verticalLayout.addWidget(self.btn_serial_connect)
        self.gridLayout_3.addLayout(self.verticalLayout, 3, 2, 1, 1)
        self.lbl_tx = QtGui.QLabel(self.page_serial_connection)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lbl_tx.sizePolicy().hasHeightForWidth())
        self.lbl_tx.setSizePolicy(sizePolicy)
        self.lbl_tx.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lbl_tx.setObjectName(_fromUtf8("lbl_tx"))
        self.gridLayout_3.addWidget(self.lbl_tx, 4, 1, 1, 1)
        self.lbl_rx = QtGui.QLabel(self.page_serial_connection)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lbl_rx.sizePolicy().hasHeightForWidth())
        self.lbl_rx.setSizePolicy(sizePolicy)
        self.lbl_rx.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lbl_rx.setObjectName(_fromUtf8("lbl_rx"))
        self.gridLayout_3.addWidget(self.lbl_rx, 5, 1, 1, 1)
        self.lbl_bytes_sent = QtGui.QLabel(self.page_serial_connection)
        self.lbl_bytes_sent.setText(_fromUtf8(""))
        self.lbl_bytes_sent.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lbl_bytes_sent.setObjectName(_fromUtf8("lbl_bytes_sent"))
        self.gridLayout_3.addWidget(self.lbl_bytes_sent, 4, 2, 1, 1)
        self.lbl_bytes_received = QtGui.QLabel(self.page_serial_connection)
        self.lbl_bytes_received.setText(_fromUtf8(""))
        self.lbl_bytes_received.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lbl_bytes_received.setObjectName(_fromUtf8("lbl_bytes_received"))
        self.gridLayout_3.addWidget(self.lbl_bytes_received, 5, 2, 1, 1)
        self.gridLayout_6.addLayout(self.gridLayout_3, 3, 1, 1, 1)
        self.toolBox.addItem(self.page_serial_connection, _fromUtf8(""))
        self.page_objects_IO = QtGui.QWidget()
        self.page_objects_IO.setGeometry(QtCore.QRect(0, 0, 239, 280))
        self.page_objects_IO.setObjectName(_fromUtf8("page_objects_IO"))
        self.gridLayout_7 = QtGui.QGridLayout(self.page_objects_IO)
        self.gridLayout_7.setMargin(0)
        self.gridLayout_7.setSpacing(0)
        self.gridLayout_7.setObjectName(_fromUtf8("gridLayout_7"))
        self.pushButton_8 = QtGui.QPushButton(self.page_objects_IO)
        self.pushButton_8.setObjectName(_fromUtf8("pushButton_8"))
        self.gridLayout_7.addWidget(self.pushButton_8, 2, 3, 1, 1)
        self.pushButton_9 = QtGui.QPushButton(self.page_objects_IO)
        self.pushButton_9.setObjectName(_fromUtf8("pushButton_9"))
        self.gridLayout_7.addWidget(self.pushButton_9, 2, 1, 1, 1)
        self.pushButton_4 = QtGui.QPushButton(self.page_objects_IO)
        self.pushButton_4.setObjectName(_fromUtf8("pushButton_4"))
        self.gridLayout_7.addWidget(self.pushButton_4, 1, 1, 1, 1)
        self.pushButton_5 = QtGui.QPushButton(self.page_objects_IO)
        self.pushButton_5.setObjectName(_fromUtf8("pushButton_5"))
        self.gridLayout_7.addWidget(self.pushButton_5, 1, 3, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_7.addItem(spacerItem1, 0, 1, 1, 1)
        self.toolBox.addItem(self.page_objects_IO, _fromUtf8(""))
        self.gridLayout_2.addWidget(self.toolBox, 0, 0, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_2, 0, 0, 1, 1)

        self.retranslateUi(tab_serial)
        self.toolBox.setCurrentIndex(0)
        self.toolBox.layout().setSpacing(0)
        QtCore.QMetaObject.connectSlotsByName(tab_serial)

    def retranslateUi(self, tab_serial):
        tab_serial.setWindowTitle(QtGui.QApplication.translate("tab_serial", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.lbl_serial_port.setText(QtGui.QApplication.translate("tab_serial", "Available Serial Ports:", None, QtGui.QApplication.UnicodeUTF8))
        self.btn_serial_refresh.setText(QtGui.QApplication.translate("tab_serial", "Refresh", None, QtGui.QApplication.UnicodeUTF8))
        self.btn_serial_connect.setText(QtGui.QApplication.translate("tab_serial", "Connect", None, QtGui.QApplication.UnicodeUTF8))
        self.lbl_tx.setText(QtGui.QApplication.translate("tab_serial", "transferred:", None, QtGui.QApplication.UnicodeUTF8))
        self.lbl_rx.setText(QtGui.QApplication.translate("tab_serial", "received:", None, QtGui.QApplication.UnicodeUTF8))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_serial_connection), QtGui.QApplication.translate("tab_serial", "Connection", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_8.setText(QtGui.QApplication.translate("tab_serial", "Save", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_9.setText(QtGui.QApplication.translate("tab_serial", "Open", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_4.setText(QtGui.QApplication.translate("tab_serial", "Clone", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_5.setText(QtGui.QApplication.translate("tab_serial", "Delete", None, QtGui.QApplication.UnicodeUTF8))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_objects_IO), QtGui.QApplication.translate("tab_serial", "In/Out", None, QtGui.QApplication.UnicodeUTF8))

