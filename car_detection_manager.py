import cv2
import numpy as np
from typing import List, Tuple, Dict, Optional
from PyQt5.QtCore import QObject, pyqtSignal, QTimer, QThread, pyqtSlot
import time

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("Warning: ultralytics not available. Car detection will be disabled.")


class CarDetection:
    """Represents a detected car"""
    
    def __init__(self, bbox: Tuple[int, int, int, int], confidence: float, center_point: Tuple[int, int]):
        self.bbox = bbox  # (x1, y1, x2, y2)
        self.confidence = confidence
        self.center_point = center_point  # (x, y)
        self.area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])


class CarDetectionWorker(QThread):
    """Worker thread for running car detection to avoid blocking the GUI"""
    
    detection_complete = pyqtSignal(list, np.ndarray)  # detections, annotated_frame
    
    def __init__(self):
        super().__init__()
        self.model = None
        self.frame = None
        self.running = False
        self.confidence_threshold = 0.5
        
    def initialize_model(self):
        """Initialize the YOLOv11 model"""
        if not YOLO_AVAILABLE:
            return False
        
        try:
            # Load YOLOv11 model with COCO weights
            self.model = YOLO('yolo11n.pt')  # nano version for speed
            print("YOLOv11 model loaded successfully")
            return True
        except Exception as e:
            print(f"Error loading YOLOv11 model: {e}")
            return False
    
    def set_frame(self, frame: np.ndarray):
        """Set the frame to process"""
        self.frame = frame.copy()
    
    def set_confidence_threshold(self, threshold: float):
        """Set the confidence threshold for detections"""
        self.confidence_threshold = threshold
    
    def run(self):
        """Run detection on the current frame"""
        if self.model is None or self.frame is None:
            self.detection_complete.emit([], self.frame if self.frame is not None else np.array([]))
            return
        
        try:
            # Check if frame is valid
            if self.frame.size == 0:
                self.detection_complete.emit([], self.frame)
                return
            
            # Run inference
            results = self.model(self.frame, conf=self.confidence_threshold, verbose=False)
            
            # Extract car detections (class 2 in COCO dataset)
            car_detections = []
            annotated_frame = self.frame.copy()
            
            for result in results:
                if result is None:
                    continue
                    
                boxes = result.boxes
                if boxes is not None and len(boxes) > 0:
                    for box in boxes:
                        try:
                            # Check if detection is a car (class 2 in COCO)
                            class_id = int(box.cls[0])
                            if class_id == 2:  # Car class in COCO
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
                                detection = CarDetection(
                                    bbox=(x1, y1, x2, y2),
                                    confidence=confidence,
                                    center_point=(center_x, center_y)
                                )
                                car_detections.append(detection)
                                
                                # Draw detection on frame
                                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                                cv2.putText(annotated_frame, f'Car: {confidence:.2f}', 
                                          (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                                          
                        except Exception as e:
                            print(f"Error processing detection box: {e}")
                            continue
            
            # Emit results
            self.detection_complete.emit(car_detections, annotated_frame)
            
        except Exception as e:
            print(f"Error during car detection: {e}")
            # Emit empty results on error
            try:
                self.detection_complete.emit([], self.frame)
            except:
                self.detection_complete.emit([], np.array([]))


class CarDetectionManager(QObject):
    """Manages car detection and parking spot occupancy analysis"""
    
    detections_updated = pyqtSignal(list)  # car_detections
    occupancy_updated = pyqtSignal(dict)  # spot_id -> is_occupied
    
    def __init__(self):
        super().__init__()
        self.detection_worker = CarDetectionWorker()
        self.detection_worker.detection_complete.connect(self.on_detection_complete)
        
        self.is_enabled = False
        self.current_detections: List[CarDetection] = []
        self.parking_spot_manager = None
        self.last_detection_time = 0
        self.detection_interval = 1.0  # Run detection every 1 second
        self.confidence_threshold = 0.5
        self.overlap_threshold = 0.3  # Minimum overlap to consider spot occupied
        
        # Detection statistics
        self.total_detections = 0
        self.detection_fps = 0
        self.last_fps_time = time.time()
        self.fps_counter = 0
    
    def initialize(self) -> bool:
        """Initialize the car detection system"""
        if not YOLO_AVAILABLE:
            return False
        
        return self.detection_worker.initialize_model()
    
    def set_parking_spot_manager(self, spot_manager):
        """Set the parking spot manager reference"""
        self.parking_spot_manager = spot_manager
    
    def set_enabled(self, enabled: bool):
        """Enable or disable car detection"""
        self.is_enabled = enabled
        if not enabled:
            # Wait for any running detection to complete
            if self.detection_worker.isRunning():
                self.detection_worker.wait(1000)  # Wait up to 1 second
            
            # Clear all detections when disabled
            self.current_detections.clear()
            if self.parking_spot_manager:
                try:
                    self.update_spot_occupancy()
                except Exception as e:
                    print(f"Error updating spot occupancy when disabling detection: {e}")
    
    def set_confidence_threshold(self, threshold: float):
        """Set the confidence threshold for detections"""
        self.confidence_threshold = threshold
        self.detection_worker.set_confidence_threshold(threshold)
    
    def set_detection_interval(self, interval: float):
        """Set the detection interval in seconds"""
        self.detection_interval = interval
    
    def set_overlap_threshold(self, threshold: float):
        """Set the overlap threshold for spot occupancy"""
        self.overlap_threshold = threshold
    
    def process_frame(self, frame: np.ndarray) -> np.ndarray:
        """Process frame for car detection"""
        if not self.is_enabled or not YOLO_AVAILABLE:
            return frame
        
        current_time = time.time()
        
        # Run detection at specified interval
        if current_time - self.last_detection_time >= self.detection_interval:
            if not self.detection_worker.isRunning():
                self.detection_worker.set_frame(frame)
                self.detection_worker.start()
                self.last_detection_time = current_time
        
        # Draw existing detections on frame
        annotated_frame = self.draw_detections_on_frame(frame)
        return annotated_frame
    
    @pyqtSlot(list, np.ndarray)
    def on_detection_complete(self, detections: List[CarDetection], annotated_frame: np.ndarray):
        """Handle completed detection results"""
        self.current_detections = detections
        self.total_detections += len(detections)
        
        # Update FPS statistics
        self.fps_counter += 1
        current_time = time.time()
        if current_time - self.last_fps_time >= 1.0:
            self.detection_fps = self.fps_counter
            self.fps_counter = 0
            self.last_fps_time = current_time
        
        # Update parking spot occupancy
        self.update_spot_occupancy()
        
        # Emit signals
        self.detections_updated.emit(detections)
    
    def draw_detections_on_frame(self, frame: np.ndarray) -> np.ndarray:
        """Draw current car detections on frame"""
        if not self.current_detections:
            return frame
        
        annotated_frame = frame.copy()
        
        for detection in self.current_detections:
            x1, y1, x2, y2 = detection.bbox
            confidence = detection.confidence
            
            # Draw bounding box
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Draw confidence label
            label = f'Car: {confidence:.2f}'
            cv2.putText(annotated_frame, label, (x1, y1 - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Draw center point
            cv2.circle(annotated_frame, detection.center_point, 5, (0, 255, 0), -1)
        
        # Draw detection statistics
        stats_text = f"Cars: {len(self.current_detections)} | FPS: {self.detection_fps}"
        cv2.putText(annotated_frame, stats_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        return annotated_frame
    
    def update_spot_occupancy(self):
        """Update parking spot occupancy based on car detections"""
        if not self.parking_spot_manager:
            return
        
        try:
            spots = self.parking_spot_manager.get_all_spots()
            if not spots:
                return
                
            occupancy_changes = {}
            
            for spot_id, spot in spots.items():
                try:
                    was_occupied = spot.is_occupied
                    is_occupied = self.is_spot_occupied(spot)
                    
                    # Update spot status
                    spot.is_occupied = is_occupied
                    
                    # Track changes
                    if was_occupied != is_occupied:
                        occupancy_changes[spot_id] = is_occupied
                        
                except Exception as e:
                    print(f"Error updating occupancy for spot {spot_id}: {e}")
                    continue
            
            # Emit occupancy update if there were changes
            if occupancy_changes:
                try:
                    all_occupancy = {spot_id: spot.is_occupied for spot_id, spot in spots.items() if hasattr(spot, 'is_occupied')}
                    self.occupancy_updated.emit(all_occupancy)
                except Exception as e:
                    print(f"Error emitting occupancy update: {e}")
                    
        except Exception as e:
            print(f"Error in update_spot_occupancy: {e}")
            return
    
    def is_spot_occupied(self, spot) -> bool:
        """Check if a parking spot is occupied by a detected car"""
        if not self.current_detections:
            return False
        
        spot_polygon = np.array(spot.polygon_points, dtype=np.int32)
        
        for detection in self.current_detections:
            # Check if car center is inside the parking spot
            # Convert center_point to tuple of floats for OpenCV
            center_point_float = (float(detection.center_point[0]), float(detection.center_point[1]))
            center_inside = cv2.pointPolygonTest(spot_polygon, center_point_float, False) >= 0
            
            if center_inside:
                return True
            
            # Additional check: calculate overlap between car bbox and spot polygon
            overlap_ratio = self.calculate_bbox_polygon_overlap(detection.bbox, spot_polygon)
            if overlap_ratio >= self.overlap_threshold:
                return True
        
        return False
    
    def calculate_bbox_polygon_overlap(self, bbox: Tuple[int, int, int, int], polygon: np.ndarray) -> float:
        """Calculate overlap ratio between bounding box and polygon"""
        x1, y1, x2, y2 = bbox
        
        # Ensure valid bounding box
        if x2 <= x1 or y2 <= y1:
            return 0.0
        
        try:
            # Create a mask for the polygon with proper dimensions
            min_x = max(0, min(polygon[:, 0].min(), x1) - 10)
            min_y = max(0, min(polygon[:, 1].min(), y1) - 10)
            max_x = max(polygon[:, 0].max(), x2) + 10
            max_y = max(polygon[:, 1].max(), y2) + 10
            
            mask_width = int(max_x - min_x)
            mask_height = int(max_y - min_y)
            
            if mask_width <= 0 or mask_height <= 0:
                return 0.0
            
            # Adjust polygon coordinates relative to mask origin
            adjusted_polygon = polygon.copy().astype(np.int32)
            adjusted_polygon[:, 0] -= int(min_x)
            adjusted_polygon[:, 1] -= int(min_y)
            
            # Create masks
            polygon_mask = np.zeros((mask_height, mask_width), dtype=np.uint8)
            bbox_mask = np.zeros((mask_height, mask_width), dtype=np.uint8)
            
            # Fill polygon mask
            cv2.fillPoly(polygon_mask, [adjusted_polygon], 255)
            
            # Fill bbox mask (adjust coordinates)
            bbox_x1 = max(0, int(x1 - min_x))
            bbox_y1 = max(0, int(y1 - min_y))
            bbox_x2 = min(mask_width, int(x2 - min_x))
            bbox_y2 = min(mask_height, int(y2 - min_y))
            
            if bbox_x2 > bbox_x1 and bbox_y2 > bbox_y1:
                cv2.rectangle(bbox_mask, (bbox_x1, bbox_y1), (bbox_x2, bbox_y2), 255, -1)
            
            # Calculate intersection
            intersection = cv2.bitwise_and(polygon_mask, bbox_mask)
            intersection_area = np.sum(intersection > 0)
            bbox_area = (x2 - x1) * (y2 - y1)
            
            if bbox_area == 0:
                return 0.0
            
            return intersection_area / bbox_area
            
        except Exception as e:
            print(f"Error calculating overlap: {e}")
            return 0.0
    
    def get_detection_stats(self) -> Dict:
        """Get detection statistics"""
        return {
            'total_detections': self.total_detections,
            'current_cars': len(self.current_detections),
            'detection_fps': self.detection_fps,
            'confidence_threshold': self.confidence_threshold,
            'overlap_threshold': self.overlap_threshold,
            'detection_interval': self.detection_interval,
            'enabled': self.is_enabled
        } 