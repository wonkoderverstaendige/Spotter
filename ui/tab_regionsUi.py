# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'tab_regionsUi.ui'
#
# Created: Fri Feb 15 16:45:09 2013
#      by: PyQt4 UI code generator 4.9.5
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_tab_regions(object):
    def setupUi(self, tab_regions):
        tab_regions.setObjectName(_fromUtf8("tab_regions"))
        tab_regions.resize(241, 325)
        self.gridLayout = QtGui.QGridLayout(tab_regions)
        self.gridLayout.setMargin(0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setSpacing(1)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.toolBox = QtGui.QToolBox(tab_regions)
        self.toolBox.setFrameShape(QtGui.QFrame.NoFrame)
        self.toolBox.setFrameShadow(QtGui.QFrame.Plain)
        self.toolBox.setLineWidth(0)
        self.toolBox.setObjectName(_fromUtf8("toolBox"))
        self.page_regions_overview = QtGui.QWidget()
        self.page_regions_overview.setGeometry(QtCore.QRect(0, 0, 239, 260))
        self.page_regions_overview.setObjectName(_fromUtf8("page_regions_overview"))
        self.gridLayout_6 = QtGui.QGridLayout(self.page_regions_overview)
        self.gridLayout_6.setMargin(0)
        self.gridLayout_6.setSpacing(0)
        self.gridLayout_6.setObjectName(_fromUtf8("gridLayout_6"))
        self.gridLayout_5 = QtGui.QGridLayout()
        self.gridLayout_5.setSpacing(1)
        self.gridLayout_5.setContentsMargins(-1, 0, -1, -1)
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.gridLayout_3 = QtGui.QGridLayout()
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.gridLayout_5.addLayout(self.gridLayout_3, 12, 1, 1, 2)
        self.combo_Object = QtGui.QComboBox(self.page_regions_overview)
        self.combo_Object.setEnabled(False)
        self.combo_Object.setEditable(False)
        self.combo_Object.setObjectName(_fromUtf8("combo_Object"))
        self.gridLayout_5.addWidget(self.combo_Object, 8, 0, 1, 3)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.btn_remove_shape = QtGui.QPushButton(self.page_regions_overview)
        self.btn_remove_shape.setMinimumSize(QtCore.QSize(30, 0))
        self.btn_remove_shape.setObjectName(_fromUtf8("btn_remove_shape"))
        self.horizontalLayout_2.addWidget(self.btn_remove_shape)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.lbl_y = QtGui.QLabel(self.page_regions_overview)
        self.lbl_y.setObjectName(_fromUtf8("lbl_y"))
        self.horizontalLayout_2.addWidget(self.lbl_y)
        self.spin_shape_y = QtGui.QSpinBox(self.page_regions_overview)
        self.spin_shape_y.setButtonSymbols(QtGui.QAbstractSpinBox.PlusMinus)
        self.spin_shape_y.setAccelerated(True)
        self.spin_shape_y.setMinimum(-2048)
        self.spin_shape_y.setMaximum(2048)
        self.spin_shape_y.setObjectName(_fromUtf8("spin_shape_y"))
        self.horizontalLayout_2.addWidget(self.spin_shape_y)
        self.gridLayout_5.addLayout(self.horizontalLayout_2, 5, 0, 1, 3)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.btn_add_shape = QtGui.QPushButton(self.page_regions_overview)
        self.btn_add_shape.setMinimumSize(QtCore.QSize(30, 0))
        self.btn_add_shape.setCheckable(True)
        self.btn_add_shape.setObjectName(_fromUtf8("btn_add_shape"))
        self.horizontalLayout.addWidget(self.btn_add_shape)
        self.ckb_trigger = QtGui.QCheckBox(self.page_regions_overview)
        self.ckb_trigger.setChecked(True)
        self.ckb_trigger.setObjectName(_fromUtf8("ckb_trigger"))
        self.horizontalLayout.addWidget(self.ckb_trigger)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.lbl_x = QtGui.QLabel(self.page_regions_overview)
        self.lbl_x.setObjectName(_fromUtf8("lbl_x"))
        self.horizontalLayout.addWidget(self.lbl_x)
        self.spin_shape_x = QtGui.QSpinBox(self.page_regions_overview)
        self.spin_shape_x.setButtonSymbols(QtGui.QAbstractSpinBox.PlusMinus)
        self.spin_shape_x.setAccelerated(True)
        self.spin_shape_x.setMinimum(-2048)
        self.spin_shape_x.setMaximum(2048)
        self.spin_shape_x.setObjectName(_fromUtf8("spin_shape_x"))
        self.horizontalLayout.addWidget(self.spin_shape_x)
        self.gridLayout_5.addLayout(self.horizontalLayout, 3, 0, 1, 3)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setContentsMargins(0, 0, -1, -1)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.tree_region_shapes = QtGui.QTreeWidget(self.page_regions_overview)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tree_region_shapes.sizePolicy().hasHeightForWidth())
        self.tree_region_shapes.setSizePolicy(sizePolicy)
        self.tree_region_shapes.setProperty("showDropIndicator", False)
        self.tree_region_shapes.setAlternatingRowColors(True)
        self.tree_region_shapes.setIndentation(0)
        self.tree_region_shapes.setObjectName(_fromUtf8("tree_region_shapes"))
        self.horizontalLayout_3.addWidget(self.tree_region_shapes)
        self.tree_region_digital = QtGui.QTreeWidget(self.page_regions_overview)
        self.tree_region_digital.setProperty("showDropIndicator", False)
        self.tree_region_digital.setAlternatingRowColors(True)
        self.tree_region_digital.setIndentation(0)
        self.tree_region_digital.setObjectName(_fromUtf8("tree_region_digital"))
        self.horizontalLayout_3.addWidget(self.tree_region_digital)
        self.gridLayout_5.addLayout(self.horizontalLayout_3, 9, 0, 1, 1)
        self.gridLayout_6.addLayout(self.gridLayout_5, 0, 1, 1, 1)
        self.toolBox.addItem(self.page_regions_overview, _fromUtf8(""))
        self.page_regions_conditions = QtGui.QWidget()
        self.page_regions_conditions.setGeometry(QtCore.QRect(0, 0, 239, 260))
        self.page_regions_conditions.setObjectName(_fromUtf8("page_regions_conditions"))
        self.gridLayout_8 = QtGui.QGridLayout(self.page_regions_conditions)
        self.gridLayout_8.setMargin(0)
        self.gridLayout_8.setSpacing(0)
        self.gridLayout_8.setObjectName(_fromUtf8("gridLayout_8"))
        self.toolBox.addItem(self.page_regions_conditions, _fromUtf8(""))
        self.page_regions_IO = QtGui.QWidget()
        self.page_regions_IO.setGeometry(QtCore.QRect(0, 0, 239, 260))
        self.page_regions_IO.setObjectName(_fromUtf8("page_regions_IO"))
        self.gridLayout_7 = QtGui.QGridLayout(self.page_regions_IO)
        self.gridLayout_7.setMargin(0)
        self.gridLayout_7.setSpacing(0)
        self.gridLayout_7.setObjectName(_fromUtf8("gridLayout_7"))
        self.pushButton_8 = QtGui.QPushButton(self.page_regions_IO)
        self.pushButton_8.setObjectName(_fromUtf8("pushButton_8"))
        self.gridLayout_7.addWidget(self.pushButton_8, 2, 3, 1, 1)
        self.pushButton_9 = QtGui.QPushButton(self.page_regions_IO)
        self.pushButton_9.setObjectName(_fromUtf8("pushButton_9"))
        self.gridLayout_7.addWidget(self.pushButton_9, 2, 1, 1, 1)
        self.pushButton_4 = QtGui.QPushButton(self.page_regions_IO)
        self.pushButton_4.setObjectName(_fromUtf8("pushButton_4"))
        self.gridLayout_7.addWidget(self.pushButton_4, 1, 1, 1, 1)
        self.pushButton_5 = QtGui.QPushButton(self.page_regions_IO)
        self.pushButton_5.setObjectName(_fromUtf8("pushButton_5"))
        self.gridLayout_7.addWidget(self.pushButton_5, 1, 3, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_7.addItem(spacerItem2, 0, 1, 1, 1)
        self.toolBox.addItem(self.page_regions_IO, _fromUtf8(""))
        self.gridLayout_2.addWidget(self.toolBox, 0, 0, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_2, 0, 0, 1, 1)

        self.retranslateUi(tab_regions)
        self.toolBox.setCurrentIndex(0)
        self.toolBox.layout().setSpacing(0)
        QtCore.QMetaObject.connectSlotsByName(tab_regions)

    def retranslateUi(self, tab_regions):
        tab_regions.setWindowTitle(QtGui.QApplication.translate("tab_regions", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.btn_remove_shape.setText(QtGui.QApplication.translate("tab_regions", "&Remove", None, QtGui.QApplication.UnicodeUTF8))
        self.lbl_y.setText(QtGui.QApplication.translate("tab_regions", "y:", None, QtGui.QApplication.UnicodeUTF8))
        self.btn_add_shape.setStatusTip(QtGui.QApplication.translate("tab_regions", "Drag: Rectangle. Shift+drag: Line. Ctrl+drag: Circle.", None, QtGui.QApplication.UnicodeUTF8))
        self.btn_add_shape.setText(QtGui.QApplication.translate("tab_regions", "&Add", None, QtGui.QApplication.UnicodeUTF8))
        self.ckb_trigger.setText(QtGui.QApplication.translate("tab_regions", "Trigger", None, QtGui.QApplication.UnicodeUTF8))
        self.lbl_x.setText(QtGui.QApplication.translate("tab_regions", "x:", None, QtGui.QApplication.UnicodeUTF8))
        self.tree_region_shapes.headerItem().setText(0, QtGui.QApplication.translate("tab_regions", "Shapes", None, QtGui.QApplication.UnicodeUTF8))
        self.tree_region_digital.headerItem().setText(0, QtGui.QApplication.translate("tab_regions", "Digital Out", None, QtGui.QApplication.UnicodeUTF8))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_regions_overview), QtGui.QApplication.translate("tab_regions", "Shapes", None, QtGui.QApplication.UnicodeUTF8))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_regions_conditions), QtGui.QApplication.translate("tab_regions", "Conditions/Triggers", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_8.setText(QtGui.QApplication.translate("tab_regions", "Save", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_9.setText(QtGui.QApplication.translate("tab_regions", "Open", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_4.setText(QtGui.QApplication.translate("tab_regions", "Clone", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_5.setText(QtGui.QApplication.translate("tab_regions", "Delete", None, QtGui.QApplication.UnicodeUTF8))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_regions_IO), QtGui.QApplication.translate("tab_regions", "In/Out", None, QtGui.QApplication.UnicodeUTF8))

