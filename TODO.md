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

General behavior:
=================

    - benchmark how long it takes to open one frame, vs. 5 frames, etc.
    - if video from disk, keep a frame buffer filled up, otherwise only process
    most recent frame. From disk any access to a slow HD will delay reading
    frames, leading to stutters.
    - if from disk, allow freezing and moving frame by frame/jumping inside
    the file for fast access of specific time points
