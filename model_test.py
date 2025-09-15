#!/usr/bin/env python3
"""
Model test script for Hailo detector
"""

import sys
import os
import cv2
import numpy as np

# Add src to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_model():
    """Test model initialization"""
    print("Testing model initialization...")
    try:
        from detection.hailo_detector import HailoDetector, HAILO_AVAILABLE
        
        # Check if Hailo is available
        if HAILO_AVAILABLE:
            print("  - Hailo libraries: AVAILABLE")
        else:
            print("  - Hailo libraries: NOT AVAILABLE (using OpenCV fallback)")
        
        # Create a minimal config for testing
        config = {
            'model_path': 'models/yolov8n_hailo.hef',
            'min_confidence': 0.7,
            'nms_threshold': 0.45,
            'input_resolution': {'width': 640, 'height': 640}
        }
        
        detector = HailoDetector(config)
        result = detector.initialize()
        
        if result:
            print("✓ Model test: PASSED")
            # Test with a dummy frame
            dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            detections = detector.detect(dummy_frame)
            print(f"  - Model processed dummy frame, found {len(detections)} detections")
            detector.cleanup()
            return True
        else:
            print("✗ Model test: FAILED - Could not initialize detector")
            return False
            
    except Exception as e:
        print(f"✗ Model test: ERROR - {e}")
        return False

def main():
    print("VisionAI4SchoolBus Model Component Test")
    print("======================================")
    
    model_result = test_model()
    
    print("\n" + "="*50)
    print("MODEL TEST RESULTS")
    print("="*50)
    
    if model_result:
        print("✓ Model component: WORKING")
        return 0
    else:
        print("✗ Model component: NOT WORKING")
        return 1

if __name__ == "__main__":
    sys.exit(main())
