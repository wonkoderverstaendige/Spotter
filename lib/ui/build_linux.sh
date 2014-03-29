#!/bin/sh
pyuic4 mainUi.ui -o mainUi.py
pyuic4 statusBarUi.ui -o statusBarUi.py
pyuic4 serialIndicatorUi.ui -o serialIndicatorUi.py

pyuic4 PGFrameUi.ui -o PGFrameUi.py

pyuic4 side_barUi.ui -o side_barUi.py
pyuic4 tab_serialUi.ui -o tab_serialUi.py
pyuic4 tab_sourceUi.ui -o tab_sourceUi.py
pyuic4 tab_recordUi.ui -o tab_recordUi.py
pyuic4 tab_objectsUi.ui -o tab_objectsUi.py
pyuic4 tab_regionsUi.ui -o tab_regionsUi.py
pyuic4 tab_featuresUi.ui -o tab_featuresUi.py
pyuic4 main_tab_pageUi.ui -o main_tab_pageUi.py

pyrcc4 icons.qrc -o icons_rc.py
pyrcc4 images.qrc -o images_rc.py