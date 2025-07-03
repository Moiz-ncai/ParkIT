# ParkIT Executable Distribution

## Overview

ParkIT is available as a standalone Windows executable that requires no Python installation or dependency management. The executable includes all necessary libraries and frameworks.

## Download

**File Size:** ~328 MB  
**Platform:** Windows 10/11 (64-bit)  
**Requirements:** Minimum 4GB RAM (8GB recommended for AI detection)

## Distribution Package Contents

```
ParkIT_Distribution/
├── ParkIT.exe              # Main executable (328MB)
├── EXECUTABLE_README.txt   # User documentation
└── Run_ParkIT.bat         # Optional launcher script
```

## Building the Executable (For Developers)

### Prerequisites

1. Complete ParkIT development environment setup
2. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```

### Build Process

1. **Create Icon File:**
   ```bash
   python -c "from PIL import Image; img = Image.open('assets/company_logo.png'); img.save('assets/icon.ico', format='ICO', sizes=[(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)])"
   ```

2. **Build Executable:**
   ```bash
   pyinstaller ParkIT.spec
   ```

3. **Build Output:**
   - Executable: `dist/ParkIT.exe`
   - Build artifacts: `build/` (can be deleted)

### Build Configuration

The build is configured via `ParkIT.spec` which includes:

- **Hidden Imports:** All PyQt5, PyTorch, OpenCV, and ultralytics dependencies
- **Data Files:** Company logo, assets directory, YOLO models (if present)
- **Optimizations:** UPX compression, unnecessary module exclusions
- **GUI Mode:** Console=False for proper desktop application behavior
- **Icon:** Custom company logo as application icon

### Build Details

**Included Dependencies:**
- PyQt5 GUI framework
- PyTorch ML framework  
- OpenCV computer vision
- ultralytics (YOLOv11)
- NumPy, Pillow, and other core libraries

**Runtime Behavior:**
- YOLO models download automatically on first use
- Application data stored in user temp directory
- No external dependencies required
- Fully portable (can be copied between machines)

### Distribution Notes

- The executable is self-contained and portable
- First run may be slower due to model download
- Antivirus software may flag the executable (false positive)
- Windows Defender SmartScreen may show warning on first run

## Usage

### For End Users

1. Download the distribution package
2. Extract to any folder
3. Double-click `ParkIT.exe` or use `Run_ParkIT.bat`
4. Allow Windows Defender/firewall if prompted
5. The YOLOv11 model will download automatically on first use

### Camera Setup

- **Webcam Testing:** Use "0" in RTSP URL field
- **IP Camera:** Enter RTSP URL: `rtsp://username:password@ip:port/stream`

## Troubleshooting

### Common Issues

1. **Application won't start:**
   - Run as Administrator
   - Check Windows Defender exclusions
   - Ensure minimum system requirements

2. **Model download fails:**
   - Check internet connection
   - Verify firewall allows application
   - Try running from command line to see errors

3. **Camera connection issues:**
   - Test with webcam first (use "0")
   - Verify RTSP URL format
   - Check network connectivity to camera

### Size Optimization

The current executable (~328MB) includes full PyTorch and ML dependencies. Future optimizations may include:

- OpenVINO optimization for smaller Intel-optimized models
- Conditional dependency loading
- Model streaming instead of embedding

## Deployment

### Enterprise Deployment

For enterprise environments:
1. Test on target systems first
2. Configure antivirus exclusions
3. Consider network policy for model downloads
4. Document camera access requirements

### Updates

To update the executable:
1. Pull latest code changes
2. Rebuild using `pyinstaller ParkIT.spec --clean`
3. Redistribute the new executable

## Support

For executable-specific issues:
- Check Windows Event Viewer for application errors
- Run from command line to see console output
- Verify system meets minimum requirements
- Report issues via GitHub repository 