# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = []
binaries = []
hiddenimports = []
tmp_ret = collect_all('yt_dlp')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'torch', 'torchaudio', 'torchvision', 'pandas', 'scipy', 'numpy', 'numba',
        'IPython', 'ipykernel', 'matplotlib', 'transformers', 'onnx', 'onnxruntime',
        'tornado', 'jupyter', 'PIL', 'Pillow', 'sympy', 'safetensors', 'cv2',
        'huggingface_hub', 'debugpy', 'jedi', 'starlette', 'fastapi', 'uvicorn',
        'psycopg', 'psycopg2', 'soundfile', 'sklearn', 'scikit-learn', 'seaborn'
    ],
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
    name='YouTubeDownloader',
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
