# -*- coding: utf-8 -*-

TO DO:

Writer Process:
===============

    - Requires periodic "Stay Alive" signal or commits suicide after timeout to
    prevent suicides processes accumulating.
        --> Seems to work for now. Not sure why though...

General behavior:
=================

    - benchmark how long it takes to open one frame, vs. 5 frames, etc.
    - if video from disk, keep a frame buffer filled up, otherwise only process
    most recent frame. From disk any access to a slow HD will delay reading
    frames, leading to stutters.
    - if from disk, allow freezing and moving frame by frame/jumping inside
    the file for fast access of specific time points
