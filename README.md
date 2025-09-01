# VisionAI4SchoolBus

A comprehensive computer vision application for automatic school bus detection and home automation integration using Raspberry Pi 5 with AI Kit (M.2 HAT+ and Hailo AI acceleration module).

## Overview

This system continuously monitors a USB camera feed positioned to view the street in front of a residential property, utilizes the Hailo AI accelerator for real-time object detection to identify school buses with high accuracy and minimal false positives, and triggers automated responses when a school bus is detected within the camera's field of view.

## Features

- **Real-time School Bus Detection**: Uses Hailo NPU for optimized AI inference
- **Home Automation Integration**: MQTT-based control of Home Assistant smart devices
- **Configurable Timing Controls**: Customizable device activation duration
- **Voice Announcements**: Modular MQTT-based audio notifications
- **Robust Error Handling**: Comprehensive logging and fault tolerance
- **Easy Configuration**: JSON-based settings for camera and detection parameters
- **Performance Monitoring**: Track detection accuracy and system metrics
- **Automatic Startup**: systemd service configuration
- **Testing Mode**: Calibration and validation capabilities

## Hardware Requirements

- Raspberry Pi 5
- Raspberry Pi AI Kit (M.2 HAT+ and Hailo AI acceleration module)
- USB Camera
- MicroSD Card (32GB+ recommended)
- Power Supply (5V/5A recommended for Pi 5 + AI Kit)

## Software Dependencies

- Python 3.11+
- OpenCV
- Hailo Runtime Libraries
- MQTT Client (paho-mqtt)
- NumPy
- PyYAML
- systemd (for service management)

## Quick Start

1. **Hardware Setup**
   ```bash
   # See docs/hardware_setup.md for detailed instructions
   ```

2. **Installation**
   ```bash
   git clone https://github.com/msasikumar/visionAI4schoolbus.git
   cd visionAI4schoolbus
   ./install.sh
   ```

3. **Configuration**
   ```bash
   cp config/config.template.yaml config/config.yaml
   # Edit config/config.yaml with your settings
   ```

4. **Run**
   ```bash
   python main.py
   ```

## Project Structure

```
visionAI4schoolbus/
├── src/                    # Main source code
│   ├── detection/         # AI detection modules
│   ├── automation/        # Home automation integration
│   ├── camera/           # Camera handling
│   └── utils/            # Utility functions
├── config/               # Configuration files
├── models/              # AI models and weights
├── logs/                # Log files
├── tests/               # Test suite
├── docs/                # Documentation
├── scripts/             # Setup and utility scripts
└── systemd/             # Service configuration
```

## Documentation

- [Hardware Setup](docs/hardware_setup.md)
- [Software Installation](docs/installation.md)
- [Configuration Guide](docs/configuration.md)
- [Home Assistant Integration](docs/home_assistant.md)
- [API Reference](docs/api.md)
- [Troubleshooting](docs/troubleshooting.md)

## License

MIT License - see LICENSE file for details
