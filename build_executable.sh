#!/bin/bash

pyinstaller --onefile --noconsole \
--icon=resources/icons/suraj_icon_210.png \
--add-data "resources/icons/manager.png:resources/icons" \
--add-data "resources/icons/clipboard.png:resources/icons" \
--add-data "resources/icons/launcher.png:resources/icons" \
--add-data "resources/icons/url_list.png:resources/icons" \
--add-data "resources/icons/file_search.png:resources/icons" \
--add-data "resources/icons/minimize_taskbar.png:resources/icons" \
--add-data "resources/icons/cross_taskbar_close.png:resources/icons" \
--add-data "resources/icons/suraj_icon_210.png:resources/icons" \
--add-data "static/taskbar.qss:static" \
--add-data "themes/:themes/" \
--add-data "launcher_entries.json:." \
--add-data "files_index.pkl:." \
--hidden-import "app.main_window" \
--hidden-import "app.taskbar" \
--hidden-import "app.clipboard_manager" \
--hidden-import "app.clipboard_notepad" \
--hidden-import "app.url_access" \
--hidden-import "app.file_indexer" \
--hidden-import "PyQt5.QtWidgets" \
--hidden-import "PyQt5.QtCore" \
--hidden-import "PyQt5.QtGui" \
--hidden-import "sip" \
main.py
