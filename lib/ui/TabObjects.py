# -*- coding: utf-8 -*-
"""
Created on Sun Jan 13 14:19:24 2013
@author: <Ronny Eichler> ronny.eichler@gmail.com


"""
import logging
from PyQt4 import QtGui, QtCore
from tab_objectsUi import Ui_tab_objects


class Tab(QtGui.QWidget, Ui_tab_objects):

    label = None
    accept_events = False
    tab_type = "object"

    def __init__(self, object_ref, label=None, *args, **kwargs):
        #super(QtGui.QWidget, self).__init__(parent)
        QtGui.QWidget.__init__(self)
        self.log = logging.getLogger(__name__)
        self.setupUi(self)
        self.object = object_ref

        assert 'spotter' in kwargs
        self.spotter = kwargs['spotter']

        if label is None:
            self.label = self.object.label
        else:
            self.label = label
            self.object.label = label

        self.all_features = self.spotter.tracker.leds
        self.all_regions = self.spotter.tracker.rois

        self.populate_feature_list()
        self.connect(self.tree_link_features, QtCore.SIGNAL('itemChanged(QTreeWidgetItem *, int)'), self.feature_item_changed)

        self.connect(self.ckb_track, QtCore.SIGNAL('stateChanged(int)'), self.update_object)
        self.connect(self.ckb_trace, QtCore.SIGNAL('stateChanged(int)'), self.update_object)
        self.connect(self.ckb_analog_pos, QtCore.SIGNAL('stateChanged(int)'), self.update_object)

        #self.connect(self.btn_lock_table, QtCore.SIGNAL('toggled(bool)'), self.lock_slot_table)

        # slot table is static for Object, lists object properties
        self.populate_slot_table()
        self.update()

    def update(self):
        if self.label is None:
            self.log.debug("Updating empty tab")
            return

        self.refresh_feature_list()
        self.refresh_slot_table()

        if not self.ckb_trace.isChecked() == self.object.traced:
            self.ckb_trace.setChecked(self.object.traced)

        if not self.ckb_track.isChecked() == self.object.tracked:
            self.ckb_track.setChecked(self.object.tracked)

        if not self.ckb_analog_pos.isChecked() == self.object.analog_pos:
            self.ckb_analog_pos.setChecked(self.object.analog_pos)

        self.lbl_x.setText('---' if self.object.position is None else "%.0f" % self.object.position[0])
        self.lbl_y.setText('---' if self.object.position is None else "%.0f" % self.object.position[1])

        self.lbl_speed.setText('---' if self.object.speed() is None else "%.1f" % self.object.speed())

        self.dial_direction.setValue(self.dial_direction.value() if self.object.direction() is None
                                     else self.object.direction())

    def update_object(self):
        if self.label is None:
            self.log.debug("Empty object tab! This should not have happened!")
            return
        self.object.tracked = self.ckb_track.isChecked()
        self.object.traced = self.ckb_trace.isChecked()
        self.object.analog_pos = self.ckb_analog_pos.isChecked()

    def process_event(self, event):
        pass

###############################################################################
## FEATURE LIST
###############################################################################
    def populate_feature_list(self):
        """Initial population of feature list, without adding to linked_leds"""
        for f in self.object.linked_leds:
            feature_item = QtGui.QTreeWidgetItem([f.label])
            feature_item.feature = f
            feature_item.setCheckState(0, QtCore.Qt.Checked)
            self.tree_link_features.addTopLevelItem(feature_item)
            feature_item.setFlags(feature_item.flags() | QtCore.Qt.ItemIsEditable)

    def refresh_feature_list(self):
        """
        Compare the content of the list of all available features with the
        current content of the feature tree/list widget. If anything is there
        that shouldn't be, remove it, if something is missing, add it.
        """
        remove = []
        listed = []
        for idx in xrange(self.tree_link_features.topLevelItemCount()):
            list_item = self.tree_link_features.topLevelItem(idx)
            if not list_item.feature in self.all_features:
                remove.append(idx)
                self.unlink_feature(list_item.feature)
                self.log.debug("Should remove feature %s", remove[-1])
            else:
                listed.append(list_item.feature)

        [self.remove_feature(idx) for idx in remove]
        [self.add_feature(f) for f in self.all_features if f not in listed]

    def feature_item_changed(self, item, column):
        """ Checks for differences in checkbox states and linked items.
        If any item in the tree widget is changed, which should only be
        the case if the user checks/unchecks a checkbox to link/unlink a
        feature.
        """
        feature_is_linked = (item.feature in self.object.linked_leds)
        if not item.checkState(column) == feature_is_linked:
            if item.checkState(column):
                self.link_feature(item.feature)
            else:
                self.unlink_feature(item.feature)
        if not item.feature.label == item.text(0):
            item.feature.label = item.text(0)

    def add_feature(self, f):
        """ Add feature to feature list. """
        feature_item = QtGui.QTreeWidgetItem([f.label])
        feature_item.feature = f
        if feature_item.feature in self.object.linked_leds:
            feature_item.setCheckState(0, QtCore.Qt.Checked)
        else:
            feature_item.setCheckState(0, QtCore.Qt.Unchecked)
        self.tree_link_features.addTopLevelItem(feature_item)
        feature_item.setFlags(feature_item.flags() | QtCore.Qt.ItemIsEditable)

    def remove_feature(self, idx):
        """ Remove feature from feature list. """
        self.tree_link_features.takeTopLevelItem(idx)

    def link_feature(self, feature):
        """ Link the object to the feature. """
        self.object.linked_leds.append(feature)

    def unlink_feature(self, feature):
        """ Remove a specific feature from the list. """
        try:
            self.object.linked_leds.remove(feature)
        except ValueError:
            pass

###############################################################################
## SLOT TABLE
###############################################################################
    def populate_slot_table(self):
        for i, s in enumerate(self.object.slots):
            self.slots_add_row(s, i)
        self.slots_resize_columns()

    def refresh_slot_table(self):
        """
        Check if pins still exist (run refresh pin list) and compare to pins
        in the combobox. If different, refresh combo box. Each combobox has
        different pins attached to it, though!
        """
#        for i in xrange(self.table_slots.rowCount()):
#            cbx = self.table_slots.cellWidget(i, 1)
#            slot = self.object.slots[i]
#            selected_pin = cbx.currentIndex()
#            pins, enabled = self.available_pins(slot)
#
#            if selected_pin < len(pins):
#                if not slot.pin is pins[selected_pin]:
#                    slot.attach_pin(pins[selected_pin])
#            else:
#                if slot.pin:
#                    slot.detach_pin()
        for i in xrange(self.table_slots.rowCount()):
            cbx = self.table_slots.cellWidget(i, 1)
            selected_pin = cbx.currentIndex()
            slot = self.object.slots[i]
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

        # refresh combo boxes with proper availabilities. Disable all pins that
        # are already in use. Has to be repeated from above, as slot links
        # could have changed.
        for row in xrange(self.table_slots.rowCount()):
            pins, enabled = self.available_pins(self.object.slots[row])
            cbx = self.table_slots.cellWidget(row, 1)
            for i in xrange(len(pins)):
                j = cbx.model().index(i, 0)
                cbx.model().setData(j, QtCore.QVariant(enabled[i]), QtCore.Qt.UserRole-1)

    def slot_table_changed(self):
        for i in xrange(self.table_slots.rowCount()):
            cbx = self.table_slots.cellWidget(i, 1)
            slot = self.object.slots[i]
            selected_pin = cbx.currentIndex()
            pins, enabled = self.available_pins(slot)
            if selected_pin < len(pins):
                if not slot.pin is pins[selected_pin]:
                    slot.attach_pin(pins[selected_pin])
            else:
                if slot.pin:
                    slot.detach_pin()

    @staticmethod
    def _table_slot_row(row):
        """List of row widget items."""
        item_list = []
        for i in xrange(len(row)):
            item_list.append(QtGui.QTableWidgetItem(row[i]))
        return item_list

    def slots_add_row(self, slot, pos=None):
        row_items = self._table_slot_row([slot.label, '', 'IGNORE'])
        if pos is None:
            pos = len(self.slots_items)
        self.table_slots.insertRow(pos)
        for j, item in enumerate(row_items):
            if j == 1:
                self.table_slots.setCellWidget(pos, j, self._combo_pins(slot))
            self.table_slots.setItem(pos, j, item)

    def slots_remove_row(self, index):
        self.table_slots.removeRow(index)

    def slots_resize_columns(self):
        self.table_slots.resizeColumnsToContents()
        self.table_slots.resizeRowsToContents()
        self.table_slots.horizontalHeader().setStretchLastSection(True)

    def lock_slot_table(self, state):
        self.table_slots.setEnabled(state)
        if state:
            self.btn_lock_table.setText("Lock")
        else:
            self.btn_lock_table.setText("Unlock")

#        eventfilter = WheelEventFilter()
#        combobox.view().installEventFilter(eventfilter)
#class WheelEventFilter(QtCore.QObject):
#    def eventFilter(self, filteredObj, event):
#        print event.type()
#        if event.type() == QtCore.QEvent.Wheel:
#            print "pew pew"
#            return
#        return QtCore.QObject.eventFilter(self, filteredObj, event)

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
        if self.spotter is None:
            return [], []
        enable = []
        pins = self.spotter.chatter.pins(slot.type)
        for p in pins:
            if p.slot and not (p.slot is slot):
                enable.append(0)
            else:
                enable.append(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        return pins, enable

    def closeEvent(self, QCloseEvent):
        self.spotter.tracker.remove_ooi(self.object)