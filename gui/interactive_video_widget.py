from PyQt5.QtWidgets import QLabel, QInputDialog, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal, QPoint
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QBrush, QPolygon
import cv2
import numpy as np
from typing import List, Tuple, Optional


class InteractiveVideoWidget(QLabel):
    """Interactive video widget that supports polygon drawing and spot selection"""
    
    # Signals
    polygon_completed = pyqtSignal(str, list)  # name, points
    spot_clicked = pyqtSignal(int)  # spot_id
    
    # Drawing modes
    MODE_VIEW = 0
    MODE_DRAW = 1
    
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
        self.setText("No Camera Connected\n\nConnect camera to start drawing parking spots")
        # Remove setScaledContents(True) to handle scaling manually
        
        # Drawing state
        self.drawing_mode = self.MODE_VIEW
        self.current_polygon_points: List[QPoint] = []
        self.is_drawing = False
        
        # Frame and scaling
        self.current_frame = None
        self.frame_with_spots = None
        self.scale_x = 1.0
        self.scale_y = 1.0
        
        # Display parameters for coordinate conversion
        self.frame_width = 0
        self.frame_height = 0
        self.display_width = 0
        self.display_height = 0
        self.display_offset_x = 0
        self.display_offset_y = 0
        
        # Parking spot manager reference (set from parent)
        self.spot_manager = None
        
        # Enable mouse tracking for hover effects
        self.setMouseTracking(True)
    
    def set_spot_manager(self, spot_manager):
        """Set the parking spot manager reference"""
        self.spot_manager = spot_manager
        if spot_manager:
            spot_manager.spots_updated.connect(self.update_display)
    
    def set_frame(self, frame: np.ndarray):
        """Set the current frame and update display"""
        self.current_frame = frame.copy()
        
        # Draw parking spots on frame if spot manager is available
        if self.spot_manager:
            self.frame_with_spots = self.spot_manager.draw_spots_on_frame(frame.copy())
        else:
            self.frame_with_spots = frame.copy()
        
        self.update_display()
    
    def update_display(self):
        """Update the display with current frame and overlays"""
        if self.frame_with_spots is None:
            return
        
        # Create display frame
        display_frame = self.frame_with_spots.copy()
        
        # Draw current polygon being drawn
        if self.drawing_mode == self.MODE_DRAW and len(self.current_polygon_points) > 0:
            self.draw_current_polygon(display_frame)
        
        # Convert to Qt format and display
        self.display_opencv_frame(display_frame)
    
    def display_opencv_frame(self, frame: np.ndarray):
        """Convert OpenCV frame to QPixmap and display"""
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        
        # Store original frame dimensions
        self.frame_width = w
        self.frame_height = h
        
        # Get widget size
        widget_width = self.width()
        widget_height = self.height()
        
        # Calculate scaled dimensions while maintaining aspect ratio
        frame_aspect = w / h
        widget_aspect = widget_width / widget_height
        
        if frame_aspect > widget_aspect:
            # Frame is wider than widget - fit to width
            self.display_width = widget_width
            self.display_height = int(widget_width / frame_aspect)
        else:
            # Frame is taller than widget - fit to height
            self.display_height = widget_height
            self.display_width = int(widget_height * frame_aspect)
        
        # Calculate offset to center the display area
        self.display_offset_x = (widget_width - self.display_width) // 2
        self.display_offset_y = (widget_height - self.display_height) // 2
        
        # Calculate scaling factors
        self.scale_x = w / self.display_width
        self.scale_y = h / self.display_height
        
        # Create and scale the pixmap
        pixmap = QPixmap.fromImage(qt_image)
        scaled_pixmap = pixmap.scaled(self.display_width, self.display_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        self.setPixmap(scaled_pixmap)
    
    def draw_current_polygon(self, frame: np.ndarray):
        """Draw the polygon currently being drawn"""
        if len(self.current_polygon_points) < 2:
            return
        
        # Convert QPoints to frame coordinates
        frame_points = []
        for qpoint in self.current_polygon_points:
            frame_x, frame_y = self.widget_to_frame_coords(qpoint)
            frame_points.append((frame_x, frame_y))
        
        # Draw lines between points
        for i in range(len(frame_points) - 1):
            cv2.line(frame, frame_points[i], frame_points[i + 1], (0, 255, 255), 2)
        
        # Draw points
        for point in frame_points:
            cv2.circle(frame, point, 5, (0, 255, 255), -1)
        
        # Draw line from last point to first point if we have enough points
        if len(frame_points) > 2:
            cv2.line(frame, frame_points[-1], frame_points[0], (0, 255, 255), 1)
    
    def widget_to_frame_coords(self, widget_point: QPoint) -> Tuple[int, int]:
        """Convert widget coordinates to frame coordinates"""
        # Check if we have valid display parameters
        if not hasattr(self, 'display_width') or not hasattr(self, 'frame_width'):
            return (0, 0)
        
        # Get click coordinates relative to widget
        click_x = widget_point.x()
        click_y = widget_point.y()
        
        # Check if click is within the displayed image area
        image_left = self.display_offset_x
        image_right = self.display_offset_x + self.display_width
        image_top = self.display_offset_y
        image_bottom = self.display_offset_y + self.display_height
        
        if click_x < image_left or click_x >= image_right or click_y < image_top or click_y >= image_bottom:
            # Click is outside the image area, clamp to nearest edge
            click_x = max(image_left, min(click_x, image_right - 1))
            click_y = max(image_top, min(click_y, image_bottom - 1))
        
        # Convert to coordinates within the displayed image (0 to display_width/height)
        image_x = click_x - self.display_offset_x
        image_y = click_y - self.display_offset_y
        
        # Scale to original frame coordinates
        frame_x = int(image_x * self.scale_x)
        frame_y = int(image_y * self.scale_y)
        
        # Ensure frame coordinates are within bounds
        frame_x = max(0, min(frame_x, self.frame_width - 1))
        frame_y = max(0, min(frame_y, self.frame_height - 1))
        
        return (frame_x, frame_y)
    
    def start_drawing_mode(self):
        """Start polygon drawing mode"""
        self.drawing_mode = self.MODE_DRAW
        self.current_polygon_points.clear()
        self.is_drawing = True
        self.setCursor(Qt.CrossCursor)
        
        # Debug info in tooltip
        debug_info = f"Drawing mode active. "
        if hasattr(self, 'frame_width') and self.frame_width > 0:
            debug_info += f"Frame: {self.frame_width}x{self.frame_height}, "
            debug_info += f"Display: {self.display_width}x{self.display_height}, "
            debug_info += f"Scale: {self.scale_x:.2f}x{self.scale_y:.2f}, "
            debug_info += f"Offset: ({self.display_offset_x}, {self.display_offset_y})"
        
        self.setToolTip(debug_info + "\nLeft-click to add points, Right-click to finish.")
    
    def stop_drawing_mode(self):
        """Stop polygon drawing mode"""
        self.drawing_mode = self.MODE_VIEW
        self.current_polygon_points.clear()
        self.is_drawing = False
        self.setCursor(Qt.ArrowCursor)
        self.setToolTip("")
        self.update_display()
    
    def mousePressEvent(self, event):
        """Handle mouse press events"""
        if not self.current_frame is None:
            click_point = event.pos()
            frame_x, frame_y = self.widget_to_frame_coords(click_point)
            
            # Debug: Update tooltip with coordinate information
            if hasattr(self, 'display_width'):
                image_x = click_point.x() - self.display_offset_x
                image_y = click_point.y() - self.display_offset_y
                self.setToolTip(f"Widget: ({click_point.x()}, {click_point.y()}) -> Image: ({image_x}, {image_y}) -> Frame: ({frame_x}, {frame_y})\n"
                               f"Display area: {self.display_width}x{self.display_height} at offset ({self.display_offset_x}, {self.display_offset_y})")
            else:
                self.setToolTip(f"Widget: ({click_point.x()}, {click_point.y()}) -> Frame: ({frame_x}, {frame_y})")
            
            if self.drawing_mode == self.MODE_DRAW:
                if event.button() == Qt.LeftButton:
                    # Add point to current polygon
                    self.current_polygon_points.append(click_point)
                    self.update_display()
                
                elif event.button() == Qt.RightButton:
                    # Finish polygon
                    self.finish_polygon()
            
            elif self.drawing_mode == self.MODE_VIEW:
                if event.button() == Qt.LeftButton:
                    # Check if clicked on existing parking spot
                    if self.spot_manager:
                        spot_id = self.spot_manager.get_spot_at_point((frame_x, frame_y))
                        if spot_id != -1:
                            self.spot_clicked.emit(spot_id)
        
        super().mousePressEvent(event)
    
    def finish_polygon(self):
        """Finish drawing the current polygon"""
        if len(self.current_polygon_points) < 3:
            QMessageBox.warning(self, "Invalid Polygon", 
                              "A parking spot must have at least 3 points.")
            return
        
        # Get spot name from user
        name, ok = QInputDialog.getText(self, "Parking Spot Name", 
                                       "Enter name for this parking spot:",
                                       text=f"Spot {len(self.spot_manager.get_all_spots()) + 1 if self.spot_manager else 1}")
        
        if ok and name.strip():
            # Convert widget coordinates to frame coordinates
            frame_points = []
            for qpoint in self.current_polygon_points:
                frame_x, frame_y = self.widget_to_frame_coords(qpoint)
                frame_points.append((frame_x, frame_y))
            
            # Emit signal to create parking spot
            self.polygon_completed.emit(name.strip(), frame_points)
            
            # Reset drawing state
            self.stop_drawing_mode()
        else:
            # User cancelled, continue drawing
            pass
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key_Escape:
            if self.drawing_mode == self.MODE_DRAW:
                self.stop_drawing_mode()
        
        super().keyPressEvent(event)
    
    def clear_display(self):
        """Clear the video display"""
        self.current_frame = None
        self.frame_with_spots = None
        
        # Reset display parameters
        self.frame_width = 0
        self.frame_height = 0
        self.display_width = 0
        self.display_height = 0
        self.display_offset_x = 0
        self.display_offset_y = 0
        self.scale_x = 1.0
        self.scale_y = 1.0
        
        self.clear()
        self.setText("No Camera Connected\n\nConnect camera to start drawing parking spots") 