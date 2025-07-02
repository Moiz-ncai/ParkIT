# ParkIT - Parking Management System

A modern PyQt5-based application for intelligent parking management using IP cameras, computer vision, and machine learning.

## Overview

ParkIT is designed to help you monitor parking spaces through IP cameras, detect occupied/vacant spots, and identify vehicles through license plate recognition. The application is built in two phases:

1. **Setup Phase**: Configure cameras and define parking spot areas
2. **Running Phase**: Real-time monitoring with AI-powered detection

## Current Features (Phase 2)

✅ **Camera Management**
- RTSP IP camera connection
- Live video feed display
- Connection status monitoring
- Camera information display

✅ **Interactive Parking Spot Setup**
- Point-and-click polygon drawing
- Real-time visual feedback
- Parking spot naming and labeling
- Spot selection and highlighting

✅ **Camera-Specific Parking Spot Management**
- Each camera maintains its own parking spot configuration
- Automatic loading/saving of spots per camera IP/URL
- Tabbed interface for organization
- Comprehensive spot table with camera status
- Edit, delete, and clear operations per camera
- Persistent storage with multi-camera support (JSON format)
- Visual spot overlay on video feed with camera context

✅ **Modern GUI**
- Clean, intuitive interface
- Real-time video streaming
- Interactive video controls
- Responsive design with tabs
- Status indicators and statistics

## Planned Features (Coming Soon)

🚧 **Parking Spot Configuration**
- Interactive polygon drawing for parking spots
- Multiple parking area definition
- Spot numbering and labeling

🚧 **AI-Powered Detection**
- YOLOv11 car detection
- License plate recognition
- OCR for license plate text
- Real-time occupancy status

🚧 **Management Dashboard**
- Parking spot availability overview
- Historical data and analytics
- Export capabilities

## Installation

### Prerequisites

- Python 3.7 or higher
- Webcam or IP camera (for testing)

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Dependencies

- `PyQt5==5.15.10` - GUI framework
- `opencv-python==4.8.1.78` - Computer vision and camera handling
- `numpy==1.24.3` - Numerical computing
- `Pillow==10.0.1` - Image processing

## Usage

### Running the Application

```bash
python main.py
```

### Camera Setup

1. **Testing with Webcam**:
   - Leave the default value "0" in the RTSP URL field
   - Click "Connect" to use your default webcam

2. **Using IP Camera**:
   - Enter your RTSP URL in the format:
     ```
     rtsp://username:password@ip:port/stream
     ```
   - Example: `rtsp://admin:password123@192.168.1.100:554/stream1`
   - Click "Connect" to establish connection

### Interface Overview

- **Camera Setup**: Enter RTSP URL and connect/disconnect controls
- **Interactive Video Display**: Live camera feed with polygon drawing capabilities
- **Drawing Controls**: Start/cancel drawing, visibility toggle
- **Tabbed Control Panel**:
  - **Status Tab**: Connection status and camera information
  - **Parking Spots Tab**: Spot management table and controls
  - **Instructions Tab**: Comprehensive usage guidelines

### Camera-Specific Parking Spot Setup

1. **Connect Camera**: Establish RTSP connection or use webcam (0)
   - Each camera automatically loads its saved parking spots
   - New cameras start with no spots defined
2. **Draw Parking Spots**:
   - Click "Draw New Spot" button
   - Left-click on video to add polygon points
   - Right-click to finish and name the spot
   - Spots are automatically saved for this specific camera
3. **Manage Camera-Specific Spots**:
   - View spots for current camera in the Parking Spots tab
   - Click spots on video to select them
   - Edit names, delete spots, or clear all (for current camera only)
   - Toggle visibility with checkbox
4. **Switch Between Cameras**:
   - Disconnect and connect to different cameras
   - Each camera loads its own unique parking spot configuration
   - Spots are stored persistently per camera IP/URL
   - Statistics show current camera info and total cameras configured

### Keyboard Shortcuts

- **ESC**: Cancel current drawing operation
- **Left-click**: Add polygon point (drawing mode) or select spot (view mode)
- **Right-click**: Finish polygon drawing

## File Structure

```
ParkIT/
├── main.py                          # Application entry point
├── camera_manager.py                # Camera connection and streaming
├── parking_spot_manager.py          # Parking spot management and persistence
├── gui/
│   ├── __init__.py
│   ├── main_window.py               # Main GUI window with tabbed interface
│   └── interactive_video_widget.py  # Interactive video display with drawing
├── requirements.txt                 # Python dependencies
├── run_parkit.bat                  # Windows launcher script
├── parking_spots.json              # Parking spot data (auto-generated)
└── README.md                       # This file
```

## Troubleshooting

### Common Issues

1. **Camera Connection Failed**:
   - Verify RTSP URL format
   - Check network connectivity
   - Ensure camera is accessible
   - Try with webcam (use "0") for testing

2. **Application Won't Start**:
   - Install all required dependencies
   - Check Python version (3.7+)
   - Run `python main.py` to see error details

3. **Video Display Issues**:
   - Update graphics drivers
   - Try different camera resolutions
   - Check camera compatibility

### RTSP URL Formats

Different camera brands use different RTSP URL formats:

- **Generic**: `rtsp://username:password@ip:port/stream`
- **Hikvision**: `rtsp://username:password@ip:554/Streaming/Channels/101`
- **Dahua**: `rtsp://username:password@ip:554/cam/realmonitor?channel=1&subtype=0`
- **Axis**: `rtsp://username:password@ip/axis-media/media.amp`

## Development

### Adding New Features

The application is designed with modularity in mind:

- `camera_manager.py`: Handles all camera operations
- `gui/main_window.py`: Main interface and user interactions
- Additional modules can be added for AI detection, database management, etc.

### Contributing

1. Fork the repository
2. Create a feature branch
3. Add your improvements
4. Test thoroughly
5. Submit a pull request

## Future Roadmap

### Phase 2: Parking Spot Configuration ✅ COMPLETED
- [x] Interactive polygon drawing tool
- [x] Parking spot persistence
- [x] Multiple parking spot management
- [x] Visual feedback and selection

### Phase 3: AI Detection
- [ ] YOLOv11 integration
- [ ] License plate detection
- [ ] OCR implementation
- [ ] Real-time processing optimization

### Phase 4: Advanced Features
- [ ] Database integration
- [ ] Web dashboard
- [ ] Mobile app companion
- [ ] Cloud synchronization

## License

This project is developed for educational and commercial use. Please ensure you have proper permissions for using IP cameras and comply with local privacy laws.

## Support

For issues, questions, or feature requests, please create an issue in the project repository or contact the development team.

---

**ParkIT - Making parking management intelligent and efficient.** 