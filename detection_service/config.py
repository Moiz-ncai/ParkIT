"""
Configuration module for ParkIT Detection Service
"""

import os
from typing import Dict, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class DetectionConfig:
    """Detection service configuration"""
    
    # Backend API Configuration
    BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')
    API_TIMEOUT = int(os.getenv('API_TIMEOUT', '10'))
    API_RETRY_ATTEMPTS = int(os.getenv('API_RETRY_ATTEMPTS', '3'))
    API_RETRY_DELAY = int(os.getenv('API_RETRY_DELAY', '5'))
    
    # Detection Configuration
    CONFIDENCE_THRESHOLD = float(os.getenv('CONFIDENCE_THRESHOLD', '0.5'))
    OVERLAP_THRESHOLD = float(os.getenv('OVERLAP_THRESHOLD', '0.3'))
    DETECTION_INTERVAL = float(os.getenv('DETECTION_INTERVAL', '2.0'))
    
    # Camera Configuration
    MAX_CONNECTION_ATTEMPTS = int(os.getenv('MAX_CONNECTION_ATTEMPTS', '5'))
    FRAME_RATE_LIMIT = float(os.getenv('FRAME_RATE_LIMIT', '10.0'))
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'detection_service.log')
    
    # Service Configuration
    STATS_REPORTING_INTERVAL = int(os.getenv('STATS_REPORTING_INTERVAL', '60'))
    HEALTH_CHECK_INTERVAL = int(os.getenv('HEALTH_CHECK_INTERVAL', '60'))
    
    # Model Configuration
    YOLO_MODEL = os.getenv('YOLO_MODEL', 'yolo11s.pt')
    
    @classmethod
    def to_dict(cls) -> Dict:
        """Convert configuration to dictionary"""
        return {
            'backend_url': cls.BACKEND_URL,
            'api_timeout': cls.API_TIMEOUT,
            'confidence_threshold': cls.CONFIDENCE_THRESHOLD,
            'overlap_threshold': cls.OVERLAP_THRESHOLD,
            'detection_interval': cls.DETECTION_INTERVAL,
            'log_level': cls.LOG_LEVEL,
            'yolo_model': cls.YOLO_MODEL
        }


# Camera configuration for testing
TEST_CAMERA_CONFIG = {
    'test_camera_1': {
        'camera_id': 'test_camera_1',
        'rtsp_url': 0,  # Use default camera (webcam)
        'plaza_id': 1,
        'enabled': True
    }
}

# Plaza configuration for testing
TEST_PLAZA_CONFIG = {
    1: {
        'plaza_id': 1,
        'name': 'Test Plaza',
        'address': 'Test Address',
        'total_spots': 20,
        'cameras': ['test_camera_1']
    }
}


def get_camera_config() -> Dict:
    """Get camera configuration (from environment or test config)"""
    # In production, this would load from a configuration file or API
    return TEST_CAMERA_CONFIG


def get_plaza_config() -> Dict:
    """Get plaza configuration (from environment or test config)"""
    # In production, this would load from a configuration file or API
    return TEST_PLAZA_CONFIG 