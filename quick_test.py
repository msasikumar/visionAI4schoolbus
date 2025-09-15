#!/usr/bin/env python3
"""
Quick test script for camera and MQTT components
"""

import sys
import os
import cv2
import time

# Add src to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_camera():
    """Test camera access"""
    print("Testing camera access...")
    try:
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                print("✓ Camera test: PASSED")
                cap.release()
                return True
            else:
                print("✗ Camera test: FAILED - Could not read frame")
                cap.release()
                return False
        else:
            print("✗ Camera test: FAILED - Could not open camera")
            return False
    except Exception as e:
        print(f"✗ Camera test: ERROR - {e}")
        return False

def test_mqtt():
    """Test MQTT connection"""
    print("Testing MQTT connection...")
    try:
        import subprocess
        result = subprocess.run(['mosquitto_pub', '-h', 'localhost', '-t', 'test/topic', '-m', 'test message'], 
                              capture_output=True, timeout=10)
        if result.returncode == 0:
            print("✓ MQTT test: PASSED")
            return True
        else:
            print("✗ MQTT test: FAILED - Could not publish message")
            return False
    except Exception as e:
        print(f"✗ MQTT test: ERROR - {e}")
        return False

def main():
    print("VisionAI4SchoolBus Quick Component Test")
    print("======================================")
    
    camera_result = test_camera()
    mqtt_result = test_mqtt()
    
    print("\n" + "="*50)
    print("QUICK TEST RESULTS")
    print("="*50)
    
    if camera_result:
        print("✓ Camera component: WORKING")
    else:
        print("✗ Camera component: NOT WORKING")
    
    if mqtt_result:
        print("✓ MQTT component: WORKING")
    else:
        print("✗ MQTT component: NOT WORKING")
    
    if camera_result and mqtt_result:
        print("\n🎉 All tested components are working!")
        return 0
    else:
        print("\n⚠️  Some components are not working.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
