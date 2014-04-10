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



############################################    from spotterQt.py

    def numpy2qimage(self, array):
    	if np.ndim(array) == 2:
    		return self.gray2qimage(array)
    	elif np.ndim(array) == 3:
    		return self.rgb2qimage(array)
    	raise ValueError("can only convert 2D or 3D arrays")

    def gray2qimage(gray):
    	"""Convert the 2D numpy array `gray` into a 8-bit QImage with a gray
    	colormap.  The first dimension represents the vertical image axis."""
    	if len(gray.shape) != 2:
    		raise ValueError("gray2QImage can only convert 2D arrays")

    	gray = np.require(gray, np.uint8, 'C')

    	h, w = gray.shape

    	result = QtGui.QImage(gray.data, w, h, QtGui.QImage.Format_Indexed8)
    	result.ndarray = gray
    	for i in range(256):
    		result.setColor(i, QtGui.QColor(i, i, i).rgb())
    	return result

    def rgb2qimage(self, rgb):
    	"""Convert the 3D numpy array `rgb` into a 32-bit QImage.  `rgb` must
    	have three dimensions with the vertical, horizontal and RGB image axes."""
    	if len(rgb.shape) != 3:
    		raise ValueError("rgb2QImage can expects the first (or last) dimension to contain exactly three (R,G,B) channels")
    	if rgb.shape[2] != 3:
    		raise ValueError("rgb2QImage can only convert 3D arrays")

    	h, w, channels = rgb.shape

    	# Qt expects 32bit BGRA data for color images:
    	bgra = np.empty((h, w, 4), np.uint8, 'C')
    	bgra[...,0] = rgb[...,2]
    	bgra[...,1] = rgb[...,1]
    	bgra[...,2] = rgb[...,0]
    	bgra[...,3].fill(255)

    	result = QtGui.QImage(bgra.data, w, h, QtGui.QImage.Format_RGB32)
    	result.ndarray = bgra
    	return result


    def array2pixmap(self, nparray ):
        shape = nparray.shape
        a = nparray.astype(np.uint32)
        b = (255 << 24 | a[:,:,0] << 16 | a[:,:,1] << 8 | a[:,:,2]).flatten()
        im = QtGui.QImage(b, shape[0], shape[1], QtGui.QImage.Format_RGB32)
        return QtGui.QPixmap.fromImage(im)


    def testframe(self):
        a = np.random.randint(0,256,size=(1000,1000,3)).astype(np.uint32)
        self.lbl.setPixmap( self.array2pixmap(a) )

    def update( self, frame ):
#        print frame
#        pixmap = self.array2pixmap(frame)
        pixmap2 = QtGui.QPixmap.fromImage(self.rgb2qimage(frame))
        self.lbl.setPixmap( pixmap2 )



#        glRotatef(self.angle, 0.0, 1.0, 0.0)
#
#        glColor(0.1, 0.5, 0.8)
#        glBegin(OpenGL.GL.GL_TRIANGLES)
#        glVertex3f( 0.0, 0.5, 0.0)
#        glVertex3f(-0.5,-0.5, 0.0)
#        glVertex3f( 0.5,-0.5, 0.0)
#        glEnd()



############################################    from GLFrame.py
# mouse event handling differentiting types of buttons used
#        if int(mouseEvent.buttons()) != QtCore.Qt.NoButton :
#            # user is dragging
#            delta_x = mouseEvent.x() - self.oldx
#            delta_y = self.oldy - mouseEvent.y()
#            if int(mouseEvent.buttons()) & QtCore.Qt.LeftButton :
#                if int(mouseEvent.buttons()) & QtCore.Qt.MidButton :
#                    pass
##                    print delta_x
#                else:
#                    pass
##                    print delta_y
#            elif int(mouseEvent.buttons()) & QtCore.Qt.MidButton :
#            self.update()




############################################    from spotterQt.py
# Templates replaced with ini files read by ConfigObj

    # _name_, range_hue, range_area, fixed_pos
    feature_templates = dict( default = [(0, 1), (6, 0), True],
                              redLED = [( 160, 5 ), (20, 0), False],
                              blueLED = [( 105, 135 ), (20, 0), False],
                              greenLED = [( 15, 90 ), (20, 0), True] )

    # _name_, linked feature name list, from above; analog_out
    object_templates = dict( default = [[], True],
                             Subject = [['redLED', 'blueLED'], True],
                             Sync    = [['greenLED'], False] )

    # _name_, shape primitive type, points to describe shape
    shape_templates = dict( LeftSensor   = ['rectangle', [(0.20, 0.00), (0.30, 1.00)]],
                            CenterSensor = ['rectangle', [(0.45, 0.20), (0.55, 0.80)]],
                            RightSensor  = ['rectangle', [(0.70, 0.00), (0.80, 1.00)]],
                            Sync_dummy_right  = ['rectangle', [(0.90, 0.00), (1.00, 1.00)]],
                            Sync_dummy_bottom  = ['rectangle', [(0.00, 0.85), (1.00, 1.00)]])

    # _name_, connected shapes
    region_templates = dict( default = [[]],
                             LeftReward  = [['LeftSensor']],
                             Trigger     = [['CenterSensor']],
                             RightReward = [['RightSensor']],
                             Sync_trig   = [['Sync_dummy_right', 'Sync_dummy_bottom']] )

    # features, objects, regions
    full_templates = dict( LinearTrack =  [feature_templates, object_templates, region_templates] )




###############################################################################
## PIN LIST - from TabRegions.py
###############################################################################
#    def refresh_pin_list(self):
#        pass
##        # If nothing selected, select the first item in the list
##        n_items = self.tree_region_digital.topLevelItemCount()
##        if n_items and not self.tree_region_digital.currentItem():
##            self.tree_region_digital.setCurrentItem(self.tree_region_digital.topLevelItem(0))
##        pins = self.parent.spotter.chatter.pins()
##        if pins:
##            pins = pins['digital']
##        if self.parent.spotter.chatter.is_open() and pins:
##            while not self.tree_region_digital.topLevelItemCount() == pins.n:
##                self.add_pin(self.tree_region_digital.topLevelItemCount())
##        else:
##            while not self.tree_region_digital.topLevelItemCount() == 0:
##                self.remove_pin()
#
#
#    def add_pin(self, pin):
#        pass
##        """
##        Add a new digital out pin to the list of pins.
##        """
##        pin_item = QtGui.QTreeWidgetItem([str(pin)])
###        pin_item.pin = self.region.add_shape(shape_type, shape_points, shape_type)
##        pin_item.setCheckState(0, QtCore.Qt.Unchecked)
##        self.tree_region_digital.addTopLevelItem(pin_item)
##        self.tree_region_digital.setCurrentItem(pin_item)
###        pin_item.setFlags(pin_item.flags() | QtCore.Qt.ItemIsEditable)
#
#    def remove_pin(self):
#        pass
##        """ Remove a pin from the list of available digital out pins """
##        self.tree_region_digital.takeTopLevelItem(0)


###############################################################################
## PIN LIST - from TabObjects.py
###############################################################################
    def refresh_pin_list(self):
        pass
#        pins = self.parent.spotter.chatter.pins('dac')
#        if self.parent.spotter.chatter.is_open() and pins:
#            if not self.tree_link_spi_dac.topLevelItemCount() == len(pins):
#                self.add_pin(self.tree_link_spi_dac.topLevelItemCount())
#        else:
#            while not self.tree_link_spi_dac.topLevelItemCount() == 0:
#                self.remove_pin()

    def add_pin(self, pin):
        pass
#        """
#        Add a new digital out pin to the list of pins.
#        """
#        pin_item = QtGui.QTreeWidgetItem([str(pin)])
#        pin_item.setCheckState(0, QtCore.Qt.Unchecked)
#        self.tree_link_spi_dac.addTopLevelItem(pin_item)
#        self.tree_link_spi_dac.setCurrentItem(pin_item)

    def remove_pin(self, index = 0):
        pass
#        """ Remove a pin from the list of available digital out pins """
#        self.tree_link_spi_dac.takeTopLevelItem(index)

###############################################################################
## GRABBER - from grabber.py
###############################################################################
    def grab_opencv(self, index=None):
        """Grab a frame from an opencv-source, either video file or a camera."""
        # Only really loops for first frame
        n_tries = 10 if self.frame_count < 1 else 1
        for trial in xrange(2, n_tries + 2):
            # GET A NEW FRAME!
            rv, img = self.capture.read()
            if rv:
                frame = Frame(self.index, img, self.source_type)
                #self.frame_count += 1
                break
            time.sleep(0.01)
        else:
            self.log.error("Frame retrieval failed after %d" + (' tries' if n_tries - 1 else ' try'), n_tries)
            self.close()
            return None

        # First frame?
        if self.frame_count == 0:
            self.first_frame(trial)

        self.frame_count += 1
        return frame

    def grab_zmq(self, index=None):
        """Grab a frame from a ZMQ socket.

        If index is given, request a specific frame, rather than any new one.
        """
        try:
            # Send request for new frame (any message will do here)
            if index is None:
                self.capture.send(__name__, zmq.NOBLOCK)
            else:
                self.capture.send(index, zmq.NOBLOCK)  # request specific frame number

            # Receive frame
            img = np.fromstring(self.capture.recv(), np.uint8)
            shape = (600, 800, 3)  # (960, 1280, 3)
            img = np.reshape(img, shape)
            self.frame_count += 1
            if index is not None:
                self._frame_ptr = index
        except zmq.ZMQError:
            return None
        except ValueError:
            return None

        # First frame?
        if self.frame_count == 1:
            self.size = img.shape
            self.fps = 60.0
            self.fourcc = None
            self.log.info('First ZMQ frame: %s fps, %dx%d, %s',
                          str(self.fps), self.size[0], self.size[1], str(self.fourcc))

        # TODO: Should use self.index, not self.frame_count
        return Frame(self.frame_count, img, self.source_type)

    def open_file(self, source, *args, **kwargs):
        self.log.debug('Attempting to open file "%s" as capture... ', source)
        return self.open_opencv(source, 'file', *args, **kwargs)


    def open_socket(self, source='tcp://localhost:5555', *args, **kwargs):
        context = zmq.Context()
        self.log.info('Connecting to frame server %s', source)
        self.capture = context.socket(zmq.REQ)
        self.capture.connect()
        self.capture_type = 'zmq'
        self.log.debug('Opened ZMQ socket')

        # TODO: Get properties from whoever we are talking to right now!
        self.source_type = 'socket'

        # TODO: Needs proper connection state handling! Hence, purposefully failing here.
        return False

    def grab(self, index=None):
        """Grabs a new frame from the source. Returns Frame instance with
        image and meta data."""
        if self.capture is None:
            return

        #self.log.debug("Grabbing frame")
        if self.capture_type == "opencv":
            return self.grab_opencv(index)

        if self.capture_type == "zmq":
            return self.grab_zmq(index)

    def first_frame(self, trial):
        """Some housekeeping of properties when grabbing the first frame of a source."""
        self.log.debug('Updating size for first frame')
        self.size = tuple([int(self.capture_width), int(self.capture_height)])
        # There seems to be an issue with V4L where property always returns a NaN
        self.fps = self.capture.get(cv2.cv.CV_CAP_PROP_FPS)
        try:
            int(self.fps)
        except ValueError:
            self.fps = 30.0
        self.fourcc = self.capture.get(cv2.cv.CV_CAP_PROP_FOURCC)
        self.log.info('First frame: %.2f fps, %dx%d, %s after %d' + (' tries' if trial - 2 else ' try'),
                      self.fps, self.size[0], self.size[1], str(self.fourcc), trial - 1)

    @property
    def num_frames(self):
        """Total number of frames in video. Only works for indexed sources.

        Returns None for non-indexed sources.
        """
        if self.capture is not None:
            return int(self.capture.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT)) if self.source_indexed else None

    @property
    def index(self):
        """Position in video in absolute number of frames.

        Returns None for non-indexed sources.
        """
        if self.capture is not None:
            return int(self.capture.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)) if self.source_indexed else self.frame_count

    @index.setter
    def index(self, idx):
        """Move position pointer in video to position in absolute number of frames.

        Only works for indexed sources.
        """
        if self.capture is None or not self.source_indexed:
            return

        idx = int(idx)
        if idx < 0:
            idx = 0
        if idx >= self.num_frames:
            # TODO: Remove repeat. Feature creep.
            if self.repeat:
                idx = 0
            else:
                idx = self.num_frames - 1

        # if the current pointer is not the same as requested, update and seek in video file
        # (not sure about performance of the seeking, I'll avoid doing it all the time)
        # NB! Potential death trap thanks to float<>int conversions!??
        if self.index != idx:
            self.capture.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, float(idx))

    @property
    def pos_time(self):
        """Position in video in milliseconds. Unreliable if frame rate set during encoding not the
        same as frame rate of acquisition. Requires external synchronization markers.
        """
        if self.capture is not None:
            return self.capture.get(cv2.cv.CV_CAP_PROP_POS_MSEC)

    @property
    def capture_width(self):
        """ Width of the _source_ frames. As frames may be rescaled, this can differ from the
        properties of the frames emitted by the grabber.
        """
        if self.capture is not None:
            return self.capture.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)

    @capture_width.setter
    def capture_width(self, width):
        """Set capture property 'width' of capture object, if available.

        :param width:float
        """
        if self.capture is None:
            return

        if self.capture_type == 'opencv':
            self.log.debug('Setting requested frame width to: %f' % width)
            self.capture.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, width)
        elif self.capture_type == 'zmq':
            # TODO: Send command to frame server
            pass

    @property
    def capture_height(self):
        """ Height of the _source_ frames. As frames may be rescaled, this can differ from the
        properties of the frames emitted by the grabber.
        """
        if self.capture is not None:
            return self.capture.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)

    @capture_height.setter
    def capture_height(self, height):
        """Set capture property 'height' of capture object, if available.

        :param height:float
        """
        if self.capture is None:
            return
        if self.capture_type == 'opencv':
            self.log.debug('Setting requested frame height to: %f' % height)
            self.capture.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, height)
        elif self.capture_type == 'zmq':
            # TODO: Send command to frame server
            pass

    def capture_properties(self):
        #base_string = 'CV_CAP_PROP_'
        properties = ['POS_MSEC', 'POS_FRAMES', 'POS_AVI_RATIO', 'FRAME_WIDTH', 'FRAME_HEIGHT',
                      'FPS', 'FOURCC', 'FRAME_COUNT', 'FORMAT', 'MODE', 'BRIGHTNESS', 'CONTRAST',
                      'SATURATION', 'HUE', 'GAIN', 'EXPOSURE', 'CONVERT_RGB', 'WHITE_BALANCE']
        if self.capture is not None:
            self.log.info("++++++++++++++++++++++")
            for idx, prop in enumerate(properties):
                self.log.info(prop + ": %s", str(self.capture.get(idx)))
            self.log.info("++++++++++++++++++++++")
            print struct.unpack('4c', struct.pack('f', self.capture.get(6)))