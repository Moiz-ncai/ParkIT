import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QPushButton, QFrame, QTextEdit,
                            QGridLayout, QGroupBox, QSizePolicy, QSplitter,
                            QListWidget, QListWidgetItem, QMessageBox, QInputDialog,
                            QCheckBox, QTabWidget, QTableWidget, QTableWidgetItem,
                            QHeaderView, QSlider, QSpinBox, QDoubleSpinBox)
from PyQt5.QtCore import Qt, pyqtSlot, QTimer
from PyQt5.QtGui import QPixmap, QImage, QFont, QPalette, QColor
import cv2
import numpy as np
from camera_manager import CameraManager
from parking_spot_manager import ParkingSpotManager
from car_detection_manager import CarDetectionManager
from gui.interactive_video_widget import InteractiveVideoWidget





class MainWindow(QMainWindow):
    """Main application window for ParkIT"""
    
    def __init__(self):
        super().__init__()
        self.camera_manager = CameraManager()
        self.spot_manager = ParkingSpotManager()
        self.car_detection_manager = CarDetectionManager()
        self.setup_ui()
        self.connect_signals()
        self.apply_styles()
        self.initialize_detection_system()
    
    def setup_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("ParkIT")
        self.setGeometry(100, 100, 1200, 800)
        
        # Enable instant resizing behavior
        self.setDockNestingEnabled(False)  # Disable dock nesting animations
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)  # Reduced spacing from 15 to 10
        main_layout.setContentsMargins(15, 15, 15, 15)  # Reduced margins from 20 to 15
        
        # Set layout to resize immediately
        main_layout.setSizeConstraint(QVBoxLayout.SetDefaultConstraint)
        
        # Header with logo and title
        header_layout = QHBoxLayout()
        
        # Left side with logo
        left_container = QWidget()
        left_container.setFixedWidth(120)  # Fixed width to balance the layout
        left_container.setFixedHeight(80)  # Fixed height to prevent expansion
        left_layout = QHBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Company logo
        logo_label = QLabel()
        try:
            logo_pixmap = QPixmap("assets/company_logo.png")
            # Scale logo to bigger size while maintaining aspect ratio
            scaled_logo = logo_pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_logo)
        except Exception as e:
            # Fallback if logo can't be loaded
            logo_label.setText("LOGO")
            logo_label.setStyleSheet("background-color: #3498db; color: white; padding: 20px; border-radius: 5px; font-size: 12px;")
        
        logo_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        logo_label.setFixedSize(100, 100)  # Fixed size to prevent expansion
        left_layout.addWidget(logo_label)
        left_layout.addStretch()
        
        header_layout.addWidget(left_container)
        
        # Center title - this will now be truly centered
        title_container = QWidget()
        title_container.setFixedHeight(80)  # Fixed height to match logo container
        title_container_layout = QVBoxLayout(title_container)
        title_container_layout.setContentsMargins(0, 10, 0, 10)
        
        title_label = QLabel("ParkIT")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 20, QFont.Bold))  # Slightly smaller font
        title_label.setStyleSheet("color: #2c3e50;")
        title_container_layout.addWidget(title_label)
        
        header_layout.addWidget(title_container, 1)  # Give it stretch factor of 1
        
        # Right side spacer to balance the left side
        right_container = QWidget()
        right_container.setFixedWidth(120)  # Same width as left container
        right_container.setFixedHeight(80)  # Fixed height to prevent expansion
        header_layout.addWidget(right_container)
        
        # Set the header layout to not expand vertically
        header_widget = QWidget()
        header_widget.setLayout(header_layout)
        header_widget.setFixedHeight(80)  # Fixed height for entire header
        header_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        main_layout.addWidget(header_widget)
        
        # Set size policies for instant resizing
        central_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Camera setup group
        camera_group = self.create_camera_setup_group()
        main_layout.addWidget(camera_group)
        
        # Video display and controls
        content_splitter = QSplitter(Qt.Horizontal)
        
        # Disable splitter animations for instant resizing
        content_splitter.setChildrenCollapsible(False)
        content_splitter.setOpaqueResize(True)  # Resize immediately, not gradually
        
        # Video display
        video_widget = self.create_video_display()
        video_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        content_splitter.addWidget(video_widget)
        
        # Control panel
        control_panel = self.create_control_panel()
        control_panel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
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
        group.setFixedHeight(80)  # Fixed height to prevent expansion
        group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # RTSP URL input
        layout.addWidget(QLabel("RTSP URL:"))
        self.rtsp_input = QLineEdit()
        self.rtsp_input.setPlaceholderText("rtsp://username:password@ip:port/stream")
        self.rtsp_input.setText("rtsp://admin:uetpeshawar123@10.110.130.231:554/Streaming/Channels/101")  # Default to webcam for testing
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
        widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Interactive video widget
        self.video_widget = InteractiveVideoWidget()
        self.video_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.video_widget.setMinimumSize(400, 300)  # Set minimum size for proper scaling
        self.video_widget.set_spot_manager(self.spot_manager)
        layout.addWidget(self.video_widget)
        
        # Drawing controls
        controls_layout = QHBoxLayout()
        
        self.draw_spot_btn = QPushButton("Draw New Spot")
        self.draw_spot_btn.clicked.connect(self.start_drawing_spot)
        self.draw_spot_btn.setEnabled(False)
        controls_layout.addWidget(self.draw_spot_btn)
        
        self.cancel_draw_btn = QPushButton("Cancel Drawing")
        self.cancel_draw_btn.clicked.connect(self.cancel_drawing)
        self.cancel_draw_btn.setEnabled(False)
        controls_layout.addWidget(self.cancel_draw_btn)
        
        self.show_spots_cb = QCheckBox("Show Parking Spots")
        self.show_spots_cb.setChecked(True)
        self.show_spots_cb.toggled.connect(self.toggle_spots_visibility)
        controls_layout.addWidget(self.show_spots_cb)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        widget.setLayout(layout)
        return widget
    
    def create_control_panel(self):
        """Create the control panel with tabs for different functions"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Create tabs
        tab_widget = QTabWidget()
        
        # Status tab
        status_tab = self.create_status_tab()
        tab_widget.addTab(status_tab, "Status")
        
        # Parking spots tab
        spots_tab = self.create_spots_tab()
        tab_widget.addTab(spots_tab, "Parking Spots")
        
        # Vehicle detection tab
        detection_tab = self.create_detection_tab()
        tab_widget.addTab(detection_tab, "Vehicle Detection")
        
        # Instructions tab
        instructions_tab = self.create_instructions_tab()
        tab_widget.addTab(instructions_tab, "Instructions")
        
        layout.addWidget(tab_widget)
        widget.setLayout(layout)
        return widget
    
    def create_status_tab(self):
        """Create the status tab"""
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
        
        # Stretch to fill remaining space
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def create_spots_tab(self):
        """Create the parking spots management tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Parking spots list
        spots_group = QGroupBox("Parking Spots")
        spots_layout = QVBoxLayout()
        
        # Spots table
        self.spots_table = QTableWidget()
        self.spots_table.setColumnCount(4)
        self.spots_table.setHorizontalHeaderLabels(["ID", "Name", "Status", "Points"])
        self.spots_table.horizontalHeader().setStretchLastSection(True)
        self.spots_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.spots_table.itemSelectionChanged.connect(self.on_spot_table_selection_changed)
        spots_layout.addWidget(self.spots_table)
        
        # Spot management buttons
        buttons_layout = QHBoxLayout()
        
        self.edit_spot_btn = QPushButton("Edit Name")
        self.edit_spot_btn.clicked.connect(self.edit_selected_spot)
        self.edit_spot_btn.setEnabled(False)
        buttons_layout.addWidget(self.edit_spot_btn)
        
        self.delete_spot_btn = QPushButton("Delete")
        self.delete_spot_btn.clicked.connect(self.delete_selected_spot)
        self.delete_spot_btn.setEnabled(False)
        buttons_layout.addWidget(self.delete_spot_btn)
        
        self.clear_spots_btn = QPushButton("Clear All")
        self.clear_spots_btn.clicked.connect(self.clear_all_spots)
        buttons_layout.addWidget(self.clear_spots_btn)
        
        spots_layout.addLayout(buttons_layout)
        spots_group.setLayout(spots_layout)
        layout.addWidget(spots_group)
        
        # Statistics
        stats_group = QGroupBox("Statistics")
        stats_layout = QVBoxLayout()
        
        self.stats_label = QLabel("No parking spots defined")
        stats_layout.addWidget(self.stats_label)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_detection_tab(self):
        """Create the vehicle detection tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Detection control group
        detection_group = QGroupBox("Detection Control")
        detection_layout = QGridLayout()
        
        # Enable/Disable detection
        self.detection_enabled_checkbox = QCheckBox("Enable Vehicle Detection")
        self.detection_enabled_checkbox.toggled.connect(self.on_detection_enabled_changed)
        detection_layout.addWidget(self.detection_enabled_checkbox, 0, 0, 1, 2)
        
        # Confidence threshold
        detection_layout.addWidget(QLabel("Confidence Threshold:"), 1, 0)
        self.confidence_slider = QSlider(Qt.Horizontal)
        self.confidence_slider.setRange(10, 95)
        self.confidence_slider.setValue(50)
        self.confidence_slider.valueChanged.connect(self.on_confidence_changed)
        detection_layout.addWidget(self.confidence_slider, 1, 1)
        
        self.confidence_label = QLabel("0.50")
        detection_layout.addWidget(self.confidence_label, 1, 2)
        
        # Detection interval
        detection_layout.addWidget(QLabel("Detection Interval (s):"), 2, 0)
        self.interval_spinbox = QDoubleSpinBox()
        self.interval_spinbox.setRange(0.1, 10.0)
        self.interval_spinbox.setValue(1.0)
        self.interval_spinbox.setSingleStep(0.1)
        self.interval_spinbox.valueChanged.connect(self.on_interval_changed)
        detection_layout.addWidget(self.interval_spinbox, 2, 1)
        
        # Overlap threshold
        detection_layout.addWidget(QLabel("Overlap Threshold:"), 3, 0)
        self.overlap_slider = QSlider(Qt.Horizontal)
        self.overlap_slider.setRange(10, 90)
        self.overlap_slider.setValue(30)
        self.overlap_slider.valueChanged.connect(self.on_overlap_changed)
        detection_layout.addWidget(self.overlap_slider, 3, 1)
        
        self.overlap_label = QLabel("0.30")
        detection_layout.addWidget(self.overlap_label, 3, 2)
        
        detection_group.setLayout(detection_layout)
        layout.addWidget(detection_group)
        
        # Detection statistics group
        stats_group = QGroupBox("Detection Statistics")
        stats_layout = QGridLayout()
        
        # Statistics labels
        self.current_cars_label = QLabel("Current Vehicles: 0")
        self.total_detections_label = QLabel("Total Detections: 0")
        self.detection_fps_label = QLabel("Detection FPS: 0")
        self.model_status_label = QLabel("Model Status: Not Loaded")
        
        stats_layout.addWidget(self.current_cars_label, 0, 0)
        stats_layout.addWidget(self.total_detections_label, 0, 1)
        stats_layout.addWidget(self.detection_fps_label, 1, 0)
        stats_layout.addWidget(self.model_status_label, 1, 1)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Detection info
        info_group = QGroupBox("Information")
        info_layout = QVBoxLayout()
        
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setMaximumHeight(200)
        info_text.setHtml("""
                        <h4>Vehicle Detection Features:</h4>
                <ul>
                <li><strong>YOLOv11 Model:</strong> Uses COCO-trained model for vehicle detection (cars, trucks, buses, motorcycles, trains)</li>
            <li><strong>Real-time Processing:</strong> Detects cars in live video feed</li>
            <li><strong>Automatic Occupancy:</strong> Updates parking spot status based on detections</li>
            <li><strong>Configurable Settings:</strong> Adjust confidence and overlap thresholds</li>
        </ul>
        
        <h4>Settings Guide:</h4>
        <ul>
            <li><strong>Confidence:</strong> Lower = more detections, higher = fewer false positives</li>
            <li><strong>Interval:</strong> How often to run detection (lower = more frequent)</li>
            <li><strong>Overlap:</strong> How much car must overlap spot to be considered occupied</li>
        </ul>
        """)
        info_layout.addWidget(info_text)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_instructions_tab(self):
        """Create the instructions tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Instructions
        instructions_group = QGroupBox("How to Use ParkIT")
        instructions_layout = QVBoxLayout()
        
        instructions_text = QTextEdit()
        instructions_text.setReadOnly(True)
        instructions_text.setText("""
                PHASE 3: Vehicle Detection & Real-time Parking Management

1. CAMERA SETUP:
   - Enter RTSP URL: rtsp://user:pass@ip:port/stream
   - Or use '0' for webcam testing
   - Click 'Connect' to start video feed
   - Each camera maintains its own set of parking spots

2. DRAWING PARKING SPOTS:
   - Click 'Draw New Spot' button
   - Left-click on video to add polygon points
   - Right-click to finish the polygon
   - Enter a name for the parking spot
   - Spots are automatically saved for this camera

3. VEHICLE DETECTION:
   - Go to 'Vehicle Detection' tab
   - Enable vehicle detection with checkbox
   - Adjust confidence threshold (lower = more detections)
   - Set detection interval (how often to detect)
   - Configure overlap threshold (for spot occupancy)
   - View detection statistics and model status

4. REAL-TIME MONITORING:
   - Green boxes show detected cars with confidence scores
   - Parking spots automatically update:
     * Green spots = Vacant
            * Red spots = Occupied (vehicle detected)
   - View occupancy stats in Parking Spots tab
   - Status bar shows real-time occupancy counts

5. MANAGING SPOTS:
   - View spots for current camera in 'Parking Spots' tab
   - Status column shows Occupied/Vacant with color coding
   - Click on spots in video to select them
   - Edit names or delete spots as needed
   - Toggle spot visibility with checkbox

6. CAMERA SWITCHING:
   - Disconnect and connect to different cameras
   - Each camera loads its own parking spots
   - Detection settings persist across cameras
   - Spots are persistently stored per camera IP/URL

7. KEYBOARD SHORTCUTS:
   - ESC: Cancel current drawing operation

COMING SOON:
- License plate recognition
- OCR for license plate reading
- Parking history and analytics

TIPS:
- Draw parking spots to match actual parking space boundaries
- Use appropriate confidence threshold for your camera quality
- Higher overlap threshold = stricter occupancy detection
- Test detection settings with different lighting conditions
- Each camera maintains separate spot configurations
        """)
        instructions_layout.addWidget(instructions_text)
        
        instructions_group.setLayout(instructions_layout)
        layout.addWidget(instructions_group)
        
        widget.setLayout(layout)
        return widget
    
    def connect_signals(self):
        """Connect all signals"""
        # Camera manager signals
        self.camera_manager.frame_ready.connect(self.update_frame)
        self.camera_manager.connection_status_changed.connect(self.update_connection_status)
        
        # Spot manager signals
        self.spot_manager.spots_updated.connect(self.update_spots_table)
        self.spot_manager.spot_selected.connect(self.on_spot_selected)
        self.spot_manager.camera_changed.connect(self.on_camera_changed)
        
        # Vehicle detection manager signals
        self.car_detection_manager.detections_updated.connect(self.on_detections_updated)
        self.car_detection_manager.occupancy_updated.connect(self.on_occupancy_updated)
        
        # Video widget signals
        self.video_widget.polygon_completed.connect(self.on_polygon_completed)
        self.video_widget.spot_clicked.connect(self.on_spot_clicked)
        
        # Enter key in RTSP input triggers connect
        self.rtsp_input.returnPressed.connect(self.connect_camera)
    
    @pyqtSlot(np.ndarray)
    def update_frame(self, frame):
        """Update the video display with new frame"""
        # Process frame through vehicle detection if enabled
        if hasattr(self, 'car_detection_manager'):
            processed_frame = self.car_detection_manager.process_frame(frame)
            self.video_widget.set_frame(processed_frame)
        else:
            self.video_widget.set_frame(frame)
    
    @pyqtSlot(bool, str)
    def update_connection_status(self, connected, message):
        """Update connection status and UI elements"""
        if connected:
            self.status_label.setText("Connected")
            self.status_label.setStyleSheet("color: #27ae60; font-weight: bold;")
            self.connect_btn.setEnabled(False)
            self.disconnect_btn.setEnabled(True)
            self.rtsp_input.setEnabled(False)
            self.draw_spot_btn.setEnabled(True)
            
            # Set camera in spot manager to load camera-specific spots
            camera_url = self.camera_manager.current_url
            self.spot_manager.set_camera(camera_url)
            
            # Update camera info
            width, height = self.camera_manager.get_frame_size()
            total_cameras = len(self.spot_manager.get_all_cameras())
            has_spots = self.spot_manager.has_camera_data(camera_url)
            
            if width and height:
                info_text = f"""
Camera URL: {camera_url}
Resolution: {width} x {height}
Status: Connected and streaming
Parking Spots: {len(self.spot_manager.get_all_spots())} spots defined
Total Cameras: {total_cameras} cameras configured
Camera History: {'Has previous spots' if has_spots else 'New camera'}
                """
            else:
                info_text = f"""
Camera URL: {camera_url}
Status: Connected
Parking Spots: {len(self.spot_manager.get_all_spots())} spots defined
Total Cameras: {total_cameras} cameras configured
                """
            self.camera_info.setText(info_text.strip())
        else:
            self.status_label.setText("Disconnected")
            self.status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
            self.connect_btn.setEnabled(True)
            self.disconnect_btn.setEnabled(False)
            self.rtsp_input.setEnabled(True)
            self.draw_spot_btn.setEnabled(False)
            self.cancel_draw_btn.setEnabled(False)
            
            # Disconnect camera from spot manager
            self.spot_manager.disconnect_camera()
            
            total_cameras = len(self.spot_manager.get_all_cameras())
            camera_info = f"No camera connected\nTotal Cameras: {total_cameras} cameras configured"
            self.camera_info.setText(camera_info)
            
            # Reset video display
            self.video_widget.clear_display()
            # Stop any drawing mode
            self.video_widget.stop_drawing_mode()
        
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
    
    # Parking spot management methods
    def start_drawing_spot(self):
        """Start drawing a new parking spot"""
        self.video_widget.start_drawing_mode()
        self.draw_spot_btn.setEnabled(False)
        self.cancel_draw_btn.setEnabled(True)
        self.statusBar().showMessage("Drawing mode: Left-click to add points, Right-click to finish")
    
    def cancel_drawing(self):
        """Cancel current drawing operation"""
        self.video_widget.stop_drawing_mode()
        self.draw_spot_btn.setEnabled(True)
        self.cancel_draw_btn.setEnabled(False)
        self.statusBar().showMessage("Drawing cancelled")
    
    def toggle_spots_visibility(self, checked):
        """Toggle parking spots visibility"""
        if hasattr(self, 'video_widget'):
            self.video_widget.update_display()
    
    @pyqtSlot(str, list)
    def on_polygon_completed(self, name, points):
        """Handle completed polygon drawing"""
        try:
            spot_id = self.spot_manager.add_spot(name, points)
            self.statusBar().showMessage(f"Parking spot '{name}' created successfully")
            self.draw_spot_btn.setEnabled(True)
            self.cancel_draw_btn.setEnabled(False)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to create parking spot: {str(e)}")
            self.start_drawing_spot()  # Allow user to try again
    
    @pyqtSlot(int)
    def on_spot_clicked(self, spot_id):
        """Handle clicking on a parking spot"""
        self.spot_manager.select_spot(spot_id)
        # Find and select the corresponding row in the table
        for row in range(self.spots_table.rowCount()):
            item = self.spots_table.item(row, 0)
            if item and int(item.text()) == spot_id:
                self.spots_table.selectRow(row)
                break
    
    @pyqtSlot(int)
    def on_spot_selected(self, spot_id):
        """Handle spot selection from manager"""
        spot = self.spot_manager.get_spot(spot_id)
        if spot:
            self.statusBar().showMessage(f"Selected: {spot.name}")
    
    @pyqtSlot(str)
    def on_camera_changed(self, camera_url):
        """Handle camera change in spot manager"""
        if camera_url:
            spot_count = len(self.spot_manager.get_all_spots())
            if spot_count > 0:
                self.statusBar().showMessage(f"Loaded {spot_count} parking spots for camera: {camera_url}")
            else:
                self.statusBar().showMessage(f"No existing parking spots for camera: {camera_url}")
        else:
            self.statusBar().showMessage("Camera disconnected")
    
    def update_spots_table(self):
        """Update the parking spots table"""
        try:
            spots = self.spot_manager.get_all_spots()
            self.spots_table.setRowCount(len(spots))
            
            for row, (spot_id, spot) in enumerate(spots.items()):
                try:
                    # ID
                    self.spots_table.setItem(row, 0, QTableWidgetItem(str(spot_id)))
                    
                    # Name
                    self.spots_table.setItem(row, 1, QTableWidgetItem(spot.name))
                    
                    # Status
                    status = "Occupied" if hasattr(spot, 'is_occupied') and spot.is_occupied else "Vacant"
                    status_item = QTableWidgetItem(status)
                    if hasattr(spot, 'is_occupied') and spot.is_occupied:
                        status_item.setBackground(QColor(255, 200, 200))  # Light red
                    else:
                        status_item.setBackground(QColor(200, 255, 200))  # Light green
                    self.spots_table.setItem(row, 2, status_item)
                    
                    # Points count
                    self.spots_table.setItem(row, 3, QTableWidgetItem(f"{len(spot.polygon_points)} points"))
                    
                except Exception as e:
                    print(f"Error updating table row {row} for spot {spot_id}: {e}")
                    continue
            
            # Update statistics
            try:
                total_spots = len(spots)
                occupied_spots = sum(1 for spot in spots.values() if hasattr(spot, 'is_occupied') and spot.is_occupied)
                vacant_spots = total_spots - occupied_spots
                current_camera = self.spot_manager.get_current_camera_url()
                total_cameras = len(self.spot_manager.get_all_cameras())
                
                if not current_camera:
                    self.stats_label.setText(f"No camera connected\nTotal cameras with spots: {total_cameras}")
                elif total_spots == 0:
                    self.stats_label.setText(f"No parking spots defined for current camera\nCamera: {current_camera}\nTotal cameras: {total_cameras}")
                else:
                    stats_text = f"Current Camera: {current_camera}\n"
                    stats_text += f"Spots: {total_spots} | Vacant: {vacant_spots} | Occupied: {occupied_spots}\n"
                    stats_text += f"Total cameras with spots: {total_cameras}"
                    self.stats_label.setText(stats_text)
                    
            except Exception as e:
                print(f"Error updating statistics: {e}")
                self.stats_label.setText("Error updating statistics")
                
        except Exception as e:
            print(f"Error updating spots table: {e}")
            self.spots_table.setRowCount(0)
            self.stats_label.setText("Error loading parking spots")
    
    def on_spot_table_selection_changed(self):
        """Handle table selection change"""
        selected_rows = self.spots_table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            spot_id_item = self.spots_table.item(row, 0)
            if spot_id_item:
                spot_id = int(spot_id_item.text())
                self.spot_manager.select_spot(spot_id)
                self.edit_spot_btn.setEnabled(True)
                self.delete_spot_btn.setEnabled(True)
        else:
            self.spot_manager.deselect_all()
            self.edit_spot_btn.setEnabled(False)
            self.delete_spot_btn.setEnabled(False)
    
    def edit_selected_spot(self):
        """Edit the selected parking spot name"""
        selected_rows = self.spots_table.selectionModel().selectedRows()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        spot_id_item = self.spots_table.item(row, 0)
        if not spot_id_item:
            return
        
        spot_id = int(spot_id_item.text())
        spot = self.spot_manager.get_spot(spot_id)
        if not spot:
            return
        
        new_name, ok = QInputDialog.getText(self, "Edit Parking Spot", 
                                           "Enter new name:", text=spot.name)
        if ok and new_name.strip():
            self.spot_manager.update_spot(spot_id, name=new_name.strip())
            self.statusBar().showMessage(f"Parking spot renamed to '{new_name.strip()}'")
    
    def delete_selected_spot(self):
        """Delete the selected parking spot"""
        try:
            selected_rows = self.spots_table.selectionModel().selectedRows()
            if not selected_rows:
                return
            
            row = selected_rows[0].row()
            spot_id_item = self.spots_table.item(row, 0)
            spot_name_item = self.spots_table.item(row, 1)
            if not spot_id_item or not spot_name_item:
                return
            
            spot_id = int(spot_id_item.text())
            spot_name = spot_name_item.text()
            
            reply = QMessageBox.question(self, "Delete Parking Spot",
                                       f"Are you sure you want to delete '{spot_name}'?",
                                       QMessageBox.Yes | QMessageBox.No,
                                       QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                # Temporarily disable detection during deletion to prevent conflicts
                detection_was_enabled = False
                if hasattr(self, 'car_detection_manager') and self.car_detection_manager.is_enabled:
                    detection_was_enabled = True
                    self.car_detection_manager.set_enabled(False)
                    
                    # Wait for any running detection to complete
                    if self.car_detection_manager.detection_worker.isRunning():
                        self.car_detection_manager.detection_worker.wait(2000)  # Wait up to 2 seconds
                
                try:
                    # Clear table selection BEFORE deletion to prevent callbacks
                    self.spots_table.clearSelection()
                    self.edit_spot_btn.setEnabled(False)
                    self.delete_spot_btn.setEnabled(False)
                    
                    # Temporarily disconnect the spots_updated signal to prevent immediate callbacks
                    try:
                        self.spot_manager.spots_updated.disconnect(self.update_spots_table)
                        signal_was_connected = True
                    except:
                        signal_was_connected = False
                    
                    # Remove the spot
                    success = self.spot_manager.remove_spot(spot_id)
                    
                    # Reconnect the signal
                    if signal_was_connected:
                        self.spot_manager.spots_updated.connect(self.update_spots_table)
                    
                    if success:
                        self.statusBar().showMessage(f"Parking spot '{spot_name}' deleted")
                        
                        # Clear current detections to force refresh
                        if hasattr(self, 'car_detection_manager'):
                            self.car_detection_manager.current_detections.clear()
                        
                        # Manually update the table and display after a short delay
                        QTimer.singleShot(100, self.update_spots_table)
                        QTimer.singleShot(100, lambda: self.video_widget.update_display() if hasattr(self, 'video_widget') else None)
                    else:
                        QMessageBox.warning(self, "Delete Failed", f"Failed to delete parking spot '{spot_name}'")
                        
                except Exception as delete_error:
                    print(f"Error during spot deletion: {delete_error}")
                    # Reconnect signal if it was disconnected
                    try:
                        self.spot_manager.spots_updated.connect(self.update_spots_table)
                    except:
                        pass
                    raise delete_error
                        
                finally:
                    # Re-enable detection after a delay to ensure everything is settled
                    if detection_was_enabled and hasattr(self, 'car_detection_manager'):
                        QTimer.singleShot(200, lambda: self.car_detection_manager.set_enabled(True))
                        
        except Exception as e:
            print(f"Error deleting parking spot: {e}")
            QMessageBox.critical(self, "Error", f"Failed to delete parking spot: {str(e)}")
            # Make sure to re-enable detection even if there was an error
            if hasattr(self, 'car_detection_manager'):
                if hasattr(self, 'detection_enabled_checkbox') and self.detection_enabled_checkbox.isChecked():
                    QTimer.singleShot(500, lambda: self.car_detection_manager.set_enabled(True))
    
    def clear_all_spots(self):
        """Clear all parking spots"""
        try:
            spots = self.spot_manager.get_all_spots()
            if not spots:
                QMessageBox.information(self, "No Spots", "There are no parking spots to clear.")
                return
            
            reply = QMessageBox.question(self, "Clear All Spots",
                                       f"Are you sure you want to delete all {len(spots)} parking spots?",
                                       QMessageBox.Yes | QMessageBox.No,
                                       QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                # Temporarily disable detection during clearing to prevent conflicts
                detection_was_enabled = False
                if hasattr(self, 'car_detection_manager') and self.car_detection_manager.is_enabled:
                    detection_was_enabled = True
                    self.car_detection_manager.set_enabled(False)
                
                try:
                    # Clear all spots
                    self.spot_manager.clear_all_spots()
                    self.statusBar().showMessage("All parking spots cleared")
                    
                    # Clear table selection
                    self.spots_table.clearSelection()
                    self.edit_spot_btn.setEnabled(False)
                    self.delete_spot_btn.setEnabled(False)
                    
                    # Force update the display
                    if hasattr(self, 'video_widget'):
                        self.video_widget.update_display()
                        
                finally:
                    # Re-enable detection if it was enabled before
                    if detection_was_enabled and hasattr(self, 'car_detection_manager'):
                        self.car_detection_manager.set_enabled(True)
                        
        except Exception as e:
            print(f"Error clearing parking spots: {e}")
            QMessageBox.critical(self, "Error", f"Failed to clear parking spots: {str(e)}")
            # Make sure to re-enable detection even if there was an error
            if hasattr(self, 'car_detection_manager'):
                if hasattr(self, 'detection_enabled_checkbox') and self.detection_enabled_checkbox.isChecked():
                    self.car_detection_manager.set_enabled(True)
    
    def initialize_detection_system(self):
        """Initialize the vehicle detection system"""
        if self.car_detection_manager.initialize():
            self.model_status_label.setText("Model Status: Loaded Successfully")
            self.model_status_label.setStyleSheet("color: #27ae60; font-weight: bold;")
            # Set reference to spot manager
            self.car_detection_manager.set_parking_spot_manager(self.spot_manager)
        else:
            self.model_status_label.setText("Model Status: Failed to Load")
            self.model_status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
            # Disable detection controls if model failed to load
            if hasattr(self, 'detection_enabled_checkbox'):
                self.detection_enabled_checkbox.setEnabled(False)
    
    def on_detection_enabled_changed(self, enabled):
        """Handle detection enabled/disabled"""
        self.car_detection_manager.set_enabled(enabled)
        status = "Enabled" if enabled else "Disabled"
        self.statusBar().showMessage(f"Vehicle detection {status.lower()}")
    
    def on_confidence_changed(self, value):
        """Handle confidence threshold change"""
        confidence = value / 100.0
        self.confidence_label.setText(f"{confidence:.2f}")
        self.car_detection_manager.set_confidence_threshold(confidence)
    
    def on_interval_changed(self, value):
        """Handle detection interval change"""
        self.car_detection_manager.set_detection_interval(value)
    
    def on_overlap_changed(self, value):
        """Handle overlap threshold change"""
        overlap = value / 100.0
        self.overlap_label.setText(f"{overlap:.2f}")
        self.car_detection_manager.set_overlap_threshold(overlap)
    
    @pyqtSlot(list)
    def on_detections_updated(self, detections):
        """Handle updated vehicle detections"""
        stats = self.car_detection_manager.get_detection_stats()
        self.current_cars_label.setText(f"Current Vehicles: {stats['current_vehicles']}")
        self.total_detections_label.setText(f"Total Detections: {stats['total_detections']}")
        self.detection_fps_label.setText(f"Detection FPS: {stats['detection_fps']}")
    
    @pyqtSlot(dict)
    def on_occupancy_updated(self, occupancy_status):
        """Handle parking spot occupancy updates"""
        try:
            # Update the spots table to reflect occupancy changes
            self.update_spots_table()
            
            # Count occupied and vacant spots
            if occupancy_status:
                occupied_count = sum(1 for occupied in occupancy_status.values() if occupied)
                vacant_count = len(occupancy_status) - occupied_count
                
                self.statusBar().showMessage(f"Parking: {occupied_count} occupied, {vacant_count} vacant")
            else:
                self.statusBar().showMessage("No parking spots defined")
                
        except Exception as e:
            print(f"Error handling occupancy update: {e}")
            self.statusBar().showMessage("Error updating occupancy status")
    
    def closeEvent(self, event):
        """Handle application close event"""
        try:
            # Disable vehicle detection first
            if hasattr(self, 'car_detection_manager'):
                self.car_detection_manager.set_enabled(False)
                # Wait for detection worker to finish
                if hasattr(self.car_detection_manager, 'detection_worker'):
                    self.car_detection_manager.detection_worker.wait(2000)  # Wait up to 2 seconds
            
            # Disconnect camera
            self.camera_manager.disconnect_camera()
            
        except Exception as e:
            print(f"Error during application shutdown: {e}")
        finally:
            event.accept() 