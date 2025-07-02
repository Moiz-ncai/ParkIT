import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QPushButton, QFrame, QTextEdit,
                            QGridLayout, QGroupBox, QSizePolicy, QSplitter,
                            QListWidget, QListWidgetItem, QMessageBox, QInputDialog,
                            QCheckBox, QTabWidget, QTableWidget, QTableWidgetItem,
                            QHeaderView)
from PyQt5.QtCore import Qt, pyqtSlot, QTimer
from PyQt5.QtGui import QPixmap, QImage, QFont, QPalette, QColor
import cv2
import numpy as np
from camera_manager import CameraManager
from parking_spot_manager import ParkingSpotManager
from gui.interactive_video_widget import InteractiveVideoWidget





class MainWindow(QMainWindow):
    """Main application window for ParkIT"""
    
    def __init__(self):
        super().__init__()
        self.camera_manager = CameraManager()
        self.spot_manager = ParkingSpotManager()
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
        
        # Interactive video widget
        self.video_widget = InteractiveVideoWidget()
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
PHASE 2: Parking Spot Setup

1. CAMERA SETUP:
   - Enter RTSP URL: rtsp://user:pass@ip:port/stream
   - Or use '0' for webcam testing
   - Click 'Connect' to start video feed

2. DRAWING PARKING SPOTS:
   - Click 'Draw New Spot' button
   - Left-click on video to add polygon points
   - Right-click to finish the polygon
   - Enter a name for the parking spot

3. MANAGING SPOTS:
   - View all spots in the 'Parking Spots' tab
   - Click on spots in video to select them
   - Edit names or delete spots as needed
   - Toggle spot visibility with checkbox

4. KEYBOARD SHORTCUTS:
   - ESC: Cancel current drawing operation

COMING IN PHASE 3:
- YOLOv11 car detection
- License plate recognition
- OCR for license plate reading
- Real-time occupancy monitoring

TIPS:
- Draw spots around actual parking areas
- Use clear, descriptive names
- Test with webcam before using IP cameras
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
        
        # Video widget signals
        self.video_widget.polygon_completed.connect(self.on_polygon_completed)
        self.video_widget.spot_clicked.connect(self.on_spot_clicked)
        
        # Enter key in RTSP input triggers connect
        self.rtsp_input.returnPressed.connect(self.connect_camera)
    
    @pyqtSlot(np.ndarray)
    def update_frame(self, frame):
        """Update the video display with new frame"""
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
            self.draw_spot_btn.setEnabled(False)
            self.cancel_draw_btn.setEnabled(False)
            self.camera_info.setText("No camera connected")
            
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
    
    def update_spots_table(self):
        """Update the parking spots table"""
        spots = self.spot_manager.get_all_spots()
        self.spots_table.setRowCount(len(spots))
        
        for row, (spot_id, spot) in enumerate(spots.items()):
            # ID
            self.spots_table.setItem(row, 0, QTableWidgetItem(str(spot_id)))
            
            # Name
            self.spots_table.setItem(row, 1, QTableWidgetItem(spot.name))
            
            # Status
            status = "Occupied" if spot.is_occupied else "Vacant"
            status_item = QTableWidgetItem(status)
            if spot.is_occupied:
                status_item.setBackground(QColor(255, 200, 200))  # Light red
            else:
                status_item.setBackground(QColor(200, 255, 200))  # Light green
            self.spots_table.setItem(row, 2, status_item)
            
            # Points count
            self.spots_table.setItem(row, 3, QTableWidgetItem(f"{len(spot.polygon_points)} points"))
        
        # Update statistics
        total_spots = len(spots)
        occupied_spots = sum(1 for spot in spots.values() if spot.is_occupied)
        vacant_spots = total_spots - occupied_spots
        
        if total_spots == 0:
            self.stats_label.setText("No parking spots defined")
        else:
            self.stats_label.setText(f"Total: {total_spots} | Vacant: {vacant_spots} | Occupied: {occupied_spots}")
    
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
            self.spot_manager.remove_spot(spot_id)
            self.statusBar().showMessage(f"Parking spot '{spot_name}' deleted")
    
    def clear_all_spots(self):
        """Clear all parking spots"""
        spots = self.spot_manager.get_all_spots()
        if not spots:
            QMessageBox.information(self, "No Spots", "There are no parking spots to clear.")
            return
        
        reply = QMessageBox.question(self, "Clear All Spots",
                                   f"Are you sure you want to delete all {len(spots)} parking spots?",
                                   QMessageBox.Yes | QMessageBox.No,
                                   QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.spot_manager.clear_all_spots()
            self.statusBar().showMessage("All parking spots cleared")
    
    def closeEvent(self, event):
        """Handle application close event"""
        self.camera_manager.disconnect_camera()
        event.accept() 