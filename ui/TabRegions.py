# -*- coding: utf-8 -*-
"""
Created on Sun Jan 13 14:19:24 2013
@author: <Ronny Eichler> ronny.eichler@gmail.com


"""

import sys
from PyQt4 import QtGui, QtCore

sys.path.append('./ui')
from tab_regionsUi import Ui_tab_regions

tab_type = "region"

class Tab(QtGui.QWidget, Ui_tab_regions):

    name = None
    region = None
    accept_events = False

    # mouse event handling    
    start_coords = None
    coords_start = None
    coords_end = None

    def __init__(self, parent, region_handle, label = None):
        self.region = region_handle
        if label == None:
            self.name = self.region.label
        else:
            self.name = label
            self.region.label = label
            
        super(QtGui.QWidget, self).__init__(parent)
        self.setupUi(self)
        
        # Fill tree/list with all available LEDs and mark linked as checked
        for s in self.region.shapes:
            shape_item = QtGui.QTreeWidgetItem([s.label])
            shape_item.shape = s
            shape_item.setCheckState(0,QtCore.Qt.Checked)
            self.tree_region_shapes.addTopLevelItem(shape_item)        

        self.connect(self.btn_add_shape, QtCore.SIGNAL('toggled(bool)'), self.accept_selection)
        self.connect(self.btn_remove_shape, QtCore.SIGNAL('clicked()'), self.remove_shape)
        
        # if a checkbox on a shape in the list is changed
        self.connect(self.tree_region_shapes, QtCore.SIGNAL('itemChanged(QTreeWidgetItem *, int)'), self.itemChanged)

        self.update()


    def update(self):
        if self.name == None:
            print "empty tab"
            return

    def accept_selection(self, state):
        self.accept_events = state


    def process_event(self, event_type, event):
        modifiers = QtGui.QApplication.keyboardModifiers()
        if event_type == "mousePress":
            self.button_start = event.button()
            self.coords_start = (event.x(), event.y())
            
        elif event_type == "mouseDrag":
            if not event.button() == QtCore.Qt.NoButton:
                # Queue draw job for the selection                
                pass
            
        elif event_type == "mouseRelease":
            if not event.button() == self.button_start:
                # user clicked different button than intially, to cancel
                # selection I presume
                self.coords_end = None
                self.coords_start = None
                self.button_start = None                
            else:
                # Everything seems to work out, now we just finalize the new
                # selected region! Hooray!!!
                shape_type = shape_points = None
                coords_end = (event.x(), event.y())
                if modifiers == QtCore.Qt.NoModifier:
                    shape_type = 'Rectangle'
                    shape_points = (self.coords_start, coords_end)                    
                elif modifiers == QtCore.Qt.ShiftModifier:
                    shape_type = 'Circle'
                    shape_points = (self.coords_start, coords_end)
                else:
                    shape_type = 'fluffybunny'
                    shape_points = (self.coords_start, coords_end)
                    
                if shape_type and shape_points:
                    self.add_shape(shape_type, shape_points)
        else:
            print 'Event not understood. Hulk sad and confused.'
    
   
    def add_shape(self, shape_type, shape_points):
        """ Add a new geometric shape to the region. First, create a new 
        item widget. Add it to the region object via its add_shape function
        which will take care of adding it to the list etc. Then add the item
        to the tree widget. Last uncheck the "Add" button.
        """
        shape_item = QtGui.QTreeWidgetItem([shape_type])
        shape_item.shape = self.region.add_shape(shape_type, shape_points)
        shape_item.setCheckState(0,QtCore.Qt.Checked)
        self.tree_region_shapes.addTopLevelItem(shape_item)
        self.tree_region_shapes.setCurrentItem(shape_item)
        shape_item.setFlags(shape_item.flags() | QtCore.Qt.ItemIsEditable)
        self.btn_add_shape.setChecked(False)

    def remove_shape(self):
        selected_item = self.tree_region_shapes.currentItem()
        index = self.tree_region_shapes.indexOfTopLevelItem(selected_item)
        if selected_item:
            self.region.shapes.pop(self.region.shapes.index(selected_item.shape))
            self.tree_region_shapes.takeTopLevelItem(index)

    def itemChanged(self, item, column):
        """ Activate/deactive shapes. If not active, will not be included in
        collision detection and will not be drawn/will be drawn in a distinct
        way (i.e. only outline or greyed out?)
        """
        item.active = item.checkState(column)
        item.shape.label = item.text(0)

    def update_region(self):
        if self.name == None:
            print "Empty object tab! This should not have happened!"
            return
