# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app_eel.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('web', 'web'),  # 包含web目录
        ('config', 'config'),  # 包含config目录
        ('工具库', '工具库'),  # 包含工具库目录
        ('通用操作守则', '通用操作守则'),  # 包含通用操作守则目录
        ('catalog_template.xlsx', '.'),  # 包含模板文件
        ('prompt.json', '.'),
        ('step_knowledge_base.json', '.'),
        ('user_settings.json', '.'),
        ('dify_config.json', '.'),
        ('special_requirements.json', '.'),
        ('extract_template.json', '.'),
    ],
    hiddenimports=[
        'eel',
        'src.bridge',
        'src.core.ai_client',
        'src.core.config_manager',
        'src.core.excel.base',
        'src.core.excel.com_driver',
        'src.core.excel.pyxl_driver',
        'src.core.excel.factory',
        'src.services.catalog_service',
        'src.services.material_service',
        'src.services.sop_service',
    ],
    hookspath=[],
    hooksconfig={},
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
    name='AI-Work-Assistant',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
