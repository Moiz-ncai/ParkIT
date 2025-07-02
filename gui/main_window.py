import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QPushButton, QFrame, QTextEdit,
                            QGridLayout, QGroupBox, QSizePolicy, QSplitter)
from PyQt5.QtCore import Qt, pyqtSlot, QTimer
from PyQt5.QtGui import QPixmap, QImage, QFont, QPalette, QColor
import cv2
import numpy as np
from camera_manager import CameraManager


class VideoLabel(QLabel):
    """Custom QLabel for displaying video frames"""
    
    def __init__(self):
        super().__init__()
        self.setMinimumSize(640, 480)
        self.setStyleSheet("""
            QLabel {
                background-color: #2b2b2b;
                border: 2px solid #555555;
                border-radius: 8px;
                color: #ffffff;
                font-size: 14px;
            }
        """)
        self.setAlignment(Qt.AlignCenter)
        self.setText("No Camera Connected\n\nPlease enter RTSP URL and click Connect")
        self.setScaledContents(True)
    
    def set_frame(self, frame):
        """Convert OpenCV frame to QPixmap and display it"""
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        
        # Scale the image to fit the label while maintaining aspect ratio
        pixmap = QPixmap.fromImage(qt_image)
        scaled_pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.setPixmap(scaled_pixmap)


class MainWindow(QMainWindow):
    """Main application window for ParkIT"""
    
    def __init__(self):
        super().__init__()
        self.camera_manager = CameraManager()
        self.setup_ui()
        self.connect_signals()
        self.apply_styles()
    
    def setup_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("ParkIT - Parking Management System")
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("ParkIT - Parking Management System")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        main_layout.addWidget(title_label)
        
        # Camera setup group
        camera_group = self.create_camera_setup_group()
        main_layout.addWidget(camera_group)
        
        # Video display and controls
        content_splitter = QSplitter(Qt.Horizontal)
        
        # Video display
        video_widget = self.create_video_display()
        content_splitter.addWidget(video_widget)
        
        # Control panel
        control_panel = self.create_control_panel()
        content_splitter.addWidget(control_panel)
        
        # Set splitter proportions
        content_splitter.setSizes([800, 400])
        main_layout.addWidget(content_splitter)
        
        # Status bar
        self.statusBar().showMessage("Ready - Enter RTSP URL to begin")
        self.statusBar().setStyleSheet("background-color: #34495e; color: white; padding: 5px;")
    
    def create_camera_setup_group(self):
        """Create the camera setup input group"""
        group = QGroupBox("Camera Setup")
        group.setFont(QFont("Arial", 12, QFont.Bold))
        
        layout = QHBoxLayout()
        
        # RTSP URL input
        layout.addWidget(QLabel("RTSP URL:"))
        self.rtsp_input = QLineEdit()
        self.rtsp_input.setPlaceholderText("rtsp://username:password@ip:port/stream")
        self.rtsp_input.setText("0")  # Default to webcam for testing
        layout.addWidget(self.rtsp_input)
        
        # Connect button
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.connect_camera)
        layout.addWidget(self.connect_btn)
        
        # Disconnect button
        self.disconnect_btn = QPushButton("Disconnect")
        self.disconnect_btn.clicked.connect(self.disconnect_camera)
        self.disconnect_btn.setEnabled(False)
        layout.addWidget(self.disconnect_btn)
        
        group.setLayout(layout)
        return group
    
    def create_video_display(self):
        """Create the video display area"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Video display label
        self.video_label = VideoLabel()
        layout.addWidget(self.video_label)
        
        widget.setLayout(layout)
        return widget
    
    def create_control_panel(self):
        """Create the control panel"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Connection status
        status_group = QGroupBox("Connection Status")
        status_layout = QVBoxLayout()
        
        self.status_label = QLabel("Disconnected")
        self.status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        status_layout.addWidget(self.status_label)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Camera info
        info_group = QGroupBox("Camera Information")
        info_layout = QVBoxLayout()
        
        self.camera_info = QTextEdit()
        self.camera_info.setMaximumHeight(150)
        self.camera_info.setReadOnly(True)
        self.camera_info.setText("No camera connected")
        info_layout.addWidget(self.camera_info)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Instructions
        instructions_group = QGroupBox("Instructions")
        instructions_layout = QVBoxLayout()
        
        instructions_text = QTextEdit()
        instructions_text.setReadOnly(True)
        instructions_text.setMaximumHeight(200)
        instructions_text.setText("""
1. Enter your RTSP camera URL in the format:
   rtsp://username:password@ip:port/stream

2. Click 'Connect' to establish connection

3. Once connected, you will see the live video feed

4. Use '0' for default webcam (testing purposes)

Next Steps (Coming Soon):
- Parking spot polygon selection
- YOLOv11 car detection
- License plate recognition
- OCR for license plate reading
        """)
        instructions_layout.addWidget(instructions_text)
        
        instructions_group.setLayout(instructions_layout)
        layout.addWidget(instructions_group)
        
        # Stretch to fill remaining space
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def connect_signals(self):
        """Connect camera manager signals"""
        self.camera_manager.frame_ready.connect(self.update_frame)
        self.camera_manager.connection_status_changed.connect(self.update_connection_status)
        
        # Enter key in RTSP input triggers connect
        self.rtsp_input.returnPressed.connect(self.connect_camera)
    
    @pyqtSlot(np.ndarray)
    def update_frame(self, frame):
        """Update the video display with new frame"""
        self.video_label.set_frame(frame)
    
    @pyqtSlot(bool, str)
    def update_connection_status(self, connected, message):
        """Update connection status and UI elements"""
        if connected:
            self.status_label.setText("Connected")
            self.status_label.setStyleSheet("color: #27ae60; font-weight: bold;")
            self.connect_btn.setEnabled(False)
            self.disconnect_btn.setEnabled(True)
            self.rtsp_input.setEnabled(False)
            
            # Update camera info
            width, height = self.camera_manager.get_frame_size()
            if width and height:
                info_text = f"""
Camera URL: {self.camera_manager.current_url}
Resolution: {width} x {height}
Status: Connected and streaming
Connection Time: Just connected
                """
            else:
                info_text = f"""
Camera URL: {self.camera_manager.current_url}
Status: Connected
                """
            self.camera_info.setText(info_text.strip())
        else:
            self.status_label.setText("Disconnected")
            self.status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
            self.connect_btn.setEnabled(True)
            self.disconnect_btn.setEnabled(False)
            self.rtsp_input.setEnabled(True)
            self.camera_info.setText("No camera connected")
            
            # Reset video display
            self.video_label.clear()
            self.video_label.setText("No Camera Connected\n\nPlease enter RTSP URL and click Connect")
        
        self.statusBar().showMessage(message)
    
    def connect_camera(self):
        """Connect to the camera"""
        rtsp_url = self.rtsp_input.text().strip()
        if not rtsp_url:
            self.statusBar().showMessage("Please enter RTSP URL")
            return
        
        self.statusBar().showMessage("Connecting...")
        self.camera_manager.connect_camera(rtsp_url)
    
    def disconnect_camera(self):
        """Disconnect from the camera"""
        self.camera_manager.disconnect_camera()
    
    def apply_styles(self):
        """Apply modern styling to the application"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ecf0f1;
            }
            
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #2c3e50;
            }
            
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                font-size: 12px;
                background-color: white;
            }
            
            QLineEdit:focus {
                border-color: #3498db;
            }
            
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: bold;
                min-width: 80px;
            }
            
            QPushButton:hover {
                background-color: #2980b9;
            }
            
            QPushButton:pressed {
                background-color: #21618c;
            }
            
            QPushButton:disabled {
                background-color: #95a5a6;
            }
            
            QTextEdit {
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                background-color: white;
                font-size: 11px;
                padding: 5px;
            }
            
            QSplitter::handle {
                background-color: #bdc3c7;
            }
        """)
    
    def closeEvent(self, event):
        """Handle application close event"""
        self.camera_manager.disconnect_camera()
        event.accept() 