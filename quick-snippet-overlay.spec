# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller specification file for Quick Snippet Overlay

This file configures how PyInstaller bundles the application into a
Windows executable.

Build with: pyinstaller quick-snippet-overlay.spec
"""

import sys
from pathlib import Path

# Get the project root directory
project_root = Path('.').absolute()

block_cipher = None

a = Analysis(
    ['src\\main.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        # Include default config template if needed
        # ('config.yaml', '.'),
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'pynput',
        'pynput.keyboard',
        'pynput._util.win32',
        'pyperclip',
        'rapidfuzz',
        'yaml',
        'watchdog',
        'watchdog.observers',
        'watchdog.observers.winapi',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'tkinter',
    ],
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
    name='QuickSnippetOverlay',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Windows GUI application (no console window)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # Icon file (create this manually or use default Windows icon)
    # icon='icon.ico',
)
