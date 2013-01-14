# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'tab_featuresUi.ui'
#
# Created: Mon Jan 14 03:04:41 2013
#      by: PyQt4 UI code generator 4.8.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_tab_features(object):
    def setupUi(self, tab_features):
        tab_features.setObjectName(_fromUtf8("tab_features"))
        tab_features.resize(319, 324)
        tab_features.setWindowTitle(QtGui.QApplication.translate("tab_features", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.gridLayout = QtGui.QGridLayout(tab_features)
        self.gridLayout.setMargin(0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setSpacing(1)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.toolBox = QtGui.QToolBox(tab_features)
        self.toolBox.setObjectName(_fromUtf8("toolBox"))
        self.page_feature_detection = QtGui.QWidget()
        self.page_feature_detection.setGeometry(QtCore.QRect(0, 0, 317, 259))
        self.page_feature_detection.setObjectName(_fromUtf8("page_feature_detection"))
        self.gridLayout_6 = QtGui.QGridLayout(self.page_feature_detection)
        self.gridLayout_6.setMargin(2)
        self.gridLayout_6.setSpacing(2)
        self.gridLayout_6.setObjectName(_fromUtf8("gridLayout_6"))
        self.verticalLayout_4 = QtGui.QVBoxLayout()
        self.verticalLayout_4.setSpacing(1)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.lbl_colorspace = QtGui.QLabel(self.page_feature_detection)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lbl_colorspace.sizePolicy().hasHeightForWidth())
        self.lbl_colorspace.setSizePolicy(sizePolicy)
        self.lbl_colorspace.setMaximumSize(QtCore.QSize(16777215, 30))
        self.lbl_colorspace.setStyleSheet(_fromUtf8("background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(255, 0, 0, 255), stop:0.166 rgba(255, 255, 0, 255), stop:0.333 rgba(0, 255, 0, 255), stop:0.5 rgba(0, 255, 255, 255), stop:0.666 rgba(0, 0, 255, 255), stop:0.833 rgba(255, 0, 255, 255), stop:1 rgba(255, 0, 0, 255));"))
        self.lbl_colorspace.setText(_fromUtf8(""))
        self.lbl_colorspace.setObjectName(_fromUtf8("lbl_colorspace"))
        self.verticalLayout_4.addWidget(self.lbl_colorspace)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_4.addItem(spacerItem)
        self.gridLayout_6.addLayout(self.verticalLayout_4, 11, 0, 1, 1)
        self.layout_feature_parameters = QtGui.QGridLayout()
        self.layout_feature_parameters.setHorizontalSpacing(2)
        self.layout_feature_parameters.setVerticalSpacing(0)
        self.layout_feature_parameters.setObjectName(_fromUtf8("layout_feature_parameters"))
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.layout_feature_parameters.addItem(spacerItem1, 3, 4, 1, 1)
        self.spin_sat_max = QtGui.QSpinBox(self.page_feature_detection)
        self.spin_sat_max.setWrapping(True)
        self.spin_sat_max.setFrame(True)
        self.spin_sat_max.setButtonSymbols(QtGui.QAbstractSpinBox.PlusMinus)
        self.spin_sat_max.setAccelerated(True)
        self.spin_sat_max.setMaximum(255)
        self.spin_sat_max.setObjectName(_fromUtf8("spin_sat_max"))
        self.layout_feature_parameters.addWidget(self.spin_sat_max, 2, 2, 1, 1)
        self.spin_val_max = QtGui.QSpinBox(self.page_feature_detection)
        self.spin_val_max.setWrapping(True)
        self.spin_val_max.setFrame(True)
        self.spin_val_max.setButtonSymbols(QtGui.QAbstractSpinBox.PlusMinus)
        self.spin_val_max.setAccelerated(True)
        self.spin_val_max.setMaximum(255)
        self.spin_val_max.setObjectName(_fromUtf8("spin_val_max"))
        self.layout_feature_parameters.addWidget(self.spin_val_max, 3, 2, 1, 1)
        self.lbl_hue = QtGui.QLabel(self.page_feature_detection)
        self.lbl_hue.setText(QtGui.QApplication.translate("tab_features", "Hue", None, QtGui.QApplication.UnicodeUTF8))
        self.lbl_hue.setObjectName(_fromUtf8("lbl_hue"))
        self.layout_feature_parameters.addWidget(self.lbl_hue, 1, 0, 1, 1)
        self.lbl_val = QtGui.QLabel(self.page_feature_detection)
        self.lbl_val.setText(QtGui.QApplication.translate("tab_features", "Val", None, QtGui.QApplication.UnicodeUTF8))
        self.lbl_val.setObjectName(_fromUtf8("lbl_val"))
        self.layout_feature_parameters.addWidget(self.lbl_val, 3, 0, 1, 1)
        self.spin_hue_max = QtGui.QSpinBox(self.page_feature_detection)
        self.spin_hue_max.setWrapping(True)
        self.spin_hue_max.setFrame(True)
        self.spin_hue_max.setButtonSymbols(QtGui.QAbstractSpinBox.PlusMinus)
        self.spin_hue_max.setAccelerated(True)
        self.spin_hue_max.setMaximum(179)
        self.spin_hue_max.setObjectName(_fromUtf8("spin_hue_max"))
        self.layout_feature_parameters.addWidget(self.spin_hue_max, 1, 2, 1, 1)
        self.lbl_sat = QtGui.QLabel(self.page_feature_detection)
        self.lbl_sat.setText(QtGui.QApplication.translate("tab_features", "Sat", None, QtGui.QApplication.UnicodeUTF8))
        self.lbl_sat.setObjectName(_fromUtf8("lbl_sat"))
        self.layout_feature_parameters.addWidget(self.lbl_sat, 2, 0, 1, 1)
        self.spin_hue_min = QtGui.QSpinBox(self.page_feature_detection)
        self.spin_hue_min.setWrapping(True)
        self.spin_hue_min.setFrame(True)
        self.spin_hue_min.setButtonSymbols(QtGui.QAbstractSpinBox.PlusMinus)
        self.spin_hue_min.setAccelerated(True)
        self.spin_hue_min.setMaximum(179)
        self.spin_hue_min.setObjectName(_fromUtf8("spin_hue_min"))
        self.layout_feature_parameters.addWidget(self.spin_hue_min, 1, 1, 1, 1)
        self.spin_sat_min = QtGui.QSpinBox(self.page_feature_detection)
        self.spin_sat_min.setWrapping(True)
        self.spin_sat_min.setFrame(True)
        self.spin_sat_min.setButtonSymbols(QtGui.QAbstractSpinBox.PlusMinus)
        self.spin_sat_min.setAccelerated(True)
        self.spin_sat_min.setMaximum(255)
        self.spin_sat_min.setObjectName(_fromUtf8("spin_sat_min"))
        self.layout_feature_parameters.addWidget(self.spin_sat_min, 2, 1, 1, 1)
        self.btn_pick_color = QtGui.QPushButton(self.page_feature_detection)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_pick_color.sizePolicy().hasHeightForWidth())
        self.btn_pick_color.setSizePolicy(sizePolicy)
        self.btn_pick_color.setToolTip(QtGui.QApplication.translate("tab_features", "Pick thresholds from image by dragging frame around the spot of interest", None, QtGui.QApplication.UnicodeUTF8))
        self.btn_pick_color.setStatusTip(QtGui.QApplication.translate("tab_features", "Pick rage from image", None, QtGui.QApplication.UnicodeUTF8))
        self.btn_pick_color.setText(QtGui.QApplication.translate("tab_features", "Pick", None, QtGui.QApplication.UnicodeUTF8))
        self.btn_pick_color.setCheckable(True)
        self.btn_pick_color.setFlat(False)
        self.btn_pick_color.setObjectName(_fromUtf8("btn_pick_color"))
        self.layout_feature_parameters.addWidget(self.btn_pick_color, 4, 1, 1, 2)
        self.lbl_min = QtGui.QLabel(self.page_feature_detection)
        self.lbl_min.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.lbl_min.setText(QtGui.QApplication.translate("tab_features", "Min", None, QtGui.QApplication.UnicodeUTF8))
        self.lbl_min.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_min.setObjectName(_fromUtf8("lbl_min"))
        self.layout_feature_parameters.addWidget(self.lbl_min, 0, 1, 1, 1)
        self.lbl_max = QtGui.QLabel(self.page_feature_detection)
        self.lbl_max.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.lbl_max.setText(QtGui.QApplication.translate("tab_features", "Max", None, QtGui.QApplication.UnicodeUTF8))
        self.lbl_max.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_max.setObjectName(_fromUtf8("lbl_max"))
        self.layout_feature_parameters.addWidget(self.lbl_max, 0, 2, 1, 1)
        self.spin_val_min = QtGui.QSpinBox(self.page_feature_detection)
        self.spin_val_min.setWrapping(True)
        self.spin_val_min.setFrame(True)
        self.spin_val_min.setButtonSymbols(QtGui.QAbstractSpinBox.PlusMinus)
        self.spin_val_min.setAccelerated(True)
        self.spin_val_min.setMaximum(255)
        self.spin_val_min.setObjectName(_fromUtf8("spin_val_min"))
        self.layout_feature_parameters.addWidget(self.spin_val_min, 3, 1, 1, 1)
        self.line_2 = QtGui.QFrame(self.page_feature_detection)
        self.line_2.setFrameShape(QtGui.QFrame.VLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName(_fromUtf8("line_2"))
        self.layout_feature_parameters.addWidget(self.line_2, 0, 3, 5, 1)
        self.gridLayout_6.addLayout(self.layout_feature_parameters, 10, 0, 1, 1)
        self.combo_label = QtGui.QComboBox(self.page_feature_detection)
        self.combo_label.setEditable(True)
        self.combo_label.setInsertPolicy(QtGui.QComboBox.NoInsert)
        self.combo_label.setObjectName(_fromUtf8("combo_label"))
        self.combo_label.addItem(_fromUtf8(""))
        self.combo_label.setItemText(0, QtGui.QApplication.translate("tab_features", "redLED", None, QtGui.QApplication.UnicodeUTF8))
        self.combo_label.addItem(_fromUtf8(""))
        self.combo_label.setItemText(1, QtGui.QApplication.translate("tab_features", "greenLED", None, QtGui.QApplication.UnicodeUTF8))
        self.combo_label.addItem(_fromUtf8(""))
        self.combo_label.setItemText(2, QtGui.QApplication.translate("tab_features", "blueLED", None, QtGui.QApplication.UnicodeUTF8))
        self.gridLayout_6.addWidget(self.combo_label, 8, 0, 1, 1)
        self.gridLayout_3 = QtGui.QGridLayout()
        self.gridLayout_3.setContentsMargins(-1, 0, -1, -1)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_3.addItem(spacerItem2, 1, 3, 1, 1)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setContentsMargins(-1, 0, -1, -1)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.ckb_trace = QtGui.QCheckBox(self.page_feature_detection)
        self.ckb_trace.setEnabled(False)
        self.ckb_trace.setText(QtGui.QApplication.translate("tab_features", "Show Trace", None, QtGui.QApplication.UnicodeUTF8))
        self.ckb_trace.setChecked(True)
        self.ckb_trace.setObjectName(_fromUtf8("ckb_trace"))
        self.verticalLayout.addWidget(self.ckb_trace)
        self.ckb_marker = QtGui.QCheckBox(self.page_feature_detection)
        self.ckb_marker.setText(QtGui.QApplication.translate("tab_features", "Show Marker", None, QtGui.QApplication.UnicodeUTF8))
        self.ckb_marker.setChecked(True)
        self.ckb_marker.setObjectName(_fromUtf8("ckb_marker"))
        self.verticalLayout.addWidget(self.ckb_marker)
        self.gridLayout_3.addLayout(self.verticalLayout, 1, 0, 1, 1)
        self.gridLayout_4 = QtGui.QGridLayout()
        self.gridLayout_4.setContentsMargins(-1, 0, -1, -1)
        self.gridLayout_4.setHorizontalSpacing(6)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.lbl_y_lbl = QtGui.QLabel(self.page_feature_detection)
        self.lbl_y_lbl.setText(QtGui.QApplication.translate("tab_features", "y:", None, QtGui.QApplication.UnicodeUTF8))
        self.lbl_y_lbl.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lbl_y_lbl.setObjectName(_fromUtf8("lbl_y_lbl"))
        self.gridLayout_4.addWidget(self.lbl_y_lbl, 1, 0, 1, 1)
        self.lbl_xlbl = QtGui.QLabel(self.page_feature_detection)
        self.lbl_xlbl.setText(QtGui.QApplication.translate("tab_features", "x:", None, QtGui.QApplication.UnicodeUTF8))
        self.lbl_xlbl.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lbl_xlbl.setObjectName(_fromUtf8("lbl_xlbl"))
        self.gridLayout_4.addWidget(self.lbl_xlbl, 0, 0, 1, 1)
        self.lbl_x = QtGui.QLabel(self.page_feature_detection)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lbl_x.sizePolicy().hasHeightForWidth())
        self.lbl_x.setSizePolicy(sizePolicy)
        self.lbl_x.setMinimumSize(QtCore.QSize(32, 0))
        self.lbl_x.setMaximumSize(QtCore.QSize(32, 16777215))
        self.lbl_x.setText(QtGui.QApplication.translate("tab_features", "---", None, QtGui.QApplication.UnicodeUTF8))
        self.lbl_x.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lbl_x.setObjectName(_fromUtf8("lbl_x"))
        self.gridLayout_4.addWidget(self.lbl_x, 0, 1, 1, 1)
        self.lbl_y = QtGui.QLabel(self.page_feature_detection)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lbl_y.sizePolicy().hasHeightForWidth())
        self.lbl_y.setSizePolicy(sizePolicy)
        self.lbl_y.setMinimumSize(QtCore.QSize(32, 0))
        self.lbl_y.setMaximumSize(QtCore.QSize(32, 16777215))
        self.lbl_y.setText(QtGui.QApplication.translate("tab_features", "---", None, QtGui.QApplication.UnicodeUTF8))
        self.lbl_y.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lbl_y.setObjectName(_fromUtf8("lbl_y"))
        self.gridLayout_4.addWidget(self.lbl_y, 1, 1, 1, 1)
        self.gridLayout_4.setColumnMinimumWidth(0, 20)
        self.gridLayout_4.setColumnMinimumWidth(1, 20)
        self.gridLayout_3.addLayout(self.gridLayout_4, 1, 4, 1, 1)
        self.gridLayout_6.addLayout(self.gridLayout_3, 3, 0, 1, 1)
        self.line = QtGui.QFrame(self.page_feature_detection)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.gridLayout_6.addWidget(self.line, 9, 0, 1, 1)
        self.toolBox.addItem(self.page_feature_detection, _fromUtf8(""))
        self.page_feature_restriction = QtGui.QWidget()
        self.page_feature_restriction.setGeometry(QtCore.QRect(0, 0, 317, 259))
        self.page_feature_restriction.setObjectName(_fromUtf8("page_feature_restriction"))
        self.gridLayout_8 = QtGui.QGridLayout(self.page_feature_restriction)
        self.gridLayout_8.setObjectName(_fromUtf8("gridLayout_8"))
        self.ckb_track = QtGui.QCheckBox(self.page_feature_restriction)
        self.ckb_track.setText(QtGui.QApplication.translate("tab_features", "Detection Active", None, QtGui.QApplication.UnicodeUTF8))
        self.ckb_track.setChecked(True)
        self.ckb_track.setObjectName(_fromUtf8("ckb_track"))
        self.gridLayout_8.addWidget(self.ckb_track, 0, 0, 1, 1)
        self.ckb_fixed_pos = QtGui.QCheckBox(self.page_feature_restriction)
        self.ckb_fixed_pos.setText(QtGui.QApplication.translate("tab_features", "Fixed Position", None, QtGui.QApplication.UnicodeUTF8))
        self.ckb_fixed_pos.setObjectName(_fromUtf8("ckb_fixed_pos"))
        self.gridLayout_8.addWidget(self.ckb_fixed_pos, 1, 0, 1, 1)
        self.toolBox.addItem(self.page_feature_restriction, _fromUtf8(""))
        self.page_feature_IO = QtGui.QWidget()
        self.page_feature_IO.setGeometry(QtCore.QRect(0, 0, 317, 259))
        self.page_feature_IO.setObjectName(_fromUtf8("page_feature_IO"))
        self.gridLayout_7 = QtGui.QGridLayout(self.page_feature_IO)
        self.gridLayout_7.setObjectName(_fromUtf8("gridLayout_7"))
        self.pushButton_8 = QtGui.QPushButton(self.page_feature_IO)
        self.pushButton_8.setText(QtGui.QApplication.translate("tab_features", "Save", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_8.setObjectName(_fromUtf8("pushButton_8"))
        self.gridLayout_7.addWidget(self.pushButton_8, 2, 3, 1, 1)
        self.pushButton_9 = QtGui.QPushButton(self.page_feature_IO)
        self.pushButton_9.setText(QtGui.QApplication.translate("tab_features", "Open", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_9.setObjectName(_fromUtf8("pushButton_9"))
        self.gridLayout_7.addWidget(self.pushButton_9, 2, 1, 1, 1)
        self.pushButton_4 = QtGui.QPushButton(self.page_feature_IO)
        self.pushButton_4.setText(QtGui.QApplication.translate("tab_features", "Clone", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_4.setObjectName(_fromUtf8("pushButton_4"))
        self.gridLayout_7.addWidget(self.pushButton_4, 1, 1, 1, 1)
        self.pushButton_5 = QtGui.QPushButton(self.page_feature_IO)
        self.pushButton_5.setText(QtGui.QApplication.translate("tab_features", "Delete", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_5.setObjectName(_fromUtf8("pushButton_5"))
        self.gridLayout_7.addWidget(self.pushButton_5, 1, 3, 1, 1)
        spacerItem3 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_7.addItem(spacerItem3, 0, 1, 1, 1)
        self.toolBox.addItem(self.page_feature_IO, _fromUtf8(""))
        self.gridLayout_2.addWidget(self.toolBox, 0, 0, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_2, 0, 0, 1, 1)

        self.retranslateUi(tab_features)
        self.toolBox.setCurrentIndex(0)
        self.toolBox.layout().setSpacing(0)
        self.combo_label.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(tab_features)

    def retranslateUi(self, tab_features):
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_feature_detection), QtGui.QApplication.translate("tab_features", "Detection", None, QtGui.QApplication.UnicodeUTF8))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_feature_restriction), QtGui.QApplication.translate("tab_features", "Restrictions", None, QtGui.QApplication.UnicodeUTF8))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_feature_IO), QtGui.QApplication.translate("tab_features", "In/Out", None, QtGui.QApplication.UnicodeUTF8))
