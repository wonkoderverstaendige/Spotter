Spotter : simple video tracking
===============================

[Spotter](http://wonkoderverstaendige.github.com/Spotter) can track LEDs in a video stream--either from a webcam, video file or ZMQ socket--and simultaneously write encoded video to disk. It is based on the [OpenCV](http://opencv.org/) library and interfaces with Arduino Uno, Mega or Due.

For more detailed documentation, please refer to: [Spotter_0.4.pdf](docs/Spotter.pdf).

Requirements
------------

Tested on Windows 7, (X)Ubuntu 12.04, MacOSX Lion

- Python 2.7 (Python 3.x is not supported)
- numpy 1.6+
- OpenCV 2.4+
- pyOpenGL
- pyQt4
- pySerial

**Windows**

The simplest, but not very lightweight method for installing all
requirements is to download the [PythonXY](http://code.google.com/p/pythonxy/wiki/Downloads)
distribution and perform a  "full" installation. Alternatively, a custom
installation is enough if all required packages are selected.

TODO: The opencv package distributed in python XY can not decode most videos. Install without,
and grab from e.g. grohlke (see below).

_Bare install:_
Download and install Python 2.7 32bit

Add python to the PATH variable by appending 

    ;C:\Python27\;C:\Python27\Scripts

under MyComputer->Properties->Advanced->Env Variables->Path
    
Install required packages by downlaoding and innstalling following binaries
(choose win32-py2.7 links) in order:

    http://www.lfd.uci.edu/~gohlke/pythonlibs/#pip
    http://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy
    http://www.lfd.uci.edu/~gohlke/pythonlibs/#pyqt
    http://www.lfd.uci.edu/~gohlke/pythonlibs/#opencv
    http://www.lfd.uci.edu/~gohlke/pythonlibs/#pyopengl
    http://www.lfd.uci.edu/~gohlke/pythonlibs/#pyserial

**MaxOSX**
*Stand by.*
*Install XCode, install MacPorts. Install py27- packages.*

**LINUX**

    apt-get install the following packages:
    (among others...)
    python-numpy
    python-scipy
    python-qt4-gl

Installation
------------

**With git**

    git clone https://github.com/wonkoderverstaendige/Spotter.git

**Without git**

Download and extract the zip file from [here](https://github.com/wonkoderverstaendige/Spotter/archive/master.zip).

Example CLI Usage
-----------------

    python spotterQt.py --source media\vid\r52r2f117.avi

or

    python spotterQt.py --source 0 -o result.avi --dims 640x360