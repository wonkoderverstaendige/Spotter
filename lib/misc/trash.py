# -*- coding: utf-8 -*-
"""
Created on Fri Nov 02 21:23:19 2012

@author: fsm
"""
# from size calculation in grabber main
        for i,s in enumerate(size):
            size[i] = float(s)

    ts_start = time.clock()

############################################

        def write_thread( self, fb, ev ):
        """ When woken, writes frames from framebuffer until only nleaves number of
        frames left. If _alive flag set to false, flushes all remaining frames from
        buffer and deletes capture object to allow proper exit"""

        nleave_frames = 1
        while self.alive or len(fb) > 0:
            ev.wait()
            if not self.alive:
                if DEBUG: print 'Flushing buffer to file...'
                nleave_frames = 0

            frames_written = 0
            while len(fb) > nleave_frames:
                self.writer.write( fb.pop() )
                frames_written += 1
                if frames_written > 1:
                    print time.strftime('%Y-%m-%d %H:%M:%S ') + str(frames_written) + ' frames written!'

        #if not self.alive, close:
        self.close()



############################################
            frames_written = 0
            ...
            frames_written += 1
            if frames_written > 1:
                print time.strftime('%Y-%m-%d %H:%M:%S ') + str(frames_written) + ' frames written!'