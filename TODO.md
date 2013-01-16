# -*- coding: utf-8 -*-

TO DO:

Interface:
==========
    - No features/objects at start, except if a standard template is selected
    in the settings and marked as auto-track

    - no tabs if no spotter. Allow to simply kill and reinstantiate a spotter
    (i.e. check in main update if spotter = None, if so, disable all, if not
    enable all if not already so and trigger ALL updates)

    - central frame can have cute mouse (MY PRECIOUS!) as center image

    - double clicking the feature/ROI list creates a new one, adds it to the
    list as new linked one and takes user to the tab of the newly created

    - adding/removing features, ROIs, objects should trigger updates on all
    linked lists

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
    - handling mouse events by the tabs themselves seemmed like a neat idea,
    as it would allow each tab to handle the incoming events as it deems
    fruitful to its purpose, but it creates a lot of duplicate code. Either
    handle the mouse events closer to the source and send out specific types
    of events, i.e. selections, clicks, etc, or merge into a handler class?

    - accept mouse events by default. Only refuse events if the current tab
    is locked (to prevent changing settings accidentally!)

    - when dragging with middle mouse button for example, move the currently
    selected ROI around to position it

    - shift as a modifier could serve as precision placement (diving delta
    of dragging motion e.g. by four)

    - control could serve as LINE_STRIP type of selection, normal dragging as
    RECTangle

General behavior:
=================

    - benchmark how long it takes to open one frame, vs. 5 frames, etc.

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
    position will be sent to the analog out via Arduino/Funker

    - the collision check should be as close as possible to the detection to
    reduce further delays

    - maybe use priority queue for objects to track, i.e. position first, then
    sync?
