#!/usr/bin/env python3
"""
Test script for ParkIT Detection Service
Tests all components and integration with backend
"""

import sys
import os
import time
import logging
import threading
from typing import Dict, List

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from vehicle_detector import VehicleDetector, test_detection
from api_client import ParkITAPIClient, test_api_client
from config import DetectionConfig


def test_vehicle_detection():
    """Test vehicle detection functionality"""
    print("\n🔍 Testing Vehicle Detection...")
    
    try:
        # Test basic detection
        if test_detection():
            print("✅ Vehicle detection test passed")
            return True
        else:
            print("❌ Vehicle detection test failed")
            return False
    except Exception as e:
        print(f"❌ Vehicle detection test error: {e}")
        return False


def test_api_integration():
    """Test API client integration"""
    print("\n🔌 Testing API Integration...")
    
    try:
        # Test API client
        if test_api_client():
            print("✅ API integration test passed")
            return True
        else:
            print("❌ API integration test failed")
            return False
    except Exception as e:
        print(f"❌ API integration test error: {e}")
        return False


def test_occupancy_analysis():
    """Test parking spot occupancy analysis"""
    print("\n🅿️ Testing Occupancy Analysis...")
    
    try:
        detector = VehicleDetector()
        if not detector.initialize_model():
            print("❌ Failed to initialize model for occupancy test")
            return False
        
        # Create mock parking spots
        mock_spots = [
            {
                'id': 1,
                'spot_id': '1',
                'polygon_coordinates': [
                    {'x': 100, 'y': 100},
                    {'x': 200, 'y': 100},
                    {'x': 200, 'y': 160},
                    {'x': 100, 'y': 160}
                ]
            },
            {
                'id': 2,
                'spot_id': '2',
                'polygon_coordinates': [
                    {'x': 300, 'y': 100},
                    {'x': 400, 'y': 100},
                    {'x': 400, 'y': 160},
                    {'x': 300, 'y': 160}
                ]
            }
        ]
        
        # Create mock detections
        from vehicle_detector import VehicleDetection
        mock_detections = [
            VehicleDetection(
                bbox=(120, 110, 180, 150),
                confidence=0.85,
                center_point=(150, 130),
                vehicle_type="Car"
            )
        ]
        
        # Analyze occupancy
        occupancy = detector.analyze_parking_spot_occupancy(mock_detections, mock_spots)
        
        # Verify results
        if '1' in occupancy and occupancy['1'] == True:  # First spot should be occupied
            if '2' in occupancy and occupancy['2'] == False:  # Second spot should be empty
                print("✅ Occupancy analysis test passed")
                print(f"   Spot 1: {'Occupied' if occupancy['1'] else 'Available'}")
                print(f"   Spot 2: {'Occupied' if occupancy['2'] else 'Available'}")
                return True
        
        print("❌ Occupancy analysis test failed - unexpected results")
        print(f"   Results: {occupancy}")
        return False
        
    except Exception as e:
        print(f"❌ Occupancy analysis test error: {e}")
        return False


def test_full_integration():
    """Test full integration between detection and API"""
    print("\n🔄 Testing Full Integration...")
    
    try:
        # Initialize components
        detector = VehicleDetector()
        api_client = ParkITAPIClient()
        
        # Check backend connection
        if not api_client.health_check():
            print("❌ Backend not available for integration test")
            return False
        
        # Initialize detector
        if not detector.initialize_model():
            print("❌ Failed to initialize detector for integration test")
            return False
        
        # Get plazas from backend
        plazas = api_client.get_plazas()
        if not plazas:
            print("❌ No plazas available for integration test")
            return False
        
        plaza = plazas[0]
        plaza_id = plaza['id']
        print(f"   Using plaza: {plaza['name']} (ID: {plaza_id})")
        
        # Simulate occupancy change
        test_occupancy = {
            "1": True,   # Spot 1 occupied
            "2": False,  # Spot 2 available
            "3": True    # Spot 3 occupied
        }
        
        # Send occupancy update
        success = api_client.send_occupancy_data(plaza_id, test_occupancy)
        
        if success:
            print("✅ Full integration test passed")
            print(f"   Sent occupancy update for {len(test_occupancy)} spots")
            
            # Verify by checking plaza availability
            availability = api_client.get_plaza_availability(plaza_id)
            if availability:
                print(f"   Plaza availability: {availability['available_spots']}/{availability['total_spots']} spots")
            
            return True
        else:
            print("❌ Full integration test failed - could not send occupancy update")
            return False
        
    except Exception as e:
        print(f"❌ Full integration test error: {e}")
        return False


def test_configuration():
    """Test configuration loading"""
    print("\n⚙️ Testing Configuration...")
    
    try:
        config = DetectionConfig.to_dict()
        print("✅ Configuration loaded successfully")
        print(f"   Backend URL: {config['backend_url']}")
        print(f"   Confidence Threshold: {config['confidence_threshold']}")
        print(f"   Detection Interval: {config['detection_interval']}s")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test error: {e}")
        return False


def run_performance_test():
    """Run a basic performance test"""
    print("\n⚡ Running Performance Test...")
    
    try:
        detector = VehicleDetector()
        if not detector.initialize_model():
            print("❌ Failed to initialize model for performance test")
            return False
        
        # Create test frame
        import numpy as np
        test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # Time multiple detections
        start_time = time.time()
        num_tests = 5
        
        for i in range(num_tests):
            detections, annotated = detector.detect_vehicles(test_frame)
            print(f"   Test {i+1}: {len(detections)} detections")
        
        end_time = time.time()
        avg_time = (end_time - start_time) / num_tests
        fps = 1.0 / avg_time if avg_time > 0 else 0
        
        print(f"✅ Performance test completed")
        print(f"   Average detection time: {avg_time:.3f}s")
        print(f"   Estimated FPS: {fps:.1f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance test error: {e}")
        return False


def main():
    """Run all tests"""
    print("🧪 ParkIT Detection Service - Test Suite")
    print("="*50)
    
    # Configure logging for tests
    logging.basicConfig(level=logging.WARNING)  # Reduce log noise during tests
    
    tests = [
        ("Configuration", test_configuration),
        ("Vehicle Detection", test_vehicle_detection),
        ("API Integration", test_api_integration),
        ("Occupancy Analysis", test_occupancy_analysis),
        ("Full Integration", test_full_integration),
        ("Performance", run_performance_test)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔬 Running {test_name} Test...")
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} test failed")
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
    
    print("\n" + "="*50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Detection service is ready.")
        return True
    else:
        print("⚠️ Some tests failed. Check the issues above.")
        return False


def interactive_test():
    """Run interactive test mode"""
    print("\n🎮 Interactive Test Mode")
    print("Available commands:")
    print("  1 - Test vehicle detection")
    print("  2 - Test API integration")  
    print("  3 - Test occupancy analysis")
    print("  4 - Test full integration")
    print("  5 - Run performance test")
    print("  6 - Run all tests")
    print("  q - Quit")
    
    while True:
        try:
            choice = input("\nEnter command: ").strip().lower()
            
            if choice == 'q':
                break
            elif choice == '1':
                test_vehicle_detection()
            elif choice == '2':
                test_api_integration()
            elif choice == '3':
                test_occupancy_analysis()
            elif choice == '4':
                test_full_integration()
            elif choice == '5':
                run_performance_test()
            elif choice == '6':
                main()
            else:
                print("Invalid command. Try again.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_test()
    else:
        success = main()
        sys.exit(0 if success else 1) 