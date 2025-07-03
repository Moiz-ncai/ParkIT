# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect data files for ultralytics (YOLO models)
ultralytics_datas = collect_data_files('ultralytics')

# Collect PyQt5 data files
pyqt5_datas = collect_data_files('PyQt5')

# Additional data files
added_files = [
    ('assets', 'assets'),  # Include company logo and assets
]

# Check if model files exist and add them conditionally
if os.path.exists('yolo11s.pt'):
    added_files.append(('yolo11s.pt', '.'))
if os.path.exists('yolo11n.pt'):
    added_files.append(('yolo11n.pt', '.'))
if os.path.exists('yolo11s_openvino_model'):
    added_files.append(('yolo11s_openvino_model', 'yolo11s_openvino_model'))

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=added_files + ultralytics_datas + pyqt5_datas,
    hiddenimports=[
        # PyQt5 modules
        'PyQt5.QtCore',
        'PyQt5.QtGui', 
        'PyQt5.QtWidgets',
        'PyQt5.sip',
        
        # OpenCV modules
        'cv2',
        'numpy',
        
        # Ultralytics and YOLO dependencies
        'ultralytics',
        'ultralytics.models',
        'ultralytics.models.yolo',
        'ultralytics.engine',
        'ultralytics.utils',
        
        # PyTorch dependencies
        'torch',
        'torchvision',
        'torch.nn',
        'torch.nn.functional',
        
        # Other ML dependencies
        'PIL',
        'PIL.Image',
        'yaml',
        'requests',
        'tqdm',
        'matplotlib',
        'scipy',
        
        # JSON and other standard modules
        'json',
        'threading',
        'queue',
        'time',
        'datetime',
        'pathlib',
        'logging',
        
        # System modules
        'platform',
        'subprocess',
        'os',
        'sys',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary modules to reduce size
        'tkinter',
        'unittest',
        'test',
        'distutils',
        'setuptools',
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
    name='ParkIT',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for GUI application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico',  # Use company logo ICO as icon
) 