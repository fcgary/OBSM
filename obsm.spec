# obsm.spec
# -*- mode: python ; coding: utf-8 -*-

import sys
import os
block_cipher = None

try:
    obsm_root = os.path.abspath(os.path.dirname(__file__))
except NameError:
    # fallback if __file__ is not defined (e.g., in some PyInstaller contexts)
    obsm_root = os.path.abspath(os.path.dirname(sys.argv[0]))


a = Analysis(
    ['tool/obsm_gui.py', 'tool/obsm_calculator.py'],
    pathex=[obsm_root],  # Add root to module search path
    binaries=[],
    datas=[('data/obsm_effs.xlsx', 'data')],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='obsm',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    onefile=True,
    icon='data/icon.ico'
)
