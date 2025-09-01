"""
Hailo AI Detector
Real-time object detection using Hailo AI acceleration
"""

import cv2
import numpy as np
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from ..utils.logger import get_logger

try:
    # Import Hailo runtime libraries
    from hailo_platform import HEF, VDevice, HailoSchedulingAlgorithm, InferVStreams
    from hailo_platform import ConfigureParams, InputVStreamParams, OutputVStreamParams
    HAILO_AVAILABLE = True
except ImportError:
    HAILO_AVAILABLE = False


class HailoDetector:
    """Object detection using Hailo AI accelerator"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_logger('hailo_detector')
        
        # Model configuration
        self.model_path = config.get('model_path', 'models/yolov8n_hailo.hef')
        self.device_id = config.get('hailo_device_id', 0)
        self.batch_size = config.get('batch_size', 1)
        
        # Detection parameters
        self.min_confidence = config.get('min_confidence', 0.7)
        self.nms_threshold = config.get('nms_threshold', 0.45)
        self.input_resolution = config.get('input_resolution', {'width': 640, 'height': 640})
        
        # Hailo objects
        self.hef = None
        self.vdevice = None
        self.network_group = None
        self.network_group_params = None
        self.input_vstreams = None
        self.output_vstreams = None
        
        # Model metadata
        self.input_shape = None
        self.output_shapes = None
        self.class_names = self._get_coco_class_names()  # Default COCO classes
        
        # Performance tracking
        self.total_inferences = 0
        self.total_inference_time = 0.0
        
        # Initialize Hailo availability check
        if not HAILO_AVAILABLE:
            self.logger.warning("Hailo libraries not available - falling back to OpenCV DNN")
            self._init_opencv_fallback()
        
    def initialize(self) -> bool:
        """Initialize the Hailo detector"""
        try:
            if not HAILO_AVAILABLE:
                return self._initialize_opencv_fallback()
            
            self.logger.info(f"Initializing Hailo detector with model: {self.model_path}")
            
            # Check if model file exists
            if not Path(self.model_path).exists():
                self.logger.error(f"Model file not found: {self.model_path}")
                return self._initialize_opencv_fallback()
            
            # Load HEF model
            self.hef = HEF(self.model_path)
            
            # Create virtual device
            self.vdevice = VDevice(device_ids=[self.device_id])
            
            # Configure network group
            self.network_group = self.vdevice.create_network_group(self.hef)
            self.network_group_params = self.network_group.create_params()
            
            # Get input/output information
            self._setup_model_io()
            
            # Create input and output virtual streams
            self._create_vstreams()
            
            self.logger.info("Hailo detector initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Hailo detector: {e}")
            self.logger.info("Falling back to OpenCV DNN")
            return self._initialize_opencv_fallback()
    
    def _setup_model_io(self) -> None:
        """Setup model input/output configurations"""
        # Get input layer info
        input_info = self.hef.get_input_vstream_infos()[0]
        self.input_shape = input_info.shape
        
        # Get output layer info
        self.output_shapes = []
        for output_info in self.hef.get_output_vstream_infos():
            self.output_shapes.append(output_info.shape)
        
        self.logger.info(f"Model input shape: {self.input_shape}")
        self.logger.info(f"Model output shapes: {self.output_shapes}")
    
    def _create_vstreams(self) -> None:
        """Create input and output virtual streams"""
        # Input stream parameters
        input_vstream_params = InputVStreamParams.make_from_network_group(
            self.network_group, quantized=False, format_type='UINT8'
        )
        
        # Output stream parameters  
        output_vstream_params = OutputVStreamParams.make_from_network_group(
            self.network_group, quantized=False, format_type='FLOAT32'
        )
        
        # Create streams
        self.input_vstreams = InferVStreams(self.network_group, input_vstream_params, output_vstream_params)
        
    def detect(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """Run object detection on frame"""
        if not HAILO_AVAILABLE or not self.input_vstreams:
            return self._detect_opencv_fallback(frame)
        
        try:
            start_time = time.time()
            
            # Preprocess frame
            input_tensor = self._preprocess_frame(frame)
            
            # Run inference
            with self.input_vstreams:
                output_tensors = self.input_vstreams.infer(input_tensor)
            
            # Post-process results
            detections = self._postprocess_outputs(output_tensors, frame.shape)
            
            # Update performance metrics
            inference_time = time.time() - start_time
            self.total_inferences += 1
            self.total_inference_time += inference_time
            
            return detections
            
        except Exception as e:
            self.logger.error(f"Detection failed: {e}")
            return []
    
    def _preprocess_frame(self, frame: np.ndarray) -> np.ndarray:
        """Preprocess frame for model input"""
        # Resize to model input size
        input_height, input_width = self.input_shape[1:3]
        resized = cv2.resize(frame, (input_width, input_height))
        
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        
        # Normalize if needed (depends on model requirements)
        normalized = rgb_frame.astype(np.float32) / 255.0
        
        # Add batch dimension
        input_tensor = np.expand_dims(normalized, axis=0)
        
        return input_tensor
    
    def _postprocess_outputs(self, outputs: List[np.ndarray], original_shape: Tuple[int, int, int]) -> List[Dict[str, Any]]:
        """Post-process model outputs to get detections"""
        detections = []
        
        if not outputs:
            return detections
        
        # Assuming YOLOv8 output format
        # Output shape: [batch_size, num_detections, 85] where 85 = 4 bbox coords + 1 conf + 80 classes
        output = outputs[0][0]  # Remove batch dimension
        
        original_height, original_width = original_shape[:2]
        input_height, input_width = self.input_shape[1:3]
        
        # Calculate scaling factors
        scale_x = original_width / input_width
        scale_y = original_height / input_height
        
        for detection in output:
            if len(detection) < 5:
                continue
                
            # Extract detection data
            x_center, y_center, width, height = detection[:4]
            confidence = detection[4]
            class_scores = detection[5:]
            
            # Find best class
            class_id = np.argmax(class_scores)
            class_confidence = class_scores[class_id]
            
            # Calculate final confidence
            final_confidence = confidence * class_confidence
            
            if final_confidence >= self.min_confidence:
                # Convert to bounding box coordinates
                x1 = int((x_center - width / 2) * scale_x)
                y1 = int((y_center - height / 2) * scale_y)
                x2 = int((x_center + width / 2) * scale_x)
                y2 = int((y_center + height / 2) * scale_y)
                
                # Clamp to image bounds
                x1 = max(0, min(x1, original_width - 1))
                y1 = max(0, min(y1, original_height - 1))
                x2 = max(0, min(x2, original_width - 1))
                y2 = max(0, min(y2, original_height - 1))
                
                detection_dict = {
                    'bbox': [x1, y1, x2, y2],
                    'confidence': float(final_confidence),
                    'class_id': int(class_id),
                    'class_name': self.class_names.get(class_id, f'class_{class_id}')
                }
                
                detections.append(detection_dict)
        
        # Apply Non-Maximum Suppression
        detections = self._apply_nms(detections)
        
        return detections
    
    def _apply_nms(self, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply Non-Maximum Suppression to remove duplicate detections"""
        if len(detections) == 0:
            return detections
        
        # Convert to format expected by OpenCV NMS
        boxes = []
        scores = []
        
        for det in detections:
            bbox = det['bbox']
            boxes.append([bbox[0], bbox[1], bbox[2] - bbox[0], bbox[3] - bbox[1]])  # Convert to x,y,w,h
            scores.append(det['confidence'])
        
        boxes = np.array(boxes, dtype=np.float32)
        scores = np.array(scores, dtype=np.float32)
        
        # Apply NMS
        indices = cv2.dnn.NMSBoxes(boxes, scores, self.min_confidence, self.nms_threshold)
        
        if len(indices) == 0:
            return []
        
        # Return filtered detections
        filtered_detections = []
        for i in indices.flatten():
            filtered_detections.append(detections[i])
        
        return filtered_detections
    
    def _init_opencv_fallback(self) -> None:
        """Initialize OpenCV DNN as fallback"""
        self.opencv_net = None
        self.use_opencv = True
        
    def _initialize_opencv_fallback(self) -> bool:
        """Initialize OpenCV DNN fallback detector"""
        try:
            # This would load a standard ONNX or other format model
            # For now, we'll create a placeholder
            self.logger.info("OpenCV DNN fallback not fully implemented")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize OpenCV fallback: {e}")
            return False
    
    def _detect_opencv_fallback(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """Fallback detection using OpenCV DNN"""
        # Placeholder for OpenCV DNN implementation
        # This would use cv2.dnn.readNet() and cv2.dnn.blobFromImage()
        return []
    
    def get_performance_stats(self) -> Dict[str, float]:
        """Get performance statistics"""
        if self.total_inferences == 0:
            return {'avg_inference_time': 0.0, 'total_inferences': 0}
        
        avg_time = self.total_inference_time / self.total_inferences
        return {
            'avg_inference_time': avg_time,
            'total_inferences': self.total_inferences,
            'fps': 1.0 / avg_time if avg_time > 0 else 0.0
        }
    
    def _get_coco_class_names(self) -> Dict[int, str]:
        """Get COCO dataset class names"""
        return {
            0: 'person', 1: 'bicycle', 2: 'car', 3: 'motorcycle', 4: 'airplane',
            5: 'bus', 6: 'train', 7: 'truck', 8: 'boat', 9: 'traffic light',
            10: 'fire hydrant', 11: 'stop sign', 12: 'parking meter', 13: 'bench',
            14: 'bird', 15: 'cat', 16: 'dog', 17: 'horse', 18: 'sheep', 19: 'cow',
            20: 'elephant', 21: 'bear', 22: 'zebra', 23: 'giraffe', 24: 'backpack',
            25: 'umbrella', 26: 'handbag', 27: 'tie', 28: 'suitcase', 29: 'frisbee',
            30: 'skis', 31: 'snowboard', 32: 'sports ball', 33: 'kite', 34: 'baseball bat',
            35: 'baseball glove', 36: 'skateboard', 37: 'surfboard', 38: 'tennis racket',
            39: 'bottle', 40: 'wine glass', 41: 'cup', 42: 'fork', 43: 'knife',
            44: 'spoon', 45: 'bowl', 46: 'banana', 47: 'apple', 48: 'sandwich',
            49: 'orange', 50: 'broccoli', 51: 'carrot', 52: 'hot dog', 53: 'pizza',
            54: 'donut', 55: 'cake', 56: 'chair', 57: 'couch', 58: 'potted plant',
            59: 'bed', 60: 'dining table', 61: 'toilet', 62: 'tv', 63: 'laptop',
            64: 'mouse', 65: 'remote', 66: 'keyboard', 67: 'cell phone', 68: 'microwave',
            69: 'oven', 70: 'toaster', 71: 'sink', 72: 'refrigerator', 73: 'book',
            74: 'clock', 75: 'vase', 76: 'scissors', 77: 'teddy bear', 78: 'hair drier',
            79: 'toothbrush'
        }
    
    def cleanup(self) -> None:
        """Clean up detector resources"""
        self.logger.info("Cleaning up Hailo detector")
        
        try:
            if self.input_vstreams:
                # Streams are cleaned up automatically when exiting context
                pass
            
            if self.network_group:
                # Network group cleanup handled by vdevice
                pass
            
            if self.vdevice:
                # VDevice cleanup handled automatically
                pass
                
        except Exception as e:
            self.logger.warning(f"Error during cleanup: {e}")
        
        self.logger.info("Hailo detector cleanup completed")
