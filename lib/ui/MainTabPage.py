# -*- coding: utf-8 -*-
"""
Created on Sun Jan 13 14:19:24 2013
@author: <Ronny Eichler> ronny.eichler@gmail.com


"""
import logging

from PyQt4 import QtGui, QtCore
from main_tab_pageUi import Ui_main_tab_page


class MainTabPage(QtGui.QWidget, Ui_main_tab_page):

    def __init__(self, label=None, sub_page_class=None, *args, **kwargs):
        self.log = logging.getLogger(__name__)
        QtGui.QWidget.__init__(self)
        #super(QtGui.QWidget, self).__init__(parent)

        self.label = label
        self.sub_page_class = sub_page_class

        assert 'spotter' in kwargs
        self.spotter = kwargs['spotter']

        self.setupUi(self)
        self.btn_new_page.setText("New " + self.label)

        self.tabs_sub.tabCloseRequested.connect(self.remove_page)

    def add_item(self, ref, focus_new=True, *args, **kwargs):
        """
        Add new tab with Widget new_tab_class and switches to it.

        ref is the object that is being represented by the tab,
        for example an LED or Object.
        """
        new_tab = self.sub_page_class(ref, spotter=self.spotter, *args, **kwargs)
        self.tabs_sub.insertTab(self.tabs_sub.count() - 1, new_tab, new_tab.label)

        if focus_new:
            self.tabs_sub.setCurrentIndex(self.tabs_sub.count() - 2)
        else:
            self.tabs_sub.setCurrentIndex(0)

        return new_tab

    def current_page_widget(self):
        return self.tabs_sub.widget(self.tabs_sub.currentIndex())

    def remove_page(self, idx):
        if idx < self.tabs_sub.count()-1:
            self.log.debug("Removing page #%d from %s", idx, self.label)
            rv = self.tabs_sub.widget(idx).close()
            if rv:
                self.tabs_sub.removeTab(idx)
            else:
                self.log.debug("Couldn't remove the page")

    def remove_all_pages(self):
        """ Remove all pages one by one """
        for n in range(self.tabs_sub.count()-1):
            print self.label, n
            self.remove_page(0)