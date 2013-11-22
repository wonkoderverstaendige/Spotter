# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainUi.ui'
#
# Created: Fri Nov 22 04:10:21 2013
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

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(594, 388)
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
        self.horizontalLayout_2.setContentsMargins(9, 0, 0, 0)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.new_parameters = QtGui.QHBoxLayout()
        self.new_parameters.setObjectName(_fromUtf8("new_parameters"))
        self.horizontalLayout_2.addLayout(self.new_parameters)
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
        self.tab_parameters = QtGui.QTabWidget(self.centralwidget)
        self.tab_parameters.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tab_parameters.sizePolicy().hasHeightForWidth())
        self.tab_parameters.setSizePolicy(sizePolicy)
        self.tab_parameters.setMinimumSize(QtCore.QSize(270, 0))
        self.tab_parameters.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.tab_parameters.setTabShape(QtGui.QTabWidget.Triangular)
        self.tab_parameters.setTabsClosable(False)
        self.tab_parameters.setObjectName(_fromUtf8("tab_parameters"))
        self.widget_features = QtGui.QWidget()
        self.widget_features.setObjectName(_fromUtf8("widget_features"))
        self.horizontalLayout_5 = QtGui.QHBoxLayout(self.widget_features)
        self.horizontalLayout_5.setSpacing(0)
        self.horizontalLayout_5.setMargin(0)
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.tab_features = QtGui.QTabWidget(self.widget_features)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tab_features.sizePolicy().hasHeightForWidth())
        self.tab_features.setSizePolicy(sizePolicy)
        self.tab_features.setTabPosition(QtGui.QTabWidget.East)
        self.tab_features.setTabShape(QtGui.QTabWidget.Rounded)
        self.tab_features.setDocumentMode(True)
        self.tab_features.setTabsClosable(True)
        self.tab_features.setObjectName(_fromUtf8("tab_features"))
        self.tab_features_newTab = QtGui.QWidget()
        self.tab_features_newTab.setObjectName(_fromUtf8("tab_features_newTab"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.tab_features_newTab)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.btn_new_feature_tab = QtGui.QPushButton(self.tab_features_newTab)
        self.btn_new_feature_tab.setObjectName(_fromUtf8("btn_new_feature_tab"))
        self.verticalLayout_2.addWidget(self.btn_new_feature_tab)
        self.btn_feature_template = QtGui.QPushButton(self.tab_features_newTab)
        self.btn_feature_template.setEnabled(False)
        self.btn_feature_template.setCursor(QtGui.QCursor(QtCore.Qt.ForbiddenCursor))
        self.btn_feature_template.setObjectName(_fromUtf8("btn_feature_template"))
        self.verticalLayout_2.addWidget(self.btn_feature_template)
        self.tab_features.addTab(self.tab_features_newTab, _fromUtf8(""))
        self.horizontalLayout_5.addWidget(self.tab_features)
        self.tab_parameters.addTab(self.widget_features, _fromUtf8(""))
        self.widget_objects = QtGui.QWidget()
        self.widget_objects.setObjectName(_fromUtf8("widget_objects"))
        self.horizontalLayout_4 = QtGui.QHBoxLayout(self.widget_objects)
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setMargin(0)
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.tab_objects = QtGui.QTabWidget(self.widget_objects)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tab_objects.sizePolicy().hasHeightForWidth())
        self.tab_objects.setSizePolicy(sizePolicy)
        self.tab_objects.setTabPosition(QtGui.QTabWidget.East)
        self.tab_objects.setTabShape(QtGui.QTabWidget.Rounded)
        self.tab_objects.setDocumentMode(True)
        self.tab_objects.setTabsClosable(True)
        self.tab_objects.setObjectName(_fromUtf8("tab_objects"))
        self.tab_object_newTab = QtGui.QWidget()
        self.tab_object_newTab.setObjectName(_fromUtf8("tab_object_newTab"))
        self.verticalLayout = QtGui.QVBoxLayout(self.tab_object_newTab)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.btn_new_object_tab = QtGui.QPushButton(self.tab_object_newTab)
        self.btn_new_object_tab.setObjectName(_fromUtf8("btn_new_object_tab"))
        self.verticalLayout.addWidget(self.btn_new_object_tab)
        self.btn_object_template = QtGui.QPushButton(self.tab_object_newTab)
        self.btn_object_template.setEnabled(False)
        self.btn_object_template.setCursor(QtGui.QCursor(QtCore.Qt.ForbiddenCursor))
        self.btn_object_template.setObjectName(_fromUtf8("btn_object_template"))
        self.verticalLayout.addWidget(self.btn_object_template)
        self.tab_objects.addTab(self.tab_object_newTab, _fromUtf8(""))
        self.horizontalLayout_4.addWidget(self.tab_objects)
        self.tab_parameters.addTab(self.widget_objects, _fromUtf8(""))
        self.widget_regions = QtGui.QWidget()
        self.widget_regions.setObjectName(_fromUtf8("widget_regions"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.widget_regions)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.tab_regions = QtGui.QTabWidget(self.widget_regions)
        self.tab_regions.setTabPosition(QtGui.QTabWidget.East)
        self.tab_regions.setDocumentMode(True)
        self.tab_regions.setTabsClosable(True)
        self.tab_regions.setObjectName(_fromUtf8("tab_regions"))
        self.tab_regions_newTab = QtGui.QWidget()
        self.tab_regions_newTab.setObjectName(_fromUtf8("tab_regions_newTab"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.tab_regions_newTab)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setMargin(0)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.btn_new_region_tab = QtGui.QPushButton(self.tab_regions_newTab)
        self.btn_new_region_tab.setObjectName(_fromUtf8("btn_new_region_tab"))
        self.verticalLayout_3.addWidget(self.btn_new_region_tab)
        self.btn_region_template = QtGui.QPushButton(self.tab_regions_newTab)
        self.btn_region_template.setEnabled(False)
        self.btn_region_template.setObjectName(_fromUtf8("btn_region_template"))
        self.verticalLayout_3.addWidget(self.btn_region_template)
        self.tab_regions.addTab(self.tab_regions_newTab, _fromUtf8(""))
        self.horizontalLayout.addWidget(self.tab_regions)
        self.tab_parameters.addTab(self.widget_regions, _fromUtf8(""))
        self.widget_serial = QtGui.QWidget()
        self.widget_serial.setObjectName(_fromUtf8("widget_serial"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.widget_serial)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setMargin(0)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.tab_serial = QtGui.QTabWidget(self.widget_serial)
        self.tab_serial.setTabPosition(QtGui.QTabWidget.East)
        self.tab_serial.setDocumentMode(True)
        self.tab_serial.setObjectName(_fromUtf8("tab_serial"))
        self.verticalLayout_4.addWidget(self.tab_serial)
        self.tab_parameters.addTab(self.widget_serial, _fromUtf8(""))
        self.frame_parameters.addWidget(self.tab_parameters)
        self.horizontalLayout_2.addLayout(self.frame_parameters)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 594, 21))
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
        self.actionDevice = QtGui.QAction(MainWindow)
        self.actionDevice.setEnabled(False)
        self.actionDevice.setObjectName(_fromUtf8("actionDevice"))
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
        self.actionResetConfig = QtGui.QAction(MainWindow)
        self.actionResetConfig.setEnabled(False)
        self.actionResetConfig.setObjectName(_fromUtf8("actionResetConfig"))
        self.menu_Open.addAction(self.actionFile)
        self.menu_Open.addAction(self.actionDevice)
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
        self.menuTemplate.addAction(self.actionResetConfig)
        self.menubar.addAction(self.menu_File.menuAction())
        self.menubar.addAction(self.menuTemplate.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.toolBar.addAction(self.actionRecord)

        self.retranslateUi(MainWindow)
        self.tab_parameters.setCurrentIndex(0)
        self.tab_objects.setCurrentIndex(0)
        self.tab_regions.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Spotter", None))
        self.btn_new_feature_tab.setText(_translate("MainWindow", "Add LED/Feature", None))
        self.btn_feature_template.setText(_translate("MainWindow", "Quickload Feature template", None))
        self.tab_features.setTabText(self.tab_features.indexOf(self.tab_features_newTab), _translate("MainWindow", "+", None))
        self.tab_parameters.setTabText(self.tab_parameters.indexOf(self.widget_features), _translate("MainWindow", "Features", None))
        self.btn_new_object_tab.setText(_translate("MainWindow", "Add Object", None))
        self.btn_object_template.setText(_translate("MainWindow", "Quickload object template", None))
        self.tab_objects.setTabText(self.tab_objects.indexOf(self.tab_object_newTab), _translate("MainWindow", "+", None))
        self.tab_parameters.setTabText(self.tab_parameters.indexOf(self.widget_objects), _translate("MainWindow", "Objects", None))
        self.btn_new_region_tab.setText(_translate("MainWindow", "New Region", None))
        self.btn_region_template.setText(_translate("MainWindow", "Quickload region template", None))
        self.tab_regions.setTabText(self.tab_regions.indexOf(self.tab_regions_newTab), _translate("MainWindow", "+", None))
        self.tab_parameters.setTabText(self.tab_parameters.indexOf(self.widget_regions), _translate("MainWindow", "ROIs", None))
        self.tab_parameters.setTabText(self.tab_parameters.indexOf(self.widget_serial), _translate("MainWindow", "Serial", None))
        self.menu_File.setTitle(_translate("MainWindow", "&File", None))
        self.menu_Open.setTitle(_translate("MainWindow", "&Open", None))
        self.menu_Save.setTitle(_translate("MainWindow", "&Save", None))
        self.menuLoad.setTitle(_translate("MainWindow", "Load", None))
        self.menuHelp.setTitle(_translate("MainWindow", "&Help", None))
        self.menuTemplate.setTitle(_translate("MainWindow", "Configuration", None))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar", None))
        self.actionE_xit.setText(_translate("MainWindow", "E&xit", None))
        self.actionDevice.setText(_translate("MainWindow", "&Device", None))
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
        self.actionResetConfig.setText(_translate("MainWindow", "Reset All", None))

import icons_rc
