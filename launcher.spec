# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['D:/workspace/git/labubu/launcher.py'],
    pathex=['D:/workspace/git/labubu'],
    binaries=[],
    datas=[
        ('config.yaml', '.'),
        ('requirements.txt', '.'),
    ],
    hiddenimports=[
        'yaml',
        'urllib.request',
        'tempfile',
        'json',
        'platform',
        'subprocess',
        'shutil',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='labubu-launcher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
