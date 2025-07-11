"""
API Client for ParkIT Platform Backend Communication
Handles sending occupancy updates and retrieving parking spot data
"""

import requests
import logging
import time
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class ParkITAPIClient:
    """Client for communicating with ParkIT Platform backend"""
    
    def __init__(self, base_url: str = "http://localhost:8000", timeout: int = 10):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'ParkIT-Detection-Service/1.0'
        })
        
        logging.info(f"ParkIT API Client initialized with base URL: {self.base_url}")
    
    def health_check(self) -> bool:
        """Check if the backend API is healthy"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                logging.info(f"Backend health check passed: {data}")
                return True
            else:
                logging.warning(f"Backend health check failed: {response.status_code}")
                return False
        except Exception as e:
            logging.error(f"Backend health check error: {e}")
            return False
    
    def get_plazas(self) -> List[Dict]:
        """Get list of all plazas"""
        try:
            response = self.session.get(f"{self.base_url}/plazas", timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            plazas = data.get('plazas', [])
            logging.info(f"Retrieved {len(plazas)} plazas from backend")
            return plazas
            
        except Exception as e:
            logging.error(f"Error getting plazas: {e}")
            return []
    
    def get_plaza_availability(self, plaza_id: int) -> Optional[Dict]:
        """Get current availability for a specific plaza"""
        try:
            response = self.session.get(f"{self.base_url}/plazas/{plaza_id}/availability", timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            logging.debug(f"Retrieved availability for plaza {plaza_id}: {data}")
            return data
            
        except Exception as e:
            logging.error(f"Error getting plaza {plaza_id} availability: {e}")
            return None
    
    def create_plaza(self, name: str, address: str) -> Optional[Dict]:
        """Create a new plaza"""
        try:
            payload = {
                "name": name,
                "address": address
            }
            
            response = self.session.post(f"{self.base_url}/plazas", 
                                       json=payload, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            logging.info(f"Created new plaza: {data}")
            return data
            
        except Exception as e:
            logging.error(f"Error creating plaza: {e}")
            return None
    
    def update_spot_status(self, spot_id: int, status: str, vehicle_type: str = None, confidence_score: float = None) -> bool:
        """Update parking spot status"""
        try:
            # For now, we'll use the simple test backend endpoint
            # This would need to be adapted for the full FastAPI backend
            payload = {
                "status": status
            }
            
            if vehicle_type:
                payload["vehicle_type"] = vehicle_type
            if confidence_score:
                payload["confidence_score"] = confidence_score
            
            response = self.session.put(f"{self.base_url}/spots/{spot_id}/status?status={status}", 
                                      timeout=self.timeout)
            
            if response.status_code == 200:
                logging.debug(f"Updated spot {spot_id} status to {status}")
                return True
            else:
                logging.warning(f"Failed to update spot {spot_id}: {response.status_code}")
                return False
                
        except Exception as e:
            logging.error(f"Error updating spot {spot_id} status: {e}")
            return False
    
    def batch_update_spot_statuses(self, spot_updates: Dict[int, str]) -> Dict[int, bool]:
        """Update multiple parking spot statuses in batch"""
        results = {}
        
        for spot_id, status in spot_updates.items():
            success = self.update_spot_status(spot_id, status)
            results[spot_id] = success
        
        successful_updates = sum(1 for success in results.values() if success)
        logging.info(f"Batch update completed: {successful_updates}/{len(spot_updates)} successful")
        
        return results
    
    def send_occupancy_data(self, plaza_id: int, occupancy_data: Dict[str, bool], vehicle_detections: List[Dict] = None) -> bool:
        """
        Send comprehensive occupancy data to backend
        
        Args:
            plaza_id: Plaza identifier
            occupancy_data: Dictionary mapping spot_id to occupancy status
            vehicle_detections: Optional list of vehicle detection data
        """
        try:
            # Convert spot occupancy to status updates
            spot_updates = {}
            for spot_id, is_occupied in occupancy_data.items():
                # Convert spot_id to integer if it's a string
                try:
                    spot_id_int = int(spot_id)
                except (ValueError, TypeError):
                    logging.warning(f"Invalid spot_id format: {spot_id}")
                    continue
                
                status = "occupied" if is_occupied else "available"
                spot_updates[spot_id_int] = status
            
            # Send batch update
            results = self.batch_update_spot_statuses(spot_updates)
            
            successful_updates = sum(1 for success in results.values() if success)
            total_updates = len(results)
            
            logging.info(f"Occupancy update for plaza {plaza_id}: {successful_updates}/{total_updates} spots updated")
            
            return successful_updates > 0
            
        except Exception as e:
            logging.error(f"Error sending occupancy data for plaza {plaza_id}: {e}")
            return False
    
    def get_detection_history(self, spot_id: int, limit: int = 10) -> List[Dict]:
        """Get detection history for a specific spot (if available in backend)"""
        try:
            # This would be implemented when the full FastAPI backend is available
            # For now, return empty list
            logging.debug(f"Detection history not available in test backend")
            return []
            
        except Exception as e:
            logging.error(f"Error getting detection history for spot {spot_id}: {e}")
            return []
    
    def send_detection_stats(self, stats: Dict) -> bool:
        """Send detection statistics to backend"""
        try:
            # This would be used for monitoring and analytics
            # For now, just log the stats
            logging.info(f"Detection stats: {stats}")
            return True
            
        except Exception as e:
            logging.error(f"Error sending detection stats: {e}")
            return False


class APIClientManager:
    """Manages API client with connection retry and health monitoring"""
    
    def __init__(self, base_url: str = "http://localhost:8000", retry_attempts: int = 3, retry_delay: int = 5):
        self.base_url = base_url
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        self.client = ParkITAPIClient(base_url)
        self.last_health_check = 0
        self.health_check_interval = 60  # Check health every 60 seconds
        self.is_connected = False
        
    def ensure_connection(self) -> bool:
        """Ensure connection to backend with retry logic"""
        current_time = time.time()
        
        # Check if we need to verify health
        if current_time - self.last_health_check > self.health_check_interval or not self.is_connected:
            for attempt in range(self.retry_attempts):
                if self.client.health_check():
                    self.is_connected = True
                    self.last_health_check = current_time
                    return True
                else:
                    if attempt < self.retry_attempts - 1:
                        logging.warning(f"Backend connection failed, retrying in {self.retry_delay}s (attempt {attempt + 1}/{self.retry_attempts})")
                        time.sleep(self.retry_delay)
            
            self.is_connected = False
            logging.error("Failed to connect to backend after all retry attempts")
            return False
        
        return self.is_connected
    
    def send_occupancy_update(self, plaza_id: int, occupancy_data: Dict[str, bool], vehicle_detections: List[Dict] = None) -> bool:
        """Send occupancy update with connection handling"""
        if not self.ensure_connection():
            logging.error("Cannot send occupancy update - backend not available")
            return False
        
        return self.client.send_occupancy_data(plaza_id, occupancy_data, vehicle_detections)
    
    def get_plazas(self) -> List[Dict]:
        """Get plazas with connection handling"""
        if not self.ensure_connection():
            logging.error("Cannot get plazas - backend not available")
            return []
        
        return self.client.get_plazas()


# Test functions
def test_api_client():
    """Test the API client functionality"""
    logging.basicConfig(level=logging.INFO)
    
    client = ParkITAPIClient()
    
    # Test health check
    if client.health_check():
        logging.info("✅ Health check passed")
    else:
        logging.error("❌ Health check failed")
        return False
    
    # Test getting plazas
    plazas = client.get_plazas()
    logging.info(f"✅ Retrieved {len(plazas)} plazas")
    
    # Test availability check
    if plazas:
        plaza_id = plazas[0]['id']
        availability = client.get_plaza_availability(plaza_id)
        if availability:
            logging.info(f"✅ Plaza {plaza_id} availability: {availability['available_spots']}/{availability['total_spots']}")
    
    # Test occupancy update
    test_occupancy = {"1": True, "2": False, "3": True}
    success = client.send_occupancy_data(1, test_occupancy)
    if success:
        logging.info("✅ Occupancy update successful")
    else:
        logging.error("❌ Occupancy update failed")
    
    return True


if __name__ == "__main__":
    test_api_client() 