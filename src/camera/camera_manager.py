"""
Camera Management System
Handles USB camera initialization, configuration, and frame capture
"""

import cv2
import numpy as np
import time
import threading
from queue import Queue, Empty
from typing import Optional, Tuple, Dict, Any
from ..utils.logger import get_logger


class CameraManager:
    """Manages USB camera operations for real-time video capture"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_logger('camera')
        
        # Camera parameters
        self.device_id = config.get('device_id', 0)
        self.resolution = config.get('resolution', {'width': 1280, 'height': 720})
        self.fps = config.get('fps', 30)
        self.auto_exposure = config.get('auto_exposure', True)
        self.exposure_value = config.get('exposure_value', 100)
        self.gain = config.get('gain', 1.0)
        self.buffer_size = config.get('buffer_size', 1)
        
        # Camera object and state
        self.cap = None
        self.is_initialized = False
        self.is_capturing = False
        
        # Frame buffer for threading
        self.frame_queue = Queue(maxsize=self.buffer_size)
        self.capture_thread = None
        self.latest_frame = None
        self.frame_lock = threading.Lock()
        
        # Performance metrics
        self.frame_count = 0
        self.last_fps_time = time.time()
        self.current_fps = 0
    
    def initialize(self) -> bool:
        """Initialize camera with specified configuration"""
        try:
            self.logger.info(f"Initializing camera {self.device_id}")
            
            # Create VideoCapture object
            self.cap = cv2.VideoCapture(self.device_id)
            
            if not self.cap.isOpened():
                self.logger.error(f"Failed to open camera {self.device_id}")
                return False
            
            # Configure camera properties
            self._configure_camera()
            
            # Test frame capture
            ret, test_frame = self.cap.read()
            if not ret or test_frame is None:
                self.logger.error("Failed to capture test frame")
                return False
            
            self.logger.info(f"Camera initialized successfully - Resolution: {test_frame.shape[1]}x{test_frame.shape[0]}")
            self.is_initialized = True
            
            # Start capture thread
            self.start_capture()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Camera initialization failed: {e}")
            return False
    
    def _configure_camera(self) -> None:
        """Configure camera properties"""
        try:
            # Set resolution
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution['width'])
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution['height'])
            
            # Set FPS
            self.cap.set(cv2.CAP_PROP_FPS, self.fps)
            
            # Set buffer size (reduce latency)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, self.buffer_size)
            
            # Configure exposure
            if self.auto_exposure:
                self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.75)  # Auto exposure
            else:
                self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)  # Manual exposure
                self.cap.set(cv2.CAP_PROP_EXPOSURE, self.exposure_value)
            
            # Set gain
            self.cap.set(cv2.CAP_PROP_GAIN, self.gain)
            
            # Additional optimizations
            self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
            
            self.logger.info("Camera properties configured")
            
        except Exception as e:
            self.logger.warning(f"Error configuring camera properties: {e}")
    
    def start_capture(self) -> None:
        """Start continuous frame capture in background thread"""
        if self.is_capturing:
            return
        
        self.is_capturing = True
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
        self.logger.info("Frame capture started")
    
    def stop_capture(self) -> None:
        """Stop continuous frame capture"""
        self.is_capturing = False
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=2)
        self.logger.info("Frame capture stopped")
    
    def _capture_loop(self) -> None:
        """Continuous frame capture loop running in background thread"""
        while self.is_capturing and self.cap and self.cap.isOpened():
            try:
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    # Store latest frame thread-safely
                    with self.frame_lock:
                        self.latest_frame = frame.copy()
                    
                    # Update FPS calculation
                    self._update_fps()
                else:
                    time.sleep(0.01)  # Brief pause if capture fails
                    
            except Exception as e:
                self.logger.error(f"Error in capture loop: {e}")
                time.sleep(0.1)
    
    def get_frame(self) -> Optional[np.ndarray]:
        """Get the most recent frame"""
        if not self.is_initialized or not self.is_capturing:
            return None
        
        with self.frame_lock:
            if self.latest_frame is not None:
                return self.latest_frame.copy()
        
        return None
    
    def get_frame_blocking(self, timeout: float = 1.0) -> Optional[np.ndarray]:
        """Get frame with blocking wait and timeout"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            frame = self.get_frame()
            if frame is not None:
                return frame
            time.sleep(0.01)
        
        return None
    
    def _update_fps(self) -> None:
        """Update FPS calculation"""
        self.frame_count += 1
        current_time = time.time()
        
        if current_time - self.last_fps_time >= 1.0:
            self.current_fps = self.frame_count / (current_time - self.last_fps_time)
            self.frame_count = 0
            self.last_fps_time = current_time
    
    def get_fps(self) -> float:
        """Get current FPS"""
        return self.current_fps
    
    def get_resolution(self) -> Tuple[int, int]:
        """Get current camera resolution"""
        if not self.cap or not self.cap.isOpened():
            return (0, 0)
        
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return (width, height)
    
    def is_available(self) -> bool:
        """Check if camera is available and capturing"""
        return self.is_initialized and self.is_capturing and self.cap and self.cap.isOpened()
    
    def adjust_exposure(self, exposure_value: int) -> bool:
        """Adjust camera exposure"""
        try:
            if not self.cap:
                return False
            
            self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)  # Manual mode
            self.cap.set(cv2.CAP_PROP_EXPOSURE, exposure_value)
            self.exposure_value = exposure_value
            
            self.logger.info(f"Exposure adjusted to {exposure_value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to adjust exposure: {e}")
            return False
    
    def adjust_gain(self, gain_value: float) -> bool:
        """Adjust camera gain"""
        try:
            if not self.cap:
                return False
            
            self.cap.set(cv2.CAP_PROP_GAIN, gain_value)
            self.gain = gain_value
            
            self.logger.info(f"Gain adjusted to {gain_value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to adjust gain: {e}")
            return False
    
    def get_camera_info(self) -> Dict[str, Any]:
        """Get current camera information"""
        if not self.cap:
            return {}
        
        return {
            'device_id': self.device_id,
            'resolution': self.get_resolution(),
            'fps': self.get_fps(),
            'exposure': self.cap.get(cv2.CAP_PROP_EXPOSURE) if self.cap else 0,
            'gain': self.cap.get(cv2.CAP_PROP_GAIN) if self.cap else 0,
            'auto_exposure': self.cap.get(cv2.CAP_PROP_AUTO_EXPOSURE) if self.cap else 0,
            'is_capturing': self.is_capturing
        }
    
    def cleanup(self) -> None:
        """Clean up camera resources"""
        self.logger.info("Cleaning up camera resources")
        
        # Stop capture thread
        self.stop_capture()
        
        # Release camera
        if self.cap:
            self.cap.release()
            self.cap = None
        
        self.is_initialized = False
        self.latest_frame = None
        
        self.logger.info("Camera cleanup completed")


def list_available_cameras(max_cameras: int = 10) -> list:
    """List available camera devices"""
    available_cameras = []
    
    for i in range(max_cameras):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, _ = cap.read()
            if ret:
                available_cameras.append(i)
        cap.release()
    
    return available_cameras
