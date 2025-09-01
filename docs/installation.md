# Installation Guide

This guide provides step-by-step instructions for installing VisionAI4SchoolBus on a Raspberry Pi 5 with the Hailo AI Kit.

## Prerequisites

### Hardware Requirements

- Raspberry Pi 5 (4GB or 8GB recommended)
- Raspberry Pi AI Kit (M.2 HAT+ with Hailo-8L acceleration module)
- High-quality USB camera (1080p or higher recommended)
- MicroSD card (32GB+ Class 10)
- Power supply (5V/5A for Pi 5 + AI Kit)
- Reliable network connection (WiFi or Ethernet)

### Software Requirements

- Raspberry Pi OS (64-bit, latest version)
- Python 3.11 or newer
- Git for source code management
- Internet connection for package downloads

## Installation Methods

### Method 1: Automatic Installation (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/msasikumar/visionAI4schoolbus.git
   cd visionAI4schoolbus
   ```

2. **Run the installation script:**
   ```bash
   sudo ./install.sh
   ```

3. **Follow the prompts** and wait for installation to complete.

### Method 2: Manual Installation

If you prefer to install manually or need to customize the installation:

#### Step 1: System Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install system dependencies
sudo apt install -y python3 python3-pip python3-venv git wget curl \
    build-essential cmake pkg-config libjpeg-dev libpng-dev libtiff-dev \
    libavcodec-dev libavformat-dev libswscale-dev libv4l-dev \
    libxvidcore-dev libx264-dev libgtk-3-dev libatlas-base-dev \
    gfortran python3-dev mosquitto mosquitto-clients
```

#### Step 2: Hailo AI Kit Setup

1. **Physical Installation:**
   - Power off the Raspberry Pi
   - Install the M.2 HAT+ on the Pi's GPIO header
   - Insert the Hailo-8L module into the M.2 slot
   - Secure all connections

2. **Software Installation:**
   ```bash
   # Download Hailo runtime (check latest version)
   wget https://hailo.ai/developer-zone/software-downloads/...
   
   # Install according to Hailo's documentation
   # This typically involves:
   sudo dpkg -i hailo-all_*.deb
   sudo apt-get install -f
   ```

#### Step 3: Application Installation

```bash
# Clone repository
git clone https://github.com/msasikumar/visionAI4schoolbus.git
cd visionAI4schoolbus

# Create installation directory
sudo mkdir -p /opt/visionai4schoolbus
sudo cp -r . /opt/visionai4schoolbus/

# Create service user
sudo useradd -r -s /bin/false -d /opt/visionai4schoolbus visionai
sudo usermod -a -G video,dialout visionai
sudo chown -R visionai:visionai /opt/visionai4schoolbus

# Create Python environment
cd /opt/visionai4schoolbus
sudo -u visionai python3 -m venv venv
sudo -u visionai ./venv/bin/pip install --upgrade pip
sudo -u visionai ./venv/bin/pip install -r requirements.txt
```

#### Step 4: Configuration

```bash
# Create configuration file
sudo -u visionai cp config/config.template.yaml config/config.yaml
sudo nano config/config.yaml  # Edit as needed
```

#### Step 5: Service Installation

```bash
# Copy systemd service file
sudo cp systemd/visionai4schoolbus.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable visionai4schoolbus
```

## Post-Installation Setup

### 1. Camera Configuration

Test your camera connection:
```bash
# List available cameras
v4l2-ctl --list-devices

# Test camera capture
ffmpeg -f v4l2 -i /dev/video0 -t 5 -f mp4 test.mp4
```

### 2. Hailo Model Setup

Download or convert your detection model:
```bash
# Place your Hailo model file
sudo cp your_model.hef /opt/visionai4schoolbus/models/

# Update config file to point to your model
sudo nano /opt/visionai4schoolbus/config/config.yaml
```

### 3. MQTT Configuration

Configure MQTT broker settings in the config file:
```yaml
mqtt:
  broker_host: "your_mqtt_broker_ip"
  username: "your_username"
  password: "your_password"
```

### 4. Home Assistant Integration

Add your Home Assistant device entities:
```yaml
home_assistant:
  devices:
    lights:
      - "light.front_porch"
      - "light.living_room"
    switches:
      - "switch.outdoor_speakers"
```

## Testing Installation

### Basic System Test

```bash
# Test camera access
sudo -u visionai /opt/visionai4schoolbus/test.sh

# Check service status
sudo systemctl status visionai4schoolbus

# View real-time logs
sudo journalctl -u visionai4schoolbus -f
```

### Detection Test

```bash
# Start the service
sudo systemctl start visionai4schoolbus

# Monitor for detections
sudo tail -f /opt/visionai4schoolbus/logs/visionai4schoolbus.log
```

## Troubleshooting

### Common Issues

1. **Camera not detected:**
   - Check USB connections
   - Verify camera permissions: `ls -l /dev/video*`
   - Add user to video group: `sudo usermod -a -G video visionai`

2. **Hailo runtime not found:**
   - Verify Hailo installation: `lsmod | grep hailo`
   - Check device connection: `lsusb | grep 03e7`

3. **MQTT connection fails:**
   - Test broker connectivity: `mosquitto_pub -h broker_ip -t test -m "hello"`
   - Check firewall settings
   - Verify credentials

4. **High CPU usage:**
   - Reduce camera resolution in config
   - Increase detection cooldown period
   - Monitor with: `htop`

5. **Memory issues:**
   - Increase swap space
   - Reduce buffer sizes in config
   - Monitor with: `free -h`

### Log Locations

- Application logs: `/opt/visionai4schoolbus/logs/visionai4schoolbus.log`
- System logs: `sudo journalctl -u visionai4schoolbus`
- Detection images: `/opt/visionai4schoolbus/logs/detections/`
- Performance metrics: `/opt/visionai4schoolbus/logs/metrics.json`

### Getting Help

1. Check the troubleshooting section in the README
2. Review log files for error messages
3. Join the community forum (if available)
4. Open an issue on GitHub with:
   - Hardware configuration
   - Error messages
   - Log excerpts
   - Steps to reproduce

## Security Considerations

### Network Security

- Use strong MQTT credentials
- Consider TLS/SSL for MQTT connections
- Isolate IoT devices on separate network

### System Security

- Regularly update system packages
- Use minimal permissions for service user
- Monitor system resources
- Keep Hailo runtime updated

### Privacy

- Secure camera footage storage
- Consider local processing only
- Review data retention policies
- Implement access controls

## Performance Optimization

### Camera Settings

- Use appropriate resolution (1280x720 recommended)
- Adjust FPS based on processing power
- Configure proper exposure settings

### Detection Settings

- Tune confidence thresholds
- Adjust detection cooldown periods
- Use appropriate model for your needs

### System Resources

- Monitor CPU and memory usage
- Use GPU acceleration when available
- Optimize Python performance
- Consider SSD for better I/O performance

## Maintenance

### Regular Tasks

- Monitor log files for errors
- Check detection accuracy
- Update system packages
- Review performance metrics
- Clean old detection images

### Updates

```bash
# Update application
cd /opt/visionai4schoolbus
sudo -u visionai git pull
sudo -u visionai ./venv/bin/pip install -r requirements.txt --upgrade
sudo systemctl restart visionai4schoolbus
```

### Backup

```bash
# Backup configuration
sudo cp /opt/visionai4schoolbus/config/config.yaml ~/visionai-backup.yaml

# Backup detection images (if needed)
sudo tar -czf ~/detections-backup.tar.gz /opt/visionai4schoolbus/logs/detections/
```
