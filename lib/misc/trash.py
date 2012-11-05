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


############################################
    def write_thread( self, fb, ev ):
        """ When woken, writes frames from framebuffer until only nleaves number of
        frames left. If _alive flag set to false, flushes all remaining frames from
        buffer and deletes capture object to allow proper exit"""

        minimum_frames = 1
        mini_fb = list()

        while self.alive or len( fb ) > 0:
            # waiting for wake up signal from main loop
            ev.wait()

            # main loop shutting down
            if not self.alive:
                if DEBUG: print 'Flushing buffer to file...'
                minimum_frames = 0

            # flush frames to file. Writing to disk may take time and block
            # parent thread, fb content moved to temporary list and then written.
            mini_fb = list( fb.pop() for i in range( len(fb) - minimum_frames ) )
            while len(mini_fb):
                self.writer.write( mini_fb.pop() )

        #if not self.alive, close:
        self.close()



############################################    from tracker.py threshTrack

        # split HSV image into the three channels for thresholding
#        h, s, v = cv2.split( dilatedframe )

        # for simplicity, all saturation and value are thresholded for all
        # LEDs the same way, reduces amount of passes
#        rv, sat_t = cv2.threshold(s, self.min_sat, 1, cv2.THRESH_BINARY)
#        rv, val_t = cv2.threshold(v, self.min_val, 1, cv2.THRESH_BINARY)

        # mask of thresholds, Only where both value AND saturation fit
#        self.mask = cv2.bitwise_and( sat_t, val_t )

#        cv2.merge( (h, s, v), self.frame )
#        self.frame = cv2.add( self.frame, self.frame, mask = self.mask )

#        maskimg = self.frame.copy()
#        cv2.merge( (self.mask, self.mask, self.mask), maskimg )

        # place crosses at off positions to see them jumping there

            def preprocess( self, hsv_img ):
        # split
        h, s, v = cv2.split(hsv_img)

        #threshold
        rv, st = cv2.threshold(s, self.min_sat, 1, cv2.THRESH_BINARY)
        cstart = time.clock()
        rv, vt = cv2.threshold(v, self.min_val, 1, cv2.THRESH_BINARY)
        print (time.clock() - cstart)*1000
        self.mask = cv2.max( st, vt )
        self.frame = cv2.bitwise_and( hsv_img, hsv_img, mask = self.mask )

        return self.mask, self.frame

            def sumTrack( self, BGRframe ):
        # XXX: This method is obsolete! Very slow and unreliable
        kernel = np.ones((3,3),'uint8')
        BGRframe = cv2.dilate(BGRframe, kernel)

        B, G, R = cv2.split(BGRframe)
        RG = R>G
        RB = R>B
        GB = G>B

        G[ RG & ~GB ] = 0
        B[ RB & GB ] = 0
        R[ ~RG & ~RB ] = 0

        Bx = B.sum(1).argmax()
        Gx = G.sum(1).argmax()
        Rx = R.sum(1).argmax()

        Ry = R.sum(0).argmax()
        Gy = G.sum(0).argmax()
        By = B.sum(0).argmax()

        ledpos = [(Ry, Rx), (Gy, Gx), (By, Bx)]
        return ledpos
