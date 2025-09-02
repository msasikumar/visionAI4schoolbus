# Configuration Guide

This guide provides detailed information about configuring VisionAI4SchoolBus for optimal performance in your environment.

## Table of Contents

- [Configuration Overview](#configuration-overview)
- [Configuration File Structure](#configuration-file-structure)
- [Camera Configuration](#camera-configuration)
- [AI Detection Settings](#ai-detection-settings)
- [Home Automation Setup](#home-automation-setup)
- [MQTT Configuration](#mqtt-configuration)
- [Logging Configuration](#logging-configuration)
- [Performance Monitoring](#performance-monitoring)
- [Advanced Configuration](#advanced-configuration)
- [Environment-Specific Configs](#environment-specific-configs)
- [Configuration Validation](#configuration-validation)

## Configuration Overview

The VisionAI4SchoolBus system uses YAML configuration files to manage all system settings. The main configuration file is [`config/config.yaml`](../config/config.yaml), which is created from the template [`config/config.template.yaml`](../config/config.template.yaml).

### Configuration Hierarchy

```
config/
├── config.yaml              # Main configuration file
├── config.template.yaml     # Template with default values
├── production.yaml          # Production environment overrides
├── development.yaml         # Development environment settings
└── testing.yaml            # Testing configuration
```

### Configuration Loading Order

1. Default values from template
2. Main configuration file (`config.yaml`)
3. Environment-specific overrides
4. Runtime parameter overrides

## Configuration File Structure

The configuration is organized into logical sections:

```yaml
# High-level structure
camera:          # Camera hardware settings
detection:       # AI detection parameters  
automation:      # Home automation behavior
mqtt:           # MQTT broker connection
home_assistant: # Home Assistant integration
logging:        # Logging configuration
monitoring:     # Performance monitoring
testing:        # Testing and debugging
```

## Camera Configuration

### Basic Camera Settings

```yaml
camera:
  device_id: 0                    # Camera device identifier
  resolution:
    width: 1280                   # Video width in pixels
    height: 720                   # Video height in pixels
  fps: 30                         # Target frames per second
  buffer_size: 1                  # Frame buffer size (1 = low latency)
```

### Advanced Camera Settings

```yaml
camera:
  # Exposure control
  auto_exposure: true             # Use automatic exposure
  exposure_value: 100             # Manual exposure (if auto_exposure: false)
  
  # Image quality
  gain: 1.0                       # Camera sensor gain
  brightness: 0                   # Brightness adjustment (-100 to 100)
  contrast: 0                     # Contrast adjustment (-100 to 100)
  saturation: 0                   # Color saturation (-100 to 100)
  
  # Focus settings
  auto_focus: true                # Enable autofocus
  focus_value: 50                 # Manual focus distance (if auto_focus: false)
  
  # Advanced settings
  white_balance: "auto"           # White balance mode (auto, manual, presets)
  compression_quality: 95         # JPEG compression quality (0-100)
  
  # Performance optimization
  use_threading: true             # Use separate thread for camera
  timeout: 5.0                    # Camera operation timeout (seconds)
```

### Camera Selection and Testing

**Finding Your Camera Device:**
```bash
# List available cameras
v4l2-ctl --list-devices

# Test camera capabilities
v4l2-ctl --list-formats-ext -d /dev/video0

# Test camera capture
fswebcam -d /dev/video0 -r 1280x720 test.jpg
```

**Resolution Guidelines:**
- **1280x720 (720p)**: Recommended for most installations, good balance of quality and performance
- **1920x1080 (1080p)**: Higher quality, requires more processing power
- **640x480 (480p)**: Lower resource usage, suitable for constrained systems

**Frame Rate Considerations:**
- **30 FPS**: Standard for real-time monitoring
- **15-20 FPS**: Acceptable for detection, lower CPU usage
- **10 FPS**: Minimum for reliable detection

## AI Detection Settings

### Core Detection Parameters

```yaml
detection:
  model_path: "models/yolov8n_hailo.hef"     # Path to Hailo model file
  min_confidence: 0.7                        # Minimum confidence threshold (0.0-1.0)
  nms_threshold: 0.45                        # Non-maximum suppression threshold
  cooldown_seconds: 30                       # Time between detection triggers
```

### Model Configuration

```yaml
detection:
  # Input preprocessing
  input_resolution:
    width: 640                    # Model input width
    height: 640                   # Model input height
  
  # Hailo-specific settings
  hailo_device_id: 0              # Hailo NPU device ID
  batch_size: 1                   # Inference batch size
  
  # Detection filtering
  min_bus_size: 0.05              # Minimum detection size (fraction of image)
  max_detections: 10              # Maximum detections per frame
  
  # Class filtering
  target_classes:                 # Only detect these classes
    - "bus"
    - "school_bus"
  
  # Spatial filtering
  detection_zone:                 # Only detect in this region
    x_min: 0.0                    # Left boundary (0.0-1.0)
    y_min: 0.2                    # Top boundary (0.0-1.0)  
    x_max: 1.0                    # Right boundary (0.0-1.0)
    y_max: 0.8                    # Bottom boundary (0.0-1.0)
```

### Detection Optimization

**Confidence Threshold Tuning:**
```yaml
# Conservative (fewer false positives)
min_confidence: 0.8

# Balanced (recommended starting point)
min_confidence: 0.7

# Aggressive (more detections, may include false positives)
min_confidence: 0.5
```

**Cooldown Period Guidelines:**
```yaml
# Short cooldown (frequent updates)
cooldown_seconds: 10

# Standard cooldown (reduces automation spam)
cooldown_seconds: 30

# Long cooldown (single activation per bus)
cooldown_seconds: 120
```

### School Bus Identification

```yaml
detection:
  # Enhanced bus detection criteria
  school_bus_criteria:
    color_detection: true         # Enable color-based filtering
    expected_colors:              # Look for these colors
      - "yellow"
      - "orange"
    
    size_validation: true         # Validate bus size
    min_aspect_ratio: 1.5         # Width/height ratio (buses are wide)
    max_aspect_ratio: 4.0
    
    text_recognition: false       # Enable text detection (requires additional setup)
    expected_text:
      - "SCHOOL BUS"
      - "SCHOOL DISTRICT"
```

## Home Automation Setup

### Device Control Configuration

```yaml
automation:
  activation_duration_seconds: 300    # How long devices stay active (5 minutes)
  
  # Voice announcements
  voice_announcements: true
  announcement_message: "School bus detected in front of the house"
  announcement_delay: 2             # Delay before announcement (seconds)
  
  # Device activation behavior
  activation_sequence: "simultaneous"  # "simultaneous" or "sequential"
  deactivation_sequence: "reverse"     # "simultaneous", "sequential", "reverse"
  
  # Advanced timing
  pre_activation_delay: 0           # Delay before activating devices
  stagger_delay: 1.0               # Delay between sequential activations
```

### Device Categories

```yaml
automation:
  device_categories:
    priority:                     # High-priority devices (activate first)
      - "light.front_porch"
      - "switch.announcement_system"
    
    standard:                     # Standard devices
      - "light.living_room"
      - "light.kitchen"
    
    optional:                     # Optional devices (activate if system load is low)
      - "media_player.outdoor_speakers"
      - "climate.thermostat"
```

## MQTT Configuration

### Basic MQTT Settings

```yaml
mqtt:
  broker_host: "localhost"        # MQTT broker hostname/IP
  broker_port: 1883               # MQTT broker port
  client_id: "visionai4schoolbus" # Unique client identifier
  
  # Authentication (if required)
  username: ""                    # MQTT username
  password: ""                    # MQTT password
  
  # Connection parameters
  keepalive: 60                   # Connection keepalive interval
  timeout: 10                     # Connection timeout
  retry_interval: 30              # Reconnection retry interval
```

### Advanced MQTT Configuration

```yaml
mqtt:
  # TLS/SSL encryption
  use_tls: true                   # Enable TLS encryption
  ca_cert_path: "certs/ca.crt"    # Certificate Authority certificate
  cert_path: "certs/client.crt"   # Client certificate
  key_path: "certs/client.key"    # Client private key
  insecure: false                 # Skip certificate verification (not recommended)
  
  # Topic configuration
  topic_prefix: "schoolbus"       # Prefix for all topics
  status_topic: "status"          # Status reporting topic
  command_topic: "command"        # Command reception topic
  
  # Message settings
  qos: 1                          # Quality of Service level (0, 1, 2)
  retain: true                    # Retain status messages
  
  # Will/Testament (for connection loss)
  will_topic: "schoolbus/status"
  will_payload: "offline"
  will_qos: 1
  will_retain: true
```

### MQTT Topics Structure

```yaml
# Published topics (outbound)
mqtt:
  topics:
    detection: "schoolbus/detection"      # Detection events
    status: "schoolbus/status"            # System status
    metrics: "schoolbus/metrics"          # Performance metrics
    diagnostics: "schoolbus/diagnostics"  # System diagnostics
    
# Subscribed topics (inbound)
  subscriptions:
    command: "schoolbus/command"          # Remote commands
    config: "schoolbus/config"            # Configuration updates
```

## Home Assistant Integration

### Discovery Configuration

```yaml
home_assistant:
  # MQTT Discovery
  discovery_prefix: "homeassistant"  # HA MQTT discovery prefix
  device_name: "School Bus Detector" # Device name in HA
  device_id: "visionai_schoolbus"    # Unique device identifier
  
  # Device information
  device_info:
    manufacturer: "VisionAI4SchoolBus"
    model: "Raspberry Pi 5 + Hailo"
    sw_version: "1.0.0"
    identifiers:
      - "visionai_schoolbus_001"
```

### Entity Configuration

```yaml
home_assistant:
  # Binary sensor for bus detection
  binary_sensor:
    name: "School Bus Detected"
    device_class: "motion"
    icon: "mdi:bus-school"
    
  # Sensor entities
  sensors:
    detection_confidence:
      name: "Detection Confidence"
      unit: "%"
      icon: "mdi:percent"
      
    last_detection:
      name: "Last Detection Time"
      device_class: "timestamp"
      
    system_temperature:
      name: "System Temperature"
      unit: "°C"
      device_class: "temperature"
```

### Controlled Devices

```yaml
home_assistant:
  devices:
    lights:                       # Light entities to control
      - entity_id: "light.front_porch"
        friendly_name: "Front Porch Light"
        brightness: 255           # Brightness level (0-255)
        
      - entity_id: "light.living_room"
        friendly_name: "Living Room Light"
        brightness: 180
        color_temp: 3000          # Color temperature (K)
    
    switches:                     # Switch entities to control
      - entity_id: "switch.announcement_system"
        friendly_name: "Announcement System"
        
      - entity_id: "switch.security_mode"
        friendly_name: "Security Mode"
    
    media_players:                # Media player entities
      - entity_id: "media_player.outdoor_speakers"
        friendly_name: "Outdoor Speakers"
        volume: 0.7               # Volume level (0.0-1.0)
```

## Logging Configuration

### Basic Logging Setup

```yaml
logging:
  level: "INFO"                   # Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
  console_output: true            # Also output to console
  
  # File logging
  file_path: "logs/visionai4schoolbus.log"
  max_file_size: 10485760         # 10MB max file size
  backup_count: 5                 # Keep 5 backup files
  
  # Log format
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  date_format: "%Y-%m-%d %H:%M:%S"
```

### Advanced Logging Configuration

```yaml
logging:
  # Logger-specific levels
  loggers:
    "detection":
      level: "DEBUG"              # Detailed detection logging
      
    "camera":
      level: "INFO"               # Camera operation logging
      
    "mqtt":
      level: "WARNING"            # Only MQTT warnings and errors
      
    "performance":
      level: "INFO"               # Performance metrics logging
  
  # Structured logging
  structured_logging: true        # Use JSON format
  include_context: true           # Include execution context
  
  # Log rotation
  rotation_schedule: "midnight"   # Rotate at midnight
  rotation_interval: 1            # Rotate daily
  compression: true               # Compress rotated logs
```

### Log Categories

```yaml
logging:
  categories:
    system:                       # System-level events
      enabled: true
      level: "INFO"
      
    detection:                    # Detection events
      enabled: true
      level: "INFO"
      include_images: false       # Save detection images
      
    automation:                   # Home automation events
      enabled: true
      level: "INFO"
      
    performance:                  # Performance metrics
      enabled: true
      level: "INFO"
      log_interval: 60            # Log every 60 seconds
      
    debug:                        # Debug information
      enabled: false              # Disable in production
      level: "DEBUG"
```

## Performance Monitoring

### Basic Monitoring

```yaml
monitoring:
  enabled: true                   # Enable performance monitoring
  metrics_file: "logs/metrics.json"
  performance_log_interval: 60    # Seconds between performance logs
```

### Detailed Monitoring Configuration

```yaml
monitoring:
  # System metrics
  system_metrics:
    cpu_usage: true               # Monitor CPU usage
    memory_usage: true            # Monitor memory usage
    disk_usage: true              # Monitor disk usage
    temperature: true             # Monitor system temperature
    
  # Application metrics  
  application_metrics:
    inference_time: true          # AI inference timing
    detection_count: true         # Number of detections
    frame_rate: true              # Camera frame rate
    processing_latency: true      # End-to-end latency
    
  # Thresholds and alerts
  alerts:
    max_inference_time: 0.1       # Alert if inference > 100ms
    min_fps: 10.0                 # Alert if FPS < 10
    max_cpu_usage: 80.0           # Alert if CPU > 80%
    max_memory_usage: 80.0        # Alert if memory > 80%
    max_temperature: 75.0         # Alert if temp > 75°C
    
  # Data retention
  retention:
    metrics_days: 30              # Keep metrics for 30 days
    logs_days: 7                  # Keep detailed logs for 7 days
    detection_images_days: 3      # Keep detection images for 3 days
```

### Performance Optimization Settings

```yaml
monitoring:
  optimization:
    auto_quality_adjustment: true    # Automatically adjust quality for performance
    frame_skip_threshold: 0.2        # Skip frames if processing time > 200ms
    memory_cleanup_interval: 300     # Clean up memory every 5 minutes
    
    # Performance profiles
    performance_profile: "balanced"   # "performance", "balanced", "efficiency"
    
    # Resource limits
    max_memory_mb: 1024              # Maximum memory usage (MB)
    max_cpu_percent: 75              # Maximum CPU usage (%)
```

## Advanced Configuration

### Multi-Camera Setup

```yaml
cameras:
  camera_1:
    device_id: 0
    location: "front_yard"
    resolution: { width: 1280, height: 720 }
    detection_zone: { x_min: 0.0, y_min: 0.2, x_max: 1.0, y_max: 0.8 }
    
  camera_2:
    device_id: 1
    location: "side_street"
    resolution: { width: 1280, height: 720 }
    detection_zone: { x_min: 0.1, y_min: 0.1, x_max: 0.9, y_max: 0.9 }
```

### Time-Based Configuration

```yaml
scheduling:
  enabled: true
  timezone: "America/Chicago"
  
  # School day schedule
  school_days:
    - "monday"
    - "tuesday"
    - "wednesday" 
    - "thursday"
    - "friday"
    
  # Active time periods
  active_periods:
    morning:
      start_time: "07:00"
      end_time: "09:00"
    afternoon:
      start_time: "14:30"
      end_time: "16:30"
      
  # Holiday exceptions
  holidays:
    - "2024-12-25"    # Christmas
    - "2024-07-04"    # Independence Day
```

### Security Configuration

```yaml
security:
  # Access control
  api_key: "your-secret-api-key"
  allowed_hosts:
    - "192.168.1.0/24"
    - "localhost"
    
  # Data protection
  encrypt_logs: false
  anonymize_detections: true
  
  # Audit logging
  audit_logging: true
  audit_log_path: "logs/audit.log"
```

## Environment-Specific Configs

### Development Configuration

```yaml
# config/development.yaml
logging:
  level: "DEBUG"
  console_output: true

monitoring:
  save_detection_images: true
  
testing:
  enabled: true
  mock_devices: true
```

### Production Configuration

```yaml
# config/production.yaml
logging:
  level: "INFO"
  console_output: false
  
monitoring:
  save_detection_images: false
  
security:
  encrypt_logs: true
```

### Testing Configuration

```yaml
# config/testing.yaml
camera:
  device_id: -1  # Use test images
  
detection:
  cooldown_seconds: 5  # Shorter cooldown for testing
  
testing:
  enabled: true
  test_images_path: "test_images"
  save_test_results: true
```

## Configuration Validation

### Validation Script

```bash
#!/bin/bash
# validate_config.sh

cd /opt/visionAI4schoolbus

# Test configuration loading
sudo -u visionai ./venv/bin/python -c "
import yaml
import sys
from src.utils.config_manager import ConfigManager

try:
    config = ConfigManager('config/config.yaml')
    print('✓ Configuration file loaded successfully')
    
    # Validate required sections
    required_sections = ['camera', 'detection', 'mqtt', 'home_assistant']
    for section in required_sections:
        if config.get(section):
            print(f'✓ {section} section found')
        else:
            print(f'✗ {section} section missing')
            
    # Validate camera device
    camera_id = config.get('camera.device_id')
    if isinstance(camera_id, int):
        print(f'✓ Camera device ID: {camera_id}')
    else:
        print(f'✗ Invalid camera device ID: {camera_id}')
        
    # Validate model path
    model_path = config.get('detection.model_path')
    import os
    if os.path.exists(model_path):
        print(f'✓ Model file found: {model_path}')
    else:
        print(f'✗ Model file not found: {model_path}')
        
except Exception as e:
    print(f'✗ Configuration error: {e}')
    sys.exit(1)
"
```

### Common Configuration Issues

```yaml
# Issue: Camera device not found
camera:
  device_id: 0  # Try different values: 0, 1, 2, etc.

# Issue: Model file missing  
detection:
  model_path: "models/yolov8n_hailo.hef"  # Ensure file exists

# Issue: MQTT connection fails
mqtt:
  broker_host: "192.168.1.100"  # Use IP instead of hostname
  timeout: 30                   # Increase timeout

# Issue: Confidence threshold too high
detection:
  min_confidence: 0.5  # Lower threshold for more detections
```

### Configuration Best Practices

1. **Start with Template**: Always begin with [`config.template.yaml`](../config/config.template.yaml)
2. **Gradual Changes**: Make incremental configuration changes
3. **Test Changes**: Validate configuration after each change
4. **Backup Configs**: Keep backup copies of working configurations
5. **Environment-Specific**: Use separate configs for different environments
6. **Version Control**: Track configuration changes with Git
7. **Documentation**: Comment complex configuration sections
8. **Security**: Don't commit passwords or API keys

### Configuration Testing Commands

```bash
# Test camera configuration
v4l2-ctl --list-devices
fswebcam -d /dev/video0 -r 1280x720 test.jpg

# Test MQTT configuration
mosquitto_pub -h broker_ip -p 1883 -t test -m "hello"

# Test Hailo configuration
hailortcli scan
hailortcli monitor

# Test complete configuration
sudo systemctl stop visionai4schoolbus
sudo -u visionai /opt/visionAI4schoolbus/venv/bin/python main.py --dry-run
sudo systemctl start visionai4schoolbus
```

For additional configuration help, see the [Troubleshooting Guide](troubleshooting.md) or [API Reference](api-reference.md).