# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_tab_pageUi.ui'
#
# Created: Mon Nov 25 22:32:41 2013
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

class Ui_main_tab_page(object):
    def setupUi(self, main_tab_page):
        main_tab_page.setObjectName(_fromUtf8("main_tab_page"))
        main_tab_page.resize(295, 300)
        self.horizontalLayout = QtGui.QHBoxLayout(main_tab_page)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.tabs_sub = QtGui.QTabWidget(main_tab_page)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabs_sub.sizePolicy().hasHeightForWidth())
        self.tabs_sub.setSizePolicy(sizePolicy)
        self.tabs_sub.setFocusPolicy(QtCore.Qt.WheelFocus)
        self.tabs_sub.setTabPosition(QtGui.QTabWidget.East)
        self.tabs_sub.setTabShape(QtGui.QTabWidget.Rounded)
        self.tabs_sub.setDocumentMode(True)
        self.tabs_sub.setTabsClosable(True)
        self.tabs_sub.setObjectName(_fromUtf8("tabs_sub"))
        self.page_base = QtGui.QWidget()
        self.page_base.setObjectName(_fromUtf8("page_base"))
        self.verticalLayout = QtGui.QVBoxLayout(self.page_base)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.btn_new_page = QtGui.QPushButton(self.page_base)
        self.btn_new_page.setObjectName(_fromUtf8("btn_new_page"))
        self.gridLayout.addWidget(self.btn_new_page, 0, 0, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.tabs_sub.addTab(self.page_base, _fromUtf8(""))
        self.horizontalLayout.addWidget(self.tabs_sub)

        self.retranslateUi(main_tab_page)
        QtCore.QMetaObject.connectSlotsByName(main_tab_page)

    def retranslateUi(self, main_tab_page):
        main_tab_page.setWindowTitle(_translate("main_tab_page", "Form", None))
        self.btn_new_page.setText(_translate("main_tab_page", "New Page", None))
        self.tabs_sub.setTabText(self.tabs_sub.indexOf(self.page_base), _translate("main_tab_page", "+", None))

