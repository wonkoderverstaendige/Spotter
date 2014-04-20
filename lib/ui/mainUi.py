# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainUi.ui'
#
# Created: Sun Apr 20 05:05:21 2014
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
        MainWindow.resize(1032, 536)
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
        self.centralwidget.setStyleSheet(_fromUtf8(""))
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setMargin(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.frame_parameters = QtGui.QHBoxLayout()
        self.frame_parameters.setSpacing(0)
        self.frame_parameters.setObjectName(_fromUtf8("frame_parameters"))
        self.gridLayout.addLayout(self.frame_parameters, 0, 3, 3, 1)
        spacerItem = QtGui.QSpacerItem(1024, 1, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 1, 2, 1, 1)
        self.frame_video = QtGui.QHBoxLayout()
        self.frame_video.setSpacing(0)
        self.frame_video.setObjectName(_fromUtf8("frame_video"))
        self.frame = QtGui.QFrame(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setStyleSheet(_fromUtf8("background-image: url(:/logo_name_translucent.png); background-repeat: no-repeat; background-position: center center;"))
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Sunken)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.gridLayout_2 = QtGui.QGridLayout(self.frame)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.frame_video.addWidget(self.frame)
        self.gridLayout.addLayout(self.frame_video, 0, 2, 1, 1)
        self.gridLayout_3 = QtGui.QGridLayout()
        self.gridLayout_3.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
        self.gridLayout_3.setContentsMargins(3, -1, -1, -1)
        self.gridLayout_3.setHorizontalSpacing(3)
        self.gridLayout_3.setVerticalSpacing(0)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.spin_offset = QtGui.QSpinBox(self.centralwidget)
        self.spin_offset.setFocusPolicy(QtCore.Qt.NoFocus)
        self.spin_offset.setFrame(False)
        self.spin_offset.setButtonSymbols(QtGui.QAbstractSpinBox.PlusMinus)
        self.spin_offset.setAccelerated(True)
        self.spin_offset.setMinimum(-99)
        self.spin_offset.setMaximum(999)
        self.spin_offset.setProperty("value", -10)
        self.spin_offset.setObjectName(_fromUtf8("spin_offset"))
        self.gridLayout_3.addWidget(self.spin_offset, 1, 9, 1, 1)
        self.pushButton_2 = QtGui.QPushButton(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_2.sizePolicy().hasHeightForWidth())
        self.pushButton_2.setSizePolicy(sizePolicy)
        self.pushButton_2.setFocusPolicy(QtCore.Qt.NoFocus)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/go_back.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_2.setIcon(icon1)
        self.pushButton_2.setObjectName(_fromUtf8("pushButton_2"))
        self.gridLayout_3.addWidget(self.pushButton_2, 1, 3, 1, 1)
        self.lbl_fps = QtGui.QLabel(self.centralwidget)
        self.lbl_fps.setMinimumSize(QtCore.QSize(55, 0))
        self.lbl_fps.setFrameShape(QtGui.QFrame.NoFrame)
        self.lbl_fps.setObjectName(_fromUtf8("lbl_fps"))
        self.gridLayout_3.addWidget(self.lbl_fps, 1, 8, 1, 1)
        self.lbl_frame_t = QtGui.QLabel(self.centralwidget)
        self.lbl_frame_t.setObjectName(_fromUtf8("lbl_frame_t"))
        self.gridLayout_3.addWidget(self.lbl_frame_t, 1, 0, 1, 1)
        self.push_rewind = QtGui.QPushButton(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.push_rewind.sizePolicy().hasHeightForWidth())
        self.push_rewind.setSizePolicy(sizePolicy)
        self.push_rewind.setFocusPolicy(QtCore.Qt.NoFocus)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/rewind.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.push_rewind.setIcon(icon2)
        self.push_rewind.setIconSize(QtCore.QSize(16, 16))
        self.push_rewind.setObjectName(_fromUtf8("push_rewind"))
        self.gridLayout_3.addWidget(self.push_rewind, 1, 2, 1, 1)
        self.pushButton_3 = QtGui.QPushButton(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_3.sizePolicy().hasHeightForWidth())
        self.pushButton_3.setSizePolicy(sizePolicy)
        self.pushButton_3.setFocusPolicy(QtCore.Qt.NoFocus)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(_fromUtf8(":/go_forward.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_3.setIcon(icon3)
        self.pushButton_3.setObjectName(_fromUtf8("pushButton_3"))
        self.gridLayout_3.addWidget(self.pushButton_3, 1, 5, 1, 1)
        self.scrollbar_pos = QtGui.QScrollBar(self.centralwidget)
        self.scrollbar_pos.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollbar_pos.sizePolicy().hasHeightForWidth())
        self.scrollbar_pos.setSizePolicy(sizePolicy)
        self.scrollbar_pos.setOrientation(QtCore.Qt.Horizontal)
        self.scrollbar_pos.setInvertedAppearance(False)
        self.scrollbar_pos.setInvertedControls(True)
        self.scrollbar_pos.setObjectName(_fromUtf8("scrollbar_pos"))
        self.gridLayout_3.addWidget(self.scrollbar_pos, 0, 0, 1, 10)
        self.spin_index = QtGui.QSpinBox(self.centralwidget)
        self.spin_index.setEnabled(False)
        self.spin_index.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.spin_index.setMaximum(1)
        self.spin_index.setObjectName(_fromUtf8("spin_index"))
        self.gridLayout_3.addWidget(self.spin_index, 1, 4, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_3.addItem(spacerItem1, 1, 7, 1, 1)
        self.push_fast_forward = QtGui.QPushButton(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.push_fast_forward.sizePolicy().hasHeightForWidth())
        self.push_fast_forward.setSizePolicy(sizePolicy)
        self.push_fast_forward.setFocusPolicy(QtCore.Qt.NoFocus)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(_fromUtf8(":/fast_forward.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.push_fast_forward.setIcon(icon4)
        self.push_fast_forward.setObjectName(_fromUtf8("push_fast_forward"))
        self.gridLayout_3.addWidget(self.push_fast_forward, 1, 6, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_3.addItem(spacerItem2, 1, 1, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_3, 2, 2, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1032, 21))
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
        self.toolBar.setEnabled(True)
        self.toolBar.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.toolBar.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.toolBar.setObjectName(_fromUtf8("toolBar"))
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.actionE_xit = QtGui.QAction(MainWindow)
        self.actionE_xit.setObjectName(_fromUtf8("actionE_xit"))
        self.actionCamera = QtGui.QAction(MainWindow)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(_fromUtf8(":/LiveCam.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionCamera.setIcon(icon5)
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
        self.actionRecord.setEnabled(False)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(_fromUtf8(":/record_on.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionRecord.setIcon(icon6)
        self.actionRecord.setObjectName(_fromUtf8("actionRecord"))
        self.actionArduino = QtGui.QAction(MainWindow)
        self.actionArduino.setEnabled(False)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(_fromUtf8(":/arduino_off.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionArduino.setIcon(icon7)
        self.actionArduino.setObjectName(_fromUtf8("actionArduino"))
        self.actionLoadTemplate = QtGui.QAction(MainWindow)
        self.actionLoadTemplate.setObjectName(_fromUtf8("actionLoadTemplate"))
        self.actionSaveTemplate = QtGui.QAction(MainWindow)
        self.actionSaveTemplate.setObjectName(_fromUtf8("actionSaveTemplate"))
        self.actionRemoveTemplate = QtGui.QAction(MainWindow)
        self.actionRemoveTemplate.setObjectName(_fromUtf8("actionRemoveTemplate"))
        self.actionSourceProperties = QtGui.QAction(MainWindow)
        self.actionSourceProperties.setObjectName(_fromUtf8("actionSourceProperties"))
        self.actionOnTop = QtGui.QAction(MainWindow)
        self.actionOnTop.setCheckable(True)
        self.actionOnTop.setObjectName(_fromUtf8("actionOnTop"))
        self.actionClearRecentFiles = QtGui.QAction(MainWindow)
        self.actionClearRecentFiles.setObjectName(_fromUtf8("actionClearRecentFiles"))
        self.actionPlay = QtGui.QAction(MainWindow)
        self.actionPlay.setCheckable(True)
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap(_fromUtf8(":/play.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionPlay.setIcon(icon8)
        self.actionPlay.setObjectName(_fromUtf8("actionPlay"))
        self.actionPause = QtGui.QAction(MainWindow)
        self.actionPause.setCheckable(True)
        self.actionPause.setEnabled(False)
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap(_fromUtf8(":/pause.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionPause.setIcon(icon9)
        self.actionPause.setObjectName(_fromUtf8("actionPause"))
        self.actionRepeat = QtGui.QAction(MainWindow)
        self.actionRepeat.setCheckable(True)
        self.actionRepeat.setObjectName(_fromUtf8("actionRepeat"))
        self.actionRewind = QtGui.QAction(MainWindow)
        self.actionRewind.setIcon(icon2)
        self.actionRewind.setObjectName(_fromUtf8("actionRewind"))
        self.actionFastForward = QtGui.QAction(MainWindow)
        self.actionFastForward.setIcon(icon4)
        self.actionFastForward.setObjectName(_fromUtf8("actionFastForward"))
        self.actionClearRecentTemplates = QtGui.QAction(MainWindow)
        self.actionClearRecentTemplates.setObjectName(_fromUtf8("actionClearRecentTemplates"))
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
        self.menuTemplate.addAction(self.actionLoadTemplate)
        self.menuTemplate.addAction(self.actionSaveTemplate)
        self.menuTemplate.addSeparator()
        self.menuTemplate.addAction(self.actionRemoveTemplate)
        self.menuView.addAction(self.actionOnTop)
        self.menubar.addAction(self.menu_File.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuTemplate.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.toolBar.addAction(self.actionPlay)
        self.toolBar.addAction(self.actionPause)
        self.toolBar.addAction(self.actionRecord)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Spotter", None))
        self.spin_offset.setToolTip(_translate("MainWindow", "Bias GUI refresh interval", None))
        self.spin_offset.setSuffix(_translate("MainWindow", " ms", None))
        self.lbl_fps.setToolTip(_translate("MainWindow", "Interface refresh rate, NOT the acquisition rate if grabbing from a camera.", None))
        self.lbl_fps.setText(_translate("MainWindow", "FPS: 100.0", None))
        self.lbl_frame_t.setText(_translate("MainWindow", "00:00:00.000", None))
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
        self.actionCamera.setShortcut(_translate("MainWindow", "Ctrl+D", None))
        self.actionFile.setText(_translate("MainWindow", "&File", None))
        self.actionFile.setToolTip(_translate("MainWindow", "Open video file", None))
        self.actionFile.setShortcut(_translate("MainWindow", "Ctrl+O", None))
        self.actionSave.setText(_translate("MainWindow", "&Transcode", None))
        self.action_Parameters.setText(_translate("MainWindow", "&Parameters", None))
        self.action_Transcode_Video.setText(_translate("MainWindow", "&Transcode Video", None))
        self.actionParameters.setText(_translate("MainWindow", "Parameters", None))
        self.actionAbout.setText(_translate("MainWindow", "&About", None))
        self.actionRecord.setText(_translate("MainWindow", "Record", None))
        self.actionRecord.setToolTip(_translate("MainWindow", "Record Video", None))
        self.actionArduino.setText(_translate("MainWindow", "Arduino", None))
        self.actionArduino.setToolTip(_translate("MainWindow", "Arduino State", None))
        self.actionLoadTemplate.setText(_translate("MainWindow", "Load", None))
        self.actionLoadTemplate.setToolTip(_translate("MainWindow", "Load (Ctrl+T)", None))
        self.actionLoadTemplate.setShortcut(_translate("MainWindow", "Ctrl+T", None))
        self.actionSaveTemplate.setText(_translate("MainWindow", "Save", None))
        self.actionSaveTemplate.setToolTip(_translate("MainWindow", "Save current configuration", None))
        self.actionRemoveTemplate.setText(_translate("MainWindow", "Remove all", None))
        self.actionSourceProperties.setText(_translate("MainWindow", "Source Props", None))
        self.actionOnTop.setText(_translate("MainWindow", "Always on Top", None))
        self.actionClearRecentFiles.setText(_translate("MainWindow", "Clear recent", None))
        self.actionClearRecentFiles.setToolTip(_translate("MainWindow", "Clear list of recently opened files", None))
        self.actionPlay.setText(_translate("MainWindow", "Play", None))
        self.actionPlay.setToolTip(_translate("MainWindow", "Start playback (Shift+Space)", None))
        self.actionPlay.setShortcut(_translate("MainWindow", "Shift+Space", None))
        self.actionPause.setText(_translate("MainWindow", "Pause", None))
        self.actionPause.setToolTip(_translate("MainWindow", "Pause display (Space)", None))
        self.actionPause.setShortcut(_translate("MainWindow", "Space", None))
        self.actionRepeat.setText(_translate("MainWindow", "Repeat", None))
        self.actionRepeat.setToolTip(_translate("MainWindow", "Loop video source", None))
        self.actionRewind.setText(_translate("MainWindow", "Rewind", None))
        self.actionRewind.setToolTip(_translate("MainWindow", "Rewind to first frame", None))
        self.actionFastForward.setText(_translate("MainWindow", "FastForward", None))
        self.actionFastForward.setToolTip(_translate("MainWindow", "Jump to last frame", None))
        self.actionClearRecentTemplates.setText(_translate("MainWindow", "Clear recent", None))
        self.actionClearRecentTemplates.setToolTip(_translate("MainWindow", "Clear list of recently opened templates", None))

import icons_rc
import images_rc
