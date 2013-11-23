# -*- coding: utf-8 -*-

TO DO:

Interface:
==========
DONE- No features/objects at start, except if a standard template is selected
    in the settings and marked as auto-track

    - no tabs if no spotter. Allow to simply kill and reinstantiate a spotter
    (i.e. check in main update if spotter = None, if so, disable all, if not
    enable all if not already so and trigger ALL updates)

    - central frame can have cute mouse (MY PRECIOUS!) as center image

    - double clicking the feature/ROI list creates a new one, adds it to the
    list as new linked one and takes user to the tab of the newly created

    - adding/removing features, ROIs, objects should trigger updates on all
    linked lists

    - Allow switching between video source and static image

    - Settings. Set all the things (warnings ON/OFF, Dialog confirmations, etc)

GL Frame:
=========
    - use double buffering to reduce flickering, esp. when drawing into the
    frame.

    - direct mode (glBegin, glEnd) is much slower in python, so it may be
    better to use immediate mode via arrays with all drawing functions

    - array based trace drawing does not need to rebuild the whole array,
    just pop() oldest item and append newest. Make it a queue, not a list.

Mouse handling:
===============
    - handling mouse events by the tabs themselves seemed like a neat idea,
    as it would allow each tab to handle the incoming events as it deems
    fruitful to its purpose, but it creates a lot of duplicate code. Either
    handle the mouse events closer to the source and send out specific types
    of events, i.e. selections, clicks, etc, or merge into a handler class?

    - accept mouse events by default. Only refuse events if the current tab
    is locked (to prevent changing settings accidentally!)

DONE- when dragging with middle mouse button for example, move the currently
    selected ROI around to position it
        --> Middle mouse dragging moves ROI, holding shift moves only selected
            shape

DROP- shift as a modifier could serve as precision placement (diving delta
    of dragging motion e.g. by four)

    - control could serve as LINE_STRIP type of selection, normal dragging as
    RECTangle

General behavior:
=================

    - benchmark how long it takes to open one frame, vs. 5 frames, etc. from HD

    - if video from disk, keep a frame buffer filled up, otherwise only process
    most recent frame. From disk any access to a slow HD will delay reading
    frames, leading to stutters.

    - if from disk, allow freezing and moving frame by frame/jumping inside
    the file for fast access of specific time points

    - proper setting/template loading and saving, possibly using pythons
    Config-Parser module

Physical Out:
============

    - non-editable combo box with all objects being tracked. Choose one whose
    position will be sent to the analog out via Arduino/Chatter

    - the collision check should be as close as possible to the detection to
    reduce further delays

    - maybe use priority queue for objects to track, i.e. position first, then
    sync?

    - portlist for windows:
    http://eli.thegreenplace.net/2009/07/31/listing-all-serial-ports-on-windows-with-python/

    - robust serial communication protocol: Reserved symbol (e.g. 0x00),
    followed by 24 bit message, consisting of 8 bit command, 16 bit data
        * extend data to allow nullable symbol?
        * messages: 0d48/49 DAC + 0x??? 12 bit data each

    - arduino answers with OK/ERROR byte, followed by 8 bit state split into
    4 bit in, 4 bit out states

Modules:
========

    - Move all modules into appropriate paths and import from there, rather than using the
    crude path append way
DONE- rename writer_process to just writer

Performance/Timings:
====================

    - time spent on read_all/read/send calls in serial communication. If too
    long, put chatter into separate thread with buffer (NB: No FIFOs or stuff,
    otherwise may delay output/send old data)

    - time spent on drawing the numpy array into the OpenGL frame via different
    methods. For some reason the main loop is extremely slow on the Acer Aspire
    with Intel snail-graphics

    - time spent on 2x setDAC(), 4x readSensors(), 4x setPin()