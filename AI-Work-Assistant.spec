# -*- mode: python ; coding: utf-8 -*-

import os

a = Analysis(
    ['app_eel.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('web', 'web'),
        ('config', 'config'),
        ('catalog_template.xlsx', '.'),
    ],
    hiddenimports=['eel', 'openpyxl', 'pandas', 'requests', 'PIL', 'pywin32', 'src', 'src.bridge', 'src.core', 'src.services', 'src.core.excel', 'src.core.ai_client', 'src.core.config_manager', 'src.services.sop_service', 'src.services.material_service', 'src.services.catalog_service'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AI-Work-Assistant',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    runtime_tmpdir=None,
    console=True,  # Enable console to see errors
    disable_windowed_traceback=False,
    argv_emulation=False,
)
