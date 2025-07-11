"""
ParkIT Detection Service - Main Service
Orchestrates vehicle detection, parking spot analysis, and backend communication
"""

import os
import time
import threading
import logging
import cv2
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json

from vehicle_detector import VehicleDetector, VehicleDetection
from api_client import APIClientManager


class CameraStream:
    """Manages a single camera stream"""
    
    def __init__(self, camera_id: str, rtsp_url: str, plaza_id: int):
        self.camera_id = camera_id
        self.rtsp_url = rtsp_url
        self.plaza_id = plaza_id
        self.cap = None
        self.is_connected = False
        self.last_frame = None
        self.frame_count = 0
        self.connection_attempts = 0
        self.max_connection_attempts = 5
        
    def connect(self) -> bool:
        """Connect to camera stream"""
        try:
            if self.cap is not None:
                self.cap.release()
            
            # Try to connect to camera
            self.cap = cv2.VideoCapture(self.rtsp_url)
            
            if self.cap.isOpened():
                # Test read a frame
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    self.is_connected = True
                    self.connection_attempts = 0
                    logging.info(f"✅ Camera {self.camera_id} connected successfully")
                    return True
            
            self.is_connected = False
            self.connection_attempts += 1
            logging.warning(f"❌ Failed to connect to camera {self.camera_id} (attempt {self.connection_attempts})")
            return False
            
        except Exception as e:
            logging.error(f"Error connecting to camera {self.camera_id}: {e}")
            self.is_connected = False
            self.connection_attempts += 1
            return False
    
    def read_frame(self) -> Optional[np.ndarray]:
        """Read a frame from the camera"""
        if not self.is_connected or self.cap is None:
            return None
        
        try:
            ret, frame = self.cap.read()
            if ret and frame is not None:
                self.last_frame = frame.copy()
                self.frame_count += 1
                return frame
            else:
                logging.warning(f"Failed to read frame from camera {self.camera_id}")
                self.is_connected = False
                return None
                
        except Exception as e:
            logging.error(f"Error reading frame from camera {self.camera_id}: {e}")
            self.is_connected = False
            return None
    
    def disconnect(self):
        """Disconnect from camera"""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.is_connected = False
        logging.info(f"Camera {self.camera_id} disconnected")


class PlazaDetectionProcessor:
    """Processes detection for a single plaza"""
    
    def __init__(self, plaza_id: int, plaza_data: Dict, detector: VehicleDetector, api_client: APIClientManager):
        self.plaza_id = plaza_id
        self.plaza_data = plaza_data
        self.detector = detector
        self.api_client = api_client
        
        # Create mock parking spots for testing (would normally come from API)
        self.parking_spots = self._create_mock_parking_spots()
        
        # Processing state
        self.last_occupancy = {}
        self.processing_enabled = True
        self.detection_interval = 2.0  # Process every 2 seconds
        self.last_detection_time = 0
        
        logging.info(f"Plaza {plaza_id} processor initialized with {len(self.parking_spots)} parking spots")
    
    def _create_mock_parking_spots(self) -> List[Dict]:
        """Create mock parking spots for testing (replace with real API call)"""
        spots = []
        plaza_name = self.plaza_data.get('name', 'Unknown Plaza')
        total_spots = self.plaza_data.get('total_spots', 50)
        
        # Create mock polygon coordinates for spots
        # In a real implementation, these would come from the plaza configuration
        for i in range(1, min(total_spots + 1, 21)):  # Limit to 20 spots for testing
            # Create a mock rectangular parking spot
            x_offset = (i % 5) * 120  # 5 spots per row
            y_offset = (i // 5) * 80   # Rows of spots
            
            spot = {
                'id': i,
                'spot_id': str(i),
                'spot_number': f"{plaza_name[:1]}{i:03d}",
                'plaza_id': self.plaza_id,
                'polygon_coordinates': [
                    {'x': x_offset, 'y': y_offset},
                    {'x': x_offset + 100, 'y': y_offset},
                    {'x': x_offset + 100, 'y': y_offset + 60},
                    {'x': x_offset, 'y': y_offset + 60}
                ]
            }
            spots.append(spot)
        
        return spots
    
    def process_frame(self, frame: np.ndarray, camera_id: str) -> Dict:
        """Process a frame for vehicle detection and occupancy analysis"""
        if not self.processing_enabled:
            return {}
        
        current_time = time.time()
        if current_time - self.last_detection_time < self.detection_interval:
            return {}
        
        try:
            # Run vehicle detection
            detections, annotated_frame = self.detector.detect_vehicles(frame)
            
            # Analyze parking spot occupancy
            occupancy_status = self.detector.analyze_parking_spot_occupancy(detections, self.parking_spots)
            
            # Check for changes in occupancy
            changes = self._detect_occupancy_changes(occupancy_status)
            
            if changes:
                # Send updates to backend
                detection_data = [det.to_dict() for det in detections]
                success = self.api_client.send_occupancy_update(
                    self.plaza_id, occupancy_status, detection_data
                )
                
                if success:
                    logging.info(f"Plaza {self.plaza_id}: Sent occupancy update - {len(changes)} changes")
                    self.last_occupancy = occupancy_status.copy()
                else:
                    logging.warning(f"Plaza {self.plaza_id}: Failed to send occupancy update")
            
            self.last_detection_time = current_time
            
            # Return processing results
            return {
                'detections': len(detections),
                'occupancy_changes': len(changes),
                'total_spots': len(self.parking_spots),
                'occupied_spots': sum(1 for occupied in occupancy_status.values() if occupied),
                'available_spots': sum(1 for occupied in occupancy_status.values() if not occupied)
            }
            
        except Exception as e:
            logging.error(f"Error processing frame for plaza {self.plaza_id}: {e}")
            return {}
    
    def _detect_occupancy_changes(self, current_occupancy: Dict[str, bool]) -> Dict[str, bool]:
        """Detect changes in occupancy status"""
        changes = {}
        
        for spot_id, is_occupied in current_occupancy.items():
            previous_status = self.last_occupancy.get(spot_id)
            if previous_status is None or previous_status != is_occupied:
                changes[spot_id] = is_occupied
        
        return changes


class DetectionService:
    """Main detection service orchestrating all components"""
    
    def __init__(self, config_file: str = None):
        # Initialize logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('detection_service.log'),
                logging.StreamHandler()
            ]
        )
        
        # Initialize components
        self.detector = VehicleDetector(confidence_threshold=0.5)
        self.api_client = APIClientManager()
        
        # Service state
        self.cameras: Dict[str, CameraStream] = {}
        self.plaza_processors: Dict[int, PlazaDetectionProcessor] = {}
        self.processing_threads: Dict[str, threading.Thread] = {}
        self.running = False
        
        # Statistics
        self.stats = {
            'service_start_time': time.time(),
            'total_frames_processed': 0,
            'total_detections': 0,
            'total_occupancy_updates': 0
        }
        
        logging.info("Detection Service initialized")
    
    def initialize(self) -> bool:
        """Initialize the detection service"""
        try:
            # Initialize vehicle detector
            if not self.detector.initialize_model():
                logging.error("Failed to initialize vehicle detection model")
                return False
            
            # Get plazas from backend
            plazas = self.api_client.get_plazas()
            if not plazas:
                logging.warning("No plazas found in backend - creating test plaza")
                # For testing, we'll continue with mock data
                plazas = [
                    {
                        'id': 1,
                        'name': 'Test Plaza',
                        'address': 'Test Address',
                        'total_spots': 150,
                        'available_spots': 23
                    }
                ]
            
            # Initialize plaza processors
            for plaza in plazas:
                plaza_id = plaza['id']
                processor = PlazaDetectionProcessor(plaza_id, plaza, self.detector, self.api_client)
                self.plaza_processors[plaza_id] = processor
                logging.info(f"Initialized processor for plaza {plaza_id}: {plaza['name']}")
            
            # For testing, add a mock camera (would normally come from plaza configuration)
            self._add_test_camera()
            
            logging.info("Detection service initialization completed")
            return True
            
        except Exception as e:
            logging.error(f"Failed to initialize detection service: {e}")
            return False
    
    def _add_test_camera(self):
        """Add a test camera for demonstration (replace with real camera configuration)"""
        # For testing, we'll use camera index 0 (webcam) if available
        # In production, this would come from the plaza camera configuration
        camera_id = "test_camera_1"
        rtsp_url = 0  # Use default camera (webcam)
        plaza_id = 1
        
        camera = CameraStream(camera_id, rtsp_url, plaza_id)
        self.cameras[camera_id] = camera
        
        logging.info(f"Added test camera {camera_id} for plaza {plaza_id}")
    
    def start(self):
        """Start the detection service"""
        if self.running:
            logging.warning("Detection service is already running")
            return
        
        self.running = True
        logging.info("Starting detection service...")
        
        # Connect to cameras
        for camera_id, camera in self.cameras.items():
            if camera.connect():
                # Start processing thread for this camera
                thread = threading.Thread(
                    target=self._camera_processing_loop,
                    args=(camera_id,),
                    daemon=True
                )
                thread.start()
                self.processing_threads[camera_id] = thread
                logging.info(f"Started processing thread for camera {camera_id}")
            else:
                logging.error(f"Failed to connect to camera {camera_id}")
        
        # Start statistics reporting
        stats_thread = threading.Thread(target=self._stats_reporting_loop, daemon=True)
        stats_thread.start()
        
        logging.info("Detection service started successfully")
    
    def stop(self):
        """Stop the detection service"""
        if not self.running:
            return
        
        logging.info("Stopping detection service...")
        self.running = False
        
        # Disconnect cameras
        for camera in self.cameras.values():
            camera.disconnect()
        
        # Wait for threads to finish (with timeout)
        for thread in self.processing_threads.values():
            thread.join(timeout=5.0)
        
        logging.info("Detection service stopped")
    
    def _camera_processing_loop(self, camera_id: str):
        """Main processing loop for a camera"""
        camera = self.cameras[camera_id]
        
        while self.running and camera_id in self.cameras:
            try:
                if not camera.is_connected:
                    # Try to reconnect
                    if camera.connection_attempts < camera.max_connection_attempts:
                        camera.connect()
                        time.sleep(5)  # Wait before next attempt
                    else:
                        logging.error(f"Camera {camera_id} exceeded max connection attempts")
                        break
                    continue
                
                # Read frame
                frame = camera.read_frame()
                if frame is None:
                    time.sleep(0.1)
                    continue
                
                # Process frame with appropriate plaza processor
                processor = self.plaza_processors.get(camera.plaza_id)
                if processor:
                    results = processor.process_frame(frame, camera_id)
                    
                    if results:
                        self.stats['total_frames_processed'] += 1
                        self.stats['total_detections'] += results.get('detections', 0)
                        if results.get('occupancy_changes', 0) > 0:
                            self.stats['total_occupancy_updates'] += 1
                
                # Control processing rate
                time.sleep(0.1)  # 10 FPS max
                
            except Exception as e:
                logging.error(f"Error in camera {camera_id} processing loop: {e}")
                time.sleep(1)
        
        logging.info(f"Camera {camera_id} processing loop ended")
    
    def _stats_reporting_loop(self):
        """Report statistics periodically"""
        while self.running:
            try:
                # Wait for reporting interval
                time.sleep(60)  # Report every minute
                
                if not self.running:
                    break
                
                # Calculate runtime
                runtime = time.time() - self.stats['service_start_time']
                
                # Get detector stats
                detector_stats = self.detector.get_detection_stats()
                
                # Combine stats
                combined_stats = {
                    **self.stats,
                    **detector_stats,
                    'runtime_seconds': runtime,
                    'active_cameras': len([c for c in self.cameras.values() if c.is_connected]),
                    'total_cameras': len(self.cameras),
                    'active_plazas': len(self.plaza_processors)
                }
                
                # Send stats to backend
                self.api_client.client.send_detection_stats(combined_stats)
                
                # Log summary
                logging.info(f"📊 Service Stats - Runtime: {runtime:.0f}s, "
                           f"Frames: {self.stats['total_frames_processed']}, "
                           f"Detections: {self.stats['total_detections']}, "
                           f"Updates: {self.stats['total_occupancy_updates']}")
                
            except Exception as e:
                logging.error(f"Error in stats reporting: {e}")
    
    def get_status(self) -> Dict:
        """Get current service status"""
        runtime = time.time() - self.stats['service_start_time']
        
        return {
            'running': self.running,
            'runtime_seconds': runtime,
            'cameras': {
                camera_id: {
                    'connected': camera.is_connected,
                    'plaza_id': camera.plaza_id,
                    'frame_count': camera.frame_count
                }
                for camera_id, camera in self.cameras.items()
            },
            'plazas': {
                plaza_id: {
                    'name': processor.plaza_data.get('name', 'Unknown'),
                    'parking_spots': len(processor.parking_spots)
                }
                for plaza_id, processor in self.plaza_processors.items()
            },
            'stats': self.stats
        }


def main():
    """Main entry point for the detection service"""
    print("🚀 Starting ParkIT Detection Service...")
    
    service = DetectionService()
    
    try:
        # Initialize service
        if not service.initialize():
            print("❌ Failed to initialize detection service")
            return
        
        # Start service
        service.start()
        
        print("✅ Detection service started successfully!")
        print("Press Ctrl+C to stop the service")
        
        # Keep running until interrupted
        while service.running:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Shutting down detection service...")
                break
    
    except Exception as e:
        print(f"❌ Error running detection service: {e}")
    
    finally:
        service.stop()
        print("✅ Detection service stopped")


if __name__ == "__main__":
    main() 