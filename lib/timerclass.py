#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 28 15:48:27 2013
@author: <Ronny Eichler> ronny.eichler@gmail.com

"""

import time

class Timer(object):
    def __init__(self, verbose=False, timelog=None):
        self.verbose = verbose
        self.timelog = timelog

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        self.end = time.time()
        self.secs = self.end - self.start
        self.msecs = self.secs * 1000  # millisecs
        if self.verbose:
            print 'elapsed time: %f ms' % self.msecs
        if self.timelog is not None:
            self.timelog.append(self.msecs)
