"""
Performance Monitor
Tracks system performance, detection metrics, and resource usage
"""

import time
import json
import psutil
import threading
import cv2
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Optional
from collections import deque
from ..utils.logger import get_logger


class PerformanceMonitor:
    """Monitors system performance and detection metrics"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_logger('performance_monitor')
        
        # Configuration
        self.enabled = config.get('enabled', True)
        self.metrics_file = config.get('metrics_file', 'logs/metrics.json')
        self.log_interval = config.get('performance_log_interval', 60)
        self.save_detection_images = config.get('save_detection_images', True)
        self.detection_images_path = config.get('detection_images_path', 'logs/detections')
        
        # Metrics storage
        self.inference_times = deque(maxlen=1000)  # Keep last 1000 inference times
        self.detection_history = deque(maxlen=100)  # Keep last 100 detections
        self.fps_history = deque(maxlen=100)  # Keep last 100 FPS measurements
        self.system_stats = deque(maxlen=100)  # Keep last 100 system stat snapshots
        
        # Counters
        self.total_frames_processed = 0
        self.total_detections = 0
        self.true_positives = 0
        self.false_positives = 0
        self.startup_time = time.time()
        
        # Performance thresholds
        self.max_inference_time = config.get('max_inference_time', 0.1)  # 100ms
        self.min_fps = config.get('min_fps', 10.0)
        self.max_cpu_usage = config.get('max_cpu_usage', 80.0)  # 80%
        self.max_memory_usage = config.get('max_memory_usage', 80.0)  # 80%
        
        # Threading
        self.monitoring_thread = None
        self.running = False
        
        # Create directories
        if self.save_detection_images:
            Path(self.detection_images_path).mkdir(parents=True, exist_ok=True)
        Path(self.metrics_file).parent.mkdir(parents=True, exist_ok=True)
        
        if not self.enabled:
            self.logger.info("Performance monitoring disabled")
        else:
            self.logger.info("Performance monitor initialized")
    
    def start_monitoring(self):
        """Start performance monitoring in background thread"""
        if not self.enabled or self.running:
            return
        
        self.running = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        self.logger.info("Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.running = False
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5)
        self.logger.info("Performance monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                # Collect system stats
                self.collect_system_stats()
                
                # Save metrics to file
                self.save_metrics()
                
                # Check for performance issues
                self._check_performance_alerts()
                
                time.sleep(self.log_interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.log_interval)
    
    def update_metrics(self, inference_time: float, detections_count: int, bus_detected: bool = False):
        """Update performance metrics"""
        if not self.enabled:
            return
        
        # Update counters
        self.total_frames_processed += 1
        self.total_detections += detections_count
        
        # Store inference time
        self.inference_times.append(inference_time)
        
        # Calculate and store FPS
        if inference_time > 0:
            fps = 1.0 / inference_time
            self.fps_history.append(fps)
        
        # Log detection
        if bus_detected:
            self._log_bus_detection()
    
    def log_detection(self, detection: Dict[str, Any], frame: Optional[np.ndarray] = None):
        """Log a specific detection with details"""
        if not self.enabled:
            return
        
        detection_data = {
            'timestamp': time.time(),
            'confidence': detection.get('confidence', 0),
            'class_name': detection.get('class_name', 'unknown'),
            'bbox': detection.get('bbox', []),
            'frame_number': self.total_frames_processed
        }
        
        self.detection_history.append(detection_data)
        
        # Save detection image if enabled
        if self.save_detection_images and frame is not None:
            self._save_detection_image(detection, frame)
        
        self.logger.debug(f"Logged detection: {detection_data}")
    
    def _log_bus_detection(self):
        """Log bus detection event"""
        self.true_positives += 1  # Assuming all detections are true positives for now
        
    def _save_detection_image(self, detection: Dict[str, Any], frame: np.ndarray):
        """Save image with detection bounding box"""
        try:
            timestamp = int(time.time())
            filename = f"detection_{timestamp}_{detection.get('confidence', 0):.2f}.jpg"
            filepath = Path(self.detection_images_path) / filename
            
            # Draw bounding box on frame
            annotated_frame = frame.copy()
            bbox = detection.get('bbox', [])
            
            if len(bbox) == 4:
                x1, y1, x2, y2 = map(int, bbox)
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # Add label
                label = f"{detection.get('class_name', 'unknown')}: {detection.get('confidence', 0):.2f}"
                cv2.putText(annotated_frame, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            
            # Save image
            cv2.imwrite(str(filepath), annotated_frame)
            self.logger.debug(f"Saved detection image: {filename}")
            
        except Exception as e:
            self.logger.error(f"Error saving detection image: {e}")
    
    def collect_system_stats(self):
        """Collect current system statistics"""
        if not self.enabled:
            return
        
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available = memory.available
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # Process-specific stats
            process = psutil.Process()
            process_memory = process.memory_info().rss / 1024 / 1024  # MB
            process_cpu = process.cpu_percent()
            
            # Temperature (if available)
            temperature = None
            try:
                temps = psutil.sensors_temperatures()
                if temps:
                    # Get first available temperature sensor
                    for name, entries in temps.items():
                        if entries:
                            temperature = entries[0].current
                            break
            except:
                pass
            
            stats = {
                'timestamp': time.time(),
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'memory_available_mb': memory_available / 1024 / 1024,
                'disk_percent': disk_percent,
                'process_memory_mb': process_memory,
                'process_cpu_percent': process_cpu,
                'temperature_celsius': temperature
            }
            
            self.system_stats.append(stats)
            
        except Exception as e:
            self.logger.error(f"Error collecting system stats: {e}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get current performance summary"""
        try:
            current_time = time.time()
            uptime = current_time - self.startup_time
            
            # Inference statistics
            if self.inference_times:
                avg_inference_time = sum(self.inference_times) / len(self.inference_times)
                max_inference_time = max(self.inference_times)
                min_inference_time = min(self.inference_times)
            else:
                avg_inference_time = max_inference_time = min_inference_time = 0
            
            # FPS statistics
            if self.fps_history:
                avg_fps = sum(self.fps_history) / len(self.fps_history)
                max_fps = max(self.fps_history)
                min_fps = min(self.fps_history)
            else:
                avg_fps = max_fps = min_fps = 0
            
            # Detection statistics
            detection_rate = self.total_detections / max(self.total_frames_processed, 1)
            
            # System statistics
            latest_stats = self.system_stats[-1] if self.system_stats else {}
            
            summary = {
                'uptime_seconds': uptime,
                'total_frames_processed': self.total_frames_processed,
                'total_detections': self.total_detections,
                'true_positives': self.true_positives,
                'false_positives': self.false_positives,
                'detection_rate': detection_rate,
                'inference_stats': {
                    'avg_time_ms': avg_inference_time * 1000,
                    'max_time_ms': max_inference_time * 1000,
                    'min_time_ms': min_inference_time * 1000
                },
                'fps_stats': {
                    'avg_fps': avg_fps,
                    'max_fps': max_fps,
                    'min_fps': min_fps
                },
                'system_stats': latest_stats,
                'timestamp': current_time
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generating performance summary: {e}")
            return {}
    
    def save_metrics(self):
        """Save metrics to file"""
        try:
            summary = self.get_performance_summary()
            
            # Load existing metrics or create new
            metrics_data = []
            if Path(self.metrics_file).exists():
                try:
                    with open(self.metrics_file, 'r') as f:
                        metrics_data = json.load(f)
                except:
                    metrics_data = []
            
            # Add current summary
            metrics_data.append(summary)
            
            # Keep only recent metrics (last 1000 entries)
            if len(metrics_data) > 1000:
                metrics_data = metrics_data[-1000:]
            
            # Save to file
            with open(self.metrics_file, 'w') as f:
                json.dump(metrics_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error saving metrics: {e}")
    
    def log_system_stats(self):
        """Log current system stats"""
        try:
            summary = self.get_performance_summary()
            
            self.logger.info(
                f"Performance Stats - "
                f"FPS: {summary.get('fps_stats', {}).get('avg_fps', 0):.1f}, "
                f"Inference: {summary.get('inference_stats', {}).get('avg_time_ms', 0):.1f}ms, "
                f"CPU: {summary.get('system_stats', {}).get('cpu_percent', 0):.1f}%, "
                f"Memory: {summary.get('system_stats', {}).get('memory_percent', 0):.1f}%, "
                f"Detections: {summary.get('total_detections', 0)}"
            )
            
        except Exception as e:
            self.logger.error(f"Error logging system stats: {e}")
    
    def _check_performance_alerts(self):
        """Check for performance issues and log alerts"""
        try:
            summary = self.get_performance_summary()
            
            # Check inference time
            avg_inference_ms = summary.get('inference_stats', {}).get('avg_time_ms', 0)
            if avg_inference_ms > self.max_inference_time * 1000:
                self.logger.warning(f"High inference time detected: {avg_inference_ms:.1f}ms")
            
            # Check FPS
            avg_fps = summary.get('fps_stats', {}).get('avg_fps', 0)
            if avg_fps < self.min_fps and avg_fps > 0:
                self.logger.warning(f"Low FPS detected: {avg_fps:.1f}")
            
            # Check CPU usage
            cpu_percent = summary.get('system_stats', {}).get('cpu_percent', 0)
            if cpu_percent > self.max_cpu_usage:
                self.logger.warning(f"High CPU usage: {cpu_percent:.1f}%")
            
            # Check memory usage
            memory_percent = summary.get('system_stats', {}).get('memory_percent', 0)
            if memory_percent > self.max_memory_usage:
                self.logger.warning(f"High memory usage: {memory_percent:.1f}%")
            
            # Check temperature
            temperature = summary.get('system_stats', {}).get('temperature_celsius')
            if temperature and temperature > 80:  # 80°C threshold
                self.logger.warning(f"High system temperature: {temperature:.1f}°C")
                
        except Exception as e:
            self.logger.error(f"Error checking performance alerts: {e}")
    
    def get_detection_accuracy(self) -> Dict[str, float]:
        """Calculate detection accuracy metrics"""
        try:
            if self.true_positives + self.false_positives == 0:
                return {'precision': 0.0, 'total_detections': 0}
            
            precision = self.true_positives / (self.true_positives + self.false_positives)
            
            return {
                'precision': precision,
                'true_positives': self.true_positives,
                'false_positives': self.false_positives,
                'total_detections': self.true_positives + self.false_positives
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating accuracy: {e}")
            return {'precision': 0.0, 'total_detections': 0}
    
    def reset_metrics(self):
        """Reset all performance metrics"""
        self.inference_times.clear()
        self.detection_history.clear()
        self.fps_history.clear()
        self.system_stats.clear()
        
        self.total_frames_processed = 0
        self.total_detections = 0
        self.true_positives = 0
        self.false_positives = 0
        self.startup_time = time.time()
        
        self.logger.info("Performance metrics reset")
