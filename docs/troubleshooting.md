# Troubleshooting Guide

This guide helps diagnose and resolve common issues with the VisionAI4SchoolBus system.

## Table of Contents

- [Quick Diagnostics](#quick-diagnostics)
- [System Issues](#system-issues)
- [Hardware Problems](#hardware-problems)
- [Software Issues](#software-issues)
- [Performance Problems](#performance-problems)
- [Network and Connectivity](#network-and-connectivity)
- [Detection Issues](#detection-issues)
- [Home Automation Problems](#home-automation-problems)
- [Log Analysis](#log-analysis)
- [Recovery Procedures](#recovery-procedures)
- [Getting Help](#getting-help)

## Quick Diagnostics

### System Status Check

Run this comprehensive diagnostic script to quickly identify issues:

```bash
#!/bin/bash
# quick_diagnostics.sh

echo "=== VisionAI4SchoolBus Quick Diagnostics ==="
echo "Timestamp: $(date)"
echo

# Check service status
echo "1. Service Status:"
systemctl is-active visionai4schoolbus
systemctl status visionai4schoolbus --no-pager -l | head -10
echo

# Check hardware
echo "2. Hardware Detection:"
echo "Cameras:"
v4l2-ctl --list-devices 2>/dev/null || echo "No cameras detected"
echo "Hailo Device:"
lspci | grep -i hailo || echo "Hailo device not found"
echo

# Check system resources
echo "3. System Resources:"
echo "CPU Temperature: $(vcgencmd measure_temp)"
echo "Memory Usage:"
free -h | grep Mem
echo "Disk Usage:"
df -h / | tail -1
echo

# Check network
echo "4. Network Connectivity:"
ping -c 1 8.8.8.8 >/dev/null 2>&1 && echo "Internet: OK" || echo "Internet: FAILED"
echo

# Check logs
echo "5. Recent Errors:"
journalctl -u visionai4schoolbus --since "1 hour ago" | grep -i error | tail -5
echo

echo "=== Diagnostics Complete ==="
```

Save and run:
```bash
chmod +x quick_diagnostics.sh
./quick_diagnostics.sh
```

### Common Quick Fixes

1. **Service not running**:
   ```bash
   sudo systemctl start visionai4schoolbus
   sudo systemctl enable visionai4schoolbus
   ```

2. **Camera permission issues**:
   ```bash
   sudo usermod -a -G video visionai
   sudo systemctl restart visionai4schoolbus
   ```

3. **Configuration file missing**:
   ```bash
   cd /opt/visionAI4schoolbus
   sudo -u visionai cp config/config.template.yaml config/config.yaml
   ```

4. **Clear logs and restart**:
   ```bash
   sudo truncate -s 0 /opt/visionAI4schoolbus/logs/*.log
   sudo systemctl restart visionai4schoolbus
   ```

## System Issues

### Service Won't Start

**Symptoms**: Service fails to start or immediately stops

**Diagnosis**:
```bash
# Check service status
sudo systemctl status visionai4schoolbus -l

# View detailed logs
sudo journalctl -u visionai4schoolbus --no-pager -l

# Check service file
systemctl cat visionai4schoolbus
```

**Common Solutions**:

1. **File permissions**:
   ```bash
   sudo chown -R visionai:visionai /opt/visionAI4schoolbus
   sudo chmod +x /opt/visionAI4schoolbus/main.py
   ```

2. **Python environment**:
   ```bash
   # Recreate virtual environment
   cd /opt/visionAI4schoolbus
   sudo -u visionai rm -rf venv
   sudo -u visionai python3 -m venv venv
   sudo -u visionai ./venv/bin/pip install -r requirements.txt
   ```

3. **Configuration file**:
   ```bash
   # Validate configuration
   sudo -u visionai ./venv/bin/python -c "
   from src.utils.config_manager import ConfigManager
   config = ConfigManager('config/config.yaml')
   print('Configuration OK')
   "
   ```

### High CPU Usage

**Symptoms**: System becomes unresponsive, high CPU temperature

**Diagnosis**:
```bash
# Monitor CPU usage
htop
top -p $(pgrep -f visionai4schoolbus)

# Check temperature
vcgencmd measure_temp
vcgencmd get_throttled

# Monitor inference performance
tail -f /opt/visionAI4schoolbus/logs/visionai4schoolbus.log | grep "inference"
```

**Solutions**:

1. **Reduce camera resolution**:
   ```yaml
   # config/config.yaml
   camera:
     resolution:
       width: 960   # Reduce from 1280
       height: 540  # Reduce from 720
     fps: 15        # Reduce from 30
   ```

2. **Optimize detection settings**:
   ```yaml
   detection:
     cooldown_seconds: 60    # Increase cooldown
     batch_size: 1          # Keep batch size at 1
     max_detections: 5      # Limit detections per frame
   ```

3. **Add cooling**:
   - Install heat sinks on Pi 5 CPU
   - Add cooling fan with PWM control
   - Ensure adequate ventilation

### Memory Issues

**Symptoms**: Out of memory errors, system freezing

**Diagnosis**:
```bash
# Monitor memory usage
free -h
ps aux --sort=-%mem | head

# Check for memory leaks
sudo -u visionai ./venv/bin/python -c "
import psutil
import os
process = psutil.Process(os.getpid())
print(f'Memory usage: {process.memory_info().rss / 1024 / 1024:.2f} MB')
"
```

**Solutions**:

1. **Increase swap space**:
   ```bash
   # Create 2GB swap file
   sudo fallocate -l 2G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   
   # Make permanent
   echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
   ```

2. **Optimize memory usage**:
   ```yaml
   # config/config.yaml
   camera:
     buffer_size: 1         # Minimize buffer
   monitoring:
     retention:
       detection_images_days: 1  # Reduce image retention
   ```

3. **Memory cleanup**:
   ```bash
   # Add to crontab for regular cleanup
   0 2 * * * /opt/visionAI4schoolbus/scripts/cleanup_logs.sh
   ```

## Hardware Problems

### Camera Issues

**Camera Not Detected**:

```bash
# Diagnosis
lsusb | grep -i camera
v4l2-ctl --list-devices
dmesg | grep -i video

# Solutions
# 1. Try different USB ports
# 2. Check USB cable quality
# 3. Power cycle camera
sudo modprobe -r uvcvideo
sudo modprobe uvcvideo
```

**Poor Image Quality**:

```bash
# Check camera capabilities
v4l2-ctl --list-formats-ext -d /dev/video0

# Test manual exposure
v4l2-ctl -d /dev/video0 --set-ctrl=exposure_auto=1
v4l2-ctl -d /dev/video0 --set-ctrl=exposure_absolute=100
```

**Camera Disconnections**:

```yaml
# config/config.yaml - Add reconnection logic
camera:
  timeout: 10.0
  reconnect_attempts: 3
  reconnect_delay: 5
```

### Hailo AI Kit Issues

**Device Not Found**:

```bash
# Diagnosis
lspci | grep -i hailo
lsmod | grep hailo
dmesg | grep -i hailo

# Solutions
# 1. Check physical connection
# 2. Reinstall drivers
sudo modprobe -r hailo_pci
sudo modprobe hailo_pci

# 3. Check PCIe slot
sudo dmesg | grep -i pcie
```

**Inference Errors**:

```bash
# Test Hailo device
hailortcli scan
hailortcli fw-control identify

# Check model compatibility
hailortcli parse-hef models/yolov8n_hailo.hef
```

**Thermal Throttling**:

```bash
# Monitor Hailo temperature
hailortcli monitor

# Solutions:
# 1. Add heat sink to Hailo chip
# 2. Improve case ventilation
# 3. Reduce inference frequency
```

### Power Supply Issues

**Under-voltage Warnings**:

```bash
# Check power status
vcgencmd get_throttled
# 0x0 = no issues
# 0x50000 = currently throttled
# 0x50005 = throttled + under-voltage

# Solutions:
# 1. Use official Pi 5 power supply (5V/5A)
# 2. Use high-quality USB-C cable
# 3. Check power connections
```

## Software Issues

### Python Dependencies

**Import Errors**:

```bash
# Diagnosis
sudo -u visionai /opt/visionAI4schoolbus/venv/bin/python -c "import cv2, numpy, yaml"

# Solutions
# 1. Reinstall packages
sudo -u visionai /opt/visionAI4schoolbus/venv/bin/pip install --upgrade --force-reinstall opencv-python

# 2. System package dependencies
sudo apt install python3-opencv libopencv-dev

# 3. Clear pip cache
sudo -u visionai /opt/visionAI4schoolbus/venv/bin/pip cache purge
```

**Version Conflicts**:

```bash
# Check installed versions
sudo -u visionai /opt/visionAI4schoolbus/venv/bin/pip list

# Create fresh environment
cd /opt/visionAI4schoolbus
sudo -u visionai rm -rf venv
sudo -u visionai python3 -m venv venv
sudo -u visionai ./venv/bin/pip install -r requirements.txt
```

### Configuration Issues

**YAML Parsing Errors**:

```bash
# Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('config/config.yaml'))"

# Common fixes:
# 1. Check indentation (use spaces, not tabs)
# 2. Quote special characters
# 3. Validate boolean values (true/false, not True/False)
```

**Configuration Loading Failures**:

```bash
# Test configuration loading
sudo -u visionai /opt/visionAI4schoolbus/venv/bin/python -c "
from src.utils.config_manager import ConfigManager
config = ConfigManager('config/config.yaml')
print('Camera device:', config.get('camera.device_id'))
print('Model path:', config.get('detection.model_path'))
"
```

## Performance Problems

### Slow Detection

**Diagnosis**:
```bash
# Monitor inference times
tail -f /opt/visionAI4schoolbus/logs/visionai4schoolbus.log | grep "inference_time"

# Check system load
iostat 1 5
sar -u 1 5
```

**Optimization**:

1. **Model optimization**:
   ```yaml
   detection:
     input_resolution:
       width: 416      # Reduce from 640
       height: 416     # Reduce from 640
   ```

2. **Frame skipping**:
   ```yaml
   camera:
     fps: 15           # Reduce frame rate
   monitoring:
     optimization:
       frame_skip_threshold: 0.15  # Skip frames if processing is slow
   ```

3. **Preprocessing optimization**:
   ```python
   # In detection code, use efficient preprocessing
   import cv2
   frame_resized = cv2.resize(frame, (416, 416), interpolation=cv2.INTER_LINEAR)
   ```

### Low Frame Rate

**Causes and Solutions**:

1. **Camera bandwidth limitations**:
   ```yaml
   camera:
     resolution:
       width: 1280
       height: 720
     fps: 20         # Reduce if necessary
   ```

2. **USB bandwidth**:
   - Use USB 3.0 ports
   - Avoid USB hubs
   - Use high-quality cables

3. **Processing bottleneck**:
   ```yaml
   detection:
     cooldown_seconds: 30    # Prevent overprocessing
   ```

## Network and Connectivity

### MQTT Connection Issues

**Diagnosis**:
```bash
# Test MQTT broker connectivity
nc -zv mqtt_broker_ip 1883

# Test authentication
mosquitto_pub -h mqtt_broker_ip -u username -P password -t test -m "hello"

# Check network connectivity
ping -c 4 mqtt_broker_ip
```

**Common Solutions**:

1. **Firewall issues**:
   ```bash
   # Check local firewall
   sudo ufw status
   
   # Allow MQTT port
   sudo ufw allow 1883
   ```

2. **Authentication problems**:
   ```yaml
   # config/config.yaml
   mqtt:
     username: "correct_username"
     password: "correct_password"
     timeout: 30          # Increase timeout
   ```

3. **Network configuration**:
   ```bash
   # Static IP configuration
   sudo nano /etc/dhcpcd.conf
   # Add:
   interface eth0
   static ip_address=192.168.1.100/24
   static routers=192.168.1.1
   ```

### WiFi Connectivity Issues

**Diagnosis**:
```bash
# Check WiFi status
iwconfig wlan0
wpa_cli status

# Check signal strength
iwconfig wlan0 | grep Signal
```

**Solutions**:

1. **Improve signal strength**:
   ```bash
   # Move Pi closer to router
   # Use external antenna
   # Switch to 5GHz band if available
   ```

2. **WiFi configuration**:
   ```bash
   sudo nano /etc/wpa_supplicant/wpa_supplicant.conf
   # Add:
   network={
       ssid="YourNetwork"
       psk="YourPassword"
       scan_ssid=1
       priority=1
   }
   ```

### Home Assistant Integration Issues

**Discovery Problems**:
```bash
# Check MQTT discovery messages
mosquitto_sub -h mqtt_broker_ip -t "homeassistant/+/+/config"

# Manual device registration
# Check HA logs for MQTT discovery
```

**Device Control Failures**:
```yaml
# Verify entity IDs in Home Assistant
home_assistant:
  devices:
    lights:
      - "light.front_porch"  # Ensure exact entity ID
```

## Detection Issues

### No Detections

**Diagnosis**:
```bash
# Test with sample images
sudo -u visionai /opt/visionAI4schoolbus/venv/bin/python test_detection.py

# Check model loading
sudo -u visionai /opt/visionAI4schoolbus/venv/bin/python -c "
from src.detection.hailo_detector import HailoDetector
detector = HailoDetector({'model_path': 'models/yolov8n_hailo.hef'})
print('Model loaded:', detector.initialize())
"
```

**Solutions**:

1. **Lower confidence threshold**:
   ```yaml
   detection:
     min_confidence: 0.4    # Reduce from 0.7
   ```

2. **Check detection zone**:
   ```yaml
   detection:
     detection_zone:
       x_min: 0.0    # Full image width
       y_min: 0.0    # Full image height
       x_max: 1.0
       y_max: 1.0
   ```

3. **Verify model classes**:
   ```bash
   hailortcli parse-hef models/yolov8n_hailo.hef
   ```

### False Positives

**Solutions**:

1. **Increase confidence threshold**:
   ```yaml
   detection:
     min_confidence: 0.8    # Increase from 0.7
   ```

2. **Add size filtering**:
   ```yaml
   detection:
     min_bus_size: 0.1      # Increase minimum size
     max_detections: 3      # Limit detections
   ```

3. **Implement additional filtering**:
   ```yaml
   detection:
     school_bus_criteria:
       color_detection: true
       expected_colors: ["yellow", "orange"]
   ```

### Inconsistent Detections

**Causes and Solutions**:

1. **Lighting conditions**:
   ```yaml
   camera:
     auto_exposure: true
     brightness: 10        # Adjust for conditions
   ```

2. **Model performance**:
   - Use higher-quality model
   - Retrain with environment-specific data
   - Implement detection smoothing

## Log Analysis

### Key Log Files

```bash
# Application logs
tail -f /opt/visionAI4schoolbus/logs/visionai4schoolbus.log

# System service logs
sudo journalctl -u visionai4schoolbus -f

# System logs
sudo journalctl --since "1 hour ago" | grep -i error

# Performance metrics
cat /opt/visionAI4schoolbus/logs/metrics.json | jq '.'
```

### Log Analysis Scripts

```bash
#!/bin/bash
# analyze_logs.sh

echo "=== Log Analysis ==="

# Error summary
echo "Recent Errors:"
grep -i error /opt/visionAI4schoolbus/logs/visionai4schoolbus.log | tail -10

# Detection statistics
echo -e "\nDetection Statistics:"
grep "School bus detected" /opt/visionAI4schoolbus/logs/visionai4schoolbus.log | wc -l
echo "Total detections today"

# Performance issues
echo -e "\nPerformance Issues:"
grep "inference_time" /opt/visionAI4schoolbus/logs/visionai4schoolbus.log | \
awk '{print $NF}' | sort -n | tail -5
echo "Slowest inference times (seconds)"

# System resource warnings
echo -e "\nResource Warnings:"
grep -E "(CPU|memory|temperature)" /opt/visionAI4schoolbus/logs/visionai4schoolbus.log | tail -5
```

### Common Log Patterns

**Successful Operation**:
```
2024-01-15 08:30:15 - detection - INFO - School bus detected! Confidence: 0.85
2024-01-15 08:30:15 - automation - INFO - Activating smart devices
2024-01-15 08:30:16 - mqtt - INFO - Published detection event
```

**Error Patterns**:
```
# Camera issues
ERROR - Camera device not found: /dev/video0

# Hailo issues  
ERROR - Failed to initialize Hailo detector: Device not found

# MQTT issues
WARNING - MQTT connection lost, attempting reconnection

# Memory issues
ERROR - Out of memory: Cannot allocate buffer
```

## Recovery Procedures

### Complete System Reset

```bash
#!/bin/bash
# emergency_reset.sh

echo "=== Emergency System Reset ==="

# Stop service
sudo systemctl stop visionai4schoolbus

# Backup current configuration
sudo cp /opt/visionAI4schoolbus/config/config.yaml /opt/visionAI4schoolbus/config/config.yaml.backup

# Reset to template
sudo -u visionai cp /opt/visionAI4schoolbus/config/config.template.yaml /opt/visionAI4schoolbus/config/config.yaml

# Clear logs
sudo truncate -s 0 /opt/visionAI4schoolbus/logs/*.log

# Restart hardware
sudo modprobe -r uvcvideo hailo_pci
sleep 2
sudo modprobe uvcvideo hailo_pci

# Restart service
sudo systemctl start visionai4schoolbus

echo "=== Reset Complete ==="
echo "Check service status: sudo systemctl status visionai4schoolbus"
```

### Configuration Rollback

```bash
# Backup current config
sudo cp /opt/visionAI4schoolbus/config/config.yaml /opt/visionAI4schoolbus/config/config.yaml.$(date +%Y%m%d_%H%M%S)

# Restore from backup
sudo cp /opt/visionAI4schoolbus/config/config.yaml.backup /opt/visionAI4schoolbus/config/config.yaml

# Restart service
sudo systemctl restart visionai4schoolbus
```

### Factory Reset

```bash
#!/bin/bash
# factory_reset.sh

echo "WARNING: This will reset the entire system!"
read -p "Continue? (yes/no): " confirm

if [ "$confirm" = "yes" ]; then
    # Remove application
    sudo systemctl stop visionai4schoolbus
    sudo systemctl disable visionai4schoolbus
    sudo rm -rf /opt/visionAI4schoolbus
    
    # Remove service
    sudo rm /etc/systemd/system/visionai4schoolbus.service
    sudo systemctl daemon-reload
    
    # Remove user
    sudo userdel visionai
    
    echo "Factory reset complete. Reinstall required."
fi
```

## Getting Help

### Before Asking for Help

1. **Run diagnostics script**:
   ```bash
   ./quick_diagnostics.sh > system_report.txt
   ```

2. **Collect relevant logs**:
   ```bash
   # Recent application logs
   tail -100 /opt/visionAI4schoolbus/logs/visionai4schoolbus.log > app_logs.txt
   
   # System service logs
   sudo journalctl -u visionai4schoolbus --since "1 day ago" > service_logs.txt
   
   # System information
   uname -a > system_info.txt
   lsusb >> system_info.txt
   lspci >> system_info.txt
   ```

3. **Document your issue**:
   - What were you trying to do?
   - What actually happened?
   - What error messages did you see?
   - What steps have you tried?

### Community Support

**GitHub Issues**:
- Check existing issues: https://github.com/msasikumar/visionAI4schoolbus/issues
- Create new issue with:
  - Clear problem description
  - Hardware configuration
  - Software versions
  - Log excerpts
  - Steps to reproduce

**Documentation**:
- [Hardware Setup Guide](hardware-setup.md)
- [Installation Guide](installation-guide.md)
- [Configuration Guide](configuration.md)
- [API Reference](api-reference.md)

### Professional Support

For complex issues or commercial deployments:
- Include detailed system specifications
- Provide complete log files
- Document business requirements
- Consider professional consultation

### Emergency Contacts

**System Down**:
1. Run emergency reset procedure
2. Check hardware connections
3. Verify power supply
4. Contact system administrator

**Security Issues**:
1. Disconnect from network
2. Review access logs
3. Update passwords
4. Contact security team

Remember: Most issues can be resolved by carefully following the diagnostic steps and checking the basics (power, connections, permissions, configuration).