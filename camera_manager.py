import cv2
import threading
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
import numpy as np


class CameraManager(QObject):
    """Manages camera connections and video capture from RTSP streams"""
    
    frame_ready = pyqtSignal(np.ndarray)
    connection_status_changed = pyqtSignal(bool, str)  # connected, message
    
    def __init__(self):
        super().__init__()
        self.cap = None
        self.is_connected = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.capture_frame)
        self.current_url = ""
    
    def connect_camera(self, rtsp_url):
        """Connect to RTSP camera stream"""
        try:
            # Release previous connection if exists
            self.disconnect_camera()
            
            # Try to connect to the camera
            self.cap = cv2.VideoCapture(rtsp_url)
            
            # Set buffer size to reduce latency
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            # Test if connection is successful
            ret, frame = self.cap.read()
            if ret and frame is not None:
                self.is_connected = True
                self.current_url = rtsp_url
                self.timer.start(30)  # 30ms interval for ~33 FPS
                self.connection_status_changed.emit(True, f"Connected to {rtsp_url}")
                return True
            else:
                self.disconnect_camera()
                self.connection_status_changed.emit(False, "Failed to read from camera")
                return False
                
        except Exception as e:
            self.disconnect_camera()
            self.connection_status_changed.emit(False, f"Connection error: {str(e)}")
            return False
    
    def disconnect_camera(self):
        """Disconnect from camera stream"""
        self.timer.stop()
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.is_connected = False
        self.current_url = ""
        self.connection_status_changed.emit(False, "Disconnected")
    
    def capture_frame(self):
        """Capture and emit a frame from the camera"""
        if self.cap is not None and self.is_connected:
            ret, frame = self.cap.read()
            if ret and frame is not None:
                self.frame_ready.emit(frame)
            else:
                # Connection lost
                self.disconnect_camera()
    
    def get_frame_size(self):
        """Get the frame dimensions"""
        if self.cap is not None:
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            return width, height
        return None, None 