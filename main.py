#!/usr/bin/env python3
"""
VisionAI4SchoolBus - Main Application Entry Point
Real-time school bus detection with home automation integration
"""

import sys
import os
import signal
import logging
import threading
import time
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

class SchoolBusDetectionSystem:
    """Main application class for school bus detection system"""
    
    def __init__(self, config_path='config/config.yaml'):
        self.config_path = config_path
        self.config = None
        self.logger = None
        self.running = False
        
        # Core components
        self.camera_manager = None
        self.detector = None
        self.mqtt_client = None
        self.ha_controller = None
        self.performance_monitor = None
        
        # Threading
        self.detection_thread = None
        self.monitoring_thread = None
        
        # Detection state
        self.last_detection_time = 0
        self.detection_cooldown = 30  # seconds
        self.devices_activated = False
        self.activation_start_time = 0
        
    def initialize(self):
        """Initialize all system components"""
        try:
            # Load configuration
            self.config = ConfigManager(self.config_path)
            
            # Setup logging
            self.logger = setup_logging(self.config.get('logging', {}))
            self.logger.info("Starting VisionAI4SchoolBus System")
            
            # Initialize performance monitor
            self.performance_monitor = PerformanceMonitor(self.config.get('monitoring', {}))
            
            # Initialize camera
            camera_config = self.config.get('camera', {})
            self.camera_manager = CameraManager(camera_config)
            if not self.camera_manager.initialize():
                raise RuntimeError("Failed to initialize camera")
            
            # Initialize Hailo detector
            detection_config = self.config.get('detection', {})
            self.detector = HailoDetector(detection_config)
            if not self.detector.initialize():
                raise RuntimeError("Failed to initialize Hailo detector")
            
            # Initialize MQTT client
            mqtt_config = self.config.get('mqtt', {})
            self.mqtt_client = MQTTClient(mqtt_config)
            if not self.mqtt_client.connect():
                self.logger.warning("Failed to connect to MQTT broker - continuing without MQTT")
            
            # Initialize Home Assistant controller
            ha_config = self.config.get('home_assistant', {})
            self.ha_controller = HomeAssistantController(self.mqtt_client, ha_config)
            
            # Get detection parameters
            self.detection_cooldown = self.config.get('detection.cooldown_seconds', 30)
            
            self.logger.info("All components initialized successfully")
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Initialization failed: {e}")
            else:
                print(f"Initialization failed: {e}")
            return False
    
    def run_detection_loop(self):
        """Main detection loop running in separate thread"""
        self.logger.info("Starting detection loop")
        
        while self.running:
            try:
                # Capture frame
                frame = self.camera_manager.get_frame()
                if frame is None:
                    time.sleep(0.1)
                    continue
                
                # Run detection
                start_time = time.time()
                detections = self.detector.detect(frame)
                inference_time = time.time() - start_time
                
                # Process detections
                school_bus_detected = self.process_detections(detections, frame)
                
                # Update performance metrics
                self.performance_monitor.update_metrics(
                    inference_time=inference_time,
                    detections_count=len(detections),
                    bus_detected=school_bus_detected
                )
                
                # Handle device activation/deactivation
                self.handle_device_control(school_bus_detected)
                
                # Small delay to prevent CPU overload
                time.sleep(0.05)
                
            except Exception as e:
                self.logger.error(f"Error in detection loop: {e}")
                time.sleep(1)
    
    def process_detections(self, detections, frame):
        """Process detection results and filter for school buses"""
        school_bus_detected = False
        current_time = time.time()
        
        for detection in detections:
            if self.is_school_bus_detection(detection):
                # Check cooldown period
                if current_time - self.last_detection_time > self.detection_cooldown:
                    school_bus_detected = True
                    self.last_detection_time = current_time
                    
                    self.logger.info(f"School bus detected! Confidence: {detection['confidence']:.2f}")
                    
                    # Log detection details
                    self.performance_monitor.log_detection(detection, frame)
                    
                    # Send MQTT notification if available
                    if self.mqtt_client and self.mqtt_client.is_connected():
                        self.mqtt_client.publish_detection(detection)
                
                break
        
        return school_bus_detected
    
    def is_school_bus_detection(self, detection):
        """Determine if detection is a school bus"""
        # Check if it's a bus class
        if detection.get('class_name', '').lower() not in ['bus', 'school_bus']:
            return False
        
        # Check confidence threshold
        min_confidence = self.config.get('detection.min_confidence', 0.7)
        if detection.get('confidence', 0) < min_confidence:
            return False
        
        # Check size constraints (school buses are typically large)
        bbox = detection.get('bbox', [0, 0, 0, 0])
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        min_size = self.config.get('detection.min_bus_size', 0.1)  # 10% of image
        
        if width * height < min_size:
            return False
        
        # Additional school bus specific checks could be added here
        # (color detection, text recognition, etc.)
        
        return True
    
    def handle_device_control(self, bus_detected):
        """Handle smart device activation/deactivation"""
        current_time = time.time()
        activation_duration = self.config.get('automation.activation_duration_seconds', 300)  # 5 minutes
        
        if bus_detected and not self.devices_activated:
            # Activate devices
            self.logger.info("Activating smart devices - school bus detected")
            self.ha_controller.activate_devices()
            self.devices_activated = True
            self.activation_start_time = current_time
            
        elif self.devices_activated:
            # Check if we should deactivate
            if current_time - self.activation_start_time > activation_duration:
                self.logger.info("Deactivating smart devices - timeout reached")
                self.ha_controller.deactivate_devices()
                self.devices_activated = False
    
    def run_monitoring_loop(self):
        """Performance monitoring loop"""
        while self.running:
            try:
                self.performance_monitor.log_system_stats()
                time.sleep(60)  # Log every minute
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)
    
    def start(self):
        """Start the detection system"""
        if not self.initialize():
            return False
        
        self.running = True
        
        # Start detection thread
        self.detection_thread = threading.Thread(target=self.run_detection_loop)
        self.detection_thread.daemon = True
        self.detection_thread.start()
        
        # Start monitoring thread
        self.monitoring_thread = threading.Thread(target=self.run_monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        self.logger.info("School bus detection system started")
        return True
    
    def stop(self):
        """Stop the detection system"""
        self.logger.info("Stopping school bus detection system")
        self.running = False
        
        # Wait for threads to finish
        if self.detection_thread and self.detection_thread.is_alive():
            self.detection_thread.join(timeout=5)
        
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5)
        
        # Cleanup resources
        if self.camera_manager:
            self.camera_manager.cleanup()
        
        if self.detector:
            self.detector.cleanup()
        
        if self.mqtt_client:
            self.mqtt_client.disconnect()
        
        # Deactivate any active devices
        if self.devices_activated and self.ha_controller:
            self.ha_controller.deactivate_devices()
        
        self.logger.info("System stopped")

def signal_handler(signum, frame):
    """Handle system signals for graceful shutdown"""
    print("\nReceived shutdown signal. Stopping system...")
    global app
    if app:
        app.stop()
    sys.exit(0)

def main():
    """Main entry point"""
    global app
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Parse command line arguments
    config_path = 'config/config.yaml'
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    
    # Create and start application
    app = SchoolBusDetectionSystem(config_path)
    
    if app.start():
        try:
            # Keep main thread alive
            while app.running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            app.stop()
    else:
        print("Failed to start application")
        sys.exit(1)

if __name__ == "__main__":
    main()
