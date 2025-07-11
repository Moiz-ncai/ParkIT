#!/usr/bin/env python3
"""
Run script for ParkIT Detection Service
Simple wrapper to start the detection service with proper error handling
"""

import sys
import os
import time
import signal
import logging

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from detection_service import DetectionService
from config import DetectionConfig


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    print("\n🛑 Received shutdown signal, stopping detection service...")
    global service
    if 'service' in globals() and service:
        service.stop()
    sys.exit(0)


def check_prerequisites():
    """Check if all prerequisites are met"""
    print("🔍 Checking prerequisites...")
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    
    # Check required packages
    required_packages = ['cv2', 'numpy', 'requests']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is available")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} is missing")
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    # Check YOLO availability
    try:
        from ultralytics import YOLO
        print("✅ YOLO (ultralytics) is available")
    except ImportError:
        print("❌ YOLO (ultralytics) is missing")
        print("Install with: pip install ultralytics")
        return False
    
    print("✅ All prerequisites met!")
    return True


def check_backend_connection():
    """Check connection to backend API"""
    print(f"\n🔌 Checking backend connection to {DetectionConfig.BACKEND_URL}...")
    
    try:
        from api_client import ParkITAPIClient
        client = ParkITAPIClient()
        
        if client.health_check():
            print("✅ Backend connection successful")
            
            # Get plazas to verify API is working
            plazas = client.get_plazas()
            print(f"✅ Found {len(plazas)} plazas in backend")
            
            return True
        else:
            print("❌ Backend health check failed")
            return False
            
    except Exception as e:
        print(f"❌ Backend connection error: {e}")
        return False


def main():
    """Main entry point"""
    print("🚀 ParkIT Detection Service Launcher")
    print("="*50)
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please install required packages.")
        return 1
    
    # Check backend connection
    if not check_backend_connection():
        print("\n⚠️ Backend not available. Service will continue but may not function properly.")
        print("Make sure the backend is running:")
        print("  cd backend && python test_basic.py")
        
        response = input("\nContinue anyway? (y/N): ").strip().lower()
        if response != 'y':
            print("Exiting...")
            return 1
    
    # Initialize and start service
    print("\n🎯 Initializing Detection Service...")
    
    global service
    service = DetectionService()
    
    try:
        # Initialize service
        if not service.initialize():
            print("❌ Failed to initialize detection service")
            return 1
        
        print("✅ Detection service initialized successfully!")
        
        # Start service
        service.start()
        
        print("✅ Detection service started!")
        print("\n📊 Service Status:")
        print(f"   Backend URL: {DetectionConfig.BACKEND_URL}")
        print(f"   Confidence Threshold: {DetectionConfig.CONFIDENCE_THRESHOLD}")
        print(f"   Detection Interval: {DetectionConfig.DETECTION_INTERVAL}s")
        print(f"   Log Level: {DetectionConfig.LOG_LEVEL}")
        
        print("\n🎮 Commands:")
        print("   Press 's' + Enter to show status")
        print("   Press 'q' + Enter to quit")
        print("   Press Ctrl+C to stop")
        
        # Main loop
        while service.running:
            try:
                user_input = input().strip().lower()
                
                if user_input == 'q':
                    print("🛑 Stopping service...")
                    break
                elif user_input == 's':
                    status = service.get_status()
                    print(f"\n📊 Service Status:")
                    print(f"   Running: {status['running']}")
                    print(f"   Runtime: {status['runtime_seconds']:.0f}s")
                    print(f"   Active Cameras: {len([c for c in status['cameras'].values() if c['connected']])}")
                    print(f"   Total Frames: {status['stats']['total_frames_processed']}")
                    print(f"   Total Detections: {status['stats']['total_detections']}")
                    print()
                    
            except EOFError:
                # Handle Ctrl+D
                break
            except KeyboardInterrupt:
                # Handle Ctrl+C
                break
    
    except Exception as e:
        print(f"❌ Error running detection service: {e}")
        return 1
    
    finally:
        if service:
            service.stop()
        print("✅ Detection service stopped successfully")
    
    return 0


def run_tests():
    """Run detection service tests"""
    print("🧪 Running Detection Service Tests...")
    
    try:
        from test_detection_service import main as run_tests_main
        success = run_tests_main()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Test error: {e}")
        return 1


def show_help():
    """Show help information"""
    print("ParkIT Detection Service")
    print("="*30)
    print()
    print("Usage:")
    print("  python run_detection_service.py [command]")
    print()
    print("Commands:")
    print("  (no command)  - Start the detection service")
    print("  test         - Run test suite")
    print("  help         - Show this help")
    print()
    print("Configuration:")
    print("  Edit .env file or set environment variables:")
    print(f"  BACKEND_URL={DetectionConfig.BACKEND_URL}")
    print(f"  CONFIDENCE_THRESHOLD={DetectionConfig.CONFIDENCE_THRESHOLD}")
    print(f"  DETECTION_INTERVAL={DetectionConfig.DETECTION_INTERVAL}")
    print()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "test":
            sys.exit(run_tests())
        elif command == "help":
            show_help()
            sys.exit(0)
        else:
            print(f"Unknown command: {command}")
            show_help()
            sys.exit(1)
    else:
        sys.exit(main()) 