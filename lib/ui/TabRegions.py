# -*- coding: utf-8 -*-
"""
Created on Sun Jan 13 14:19:24 2013
@author: <Ronny Eichler> ronny.eichler@gmail.com


"""
import logging

from PyQt4 import QtGui, QtCore
from tab_regionsUi import Ui_tab_regions
import lib.geometry as geom


class Tab(QtGui.QWidget, Ui_tab_regions):

    label = None
    region = None
    accept_events = True
    event_add_selection = False
    tab_type = "region"

    # mouse event handling
    start_coords = None
    coord_start = None
    coord_end = None
    coord_last = None
    button_start = None

    def __init__(self, region_ref, label=None, *args, **kwargs):
        #super(QtGui.QWidget, self).__init__(parent)
        QtGui.QWidget.__init__(self)
        self.log = logging.getLogger(__name__)
        self.setupUi(self)
        self.region = region_ref

        assert 'spotter' in kwargs
        self.spotter = kwargs['spotter']

        if label is None:
            self.label = self.region.label
        else:
            self.label = label
            self.region.label = label

        # Fill tree/list with all available shapes
        for s in self.region.shapes:
            shape_item = QtGui.QTreeWidgetItem([s.label])
            shape_item.shape = s
            shape_item.setCheckState(0, QtCore.Qt.Checked)
            shape_item.setFlags(shape_item.flags() | QtCore.Qt.ItemIsEditable)
            self.tree_region_shapes.addTopLevelItem(shape_item)

        # List of items in the table to compare when updated. Ugly solution.
        self.slots_items = []

        self.connect(self.btn_add_shape, QtCore.SIGNAL('toggled(bool)'), self.accept_selection)
        self.connect(self.btn_remove_shape, QtCore.SIGNAL('clicked()'), self.remove_shape)
        #self.connect(self.btn_lock_table, QtCore.SIGNAL('toggled(bool)'), self.lock_slot_table)

        # coordinate spin box update signals
        self.connect(self.spin_shape_x, QtCore.SIGNAL('valueChanged(int)'), self.update_shape_position)
        self.connect(self.spin_shape_y, QtCore.SIGNAL('valueChanged(int)'), self.update_shape_position)

        # if a checkbox or spinbox on a shape in the list is changed
        self.spin_shape = None
        self.connect(self.tree_region_shapes, QtCore.SIGNAL('itemChanged(QTreeWidgetItem *, int)'),
                     self.shape_item_changed)
        self.connect(self.tree_region_shapes, QtCore.SIGNAL('itemSelectionChanged()'), self.update_spin_boxes)

        if self.region.active_color is not None:
            ss_string = "background-color: rgba({0[0]}, {0[1]}, {0[2]})".format(self.region.active_color)
            self.lbl_color.setStyleSheet(ss_string)
        self.lbl_color.mouseReleaseEvent = self.change_color

        self.update()

    def update(self):
        self.refresh_shape_list()
        self.refresh_slot_table()
        self.update_spin_boxes()

    def update_spin_boxes(self):
        tree_item = self.tree_region_shapes.selectedItems()
        if tree_item:
            tree_item = tree_item[0]
            # update spin boxes if the coordinates differ between shape and spin box
            if not self.spin_shape_x.value() == tree_item.shape.points[0][0]:
                self.spin_shape_x.setValue(tree_item.shape.points[0][0])
            if not self.spin_shape_y.value() == tree_item.shape.points[0][1]:
                self.spin_shape_y.setValue(tree_item.shape.points[0][1])

    def accept_selection(self, state):
        """ Called by the 'Add' button toggle to accept input for new shapes """
        self.event_add_selection = state

    def process_event(self, event_type, event):
        """ Handle mouse interactions, mainly to draw and move shapes """
        modifiers = QtGui.QApplication.keyboardModifiers()

        if event_type == "mousePress":
            self.button_start = int(event.buttons())
            self.coord_start = [event.x(), event.y()]
            self.coord_last = self.coord_start
        elif event_type == "mouseDrag":
            if int(event.buttons()) == QtCore.Qt.MiddleButton:
                dx = event.x() - self.coord_last[0]
                dy = event.y() - self.coord_last[1]
                self.coord_last = [event.x(), event.y()]
                if modifiers == QtCore.Qt.ShiftModifier:
                    self.move_region(dx, dy)
                else:
                    self.move_shape(dx, dy)

                self.spin_shape = None
                self.update_spin_boxes()
        elif event_type == "mouseRelease":
            # Beware button vs. buttons. buttons() does not hold the button triggering
            # the event. button() does for release, but not for move events.
            button = int(event.button())
            if not button == self.button_start:
                # user clicked different button than initially, to cancel
                # selection I presume
                self.coord_end = None
                self.coord_start = None
                self.button_start = None
                return

            if button == QtCore.Qt.LeftButton and self.event_add_selection:
                # Finalize region selection
                self.coord_end = [event.x(), event.y()]

                shape_type = None
                if modifiers == QtCore.Qt.NoModifier:
                    shape_type = 'rectangle'
                elif modifiers == QtCore.Qt.ShiftModifier:
                    shape_type = 'circle'
                elif modifiers == QtCore.Qt.ControlModifier:
                    shape_type = 'line'

                shape_points = [self.coord_start, self.coord_end]
                if shape_type and shape_points:
                    self.add_shape(shape_type, shape_points)
        else:
            print 'Event not understood. Hulk sad and confused.'

    def move_region(self, dx, dy):
        self.region.move(dx, dy)

    def update_region(self):
        if self.label is None:
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

    def add_shape(self, shape_type, shape_points):  # , shape_label
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
            # find the shape in the shape list of the RegionOfInterest
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
            # find the shape in the shape list of the RegionOfInterest
            idx = self.region.shapes.index(self.tree_region_shapes.currentItem().shape)
            self.region.shapes[idx].move(dx, dy)
        else:
            self.spin_shape = self.tree_region_shapes.currentItem().shape
            return

    @staticmethod
    def shape_item_changed(item, column):
        """
        Activate/inactive shapes. If not active, will not be included in
        collision detection and will not be drawn/will be drawn in a distinct
        way (i.e. only outline or greyed out?)
        """
        if item.checkState(column):
            item.shape.active = True
        else:
            item.shape.active = False
        item.shape.label = item.text(0)

###############################################################################
## SLOT TABLE
###############################################################################
    def populate_slot_table(self):
        """
        Slots for regions are dynamically built, will be empty at start
        unless object template has been loaded before.
        """
        self.region.refresh_slot_list()

        # if there are no slots, the table and its list should be empty
        if not self.region.slots and self.slots_items:
            self.log.debug("Removing all rows")
            while self.table_slots.rowCount():
                self.slots_remove_row(0)
            return

        # check if table of slots is up to date. No missing slots, not listing
        # slots that no longer exist!
        if not (self.slots_items == self.region.slots):
            # Check that no slots are missing from the table
            missing = []
            remove = []
            for rs in self.region.slots:
                if not (rs in self.slots_items):
                    missing.append(rs)

            # Check that no non-existing slots are listed in the table
            for ts in self.slots_items:
                if not (ts in self.region.slots):
                    remove.append(ts)

            # remove the additional rows:
            for rs in remove:
                self.slots_remove_row(self.slots_items.index(rs))

            # add the missing rows
            for ms in missing:
                self.slots_add_row(ms)

            if len(missing) or len(remove):
                self.slots_resize_columns()

    def refresh_slot_table(self):
        # make sure table is updated
        self.populate_slot_table()
        for i in xrange(self.table_slots.rowCount()):
            cbx = self.table_slots.cellWidget(i, 1)
            selected_pin = cbx.currentIndex()
            slot = self.region.slots[i]
            pins, enabled = self.available_pins(slot)

            if selected_pin < len(pins):
                # Slot selected, but the wrong one or shouldn't be selected
                if not (slot.pin is pins[selected_pin]):
                    if slot.pin in pins:
                        pin_idx = pins.index(slot.pin)
                        if pin_idx < 0:
                            cbx.setCurrentIndex(cbx.count()-1)
                        else:
                            cbx.setCurrentIndex(pin_idx)
                    else:
                        cbx.setCurrentIndex(cbx.count()-1)
            else:
                # Nothing selected, but slot has a pin!
                if slot.pin is not None:
                    pin_idx = pins.index(slot.pin)
                    if pin_idx < 0:
                        cbx.setCurrentIndex(cbx.count()-1)
                    else:
                        cbx.setCurrentIndex(pin_idx)
                else:
                    cbx.setCurrentIndex(cbx.count()-1)

        # Disable pins that are already in use
        for row in xrange(self.table_slots.rowCount()):
            pins, enabled = self.available_pins(self.region.slots[row])
            cbx = self.table_slots.cellWidget(row, 1)
            for i in xrange(len(pins)):
                j = cbx.model().index(i, 0)
                cbx.model().setData(j, QtCore.QVariant(enabled[i]), QtCore.Qt.UserRole-1)

    def slot_table_changed(self):
        for i in xrange(self.table_slots.rowCount()):
            cbx = self.table_slots.cellWidget(i, 1)
            slot = self.region.slots[i]
            selected_pin = cbx.currentIndex()
            pins, enabled = self.available_pins(slot)

            if selected_pin < len(pins):
                if not slot.pin is pins[selected_pin]:
                    slot.attach_pin(pins[selected_pin])
            else:
                if slot.pin:
                    slot.detach_pin()
        self.refresh_slot_table()

    @staticmethod
    def _table_slot_row(row):
        """ List of row widget items. """
        item_list = []
        for i in xrange(len(row)):
            item_list.append(QtGui.QTableWidgetItem(row[i]))
        return item_list

    def lock_slot_table(self, state):
        """Toggle button to lock or unlock the whole table."""
        self.table_slots.setEnabled(state)
        if state:
            self.btn_lock_table.setText("Lock")
        else:
            self.btn_lock_table.setText("Unlock")

    def slots_add_row(self, slot, pos=-1):
        """Add new row for [slot] at position. If no position given, append."""
        item = [slot.label, '', 'IGNORE']
        row_items = self._table_slot_row(item)
        if pos < 0:
            pos = len(self.slots_items)
        self.table_slots.insertRow(pos)
        self.slots_items.append(slot)

        for j, item in enumerate(row_items):
            if j == 1:
                self.table_slots.setCellWidget(pos, j, self._combo_pins(slot))
            self.table_slots.setItem(pos, j, item)

    def slots_remove_row(self, index):
        """Remove row from table."""
        self.table_slots.removeRow(index)
        self.slots_items.pop(index)

    def slots_resize_columns(self):
        """Resizing columns to fill whole horizontal space."""
        self.table_slots.resizeColumnsToContents()
        self.table_slots.resizeRowsToContents()
        self.table_slots.horizontalHeader().setStretchLastSection(True)

###############################################################################
## PIN LIST
###############################################################################
    def _combo_pins(self, slot):
        pins, enable = self.available_pins(slot)

        cbx = QtGui.QComboBox()
        for i, p in enumerate(pins):
            cbx.addItem(p.label)
            # Disable all pins already in use somewhere
            # From: http://stackoverflow.com/questions/11099975/pyqt-set-enabled-property-of-a-row-of-qcombobox
            j = cbx.model().index(i, 0)
            cbx.model().setData(j, QtCore.QVariant(enable[i]), QtCore.Qt.UserRole-1)
        cbx.insertSeparator(len(pins))
        cbx.addItem('None')
        cbx.setCurrentIndex(len(pins)+1)

        self.connect(cbx, QtCore.SIGNAL('currentIndexChanged(int)'), self.slot_table_changed)
        return cbx

    def available_pins(self, slot):
        """
        Return list of pins suitable for a specific slot and list of flags of
        availabilities.
        """
        enable = []
        pins = self.spotter.chatter.pins_for_slot(slot)
        for p in pins:
            if p.slot and not (p.slot is slot):
                enable.append(0)
            else:
                enable.append(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        return pins, enable

    def change_color(self, *args):
        """ Allow control over the color of the associated shapes in the video """
        color = QtGui.QColorDialog.getColor()
        if color.isValid():
            self.lbl_color.setStyleSheet("background-color: %s" % color.name())
            self.region.update_color(color.getRgb())

    def closeEvent(self, QCloseEvent):
        self.spotter.tracker.remove_roi(self.region)