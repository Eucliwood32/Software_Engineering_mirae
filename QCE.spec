# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=['src'],
    binaries=[],
    datas=[('src', 'src')],
    hiddenimports=['models.parsers.git_parser', 'models.parsers.ooxml_parser', 'models.parsers.messenger_parser', 'models.analysis.alias_extractor', 'models.analysis.stopword_dictionary', 'models.analysis.detectors', 'models.analysis.aggregator', 'views.main_window', 'views.components.charts', 'views.components.anomaly_signal_panel', 'views.dialogs.alias_mapping_dialog', 'controllers.main_controller', 'controllers.worker_thread', 'kiwipiepy'],
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
    name='QCE',
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
)
