# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainUi.ui'
#
# Created: Thu Dec 05 22:25:37 2013
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

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(630, 386)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icon64.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setMargin(0)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.frame_video = QtGui.QHBoxLayout()
        self.frame_video.setSpacing(0)
        self.frame_video.setObjectName(_fromUtf8("frame_video"))
        spacerItem = QtGui.QSpacerItem(320, 0, QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Minimum)
        self.frame_video.addItem(spacerItem)
        self.frame = QtGui.QFrame(self.centralwidget)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Sunken)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.frame_video.addWidget(self.frame)
        self.horizontalLayout_2.addLayout(self.frame_video)
        self.frame_parameters = QtGui.QHBoxLayout()
        self.frame_parameters.setSpacing(0)
        self.frame_parameters.setObjectName(_fromUtf8("frame_parameters"))
        self.horizontalLayout_2.addLayout(self.frame_parameters)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 630, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menu_File = QtGui.QMenu(self.menubar)
        self.menu_File.setObjectName(_fromUtf8("menu_File"))
        self.menu_Open = QtGui.QMenu(self.menu_File)
        self.menu_Open.setObjectName(_fromUtf8("menu_Open"))
        self.menu_Save = QtGui.QMenu(self.menu_File)
        self.menu_Save.setEnabled(False)
        self.menu_Save.setObjectName(_fromUtf8("menu_Save"))
        self.menuLoad = QtGui.QMenu(self.menu_File)
        self.menuLoad.setEnabled(False)
        self.menuLoad.setObjectName(_fromUtf8("menuLoad"))
        self.menuHelp = QtGui.QMenu(self.menubar)
        self.menuHelp.setObjectName(_fromUtf8("menuHelp"))
        self.menuTemplate = QtGui.QMenu(self.menubar)
        self.menuTemplate.setObjectName(_fromUtf8("menuTemplate"))
        self.menuView = QtGui.QMenu(self.menubar)
        self.menuView.setObjectName(_fromUtf8("menuView"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QtGui.QToolBar(MainWindow)
        self.toolBar.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.toolBar.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.toolBar.setObjectName(_fromUtf8("toolBar"))
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.actionE_xit = QtGui.QAction(MainWindow)
        self.actionE_xit.setObjectName(_fromUtf8("actionE_xit"))
        self.actionCamera = QtGui.QAction(MainWindow)
        self.actionCamera.setObjectName(_fromUtf8("actionCamera"))
        self.actionFile = QtGui.QAction(MainWindow)
        self.actionFile.setObjectName(_fromUtf8("actionFile"))
        self.actionSave = QtGui.QAction(MainWindow)
        self.actionSave.setEnabled(False)
        self.actionSave.setObjectName(_fromUtf8("actionSave"))
        self.action_Parameters = QtGui.QAction(MainWindow)
        self.action_Parameters.setEnabled(False)
        self.action_Parameters.setObjectName(_fromUtf8("action_Parameters"))
        self.action_Transcode_Video = QtGui.QAction(MainWindow)
        self.action_Transcode_Video.setObjectName(_fromUtf8("action_Transcode_Video"))
        self.actionParameters = QtGui.QAction(MainWindow)
        self.actionParameters.setEnabled(False)
        self.actionParameters.setObjectName(_fromUtf8("actionParameters"))
        self.actionAbout = QtGui.QAction(MainWindow)
        self.actionAbout.setIcon(icon)
        self.actionAbout.setObjectName(_fromUtf8("actionAbout"))
        self.actionRecord = QtGui.QAction(MainWindow)
        self.actionRecord.setCheckable(True)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/record_on.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionRecord.setIcon(icon1)
        self.actionRecord.setObjectName(_fromUtf8("actionRecord"))
        self.actionArduino = QtGui.QAction(MainWindow)
        self.actionArduino.setEnabled(False)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/arduino_off.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionArduino.setIcon(icon2)
        self.actionArduino.setObjectName(_fromUtf8("actionArduino"))
        self.actionLoadConfig = QtGui.QAction(MainWindow)
        self.actionLoadConfig.setObjectName(_fromUtf8("actionLoadConfig"))
        self.actionSaveConfig = QtGui.QAction(MainWindow)
        self.actionSaveConfig.setObjectName(_fromUtf8("actionSaveConfig"))
        self.actionRemoveTemplate = QtGui.QAction(MainWindow)
        self.actionRemoveTemplate.setObjectName(_fromUtf8("actionRemoveTemplate"))
        self.actionSourceProperties = QtGui.QAction(MainWindow)
        self.actionSourceProperties.setObjectName(_fromUtf8("actionSourceProperties"))
        self.actionOnTop = QtGui.QAction(MainWindow)
        self.actionOnTop.setCheckable(True)
        self.actionOnTop.setObjectName(_fromUtf8("actionOnTop"))
        self.menu_Open.addAction(self.actionFile)
        self.menu_Open.addAction(self.actionCamera)
        self.menu_Save.addAction(self.action_Transcode_Video)
        self.menu_Save.addAction(self.actionParameters)
        self.menuLoad.addAction(self.action_Parameters)
        self.menu_File.addAction(self.menu_Open.menuAction())
        self.menu_File.addAction(self.menuLoad.menuAction())
        self.menu_File.addAction(self.menu_Save.menuAction())
        self.menu_File.addSeparator()
        self.menu_File.addAction(self.actionE_xit)
        self.menuHelp.addAction(self.actionAbout)
        self.menuTemplate.addAction(self.actionLoadConfig)
        self.menuTemplate.addAction(self.actionSaveConfig)
        self.menuTemplate.addSeparator()
        self.menuTemplate.addAction(self.actionRemoveTemplate)
        self.menuView.addAction(self.actionOnTop)
        self.menubar.addAction(self.menu_File.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuTemplate.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.toolBar.addAction(self.actionRecord)
        self.toolBar.addAction(self.actionSourceProperties)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Spotter", None))
        self.menu_File.setTitle(_translate("MainWindow", "&File", None))
        self.menu_Open.setTitle(_translate("MainWindow", "&Open", None))
        self.menu_Save.setTitle(_translate("MainWindow", "&Save", None))
        self.menuLoad.setTitle(_translate("MainWindow", "Load", None))
        self.menuHelp.setTitle(_translate("MainWindow", "&Help", None))
        self.menuTemplate.setTitle(_translate("MainWindow", "Template", None))
        self.menuView.setTitle(_translate("MainWindow", "View", None))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar", None))
        self.actionE_xit.setText(_translate("MainWindow", "E&xit", None))
        self.actionCamera.setText(_translate("MainWindow", "&Camera", None))
        self.actionFile.setText(_translate("MainWindow", "&File", None))
        self.actionSave.setText(_translate("MainWindow", "&Transcode", None))
        self.action_Parameters.setText(_translate("MainWindow", "&Parameters", None))
        self.action_Transcode_Video.setText(_translate("MainWindow", "&Transcode Video", None))
        self.actionParameters.setText(_translate("MainWindow", "Parameters", None))
        self.actionAbout.setText(_translate("MainWindow", "&About", None))
        self.actionRecord.setText(_translate("MainWindow", "Record", None))
        self.actionRecord.setToolTip(_translate("MainWindow", "Record Video", None))
        self.actionArduino.setText(_translate("MainWindow", "Arduino", None))
        self.actionArduino.setToolTip(_translate("MainWindow", "Arduino State", None))
        self.actionLoadConfig.setText(_translate("MainWindow", "Load", None))
        self.actionSaveConfig.setText(_translate("MainWindow", "Save", None))
        self.actionSaveConfig.setToolTip(_translate("MainWindow", "Save current configuration", None))
        self.actionRemoveTemplate.setText(_translate("MainWindow", "Remove all", None))
        self.actionSourceProperties.setText(_translate("MainWindow", "Source Props", None))
        self.actionOnTop.setText(_translate("MainWindow", "Always on Top", None))

import icons_rc
