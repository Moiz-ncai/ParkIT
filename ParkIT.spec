# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Define data files to include - only essential assets
datas = [
    ('assets/*', 'assets'),
    ('gui/*.py', 'gui'),
]

# Define hidden imports - streamlined for standard YOLO
hiddenimports = [
    'PyQt5.QtCore',
    'PyQt5.QtGui', 
    'PyQt5.QtWidgets',
    'cv2',
    'numpy',
    'ultralytics',
    'torch',
    'torchvision',
    'PIL',
    'gui.main_window',
    'gui.interactive_video_widget',
    'camera_manager',
    'parking_spot_manager',
    'car_detection_manager',
    'json',
    'time',
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
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
    name='ParkIT',
    debug=True,              # Enable debugging
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,            # Enable console window for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico',  # Use the icon from assets
) 