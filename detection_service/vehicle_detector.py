"""
Standalone Vehicle Detection Module for ParkIT Platform
Extracted from car_detection_manager.py and adapted for microservice architecture
"""

import os
import time
import cv2
import numpy as np
from typing import List, Tuple, Dict, Optional
import logging

# Check if YOLO is available
YOLO_AVAILABLE = True
try:
    from ultralytics import YOLO
except ImportError:
    YOLO_AVAILABLE = False
    logging.warning("ultralytics not available. Vehicle detection will be disabled.")


class VehicleDetection:
    """Represents a detected vehicle (renamed from CarDetection)"""
    
    def __init__(self, bbox: Tuple[int, int, int, int], confidence: float, center_point: Tuple[int, int], vehicle_type: str = "Vehicle"):
        self.bbox = bbox  # (x1, y1, x2, y2)
        self.confidence = confidence
        self.center_point = center_point  # (x, y)
        self.vehicle_type = vehicle_type  # Type of vehicle (Car, Truck, etc.)
        self.area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "bbox": self.bbox,
            "confidence": self.confidence,
            "center_point": self.center_point,
            "vehicle_type": self.vehicle_type,
            "area": self.area
        }


class VehicleDetector:
    """Standalone vehicle detector without GUI dependencies"""
    
    def __init__(self, confidence_threshold: float = 0.5):
        self.model = None
        self.confidence_threshold = confidence_threshold
        self.overlap_threshold = 0.3  # Minimum overlap to consider spot occupied
        
        # COCO vehicle class mapping
        self.VEHICLE_CLASSES = {
            2: 'Car',
            3: 'Motorcycle', 
            5: 'Bus',
            6: 'Train',
            7: 'Truck'
        }
        
        # Detection statistics
        self.total_detections = 0
        self.detection_fps = 0
        self.last_fps_time = time.time()
        self.fps_counter = 0
        
        logging.info("VehicleDetector initialized")
    
    def initialize_model(self) -> bool:
        """Initialize the YOLOv11 model"""
        if not YOLO_AVAILABLE:
            logging.error("YOLO not available - cannot initialize model")
            return False
        
        try:
            # Load standard YOLOv11 model (will download if not present)
            logging.info("Loading YOLOv11 model...")
            self.model = YOLO('yolo11s.pt')
            logging.info("✅ YOLOv11 model loaded successfully")
            return True
            
        except Exception as e:
            logging.error(f"❌ Error loading YOLOv11 model: {e}")
            return False
    
    def set_confidence_threshold(self, threshold: float):
        """Set the confidence threshold for detections"""
        self.confidence_threshold = threshold
        logging.info(f"Confidence threshold set to {threshold}")
    
    def set_overlap_threshold(self, threshold: float):
        """Set the overlap threshold for spot occupancy"""
        self.overlap_threshold = threshold
        logging.info(f"Overlap threshold set to {threshold}")
    
    def detect_vehicles(self, frame: np.ndarray) -> Tuple[List[VehicleDetection], np.ndarray]:
        """
        Detect vehicles in a frame
        Returns: (detections, annotated_frame)
        """
        if self.model is None:
            logging.warning("Model not initialized")
            return [], frame
        
        if frame.size == 0:
            logging.warning("Empty frame provided")
            return [], frame
        
        try:
            # Run inference
            results = self.model(frame, conf=self.confidence_threshold, verbose=False)
            
            # Extract vehicle detections
            vehicle_detections = []
            annotated_frame = frame.copy()
            
            for result in results:
                if result is None:
                    continue
                    
                boxes = result.boxes
                if boxes is not None and len(boxes) > 0:
                    for box in boxes:
                        try:
                            # Check if detection is a vehicle
                            class_id = int(box.cls[0])
                            if class_id in self.VEHICLE_CLASSES:
                                # Get bounding box coordinates
                                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                                confidence = float(box.conf[0])
                                
                                # Validate bounding box
                                if x2 <= x1 or y2 <= y1 or x1 < 0 or y1 < 0:
                                    continue
                                
                                # Calculate center point (ensure integer values)
                                center_x = int((x1 + x2) // 2)
                                center_y = int((y1 + y2) // 2)
                                
                                # Create detection object
                                vehicle_type = self.VEHICLE_CLASSES[class_id]
                                detection = VehicleDetection(
                                    bbox=(x1, y1, x2, y2),
                                    confidence=confidence,
                                    center_point=(center_x, center_y),
                                    vehicle_type=vehicle_type
                                )
                                vehicle_detections.append(detection)
                                
                                # Draw detection on frame
                                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                                cv2.putText(annotated_frame, f'{vehicle_type}: {confidence:.2f}', 
                                          (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                                          
                        except Exception as e:
                            logging.error(f"Error processing detection box: {e}")
                            continue
            
            # Update statistics
            self.total_detections += len(vehicle_detections)
            self._update_fps_stats()
            
            logging.debug(f"Detected {len(vehicle_detections)} vehicles")
            return vehicle_detections, annotated_frame
            
        except Exception as e:
            logging.error(f"Error during vehicle detection: {e}")
            return [], frame
    
    def analyze_parking_spot_occupancy(self, detections: List[VehicleDetection], parking_spots: List[Dict]) -> Dict[str, bool]:
        """
        Analyze which parking spots are occupied based on vehicle detections
        
        Args:
            detections: List of vehicle detections
            parking_spots: List of parking spot definitions with polygon coordinates
            
        Returns:
            Dictionary mapping spot_id to occupancy status (bool)
        """
        occupancy_status = {}
        
        for spot in parking_spots:
            spot_id = spot.get('spot_id') or spot.get('id')
            polygon_coords = spot.get('polygon_coordinates', [])
            
            if not polygon_coords or not spot_id:
                continue
            
            # Convert polygon coordinates to numpy array
            try:
                if isinstance(polygon_coords[0], dict):
                    # Format: [{"x": 100, "y": 200}, ...]
                    polygon = np.array([(point['x'], point['y']) for point in polygon_coords], dtype=np.int32)
                else:
                    # Format: [[100, 200], [150, 250], ...]
                    polygon = np.array(polygon_coords, dtype=np.int32)
                
                # Check if any vehicle detection overlaps with this spot
                is_occupied = self._is_spot_occupied_by_detections(detections, polygon)
                occupancy_status[spot_id] = is_occupied
                
            except Exception as e:
                logging.error(f"Error analyzing spot {spot_id}: {e}")
                occupancy_status[spot_id] = False
        
        return occupancy_status
    
    def _is_spot_occupied_by_detections(self, detections: List[VehicleDetection], polygon: np.ndarray) -> bool:
        """Check if a parking spot is occupied by any vehicle detection"""
        for detection in detections:
            # Check if vehicle center point is inside the parking spot polygon
            center_point = (float(detection.center_point[0]), float(detection.center_point[1]))
            if cv2.pointPolygonTest(polygon, center_point, False) >= 0:
                return True
            
            # Also check bounding box overlap with polygon for more robust detection
            bbox_overlap = self._calculate_bbox_polygon_overlap(detection.bbox, polygon)
            if bbox_overlap >= self.overlap_threshold:
                return True
        
        return False
    
    def _calculate_bbox_polygon_overlap(self, bbox: Tuple[int, int, int, int], polygon: np.ndarray) -> float:
        """Calculate overlap percentage between bounding box and polygon"""
        try:
            x1, y1, x2, y2 = bbox
            
            # Create mask for the bounding box
            bbox_mask = np.zeros((y2 - y1, x2 - x1), dtype=np.uint8)
            bbox_mask.fill(255)
            
            # Create mask for the polygon (adjust coordinates relative to bbox)
            polygon_adjusted = polygon.copy()
            polygon_adjusted[:, 0] -= x1
            polygon_adjusted[:, 1] -= y1
            
            polygon_mask = np.zeros((y2 - y1, x2 - x1), dtype=np.uint8)
            cv2.fillPoly(polygon_mask, [polygon_adjusted], 255)
            
            # Calculate intersection
            intersection = cv2.bitwise_and(bbox_mask, polygon_mask)
            intersection_area = cv2.countNonZero(intersection)
            bbox_area = (x2 - x1) * (y2 - y1)
            
            if bbox_area == 0:
                return 0.0
            
            overlap_percentage = intersection_area / bbox_area
            return overlap_percentage
            
        except Exception as e:
            logging.error(f"Error calculating overlap: {e}")
            return 0.0
    
    def _update_fps_stats(self):
        """Update FPS statistics"""
        self.fps_counter += 1
        current_time = time.time()
        
        if current_time - self.last_fps_time >= 1.0:  # Update every second
            self.detection_fps = self.fps_counter
            self.fps_counter = 0
            self.last_fps_time = current_time
    
    def get_detection_stats(self) -> Dict:
        """Get detection statistics"""
        return {
            "total_detections": self.total_detections,
            "detection_fps": self.detection_fps,
            "confidence_threshold": self.confidence_threshold,
            "overlap_threshold": self.overlap_threshold,
            "model_loaded": self.model is not None
        }


# Utility functions for backward compatibility
def create_vehicle_detector(confidence_threshold: float = 0.5) -> VehicleDetector:
    """Create and initialize a vehicle detector"""
    detector = VehicleDetector(confidence_threshold)
    if detector.initialize_model():
        return detector
    else:
        raise RuntimeError("Failed to initialize vehicle detection model")


def test_detection():
    """Simple test function"""
    logging.basicConfig(level=logging.INFO)
    
    try:
        detector = create_vehicle_detector()
        logging.info("Vehicle detector created successfully!")
        
        # Test with a dummy frame
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        detections, annotated = detector.detect_vehicles(test_frame)
        logging.info(f"Test detection completed: {len(detections)} vehicles detected")
        
        return True
    except Exception as e:
        logging.error(f"Test failed: {e}")
        return False


if __name__ == "__main__":
    test_detection() 