# -*- coding: utf-8 -*-
"""
Created on Sun Jan 13 14:19:24 2013
@author: <Ronny Eichler> ronny.eichler@gmail.com


"""
import logging

from PyQt4 import QtGui, QtCore

import lib.geometry as geom
import lib.utilities as utils

from MainTabPage import MainTabPage
from side_barUi import Ui_side_bar
import TabFeatures
import TabObjects
import TabRegions
import TabSource
import TabRecord
import TabSerial


class SideBar(QtGui.QWidget, Ui_side_bar):

    def __init__(self, parent, *args, **kwargs):
        self.log = logging.getLogger(__name__)
        QtGui.QWidget.__init__(self)
        #super(QtGui.QWidget, self).__init__(parent)

        self.setupUi(self)

        self.parent = parent
        self.spotter = self.parent.spotter

        self.log.debug('Opening features main tab')
        self.features_page = MainTabPage("Features", TabFeatures.Tab, spotter=self.spotter, *args, **kwargs)
        self.tabs_main.insertTab(-1, self.features_page, self.features_page.label)
        self.connect(self.features_page, QtCore.SIGNAL('currentChanged(int)'), self.tab_features_switch)
        self.connect(self.features_page.btn_new_page, QtCore.SIGNAL('clicked()'), self.add_feature)
        #self.features_page.tabs_sub.tabCloseRequested.connect(self.remove_page)

        self.log.debug('Opening objects main tab')
        self.objects_page = MainTabPage("Objects", TabObjects.Tab, spotter=self.spotter, *args, **kwargs)
        self.tabs_main.insertTab(-1, self.objects_page, self.objects_page.label)
        self.connect(self.objects_page, QtCore.SIGNAL('currentChanged(int)'), self.tab_objects_switch)
        self.connect(self.objects_page.btn_new_page, QtCore.SIGNAL('clicked()'), self.add_object)
        #self.objects_page.tabs_sub.tabCloseRequested.connect(self.remove_page)

        self.log.debug('Opening regions main tab')
        self.regions_page = MainTabPage("Regions", TabRegions.Tab, spotter=self.spotter, *args, **kwargs)
        self.tabs_main.insertTab(-1, self.regions_page, self.regions_page.label)
        self.connect(self.regions_page, QtCore.SIGNAL('currentChanged(int)'), self.tab_regions_switch)
        self.connect(self.regions_page.btn_new_page, QtCore.SIGNAL('clicked()'), self.add_region)
        #self.regions_page.tabs_sub.tabCloseRequested.connect(self.remove_page)

        self.log.debug('Opening source main tab')
        self.source_page = MainTabPage("Source", TabSource.Tab, spotter=self.spotter, *args, **kwargs)
        self.tabs_main.insertTab(-1, self.source_page, self.source_page.label)
        self.add_source(self.spotter.grabber)

        self.log.debug('Opening recording main tab')
        self.record_page = MainTabPage("Recording", TabRecord.Tab, spotter=self.spotter, *args, **kwargs)
        self.tabs_main.insertTab(-1, self.record_page, self.record_page.label)
        self.add_record(self.spotter.writer)

        self.log.debug('Opening serial main tab')
        self.serial_page = MainTabPage("Serial", TabSerial.Tab, spotter=self.spotter, *args, **kwargs)
        self.tabs_main.insertTab(-1, self.serial_page, self.serial_page.label)
        self.serial_tabs = []
        self.add_serial(self.spotter.chatter)

    def add_tab(self, tab_widget, new_tab_class, tab_equivalent, focus_new=True):
        """
        Add new tab with Widget new_tab_class and switches to it. The
        tab_equivalent is the object that is being represented by the tab,
        for example an LED or Object.
        """
        new_tab = new_tab_class.Tab(tab_equivalent, spotter=self.spotter)
        tab_widget.insertTab(tab_widget.count() - 1, new_tab, new_tab.label)
        if focus_new:
            tab_widget.setCurrentIndex(tab_widget.count() - 2)
        else:
            tab_widget.setCurrentIndex(0)
        return new_tab

    def get_top_tab_label(self):
        """ Return label of the top level tab. """
        # TODO: Unused?
        return self.tabs_main.tabText(self.tabs_main.currentIndex())

    def get_child_page(self):
        active_top_tab_label = self.tabs_main.tabText(self.tabs_main.currentIndex())
        if active_top_tab_label == "Features" and (self.tabs_main.count() > 1):
            return self.features_page.current_page_widget()
        elif active_top_tab_label == "Objects" and (self.tabs_main.count() > 1):
            return self.objects_page.current_page_widget()
        elif active_top_tab_label == "Regions" and (self.tabs_main.count() > 1):
            return self.regions_page.current_page_widget()
        elif active_top_tab_label == "Serial":
            return self.serial_page.current_page_widget()
        else:
            return None

    def update_current_page(self):
        """
        Currently visible tab is the only one that requires to be updated
        live when parameters of its associated object change, e.g. coordinates
        of tracked objects or LEDs. The rest should happen behind the scenes
        in the spotter sub-classes.
        """
        current_page = self.get_child_page()
        if current_page is not None:
            current_page.update()

    def update_all_tabs(self):
        """
        This is potentially very expensive! Best only trigger on 'large'
        event or introduce some selectivity, i.e. only update affected tabs as
        far as one can tell.
        """
        self.log.debug('NOT updating all tabs')
        return
        #for main_tab in [self.features_page, self.objects_page, self.regions_page]:
        #    for tab in main_tab.tabs_sub:
        #        tab.update()

    def remove_all_tabs(self):
        self.features_page.remove_all_pages()
        self.objects_page.remove_all_pages()
        self.regions_page.remove_all_pages()

    ###############################################################################
    ##  FEATURES Tab Updates
    ###############################################################################
    def tab_features_switch(self, idx_tab=0):
        """
        Switch to the tab page with index idx_tab.
        """
        self.features_page.tabs_sub.setCurrentIndex(idx_tab)

    def add_feature(self, template=None, label=None, focus_new=True):
        """
        Create a feature from trackables and add a corresponding tab to
        the tab widget, which is linked to show and edit feature properties.
        TODO: Create new templates when running out by fitting them into
        the color space somehow.
        """
        if not template:
            key = self.parent.template_default['FEATURES'].iterkeys().next()
            template = self.parent.template_default['FEATURES'][key]
            label = 'LED_' + str(len(self.spotter.tracker.leds))

        if not template['type'].lower() == 'led':
            return
        else:
            range_hue = map(int, template['range_hue'])
            range_sat = map(int, template['range_sat'])
            range_val = map(int, template['range_val'])
            range_area = map(int, template['range_area'])
            fixed_pos = template.as_bool('fixed_pos')
            feature = self.spotter.tracker.add_led(label, range_hue, range_sat, range_val,
                                                  range_area, fixed_pos)
        self.features_page.add_item(feature, focus_new)

    ###############################################################################
    ##  OBJECTS Tab Updates
    ###############################################################################
    def tab_objects_switch(self, idx_tab=0):
        """
        Switch to the tab page with index idx_tab.
        """
        self.objects_page.tabs_sub.setCurrentIndex(idx_tab)

    def add_object(self, template=None, label=None, focus_new=True):
        """
        Create a new object that will be linked to LEDs and/r ROIs to
        track and trigger events.
        TODO: Create new objects even when running out of templates for example
        by randomizing offsets.
        """
        if not template:
            key = self.parent.template_default['OBJECTS'].iterkeys().next()
            template = self.parent.template_default['OBJECTS'][key]
            label = 'Object_' + str(len(self.spotter.tracker.oois))

        features = []
        for n in xrange(min(len(self.spotter.tracker.leds), len(template['features']))):
            for l in self.spotter.tracker.leds:
                if template['features'][n] == l.label:
                    features.append(l)

        analog_out = template['analog_out']
        if analog_out:
            # Magnetic objects from collision list
            signal_names = template['analog_signal']
            pin_prefs = template['pin_pref']
            if pin_prefs is None:
                pin_prefs = []
            magnetic_signals = []
            if template['pin_pref_strict']:
                # If pin preference is strict but no/not enough pins given,
                # reject all/those without given pin preference
                if len(pin_prefs) == 0:
                    signal_names = []
            else:
                # if not strict but also not enough given, fill 'em up with -1
                # which sets those objects to being indifferent in their pin pref
                if len(pin_prefs) < len(signal_names):
                    pin_prefs[-(len(signal_names) - len(pin_prefs))] = -1

            # Reject all objects that still don't have a corresponding pin pref
            signal_names = signal_names[0:min(len(pin_prefs), len(signal_names))]

            # Those still in the race, assemble into
            # List of [object label, object, pin preference]
            for isig, sn in enumerate(signal_names):
            # Does an object with this name exist? If so, link its reference!
            #                obj = None
            #                for o in self.spotter.tracker.oois:
            #                    if o.label == on:
            #                        obj = o
                magnetic_signals.append([sn, pin_prefs[isig]])
        else:
            magnetic_signals = None

        trace = template['trace']
        track = template['track']
        object_ = self.spotter.tracker.add_ooi(features, label, trace, track, magnetic_signals)
        self.objects_page.add_item(object_, focus_new)

        if analog_out:
            if any(template['analog_signal']):
                if 'x position' in template['analog_signal']:
                    object_.analog_pos = True
                if 'y position' in template['analog_signal']:
                    object_.analog_pos = True
                if 'speed' in template['analog_signal']:
                    object_.analog_spd = True
                if 'direction' in template['analog_signal']:
                    object_.analog_dir = True

    ###############################################################################
    ##  REGIONS Tab Updates
    ###############################################################################
    def tab_regions_switch(self, idx_tab=0):
        """
        Switch to the tab page with index idx_tab.
        """
        self.regions_page.tabs_sub.setCurrentIndex(idx_tab)

    def add_region(self, template=None, label=None, shapes=None, abs_pos=True, focus_new=True):
        """
        Create a new region of interest that will be that will be linked
        to Objects with conditions to trigger events.
        TODO: New regions created empty!
        """
        # Defaults if nothing else given
        if not template:
            key = self.parent.template_default['REGIONS'].iterkeys().next()
            template = self.parent.template_default['REGIONS'][key]
            label = 'ROI_' + str(len(self.spotter.tracker.rois))
        if not shapes:
            shapes = self.parent.template_default['SHAPES']

        # extract shapes from shape templates
        shape_list = []
        for s_key in template['shapes']:
            if s_key in shapes:
                shape_type = shapes[s_key]['type']
                if abs_pos:
                    points = [shapes[s_key]['p1'], shapes[s_key]['p2']]
                else:
                    points = geom.scale_points([shapes[s_key]['p1'],
                                                shapes[s_key]['p2']],
                                               (self.parent.gl_frame.width,
                                                self.parent.gl_frame.height))
                shape_list.append([shape_type, points, s_key])

        # Magnetic objects from collision list
        obj_names = template['digital_collision']
        pin_prefs = template['pin_pref']
        if pin_prefs is None:
            pin_prefs = []
        magnetic_objects = []
        if template['pin_pref_strict']:
            # If pin preference is strict but no/not enough pins given,
            # reject all/those without given pin preference
            if len(pin_prefs) == 0:
                obj_names = []
        else:
            # if not strict but also not enough given, fill 'em up with -1
            # which sets those objects to being indifferent in their pin pref
            if len(pin_prefs) < len(obj_names):
                pin_prefs[-(len(obj_names) - len(pin_prefs))] = -1

        # Reject all objects that still don't have a corresponding pin pref
        obj_names = obj_names[0:min(len(pin_prefs), len(obj_names))]

        # Those still in the race, assemble into
        # List of [object label, object, pin preference]
        for io, on in enumerate(obj_names):
            # Does an object with this name exist? If so, link its reference!
            obj = None
            for o in self.spotter.tracker.oois:
                if o.label == on:
                    obj = o
            magnetic_objects.append([obj, pin_prefs[io]])

        color = template['color']

        region = self.spotter.tracker.add_roi(shape_list, label, color, magnetic_objects)
        self.regions_page.add_item(region, focus_new)

    ###############################################################################
    ##  SERIAL Tab Updates
    ###############################################################################
    def serial_check(self):
        if self.spotter.chatter.is_open():
            self.spotter.chatter.read_all()

    def add_serial(self, serial_object, label=None):
        """
        Serial object tab. Probably an Arduino compatible board linked to it.
        """
        self.serial_page.add_item(serial_object, update_all_tabs=self.update_all_tabs())

    ###############################################################################
    ##  SOURCE Tab Updates
    ###############################################################################
    def add_source(self, source_object, label=None):
        """
        Serial object tab. Probably an Arduino compatible board linked to it.
        """
        self.source_page.add_item(source_object, update_all_tabs=self.update_all_tabs())

    ###############################################################################
    ##  RECORD Tab Updates
    ###############################################################################
    def add_record(self, record_object, label=None):
        """
        Serial object tab. Probably an Arduino compatible board linked to it.
        """
        self.record_page.add_item(record_object, update_all_tabs=self.update_all_tabs())