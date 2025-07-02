import json
import os
from typing import List, Dict, Tuple
from PyQt5.QtCore import QObject, pyqtSignal
import cv2
import numpy as np


class ParkingSpot:
    """Represents a single parking spot with polygon coordinates"""
    
    def __init__(self, spot_id: int, name: str, polygon_points: List[Tuple[int, int]]):
        self.spot_id = spot_id
        self.name = name
        self.polygon_points = polygon_points
        self.is_occupied = False
        self.last_vehicle = None
        self.is_selected = False
    
    def to_dict(self):
        """Convert parking spot to dictionary for JSON serialization"""
        return {
            'spot_id': self.spot_id,
            'name': self.name,
            'polygon_points': self.polygon_points,
            'is_occupied': self.is_occupied,
            'last_vehicle': self.last_vehicle
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create parking spot from dictionary"""
        spot = cls(data['spot_id'], data['name'], data['polygon_points'])
        spot.is_occupied = data.get('is_occupied', False)
        spot.last_vehicle = data.get('last_vehicle', None)
        return spot
    
    def point_in_polygon(self, point: Tuple[int, int]) -> bool:
        """Check if a point is inside the parking spot polygon"""
        x, y = point
        n = len(self.polygon_points)
        inside = False
        
        p1x, p1y = self.polygon_points[0]
        for i in range(1, n + 1):
            p2x, p2y = self.polygon_points[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        
        return inside


class ParkingSpotManager(QObject):
    """Manages parking spots: creation, editing, deletion, and persistence"""
    
    spots_updated = pyqtSignal()
    spot_selected = pyqtSignal(int)  # spot_id
    
    def __init__(self, config_file: str = "parking_spots.json"):
        super().__init__()
        self.config_file = config_file
        self.parking_spots: Dict[int, ParkingSpot] = {}
        self.next_spot_id = 1
        self.load_spots()
    
    def add_spot(self, name: str, polygon_points: List[Tuple[int, int]]) -> int:
        """Add a new parking spot"""
        if len(polygon_points) < 3:
            raise ValueError("Parking spot must have at least 3 points")
        
        spot = ParkingSpot(self.next_spot_id, name, polygon_points)
        self.parking_spots[self.next_spot_id] = spot
        current_id = self.next_spot_id
        self.next_spot_id += 1
        
        self.save_spots()
        self.spots_updated.emit()
        return current_id
    
    def remove_spot(self, spot_id: int) -> bool:
        """Remove a parking spot"""
        if spot_id in self.parking_spots:
            del self.parking_spots[spot_id]
            self.save_spots()
            self.spots_updated.emit()
            return True
        return False
    
    def update_spot(self, spot_id: int, name: str = None, polygon_points: List[Tuple[int, int]] = None) -> bool:
        """Update an existing parking spot"""
        if spot_id not in self.parking_spots:
            return False
        
        spot = self.parking_spots[spot_id]
        if name is not None:
            spot.name = name
        if polygon_points is not None:
            if len(polygon_points) < 3:
                raise ValueError("Parking spot must have at least 3 points")
            spot.polygon_points = polygon_points
        
        self.save_spots()
        self.spots_updated.emit()
        return True
    
    def get_spot(self, spot_id: int) -> ParkingSpot:
        """Get a parking spot by ID"""
        return self.parking_spots.get(spot_id)
    
    def get_all_spots(self) -> Dict[int, ParkingSpot]:
        """Get all parking spots"""
        return self.parking_spots.copy()
    
    def select_spot(self, spot_id: int):
        """Select a parking spot"""
        # Deselect all spots first
        for spot in self.parking_spots.values():
            spot.is_selected = False
        
        # Select the specified spot
        if spot_id in self.parking_spots:
            self.parking_spots[spot_id].is_selected = True
            self.spot_selected.emit(spot_id)
        
        self.spots_updated.emit()
    
    def deselect_all(self):
        """Deselect all parking spots"""
        for spot in self.parking_spots.values():
            spot.is_selected = False
        self.spots_updated.emit()
    
    def get_spot_at_point(self, point: Tuple[int, int]) -> int:
        """Get the parking spot ID at a given point, or -1 if none"""
        for spot_id, spot in self.parking_spots.items():
            if spot.point_in_polygon(point):
                return spot_id
        return -1
    
    def save_spots(self):
        """Save parking spots to JSON file"""
        try:
            data = {
                'next_spot_id': self.next_spot_id,
                'parking_spots': {str(k): v.to_dict() for k, v in self.parking_spots.items()}
            }
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving parking spots: {e}")
    
    def load_spots(self):
        """Load parking spots from JSON file"""
        if not os.path.exists(self.config_file):
            return
        
        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)
            
            self.next_spot_id = data.get('next_spot_id', 1)
            spots_data = data.get('parking_spots', {})
            
            self.parking_spots = {}
            for spot_id_str, spot_data in spots_data.items():
                spot_id = int(spot_id_str)
                self.parking_spots[spot_id] = ParkingSpot.from_dict(spot_data)
            
        except Exception as e:
            print(f"Error loading parking spots: {e}")
            self.parking_spots = {}
            self.next_spot_id = 1
    
    def clear_all_spots(self):
        """Clear all parking spots"""
        self.parking_spots.clear()
        self.next_spot_id = 1
        self.save_spots()
        self.spots_updated.emit()
    
    def draw_spots_on_frame(self, frame: np.ndarray) -> np.ndarray:
        """Draw all parking spots on a frame"""
        overlay = frame.copy()
        
        for spot in self.parking_spots.values():
            if len(spot.polygon_points) < 3:
                continue
            
            # Convert points to numpy array
            points = np.array(spot.polygon_points, dtype=np.int32)
            
            # Choose colors based on status
            if spot.is_selected:
                fill_color = (255, 255, 0, 100)  # Yellow for selected
                border_color = (255, 255, 0)
                thickness = 3
            elif spot.is_occupied:
                fill_color = (0, 0, 255, 100)  # Red for occupied
                border_color = (0, 0, 255)
                thickness = 2
            else:
                fill_color = (0, 255, 0, 100)  # Green for vacant
                border_color = (0, 255, 0)
                thickness = 2
            
            # Draw filled polygon with transparency
            cv2.fillPoly(overlay, [points], fill_color[:3])
            
            # Draw border
            cv2.polylines(frame, [points], True, border_color, thickness)
            
            # Add spot label
            if len(points) > 0:
                # Calculate center point for label
                center_x = int(np.mean(points[:, 0]))
                center_y = int(np.mean(points[:, 1]))
                
                # Draw label background
                label = f"#{spot.spot_id}: {spot.name}"
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.6
                font_thickness = 2
                
                (text_width, text_height), _ = cv2.getTextSize(label, font, font_scale, font_thickness)
                cv2.rectangle(frame, 
                            (center_x - text_width//2 - 5, center_y - text_height//2 - 5),
                            (center_x + text_width//2 + 5, center_y + text_height//2 + 5),
                            (0, 0, 0), -1)
                
                # Draw label text
                cv2.putText(frame, label, 
                          (center_x - text_width//2, center_y + text_height//2),
                          font, font_scale, (255, 255, 255), font_thickness)
        
        # Blend overlay with original frame for transparency effect
        alpha = 0.3
        frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
        
        return frame 