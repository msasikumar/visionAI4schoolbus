# Installation Guide

This guide provides comprehensive step-by-step instructions for installing VisionAI4SchoolBus on a Raspberry Pi 5 with the Hailo AI Kit.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation Methods](#installation-methods)
- [System Preparation](#system-preparation)
- [Software Installation](#software-installation)
- [Configuration Setup](#configuration-setup)
- [Service Installation](#service-installation)
- [Post-Installation Verification](#post-installation-verification)
- [Troubleshooting Installation](#troubleshooting-installation)

## Prerequisites

### Hardware Requirements

Ensure you have completed the [Hardware Setup Guide](hardware-setup.md) before proceeding with software installation.

**Required Components:**
- Raspberry Pi 5 (4GB+ RAM recommended)
- Raspberry Pi AI Kit with Hailo-8L NPU
- USB Camera (1080p minimum)
- MicroSD card (64GB+, Class 10)
- Stable power supply (5V/5A)
- Network connectivity

### Software Requirements

**Operating System:**
- Raspberry Pi OS (64-bit) - Latest version
- Kernel version 6.1+ (for Hailo support)

**Dependencies:**
- Python 3.11 or newer
- Git version control
- Internet connection for package downloads

## Installation Methods

### Method 1: Quick Installation (Recommended)

The automated installation script handles all dependencies and configuration:

```bash
# 1. Clone the repository
git clone https://github.com/msasikumar/visionAI4schoolbus.git
cd visionAI4schoolbus

# 2. Make installation script executable
chmod +x install.sh

# 3. Run automated installation
sudo ./install.sh

# 4. Follow the interactive prompts
# The script will guide you through configuration options
```

**What the installation script does:**
- Updates system packages
- Installs Python dependencies
- Downloads and installs Hailo runtime
- Sets up system user and permissions
- Creates systemd service
- Configures logging directories
- Sets up basic configuration files

### Method 2: Manual Installation

For advanced users who prefer manual control or need customization:

#### Step 1: System Preparation

```bash
# Update package lists and system
sudo apt update && sudo apt full-upgrade -y

# Install essential system packages
sudo apt install -y \
    python3 python3-pip python3-venv python3-dev \
    git wget curl unzip \
    build-essential cmake pkg-config \
    libjpeg-dev libpng-dev libtiff-dev \
    libavcodec-dev libavformat-dev libswscale-dev \
    libv4l-dev libxvidcore-dev libx264-dev \
    libgtk-3-dev libcanberra-gtk3-dev \
    libatlas-base-dev gfortran \
    mosquitto mosquitto-clients \
    v4l-utils ffmpeg \
    htop tree nano

# Install additional Python build dependencies
sudo apt install -y \
    python3-setuptools python3-wheel \
    python3-numpy python3-opencv \
    libhdf5-dev libhdf5-serial-dev \
    libopenblas-dev liblapack-dev
```

#### Step 2: Hailo AI Kit Installation

The Hailo runtime installation varies based on the current version. Check the [Hailo Developer Zone](https://hailo.ai/developer-zone/) for the latest packages.

```bash
# Create temporary directory for Hailo installation
mkdir -p ~/hailo_install
cd ~/hailo_install

# Download Hailo runtime package (check for latest version)
# Example for version 4.17.0 (replace with current version):
wget https://hailo.ai/developer-zone/software-downloads/hailo-software-suite/hailo-rt-4.17.0-linux-arm64.tar.gz

# Extract and install
tar -xzf hailo-rt-*.tar.gz
cd hailo-rt-*/

# Install Hailo runtime
sudo dpkg -i *.deb
sudo apt-get install -f  # Fix any dependency issues

# Verify installation
hailortcli fw-control identify
```

**Alternative: Using Hailo's package repository**
```bash
# Add Hailo repository (if available)
curl -s https://hailo.ai/debian/hailo.gpg.key | sudo apt-key add -
echo "deb https://hailo.ai/debian stable main" | sudo tee /etc/apt/sources.list.d/hailo.list

# Update and install
sudo apt update
sudo apt install hailo-all
```

#### Step 3: Application Installation

```bash
# Navigate to desired installation directory
cd /opt

# Clone the repository
sudo git clone https://github.com/msasikumar/visionAI4schoolbus.git
cd visionAI4schoolbus

# Create dedicated system user
sudo useradd -r -s /bin/false -d /opt/visionAI4schoolbus -c "VisionAI4SchoolBus Service" visionai

# Add user to required groups
sudo usermod -a -G video,dialout,gpio visionai

# Set ownership and permissions
sudo chown -R visionai:visionai /opt/visionAI4schoolbus
sudo chmod +x /opt/visionAI4schoolbus/*.sh

# Create required directories
sudo -u visionai mkdir -p logs logs/detections models config
```

#### Step 4: Python Environment Setup

```bash
# Change to application directory
cd /opt/visionAI4schoolbus

# Create Python virtual environment
sudo -u visionai python3 -m venv venv

# Activate virtual environment and upgrade pip
sudo -u visionai ./venv/bin/python -m pip install --upgrade pip setuptools wheel

# Install Python dependencies
sudo -u visionai ./venv/bin/pip install -r requirements.txt

# Install additional packages for Raspberry Pi
sudo -u visionai ./venv/bin/pip install \
    RPi.GPIO \
    gpiozero \
    picamera2

# Verify installation
sudo -u visionai ./venv/bin/python -c "import cv2, numpy, yaml, paho.mqtt.client; print('All dependencies installed successfully')"
```

#### Step 5: Model Installation

```bash
# Create models directory
sudo -u visionai mkdir -p /opt/visionAI4schoolbus/models

# Download or copy your Hailo-optimized model
# Example: Download a sample model (replace with your actual model)
cd /opt/visionAI4schoolbus/models
sudo -u visionai wget https://github.com/hailo-ai/hailo_model_zoo/releases/download/v2.8.0/yolov8n_hailo.hef

# Verify model file
ls -la *.hef
```

## Configuration Setup

### Basic Configuration

```bash
# Copy template configuration
cd /opt/visionAI4schoolbus
sudo -u visionai cp config/config.template.yaml config/config.yaml

# Edit configuration file
sudo -u visionai nano config/config.yaml
```

**Essential configuration changes:**
```yaml
# Update camera device (check with 'ls /dev/video*')
camera:
  device_id: 0

# Configure detection model path
detection:
  model_path: "models/yolov8n_hailo.hef"
  min_confidence: 0.7

# Set up MQTT broker connection
mqtt:
  broker_host: "your_broker_ip"
  username: "your_username"
  password: "your_password"

# Configure Home Assistant devices
home_assistant:
  devices:
    lights:
      - "light.front_porch"
    switches:
      - "switch.announcement_system"
```

### Advanced Configuration

```bash
# Create environment-specific configuration
sudo -u visionai nano config/production.yaml
```

For detailed configuration options, see the [Configuration Guide](configuration.md).

## Service Installation

### Systemd Service Setup

```bash
# Copy service file to systemd directory
sudo cp systemd/visionai4schoolbus.service /etc/systemd/system/

# Verify service file content
cat /etc/systemd/system/visionai4schoolbus.service

# Reload systemd configuration
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable visionai4schoolbus

# Start the service
sudo systemctl start visionai4schoolbus

# Check service status
sudo systemctl status visionai4schoolbus
```

### Service Configuration Verification

```bash
# View service logs
sudo journalctl -u visionai4schoolbus -f

# Check if service is running
sudo systemctl is-active visionai4schoolbus

# Restart service if needed
sudo systemctl restart visionai4schoolbus
```

## Post-Installation Verification

### System Health Check

```bash
# Run comprehensive system test
cd /opt/visionAI4schoolbus
sudo -u visionai ./venv/bin/python test_system.py

# Check camera access
v4l2-ctl --list-devices
v4l2-ctl --list-formats-ext -d /dev/video0

# Test camera capture
sudo -u visionai ffmpeg -f v4l2 -i /dev/video0 -t 5 -y test_capture.mp4
```

### Hailo Device Verification

```bash
# Verify Hailo device detection
lspci | grep -i hailo
hailortcli scan

# Check Hailo runtime version
hailortcli fw-control identify

# Monitor device status
hailortcli monitor
```

### Application Testing

```bash
# Test configuration loading
sudo -u visionai /opt/visionAI4schoolbus/venv/bin/python -c "
from src.utils.config_manager import ConfigManager
config = ConfigManager('config/config.yaml')
print('Configuration loaded successfully')
print(f'Camera device: {config.get(\"camera.device_id\")}')
print(f'Model path: {config.get(\"detection.model_path\")}')
"

# Test MQTT connectivity
mosquitto_pub -h your_broker_ip -u your_username -P your_password -t test -m "Installation test"

# Run detection test
sudo -u visionai /opt/visionAI4schoolbus/venv/bin/python main.py --test-mode
```

### Performance Verification

```bash
# Monitor system resources
htop
iotop -o

# Check temperature and throttling
vcgencmd measure_temp
vcgencmd get_throttled

# Monitor application performance
sudo tail -f /opt/visionAI4schoolbus/logs/visionai4schoolbus.log
```

## Troubleshooting Installation

### Common Installation Issues

#### 1. Python Dependencies Failed

```bash
# Update pip and try again
sudo -u visionai /opt/visionAI4schoolbus/venv/bin/python -m pip install --upgrade pip

# Install with verbose output
sudo -u visionai /opt/visionAI4schoolbus/venv/bin/pip install -r requirements.txt -v

# Install system-wide if virtual environment fails
sudo apt install python3-opencv python3-numpy python3-yaml
```

#### 2. Hailo Installation Problems

```bash
# Check if Hailo device is detected
lspci | grep -i hailo

# Verify PCIe connection
dmesg | grep -i pcie

# Manual driver installation
sudo modprobe hailo_pci
lsmod | grep hailo
```

#### 3. Camera Access Issues

```bash
# Check camera permissions
ls -l /dev/video*
sudo usermod -a -G video visionai

# Test camera with different tools
cheese  # GUI camera test
guvcview  # Alternative camera viewer

# Check USB power
dmesg | grep -i usb
```

#### 4. Service Startup Problems

```bash
# Check service logs
sudo journalctl -u visionai4schoolbus --no-pager -l

# Verify file permissions
sudo ls -la /opt/visionAI4schoolbus/
sudo systemctl cat visionai4schoolbus

# Test manual startup
sudo -u visionai /opt/visionAI4schoolbus/venv/bin/python /opt/visionAI4schoolbus/main.py
```

#### 5. Network/MQTT Issues

```bash
# Test network connectivity
ping -c 4 8.8.8.8

# Test MQTT broker connection
nc -zv your_broker_ip 1883

# Check firewall settings
sudo ufw status
sudo iptables -L
```

### Installation Log Collection

Create a diagnostic script for troubleshooting:

```bash
#!/bin/bash
# collect_install_logs.sh

echo "=== VisionAI4SchoolBus Installation Diagnostics ===" > install_diag.log
date >> install_diag.log

echo -e "\n=== System Information ===" >> install_diag.log
uname -a >> install_diag.log
lsb_release -a >> install_diag.log

echo -e "\n=== Hardware Detection ===" >> install_diag.log
lsusb >> install_diag.log
lspci >> install_diag.log

echo -e "\n=== Python Environment ===" >> install_diag.log
/opt/visionAI4schoolbus/venv/bin/python --version >> install_diag.log
/opt/visionAI4schoolbus/venv/bin/pip list >> install_diag.log

echo -e "\n=== Service Status ===" >> install_diag.log
systemctl status visionai4schoolbus >> install_diag.log 2>&1

echo -e "\n=== Recent Logs ===" >> install_diag.log
tail -50 /opt/visionAI4schoolbus/logs/visionai4schoolbus.log >> install_diag.log 2>&1

echo -e "\n=== System Logs ===" >> install_diag.log
journalctl -u visionai4schoolbus --lines=50 >> install_diag.log 2>&1

echo "Diagnostics saved to install_diag.log"
```

### Getting Installation Help

If you encounter issues during installation:

1. **Check Prerequisites**: Ensure all hardware requirements are met
2. **Review Logs**: Check system and application logs for error messages
3. **Verify Permissions**: Ensure proper file ownership and permissions
4. **Test Components**: Verify individual components (camera, Hailo, network)
5. **Consult Documentation**: Review [Troubleshooting Guide](troubleshooting.md)
6. **Community Support**: Open an issue on GitHub with:
   - Hardware configuration details
   - Installation method used
   - Complete error messages
   - Diagnostic log output

## Next Steps

After successful installation:

1. **System Configuration**: Review the [Configuration Guide](configuration.md)
2. **Home Assistant Setup**: Configure smart device integration
3. **Testing and Calibration**: Fine-tune detection parameters
4. **Monitoring Setup**: Configure performance monitoring
5. **Backup Configuration**: Save working configuration files

The installation is complete when:
- [ ] Service starts automatically
- [ ] Camera is detected and functional
- [ ] Hailo device responds to queries
- [ ] MQTT connection is established
- [ ] Detection model loads without errors
- [ ] System logs show normal operation

For ongoing maintenance and updates, refer to the system administration section in the [Troubleshooting Guide](troubleshooting.md).