# -*- coding: utf-8 -*-
"""
Created on Sun Jan 13 14:19:24 2013
@author: <Ronny Eichler> ronny.eichler@gmail.com


"""

import sys
import math
import random
from PyQt4 import QtGui, QtCore

sys.path.append('./ui')
from tab_regionsUi import Ui_tab_regions

tab_type = "region"

class Tab(QtGui.QWidget, Ui_tab_regions):

    label = None
    region = None
    accept_events = True
    event_add_selection = False
    tab_type = "region"

    # mouse event handling
    start_coords = None
    coords_start = None
    coords_end = None

    def __init__(self, parent, region_handle, label = None):
        self.region = region_handle
        if label == None:
            self.label = self.region.label
        else:
            self.label = label
            self.region.label = label

        self.parent = parent

        super(QtGui.QWidget, self).__init__(parent)
        self.setupUi(self)

        # Fill tree/list with all available shapes
        for s in self.region.shapes:
            shape_item = QtGui.QTreeWidgetItem([s.label])
            shape_item.shape = s
            shape_item.setCheckState(0,QtCore.Qt.Checked)
            shape_item.setFlags(shape_item.flags() | QtCore.Qt.ItemIsEditable)
            self.tree_region_shapes.addTopLevelItem(shape_item)

        self.connect(self.btn_add_shape, QtCore.SIGNAL('toggled(bool)'), self.accept_selection)
        self.connect(self.btn_remove_shape, QtCore.SIGNAL('clicked()'), self.remove_shape)

        self.connect(self.spin_shape_x, QtCore.SIGNAL('valueChanged(int)'), self.update_shape_position)
        self.connect(self.spin_shape_y, QtCore.SIGNAL('valueChanged(int)'), self.update_shape_position)

        # if a checkbox or spinbox on a shape in the list is changed
        self.spin_shape = None
        self.connect(self.tree_region_shapes, QtCore.SIGNAL('itemChanged(QTreeWidgetItem *, int)'), self.shape_item_changed)
        self.connect(self.tree_region_shapes, QtCore.SIGNAL('itemSelectionChanged()'), self.update_spin_boxes)

        self.update()


    def update(self):
        self.refresh_pin_list()
        self.refresh_shape_list()

    def update_spin_boxes(self):
        tree_item = self.tree_region_shapes.selectedItems()
        if tree_item:
            tree_item = tree_item[0]
            if not self.spin_shape_x.value() == tree_item.shape.points[0][0]:
                self.spin_shape_x.setValue(tree_item.shape.points[0][0])
            if not self.spin_shape_y.value() == tree_item.shape.points[0][1]:
                self.spin_shape_y.setValue(tree_item.shape.points[0][1])


    def accept_selection(self, state):
        self.event_add_selection = state


    def process_event(self, event_type, event):
        modifiers = QtGui.QApplication.keyboardModifiers()
        if event_type == "mousePress":
            self.button_start = int(event.buttons())
            self.coords_start = [event.x(), event.y()]
            self.coords_last = self.coords_start
        elif event_type == "mouseDrag":
            if int(event.buttons()) == QtCore.Qt.MiddleButton:
                dx = event.x() - self.coords_last[0]
                dy = event.y() - self.coords_last[1]
                self.coords_last = [event.x(), event.y()]
                if modifiers == QtCore.Qt.ShiftModifier:
                     self.move_shape(dx, dy)
                else:
                    self.move_region(dx, dy)
                self.spin_shape = None
                self.update_spin_boxes()
        elif event_type == "mouseRelease":
            """
            Beware the button vs. buttons difference. buttons() does not hold
            the button triggering the event, button() does for release, but
            not for move events... what?
            """
            button = int(event.button())
            if not button == self.button_start:
                # user clicked different button than intially, to cancel
                # selection I presume
                self.coords_end = None
                self.coords_start = None
                self.button_start = None
                return
            if button == QtCore.Qt.LeftButton and self.event_add_selection:
                # Everything seems to work out, now we just finalize the new
                # selected region! Hooray!!!
                shape_type = shape_points = None
                self.coords_end = [event.x(), event.y()]
                if modifiers == QtCore.Qt.NoModifier:
                    shape_type = 'rectangle'
                elif modifiers == QtCore.Qt.ShiftModifier:
                    shape_type = 'circle'
                elif modifiers == QtCore.Qt.ControlModifier:
                    shape_type = 'line'

                shape_points = [self.coords_start, self.coords_end]
                if shape_type and shape_points:
                    self.add_shape(shape_type, shape_points, shape_type)
        else:
            print 'Event not understood. Hulk sad and confused.'

    def move_region(self, dx, dy):
        self.region.move(dx, dy)


    def update_region(self):
        if self.label == None:
            print "Empty object tab! This should not have happened!"
            return


###############################################################################
## SHAPE LIST
###############################################################################
    def refresh_shape_list(self):
        # If nothing selected, select the first item in the list
        n_items = self.tree_region_shapes.topLevelItemCount()
        if n_items and not self.tree_region_shapes.currentItem():
            self.tree_region_shapes.setCurrentItem(self.tree_region_shapes.topLevelItem(0))


    def add_shape(self, shape_type, shape_points, shape_label):
        """
        Add a new geometric shape to the region. First, create a new
        item widget. Add it to the region object via its add_shape function
        which will take care of adding it to the list etc. Then add the item
        to the tree widget. Last uncheck the "Add" button.
        """
        shape_item = QtGui.QTreeWidgetItem([shape_type])
        shape_item.shape = self.region.add_shape(shape_type, shape_points, shape_type)
        shape_item.setCheckState(0, QtCore.Qt.Checked)
        self.tree_region_shapes.addTopLevelItem(shape_item)
        self.tree_region_shapes.setCurrentItem(shape_item)
        shape_item.setFlags(shape_item.flags() | QtCore.Qt.ItemIsEditable)
        self.btn_add_shape.setChecked(False)

    def remove_shape(self):
        """ Remove a shape from the list defining a ROI """
        if not self.tree_region_shapes.currentItem():
            return
        selected_item = self.tree_region_shapes.currentItem()
        index = self.tree_region_shapes.indexOfTopLevelItem(selected_item)
        if selected_item:
            self.region.remove_shape(selected_item.shape)
            self.tree_region_shapes.takeTopLevelItem(index)

    def update_shape_position(self):
        """
        Update position of the shape if the values in the spin boxes,
        representing the top right corner of the shape, is changed. Requires
        checking if the spin box update is caused by just switching to a
        different shape in the shape tree list!
        """
        if not self.tree_region_shapes.currentItem():
            return

        if self.tree_region_shapes.currentItem().shape == self.spin_shape:
            # find the shape in the shape list of the ROI
            idx = self.region.shapes.index(self.tree_region_shapes.currentItem().shape)
            dx = self.spin_shape_x.value() - self.region.shapes[idx].points[0][0]
            dy = self.spin_shape_y.value() - self.region.shapes[idx].points[0][1]
            self.move_shape(dx, dy)
        else:
            self.spin_shape = self.tree_region_shapes.currentItem().shape
            return

    def move_shape(self, dx, dy):
        """
        Update position of geometric shape by offsetting all points of shape
        by delta coming from change of the spin boxes or dragging the mouse
        while middle clicking
        """
        if not self.tree_region_shapes.currentItem():
            return

        if self.tree_region_shapes.currentItem().shape == self.spin_shape:
            # find the shape in the shape list of the ROI
            idx = self.region.shapes.index(self.tree_region_shapes.currentItem().shape)
            self.region.shapes[idx].move(dx, dy)
        else:
            self.spin_shape = self.tree_region_shapes.currentItem().shape
            return

    def shape_item_changed(self, item, column):
        """
        Activate/deactive shapes. If not active, will not be included in
        collision detection and will not be drawn/will be drawn in a distinct
        way (i.e. only outline or greyed out?)
        """
        if item.checkState(column):
            item.shape.active = True
        else:
            item.shape.active = False
        item.shape.label = item.text(0)


###############################################################################
## PIN LIST
###############################################################################
    def refresh_pin_list(self):
        # If nothing selected, select the first item in the list
        n_items = self.tree_region_digital.topLevelItemCount()
        if n_items and not self.tree_region_digital.currentItem():
            self.tree_region_digital.setCurrentItem(self.tree_region_digital.topLevelItem(0))
        pins = self.parent.spotter.chatter.pins()
        if pins:
            pins = pins['digital']
        if self.parent.spotter.chatter.is_open() and pins:
            while not self.tree_region_digital.topLevelItemCount() == pins.n:
                self.add_pin(self.tree_region_digital.topLevelItemCount())
        else:
            while not self.tree_region_digital.topLevelItemCount() == 0:
                self.remove_pin()


    def add_pin(self, pin):
        """
        Add a new digital out pin to the list of pins.
        """
        pin_item = QtGui.QTreeWidgetItem([str(pin)])
#        pin_item.pin = self.region.add_shape(shape_type, shape_points, shape_type)
        pin_item.setCheckState(0, QtCore.Qt.Unchecked)
        self.tree_region_digital.addTopLevelItem(pin_item)
        self.tree_region_digital.setCurrentItem(pin_item)
#        pin_item.setFlags(pin_item.flags() | QtCore.Qt.ItemIsEditable)

    def remove_pin(self):
        """ Remove a pin from the list of available digital out pins """
        self.tree_region_digital.takeTopLevelItem(0)

