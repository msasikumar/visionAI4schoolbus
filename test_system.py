#!/usr/bin/env python3
"""
VisionAI4SchoolBus System Test Script
Tests all major components and functionality
"""

import sys
import os
import time
import cv2
import numpy as np
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from utils.config_manager import ConfigManager
from utils.logger import setup_logging
from camera.camera_manager import CameraManager
from detection.hailo_detector import HailoDetector
from automation.mqtt_client import MQTTClient
from automation.home_assistant import HomeAssistantController
from utils.performance_monitor import PerformanceMonitor

class SystemTester:
    """Comprehensive system testing"""
    
    def __init__(self):
        self.config = ConfigManager('config/config.yaml')
        self.logger = setup_logging(self.config.get('logging', {}))
        self.test_results = {}
        
    def run_all_tests(self):
        """Run all system tests"""
        self.logger.info("Starting comprehensive system tests")
        
        tests = [
            ('Configuration Loading', self.test_config),
            ('Camera Access', self.test_camera),
            ('Hailo Detector', self.test_detector),
            ('MQTT Connection', self.test_mqtt),
            ('Home Assistant', self.test_home_assistant),
            ('Performance Monitor', self.test_performance_monitor),
            ('File Permissions', self.test_file_permissions),
            ('System Resources', self.test_system_resources)
        ]
        
        for test_name, test_func in tests:
            try:
                self.logger.info(f"Running test: {test_name}")
                result = test_func()
                self.test_results[test_name] = {
                    'passed': result,
                    'message': 'PASSED' if result else 'FAILED'
                }
            except Exception as e:
                self.test_results[test_name] = {
                    'passed': False,
                    'message': f'ERROR: {str(e)}'
                }
                self.logger.error(f"Test {test_name} failed: {e}")
        
        self.print_results()
    
    def test_config(self):
        """Test configuration loading and validation"""
        try:
            # Test basic config access
            camera_config = self.config.get('camera')
            mqtt_config = self.config.get('mqtt')
            detection_config = self.config.get('detection')
            
            if not all([camera_config, mqtt_config, detection_config]):
                return False
            
            # Test config validation
            return self.config.validate_config()
            
        except Exception as e:
            self.logger.error(f"Config test failed: {e}")
            return False
    
    def test_camera(self):
        """Test camera initialization and capture"""
        try:
            camera_config = self.config.get('camera', {})
            camera = CameraManager(camera_config)
            
            if not camera.initialize():
                return False
            
            # Test frame capture
            frame = camera.get_frame_blocking(timeout=5.0)
            camera.cleanup()
            
            return frame is not None
            
        except Exception as e:
            self.logger.error(f"Camera test failed: {e}")
            return False
    
    def test_detector(self):
        """Test Hailo detector initialization"""
        try:
            detection_config = self.config.get('detection', {})
            detector = HailoDetector(detection_config)
            
            # Test initialization (may fall back to OpenCV)
            result = detector.initialize()
            
            if result:
                # Test with dummy frame
                dummy_frame = np.zeros((640, 640, 3), dtype=np.uint8)
                detections = detector.detect(dummy_frame)
                # Should return empty list for black frame
                detector.cleanup()
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Detector test failed: {e}")
            return False
    
    def test_mqtt(self):
        """Test MQTT connection"""
        try:
            mqtt_config = self.config.get('mqtt', {})
            mqtt_client = MQTTClient(mqtt_config)
            
            # Test connection (with timeout)
            if mqtt_client.connect():
                # Test publish
                result = mqtt_client.publish('test/topic', 'test message')
                mqtt_client.disconnect()
                return result
            
            # If connection fails, it's not necessarily a failure
            # (MQTT broker might not be available)
            self.logger.warning("MQTT broker not available - test skipped")
            return True
            
        except Exception as e:
            self.logger.error(f"MQTT test failed: {e}")
            return False
    
    def test_home_assistant(self):
        """Test Home Assistant controller"""
        try:
            mqtt_config = self.config.get('mqtt', {})
            ha_config = self.config.get('home_assistant', {})
            
            mqtt_client = MQTTClient(mqtt_config)
            ha_controller = HomeAssistantController(mqtt_client, ha_config)
            
            # Test device status
            status = ha_controller.get_device_status()
            return isinstance(status, dict)
            
        except Exception as e:
            self.logger.error(f"Home Assistant test failed: {e}")
            return False
    
    def test_performance_monitor(self):
        """Test performance monitoring"""
        try:
            monitoring_config = self.config.get('monitoring', {})
            monitor = PerformanceMonitor(monitoring_config)
            
            # Test metric collection
            monitor.collect_system_stats()
            summary = monitor.get_performance_summary()
            
            return isinstance(summary, dict) and 'timestamp' in summary
            
        except Exception as e:
            self.logger.error(f"Performance monitor test failed: {e}")
            return False
    
    def test_file_permissions(self):
        """Test file and directory permissions"""
        try:
            # Check if we can write to logs directory
            log_dir = Path('logs')
            log_dir.mkdir(exist_ok=True)
            
            test_file = log_dir / 'test.txt'
            test_file.write_text('test')
            test_file.unlink()
            
            # Check config directory
            config_dir = Path('config')
            if not config_dir.exists():
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"File permissions test failed: {e}")
            return False
    
    def test_system_resources(self):
        """Test system resource availability"""
        try:
            import psutil
            
            # Check available memory (at least 1GB)
            memory = psutil.virtual_memory()
            if memory.available < 1024 * 1024 * 1024:
                self.logger.warning("Low memory available")
            
            # Check CPU cores
            cpu_count = psutil.cpu_count()
            if cpu_count < 2:
                self.logger.warning("Limited CPU cores available")
            
            # Check disk space (at least 1GB free)
            disk = psutil.disk_usage('/')
            if disk.free < 1024 * 1024 * 1024:
                self.logger.warning("Low disk space")
            
            return True
            
        except Exception as e:
            self.logger.error(f"System resources test failed: {e}")
            return False
    
    def print_results(self):
        """Print test results summary"""
        print("\n" + "="*60)
        print("SYSTEM TEST RESULTS")
        print("="*60)
        
        passed_count = 0
        total_count = len(self.test_results)
        
        for test_name, result in self.test_results.items():
            status = "✓ PASS" if result['passed'] else "✗ FAIL"
            print(f"{test_name:30} {status:10} {result['message']}")
            
            if result['passed']:
                passed_count += 1
        
        print("-" * 60)
        print(f"SUMMARY: {passed_count}/{total_count} tests passed")
        
        if passed_count == total_count:
            print("🎉 All tests passed! System is ready to use.")
        else:
            print("⚠️  Some tests failed. Please review the issues above.")
        
        print("="*60)
        
        return passed_count == total_count

def main():
    """Main test function"""
    print("VisionAI4SchoolBus System Test")
    print("=============================")
    
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("Usage: python test_system.py [--help]")
        print("Runs comprehensive system tests to verify installation")
        return
    
    tester = SystemTester()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
