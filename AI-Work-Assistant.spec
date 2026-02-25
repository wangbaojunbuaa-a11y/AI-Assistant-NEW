# -*- mode: python ; coding: utf-8 -*-

import os

# 动态收集需要的数据文件
datas = [
    ('web', 'web'),
    ('config', 'config'),
    ('catalog_template.xlsx', '.'),
    ('step_knowledge_base.json', '.'),
    ('special_requirements.json', '.'),
    ('extract_template.json', '.'),
    ('user_settings.json', '.'),
    ('prompt.json', '.'),
    ('dify_config.json', '.'),
]

# 动态添加工具库和通用操作守则目录（如果存在）
tool_dir = '工具库'
if os.path.exists(tool_dir):
    datas.append((tool_dir, tool_dir))

rules_dir = '通用操作守则'
if os.path.exists(rules_dir):
    datas.append((rules_dir, rules_dir))

a = Analysis(
    ['app_eel.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'eel',
        'openpyxl',
        'pandas',
        'requests',
        'PIL',
        'pywin32',
        'pkg_resources',
        'src',
        'src.bridge',
        'src.core',
        'src.core.ai_client',
        'src.core.config_manager',
        'src.core.excel',
        'src.core.excel.base',
        'src.core.excel.com_driver',
        'src.core.excel.factory',
        'src.core.excel.pyxl_driver',
        'src.services',
        'src.services.sop_service',
        'src.services.material_service',
        'src.services.catalog_service',
        'src.utils',
    ],
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
