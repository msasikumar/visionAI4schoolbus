# API Reference

This document provides comprehensive API documentation for the VisionAI4SchoolBus system components.

## Table of Contents

- [Core Classes](#core-classes)
- [Configuration Manager](#configuration-manager)
- [Camera Manager](#camera-manager)
- [Hailo Detector](#hailo-detector)
- [MQTT Client](#mqtt-client)
- [Home Assistant Controller](#home-assistant-controller)
- [Performance Monitor](#performance-monitor)
- [Utility Functions](#utility-functions)
- [MQTT Message Formats](#mqtt-message-formats)
- [Configuration Schema](#configuration-schema)
- [Error Codes](#error-codes)

## Core Classes

### SchoolBusDetectionSystem

Main application class that orchestrates all system components.

#### Constructor

```python
SchoolBusDetectionSystem(config_path='config/config.yaml')
```

**Parameters:**
- `config_path` (str): Path to configuration file

#### Methods

##### initialize()
```python
def initialize() -> bool
```

Initialize all system components.

**Returns:**
- `bool`: True if initialization successful, False otherwise

**Raises:**
- `RuntimeError`: If critical components fail to initialize

##### start()
```python
def start() -> bool
```

Start the detection system with background threads.

**Returns:**
- `bool`: True if system started successfully

##### stop()
```python
def stop() -> None
```

Stop the detection system and cleanup resources.

##### is_running()
```python
def is_running() -> bool
```

Check if the detection system is currently running.

**Returns:**
- `bool`: True if system is running

#### Properties

```python
@property
def config(self) -> ConfigManager
    """Access to configuration manager"""

@property
def last_detection_time(self) -> float
    """Timestamp of last detection"""

@property
def devices_activated(self) -> bool
    """Current device activation status"""
```

#### Example Usage

```python
from main import SchoolBusDetectionSystem
import time

# Create and initialize system
system = SchoolBusDetectionSystem('config/config.yaml')

if system.initialize():
    system.start()
    
    try:
        while system.is_running():
            time.sleep(1)
    except KeyboardInterrupt:
        system.stop()
else:
    print("Failed to initialize system")
```

## Configuration Manager

### ConfigManager

Handles loading and accessing configuration values with dot notation.

#### Constructor

```python
ConfigManager(config_path: str, template_path: str = None)
```

**Parameters:**
- `config_path` (str): Path to main configuration file
- `template_path` (str, optional): Path to template configuration file

#### Methods

##### get()
```python
def get(self, key: str, default=None) -> Any
```

Get configuration value using dot notation.

**Parameters:**
- `key` (str): Configuration key in dot notation (e.g., 'camera.resolution.width')
- `default`: Default value if key not found

**Returns:**
- `Any`: Configuration value or default

**Example:**
```python
config = ConfigManager('config/config.yaml')

# Get simple values
camera_id = config.get('camera.device_id', 0)
confidence = config.get('detection.min_confidence', 0.7)

# Get complex objects
resolution = config.get('camera.resolution')
# Returns: {'width': 1280, 'height': 720}
```

##### set()
```python
def set(self, key: str, value: Any) -> None
```

Set configuration value using dot notation.

**Parameters:**
- `key` (str): Configuration key in dot notation
- `value` (Any): Value to set

##### reload()
```python
def reload() -> bool
```

Reload configuration from file.

**Returns:**
- `bool`: True if reload successful

##### validate()
```python
def validate() -> List[str]
```

Validate configuration against schema.

**Returns:**
- `List[str]`: List of validation errors (empty if valid)

## Camera Manager

### CameraManager

Handles camera operations and frame capture.

#### Constructor

```python
CameraManager(config: dict)
```

**Parameters:**
- `config` (dict): Camera configuration dictionary

#### Methods

##### initialize()
```python
def initialize() -> bool
```

Initialize camera hardware.

**Returns:**
- `bool`: True if camera initialized successfully

##### get_frame()
```python
def get_frame() -> Optional[np.ndarray]
```

Capture a frame from the camera.

**Returns:**
- `Optional[np.ndarray]`: Camera frame as OpenCV image, None if failed

##### get_frame_async()
```python
async def get_frame_async() -> Optional[np.ndarray]
```

Asynchronously capture a frame from the camera.

**Returns:**
- `Optional[np.ndarray]`: Camera frame as OpenCV image, None if failed

##### set_resolution()
```python
def set_resolution(self, width: int, height: int) -> bool
```

Set camera resolution.

**Parameters:**
- `width` (int): Frame width in pixels
- `height` (int): Frame height in pixels

**Returns:**
- `bool`: True if resolution set successfully

##### set_fps()
```python
def set_fps(self, fps: int) -> bool
```

Set camera frame rate.

**Parameters:**
- `fps` (int): Target frames per second

**Returns:**
- `bool`: True if FPS set successfully

##### get_camera_info()
```python
def get_camera_info() -> dict
```

Get camera information and capabilities.

**Returns:**
- `dict`: Camera information including supported resolutions, formats

##### cleanup()
```python
def cleanup() -> None
```

Release camera resources.

#### Properties

```python
@property
def is_initialized(self) -> bool
    """Check if camera is initialized"""

@property
def current_fps(self) -> float
    """Get current frame rate"""

@property
def frame_count(self) -> int
    """Get total frames captured"""
```

#### Example Usage

```python
from src.camera.camera_manager import CameraManager

config = {
    'device_id': 0,
    'resolution': {'width': 1280, 'height': 720},
    'fps': 30
}

camera = CameraManager(config)

if camera.initialize():
    frame = camera.get_frame()
    if frame is not None:
        print(f"Frame shape: {frame.shape}")
    camera.cleanup()
```

## Hailo Detector

### HailoDetector

AI detection using Hailo NPU acceleration.

#### Constructor

```python
HailoDetector(config: dict)
```

**Parameters:**
- `config` (dict): Detection configuration dictionary

#### Methods

##### initialize()
```python
def initialize() -> bool
```

Initialize Hailo device and load model.

**Returns:**
- `bool`: True if initialization successful

##### detect()
```python
def detect(self, frame: np.ndarray) -> List[Detection]
```

Run detection on input frame.

**Parameters:**
- `frame` (np.ndarray): Input image as OpenCV array

**Returns:**
- `List[Detection]`: List of detection objects

##### detect_batch()
```python
def detect_batch(self, frames: List[np.ndarray]) -> List[List[Detection]]
```

Run batch detection on multiple frames.

**Parameters:**
- `frames` (List[np.ndarray]): List of input images

**Returns:**
- `List[List[Detection]]`: List of detection lists for each frame

##### preprocess_frame()
```python
def preprocess_frame(self, frame: np.ndarray) -> np.ndarray
```

Preprocess frame for model input.

**Parameters:**
- `frame` (np.ndarray): Input frame

**Returns:**
- `np.ndarray`: Preprocessed frame

##### postprocess_results()
```python
def postprocess_results(self, raw_output: Any, frame_shape: Tuple[int, int]) -> List[Detection]
```

Postprocess raw model output to detection objects.

**Parameters:**
- `raw_output` (Any): Raw model inference output
- `frame_shape` (Tuple[int, int]): Original frame dimensions

**Returns:**
- `List[Detection]`: Processed detections

##### get_model_info()
```python
def get_model_info() -> dict
```

Get loaded model information.

**Returns:**
- `dict`: Model metadata and specifications

##### cleanup()
```python
def cleanup() -> None
```

Release Hailo device resources.

#### Detection Object

```python
class Detection:
    """Single detection result"""
    
    def __init__(self):
        self.class_id: int = 0
        self.class_name: str = ""
        self.confidence: float = 0.0
        self.bbox: List[float] = [0, 0, 0, 0]  # [x1, y1, x2, y2]
        self.center: Tuple[float, float] = (0.0, 0.0)
        self.area: float = 0.0
        self.timestamp: float = 0.0
    
    def to_dict(self) -> dict:
        """Convert detection to dictionary"""
        return {
            'class_id': self.class_id,
            'class_name': self.class_name,
            'confidence': self.confidence,
            'bbox': self.bbox,
            'center': self.center,
            'area': self.area,
            'timestamp': self.timestamp
        }
```

#### Example Usage

```python
from src.detection.hailo_detector import HailoDetector
import cv2

config = {
    'model_path': 'models/yolov8n_hailo.hef',
    'min_confidence': 0.7,
    'input_resolution': {'width': 640, 'height': 640}
}

detector = HailoDetector(config)

if detector.initialize():
    # Load test image
    frame = cv2.imread('test_image.jpg')
    
    # Run detection
    detections = detector.detect(frame)
    
    # Process results
    for det in detections:
        print(f"Detected {det.class_name} with confidence {det.confidence:.2f}")
        
    detector.cleanup()
```

## MQTT Client

### MQTTClient

MQTT communication for system integration.

#### Constructor

```python
MQTTClient(config: dict)
```

**Parameters:**
- `config` (dict): MQTT configuration dictionary

#### Methods

##### connect()
```python
def connect() -> bool
```

Connect to MQTT broker.

**Returns:**
- `bool`: True if connection successful

##### disconnect()
```python
def disconnect() -> None
```

Disconnect from MQTT broker.

##### publish()
```python
def publish(self, topic: str, payload: str, qos: int = 1, retain: bool = False) -> bool
```

Publish message to MQTT topic.

**Parameters:**
- `topic` (str): MQTT topic
- `payload` (str): Message payload
- `qos` (int): Quality of Service level (0, 1, 2)
- `retain` (bool): Retain message flag

**Returns:**
- `bool`: True if publish successful

##### publish_detection()
```python
def publish_detection(self, detection: Detection) -> bool
```

Publish detection event with standardized format.

**Parameters:**
- `detection` (Detection): Detection object

**Returns:**
- `bool`: True if publish successful

##### publish_status()
```python
def publish_status(self, status: dict) -> bool
```

Publish system status information.

**Parameters:**
- `status` (dict): Status information

**Returns:**
- `bool`: True if publish successful

##### subscribe()
```python
def subscribe(self, topic: str, callback: Callable, qos: int = 1) -> bool
```

Subscribe to MQTT topic with callback.

**Parameters:**
- `topic` (str): MQTT topic pattern
- `callback` (Callable): Callback function for messages
- `qos` (int): Quality of Service level

**Returns:**
- `bool`: True if subscription successful

##### is_connected()
```python
def is_connected() -> bool
```

Check MQTT connection status.

**Returns:**
- `bool`: True if connected

#### Example Usage

```python
from src.automation.mqtt_client import MQTTClient

config = {
    'broker_host': 'localhost',
    'broker_port': 1883,
    'client_id': 'visionai4schoolbus',
    'topic_prefix': 'schoolbus'
}

mqtt_client = MQTTClient(config)

if mqtt_client.connect():
    # Publish detection
    detection_data = {
        'class_name': 'bus',
        'confidence': 0.85,
        'timestamp': time.time()
    }
    mqtt_client.publish('schoolbus/detection', json.dumps(detection_data))
    
    # Subscribe to commands
    def command_callback(topic, payload):
        print(f"Received command: {payload}")
    
    mqtt_client.subscribe('schoolbus/command', command_callback)
```

## Home Assistant Controller

### HomeAssistantController

Controls Home Assistant devices via MQTT.

#### Constructor

```python
HomeAssistantController(mqtt_client: MQTTClient, config: dict)
```

**Parameters:**
- `mqtt_client` (MQTTClient): MQTT client instance
- `config` (dict): Home Assistant configuration

#### Methods

##### activate_devices()
```python
def activate_devices(self) -> bool
```

Activate configured devices.

**Returns:**
- `bool`: True if activation commands sent successfully

##### deactivate_devices()
```python
def deactivate_devices() -> bool
```

Deactivate configured devices.

**Returns:**
- `bool`: True if deactivation commands sent successfully

##### control_light()
```python
def control_light(self, entity_id: str, state: str, brightness: int = None, color_temp: int = None) -> bool
```

Control a light entity.

**Parameters:**
- `entity_id` (str): Home Assistant entity ID
- `state` (str): 'on' or 'off'
- `brightness` (int, optional): Brightness level (0-255)
- `color_temp` (int, optional): Color temperature in Kelvin

**Returns:**
- `bool`: True if command sent successfully

##### control_switch()
```python
def control_switch(self, entity_id: str, state: str) -> bool
```

Control a switch entity.

**Parameters:**
- `entity_id` (str): Home Assistant entity ID
- `state` (str): 'on' or 'off'

**Returns:**
- `bool`: True if command sent successfully

##### send_announcement()
```python
def send_announcement(self, message: str, entity_id: str = None) -> bool
```

Send voice announcement.

**Parameters:**
- `message` (str): Announcement text
- `entity_id` (str, optional): Specific TTS entity

**Returns:**
- `bool`: True if announcement sent successfully

##### register_discovery()
```python
def register_discovery(self) -> bool
```

Register device for Home Assistant MQTT discovery.

**Returns:**
- `bool`: True if registration successful

## Performance Monitor

### PerformanceMonitor

System performance monitoring and metrics collection.

#### Constructor

```python
PerformanceMonitor(config: dict)
```

**Parameters:**
- `config` (dict): Monitoring configuration

#### Methods

##### update_metrics()
```python
def update_metrics(self, **kwargs) -> None
```

Update performance metrics.

**Parameters:**
- `**kwargs`: Metric name-value pairs

##### get_metrics()
```python
def get_metrics(self) -> dict
```

Get current performance metrics.

**Returns:**
- `dict`: Current metrics

##### log_detection()
```python
def log_detection(self, detection: Detection, frame: np.ndarray = None) -> None
```

Log detection event with optional image saving.

**Parameters:**
- `detection` (Detection): Detection object
- `frame` (np.ndarray, optional): Frame image

##### log_system_stats()
```python
def log_system_stats() -> None
```

Log system resource usage statistics.

##### get_system_info()
```python
def get_system_info() -> dict
```

Get system information.

**Returns:**
- `dict`: System information including CPU, memory, temperature

##### export_metrics()
```python
def export_metrics(self, format: str = 'json') -> str
```

Export metrics in specified format.

**Parameters:**
- `format` (str): Export format ('json', 'csv')

**Returns:**
- `str`: Exported metrics data

## Utility Functions

### Logger Setup

```python
def setup_logging(config: dict) -> logging.Logger
```

Set up logging configuration.

**Parameters:**
- `config` (dict): Logging configuration

**Returns:**
- `logging.Logger`: Configured logger instance

### Image Processing

```python
def resize_frame(frame: np.ndarray, target_size: Tuple[int, int]) -> np.ndarray
```

Resize frame while maintaining aspect ratio.

**Parameters:**
- `frame` (np.ndarray): Input frame
- `target_size` (Tuple[int, int]): Target dimensions

**Returns:**
- `np.ndarray`: Resized frame

```python
def draw_detection(frame: np.ndarray, detection: Detection, color: Tuple[int, int, int] = (0, 255, 0)) -> np.ndarray
```

Draw detection bounding box on frame.

**Parameters:**
- `frame` (np.ndarray): Input frame
- `detection` (Detection): Detection object
- `color` (Tuple[int, int, int]): Box color in BGR

**Returns:**
- `np.ndarray`: Frame with drawn detection

## MQTT Message Formats

### Detection Event

**Topic:** `{prefix}/detection`

**Payload:**
```json
{
  "timestamp": 1642234567.123,
  "class_name": "bus",
  "confidence": 0.85,
  "bbox": [100, 150, 300, 400],
  "center": [200, 275],
  "area": 50000,
  "image_path": "logs/detections/20240115_083015.jpg"
}
```

### System Status

**Topic:** `{prefix}/status`

**Payload:**
```json
{
  "timestamp": 1642234567.123,
  "status": "online",
  "uptime": 86400,
  "detections_today": 5,
  "last_detection": 1642230000.0,
  "devices_active": true,
  "system": {
    "cpu_usage": 45.2,
    "memory_usage": 62.1,
    "temperature": 58.5,
    "disk_usage": 23.4
  }
}
```

### Performance Metrics

**Topic:** `{prefix}/metrics`

**Payload:**
```json
{
  "timestamp": 1642234567.123,
  "metrics": {
    "avg_inference_time": 0.045,
    "current_fps": 28.5,
    "total_frames": 123456,
    "total_detections": 89,
    "detection_rate": 0.072,
    "uptime": 86400
  }
}
```

### Command Messages

**Topic:** `{prefix}/command`

**Payload Examples:**
```json
// Start system
{"command": "start"}

// Stop system
{"command": "stop"}

// Update configuration
{
  "command": "config_update",
  "config": {
    "detection.min_confidence": 0.8
  }
}

// Manual device control
{
  "command": "activate_devices",
  "duration": 300
}
```

## Configuration Schema

### Root Schema

```yaml
# Configuration file schema validation
schema:
  type: object
  properties:
    camera:
      $ref: "#/definitions/camera"
    detection:
      $ref: "#/definitions/detection"
    automation:
      $ref: "#/definitions/automation"
    mqtt:
      $ref: "#/definitions/mqtt"
    home_assistant:
      $ref: "#/definitions/home_assistant"
    logging:
      $ref: "#/definitions/logging"
    monitoring:
      $ref: "#/definitions/monitoring"
  required:
    - camera
    - detection
    - mqtt

definitions:
  camera:
    type: object
    properties:
      device_id:
        type: integer
        minimum: 0
      resolution:
        type: object
        properties:
          width:
            type: integer
            minimum: 320
          height:
            type: integer
            minimum: 240
      fps:
        type: integer
        minimum: 1
        maximum: 60
    required:
      - device_id
      - resolution
      
  detection:
    type: object
    properties:
      model_path:
        type: string
      min_confidence:
        type: number
        minimum: 0.0
        maximum: 1.0
      cooldown_seconds:
        type: integer
        minimum: 1
    required:
      - model_path
      - min_confidence
```

## Error Codes

### System Error Codes

| Code | Name | Description |
|------|------|-------------|
| `1001` | `CAMERA_INIT_FAILED` | Camera initialization failed |
| `1002` | `CAMERA_DISCONNECTED` | Camera disconnected during operation |
| `1003` | `INVALID_FRAME` | Invalid or corrupted frame |
| `2001` | `HAILO_INIT_FAILED` | Hailo device initialization failed |
| `2002` | `MODEL_LOAD_FAILED` | AI model loading failed |
| `2003` | `INFERENCE_FAILED` | AI inference failed |
| `3001` | `MQTT_CONNECT_FAILED` | MQTT broker connection failed |
| `3002` | `MQTT_PUBLISH_FAILED` | MQTT message publish failed |
| `3003` | `MQTT_SUBSCRIBE_FAILED` | MQTT topic subscription failed |
| `4001` | `CONFIG_LOAD_FAILED` | Configuration file loading failed |
| `4002` | `CONFIG_INVALID` | Invalid configuration values |
| `5001` | `DEVICE_CONTROL_FAILED` | Home Assistant device control failed |
| `9001` | `SYSTEM_OVERLOAD` | System resource overload |
| `9002` | `MEMORY_ERROR` | Out of memory error |

### Exception Classes

```python
class VisionAIError(Exception):
    """Base exception class for VisionAI4SchoolBus"""
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"[{code}] {message}")

class CameraError(VisionAIError):
    """Camera-related errors"""
    pass

class DetectionError(VisionAIError):
    """AI detection errors"""
    pass

class MQTTError(VisionAIError):
    """MQTT communication errors"""
    pass

class ConfigurationError(VisionAIError):
    """Configuration-related errors"""
    pass
```

### Usage Example

```python
try:
    detector = HailoDetector(config)
    detector.initialize()
except DetectionError as e:
    print(f"Detection error {e.code}: {e.message}")
    if e.code == 2001:
        # Handle Hailo initialization failure
        pass
```

This API reference provides comprehensive documentation for integrating with and extending the VisionAI4SchoolBus system. For additional examples and usage patterns, see the source code and test files.