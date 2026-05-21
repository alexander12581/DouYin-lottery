# -*- mode: python ; coding: utf-8 -*-

import os
import playwright

pkg_dir = os.path.dirname(playwright.__file__)
driver_dir = os.path.join(pkg_dir, 'driver')

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[(driver_dir, 'playwright/driver')],
    hiddenimports=['url_parser', 'api', 'browser', 'lottery', 'models'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PyQt5', 'PyQt6', 'PySide2', 'PySide6'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='douyin_lottery',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='douyin_lottery',
)
