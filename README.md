# ParkIT - Parking Management System v3.0

🚀 **Production Ready** - A modern PyQt5-based application for intelligent parking management using IP cameras, computer vision, and machine learning.

## Overview

ParkIT is designed to help you monitor parking spaces through IP cameras, detect occupied/vacant spots, and provide real-time parking occupancy analysis. The application provides a complete solution for parking management with an intuitive interface and powerful AI-driven vehicle detection capabilities.

**Current Production Version: 3.0**

## Features (Production Ready)

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

✅ **YOLOv11 Vehicle Detection** (COMPLETED)
- Real-time vehicle detection using COCO-trained YOLOv11 model
- **5 Vehicle Types Supported**: Cars, Trucks, Buses, Motorcycles, Trains
- Configurable confidence threshold and detection interval
- Multi-threaded processing for smooth GUI performance
- Visual bounding boxes with vehicle type and confidence scores
- Detection statistics and FPS monitoring
- Automatic occupancy analysis based on vehicle detection

✅ **Real-time Parking Occupancy** (COMPLETED)
- Automatic parking spot status updates (Occupied/Vacant)
- Intelligent overlap detection for spot occupancy
- Color-coded parking spots (Green=Vacant, Red=Occupied)
- Real-time occupancy statistics and counts
- Camera-specific occupancy monitoring
- Configurable overlap threshold for accurate detection

✅ **Modern Professional GUI**
- Clean, intuitive interface with tabbed design
- **Centered title with company branding** and professional logo integration
- Real-time video streaming with detection overlay
- Vehicle Detection tab with configurable settings
- Interactive video controls with instant window resizing
- Responsive design with optimized layout management
- **Fixed header sizing** preventing expansion in fullscreen mode
- Comprehensive statistics display

## Planned Features (Coming Soon)

🚧 **License Plate Recognition**
- License plate detection and localization
- OCR for license plate text extraction
- Vehicle identification and tracking

🚧 **Advanced Analytics**
- Parking duration tracking
- Historical occupancy data
- Usage patterns and statistics
- Export capabilities and reporting

🚧 **Enhanced Features**
- Multiple detection models support
- Email/SMS notifications
- Database integration
- REST API for external integration

## Installation

### Prerequisites

- Python 3.7 or higher
- Webcam or IP camera (for testing)

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Dependencies

- `PyQt5>=5.15.7` - GUI framework
- `opencv-python>=4.8.0` - Computer vision and camera handling
- `numpy>=1.21.0` - Numerical computing
- `Pillow>=10.0.0` - Image processing
- `ultralytics>=8.0.0` - YOLOv11 model and inference engine
- `torch>=2.0.0` - PyTorch deep learning framework
- `torchvision>=0.15.0` - Computer vision utilities for PyTorch

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
- **Interactive Video Display**: Live camera feed with polygon drawing and vehicle detection overlay
- **Drawing Controls**: Start/cancel drawing, visibility toggle
- **Tabbed Control Panel**:
  - **Status Tab**: Connection status and camera information
  - **Parking Spots Tab**: Spot management table with occupancy status
  - **Vehicle Detection Tab**: Detection controls, statistics, and settings
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

### Vehicle Detection and Real-time Monitoring

1. **Enable Vehicle Detection**:
   - Go to the "Vehicle Detection" tab
   - Check "Enable Vehicle Detection" to start detection
   - The YOLOv11 model will automatically download on first run

2. **Configure Detection Settings**:
   - **Confidence Threshold**: Adjust sensitivity (0.10-0.95)
     - Lower values = more detections, potential false positives
     - Higher values = fewer detections, more accuracy
   - **Detection Interval**: How often to run detection (0.1-10.0 seconds)
     - Lower intervals = more frequent updates, higher CPU usage
   - **Overlap Threshold**: Minimum overlap for spot occupancy (0.10-0.90)
     - Higher values = stricter occupancy detection

3. **Monitor Real-time Status**:
   - **Video Feed**: Green bounding boxes show detected vehicles with confidence scores and vehicle type
   - **Vehicle Types Detected**: Cars, Trucks, Buses, Motorcycles, Trains
   - **Parking Spots**: Automatically update colors (Green=Vacant, Red=Occupied)
   - **Statistics**: View current vehicles, total detections, and detection FPS
   - **Status Bar**: Shows real-time occupancy counts

4. **Occupancy Management**:
   - View occupancy status in the Parking Spots tab
   - Status column shows Occupied/Vacant with color coding
   - Statistics display current camera occupancy summary
   - Each camera maintains independent detection state

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
├── car_detection_manager.py         # YOLOv11 vehicle detection and occupancy analysis
├── assets/
│   └── company_logo.png             # Company logo for branding
├── gui/
│   ├── __init__.py
│   ├── main_window.py               # Main GUI window with tabbed interface
│   └── interactive_video_widget.py  # Interactive video display with drawing
├── requirements.txt                 # Python dependencies
├── run_parkit.bat                  # Windows launcher script
├── yolo11s.pt                      # YOLOv11 model weights (auto-downloaded)
├── yolo11s_openvino_model/         # Optimized model files (auto-generated)
├── parking_spots.json              # Parking spot data (auto-generated)
├── PRODUCTION_INFO.md              # Production deployment guide
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

### Phase 1: Basic GUI and Camera Connection ✅ COMPLETED
- [x] PyQt5 interface
- [x] RTSP camera integration
- [x] Live video streaming
- [x] Basic controls and status display

### Phase 2: Parking Spot Configuration ✅ COMPLETED
- [x] Interactive polygon drawing tool
- [x] Parking spot persistence
- [x] Multiple parking spot management
- [x] Visual feedback and selection
- [x] Camera-specific spot management

### Phase 3: AI Vehicle Detection ✅ COMPLETED
- [x] YOLOv11 integration
- [x] Real-time vehicle detection (5 vehicle types)
- [x] Automatic occupancy analysis
- [x] Multi-threaded processing optimization
- [x] Configurable detection parameters

### Phase 4: Advanced Features (Coming Next)
- [ ] License plate detection and OCR
- [ ] Historical analytics and reporting
- [ ] Database integration
- [ ] Web dashboard
- [ ] Mobile app companion
- [ ] Cloud synchronization
- [ ] Email/SMS notifications
- [ ] REST API for external integration

## License

This project is developed for educational and commercial use. Please ensure you have proper permissions for using IP cameras and comply with local privacy laws.

## Support

For issues, questions, or feature requests, please create an issue in the project repository or contact the development team.

---

**ParkIT - Making parking management intelligent and efficient.** 