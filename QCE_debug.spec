# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import collect_all

datas = []
binaries = []
hiddenimports = ['qce.model.parsing.document_parser', 'qce.model.parsing.encoding_handler', 'qce.model.parsing.git_analyzer', 'qce.model.parsing.git_health_checker', 'qce.model.parsing.messenger_parser', 'qce.model.parsing.stopword_filter', 'qce.model.business.contribution_aggregator', 'qce.model.business.anomaly_signal_detector', 'qce.model.business.cache_manager', 'qce.model.business.report_exporter', 'qce.model.business.alias_mapper', 'qce.model.business.capping_scaler', 'qce.model.business.normalizer', 'qce.model.business.weight_preset_manager', 'qce.model.business.weight_rebalancer', 'qce.view.main_window', 'qce.view.contract', 'qce.controller.app_controller', 'qce.controller.analysis_orchestrator', 'charset_normalizer']
datas += collect_data_files('matplotlib')
tmp_ret = collect_all('qce')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    name='QCE_debug',
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
)
