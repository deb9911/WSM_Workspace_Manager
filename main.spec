# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('resources/icons/manager.png', 'resources/icons'), ('resources/icons/clipboard.png', 'resources/icons'), ('resources/icons/launcher.png', 'resources/icons'), ('resources/icons/url_list.png', 'resources/icons'), ('resources/icons/file_search.png', 'resources/icons'), ('resources/icons/minimize_taskbar.png', 'resources/icons'), ('resources/icons/cross_taskbar_close.png', 'resources/icons'), ('resources/icons/suraj_icon_210.png', 'resources/icons'), ('static/taskbar.qss', 'static'), ('themes/', 'themes/'), ('launcher_entries.json', '.'), ('files_index.pkl', '.')],
    hiddenimports=['app.main_window', 'app.taskbar', 'app.clipboard_manager', 'app.clipboard_notepad', 'app.url_access', 'app.file_indexer', 'PyQt5.QtWidgets', 'PyQt5.QtCore', 'PyQt5.QtGui'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['resources\\icons\\suraj_icon_210.png'],
)
