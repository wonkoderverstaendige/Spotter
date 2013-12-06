call pyuic4 mainUi.ui -o mainUi.py
call pyuic4 statusBarUi.ui -o statusBarUi.py
call pyuic4 serialIndicatorUi.ui -o serialIndicatorUi.py

call pyuic4 side_barUi.ui -o side_barUi.py
call pyuic4 tab_serialUi.ui -o tab_serialUi.py
call pyuic4 tab_sourceUi.ui -o tab_sourceUi.py
call pyuic4 tab_recordUi.ui -o tab_recordUi.py
call pyuic4 tab_objectsUi.ui -o tab_objectsUi.py
call pyuic4 tab_regionsUi.ui -o tab_regionsUi.py
call pyuic4 tab_featuresUi.ui -o tab_featuresUi.py
call pyuic4 main_tab_pageUi.ui -o main_tab_pageUi.py

call pyrcc4 icons.qrc -o icons_rc.py
call pyrcc4 images.qrc -o images_rc.py