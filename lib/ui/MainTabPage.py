# -*- coding: utf-8 -*-
"""
Created on Sun Jan 13 14:19:24 2013
@author: <Ronny Eichler> ronny.eichler@gmail.com


"""

from PyQt4 import QtGui, QtCore
from main_tab_pageUi import Ui_main_tab


class Page(QtGui.QWidget, Ui_main_tab):

    def __init__(self, parent, label=None, sub_page_class=None):
        super(QtGui.QWidget, self).__init__(parent)

        self.label = label
        self.sub_page_class = sub_page_class

        self.setupUi(self)
        self.btn_new_page.setText("New " + self.label)

    def add_item(self, ref, focus_new=True):
        """
        Add new tab with Widget new_tab_class and switches to it.

        ref is the object that is being represented by the tab,
        for example an LED or Object.
        """
        new_tab = self.sub_page_class(self, ref)
        self.tabs_sub.insertTab(self.tabs_sub.count() - 1, new_tab, new_tab.label)

        if focus_new:
            self.tabs_sub.setCurrentIndex(self.tabs_sub.count() - 2)
        else:
            self.tabs_sub.setCurrentIndex(0)

        return new_tab