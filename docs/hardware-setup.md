# Hardware Setup Guide

This guide provides detailed instructions for setting up the hardware components of the VisionAI4SchoolBus system.

## Table of Contents

- [Required Hardware](#required-hardware)
- [Component Overview](#component-overview)
- [Assembly Instructions](#assembly-instructions)
- [Camera Positioning](#camera-positioning)
- [Power Requirements](#power-requirements)
- [Network Configuration](#network-configuration)
- [Testing Hardware](#testing-hardware)
- [Troubleshooting](#troubleshooting)

## Required Hardware

### Essential Components

| Component | Model/Specification | Purpose | Estimated Cost |
|-----------|-------------------|---------|---------------|
| **Raspberry Pi 5** | 4GB or 8GB RAM | Main processing unit | $60-80 |
| **Raspberry Pi AI Kit** | M.2 HAT+ with Hailo-8L | AI acceleration | $70 |
| **USB Camera** | 1080p, 30fps, USB 2.0/3.0 | Video capture | $30-50 |
| **MicroSD Card** | 64GB+ Class 10, U3 | System storage | $15-25 |
| **Power Supply** | 5V/5A USB-C | Pi 5 + AI Kit power | $15-20 |
| **Ethernet Cable** | Cat 6 (optional) | Network connectivity | $5-10 |
| **Case** | Pi 5 compatible with M.2 HAT | Protection | $20-30 |

### Optional Components

| Component | Purpose | Notes |
|-----------|---------|-------|
| **SSD Drive** | Faster storage, log retention | USB 3.0 or M.2 NVMe |
| **Heat Sinks** | Better thermal management | For Pi 5 CPU and Hailo chip |
| **Cooling Fan** | Active cooling | 5V PWM fan recommended |
| **External Antenna** | Better WiFi reception | If using WiFi connectivity |
| **UPS/Battery** | Power backup | Prevents data loss during outages |

## Component Overview

### Raspberry Pi 5 Specifications

- **CPU**: Broadcom BCM2712, quad-core Cortex-A76 @ 2.4GHz
- **RAM**: 4GB or 8GB LPDDR4X
- **GPU**: VideoCore VII, supporting OpenGL ES 3.1, Vulkan 1.2
- **I/O**: 2× USB 3.0, 2× USB 2.0, 2× micro HDMI, GPIO header
- **Storage**: MicroSD slot, PCIe 2.0 x1 interface
- **Network**: Gigabit Ethernet, 802.11ac WiFi, Bluetooth 5.0

### Raspberry Pi AI Kit Details

- **AI Accelerator**: Hailo-8L NPU
- **Performance**: 13 TOPS at INT8
- **Interface**: M.2 2242 B+M key
- **Connection**: Via M.2 HAT+ to Pi 5's PCIe slot
- **Power**: Draws additional 2-3W under load

### Camera Specifications

**Recommended Camera Features:**
- **Resolution**: 1920x1080 (1080p) minimum
- **Frame Rate**: 30 fps
- **Interface**: USB 2.0/3.0 (USB-C cameras work with adapter)
- **Focus**: Auto-focus preferred, manual focus acceptable
- **Field of View**: 70-90 degrees
- **Low Light**: Good performance in various lighting conditions

**Tested Compatible Cameras:**
- Logitech C920/C922/C930e
- Microsoft LifeCam Studio
- ELP USB Camera modules
- Arducam USB cameras

## Assembly Instructions

### Step 1: Prepare the Raspberry Pi 5

1. **Handle with Care**
   ```bash
   # Ensure you're grounded to prevent static discharge
   # Work on anti-static mat or touch grounded metal object
   ```

2. **Insert MicroSD Card**
   - Use the official Raspberry Pi Imager
   - Flash Raspberry Pi OS (64-bit, latest version)
   - Enable SSH and set username/password before flashing

### Step 2: Install the M.2 HAT+

1. **Power Off Completely**
   ```bash
   # Ensure Pi is completely powered down and unplugged
   ```

2. **Install M.2 HAT+**
   - Align the HAT with the GPIO pins
   - Press down firmly but gently until fully seated
   - Secure with provided standoffs and screws

3. **Install Hailo-8L Module**
   - Remove M.2 mounting screw from HAT
   - Insert Hailo-8L module at 30-degree angle
   - Press down and secure with screw

### Step 3: Camera Setup

1. **Camera Selection**
   ```bash
   # Test camera compatibility first
   lsusb  # Should show camera when connected
   ```

2. **Physical Mounting**
   - Position camera with clear view of target area
   - Secure mounting to prevent vibration
   - Protect from weather if outdoor installation

3. **USB Connection**
   - Use high-quality USB cable (max 3 meters for USB 2.0)
   - Connect to USB 3.0 port for best performance
   - Avoid USB hubs if possible

### Step 4: Case Installation

1. **Choose Appropriate Case**
   - Must accommodate M.2 HAT+ height
   - Provide adequate ventilation
   - Allow access to USB ports and GPIO

2. **Install Components in Case**
   - Install heat sinks before case assembly
   - Route cables cleanly
   - Ensure no contact with moving parts (fans)

### Step 5: Power Connection

1. **Power Supply Requirements**
   - **Minimum**: 5V/3A (for basic operation)
   - **Recommended**: 5V/5A (for AI Kit + USB devices)
   - Use official Raspberry Pi power supply when possible

2. **Power Distribution**
   ```
   Component Power Draw:
   - Raspberry Pi 5 baseline: ~800mA
   - Pi 5 under load: ~1.2A
   - AI Kit (Hailo-8L): ~600mA
   - USB Camera: ~200-500mA
   - Total recommended: 5A capacity
   ```

## Camera Positioning

### Optimal Placement Guidelines

1. **Height and Angle**
   - **Height**: 8-12 feet above ground level
   - **Angle**: 15-30 degrees downward
   - **View**: Clear line of sight to street

2. **Field of View Coverage**
   ```
   Recommended Coverage:
   - 30-50 feet of street length
   - Full width of roadway
   - Minimal obstructions (trees, poles)
   ```

3. **Environmental Considerations**
   - **Weather Protection**: IP65 housing for outdoor use
   - **Sun Glare**: Avoid direct sunlight on lens
   - **Night Vision**: Consider IR illumination
   - **Vibration**: Secure mounting to prevent shake

### Installation Examples

```bash
# Example mounting positions:
# 1. House eaves/soffit
# 2. Dedicated pole mount
# 3. Existing light fixture
# 4. Window-mounted (indoor)
```

## Power Requirements

### Power Consumption Analysis

| Component | Idle Power | Peak Power | Notes |
|-----------|------------|------------|-------|
| Raspberry Pi 5 | 3.7W | 8W | Varies with CPU load |
| Hailo-8L NPU | 0.5W | 3W | During AI inference |
| USB Camera | 1W | 2.5W | Depends on resolution/fps |
| **Total System** | **5.2W** | **13.5W** | **Plus 20% margin** |

### Power Supply Recommendations

1. **Primary Power**
   ```bash
   # Official Raspberry Pi 5 Power Supply
   # 5V/5A, USB-C connector
   # Integrated cable, high efficiency
   ```

2. **Power Backup (Optional)**
   ```bash
   # UPS Options:
   # - APC Back-UPS Connect UPS
   # - CyberPower CP425SLG
   # - PiJuice HAT (for Pi-specific backup)
   ```

3. **Power Monitoring**
   ```bash
   # Monitor power draw
   vcgencmd measure_volts
   vcgencmd measure_temp
   vcgencmd get_throttled
   ```

## Network Configuration

### Ethernet Connection (Recommended)

1. **Physical Connection**
   - Use Cat 6 cable for best performance
   - Direct connection to router/switch
   - Gigabit connection provides ample bandwidth

2. **Static IP Configuration**
   ```bash
   # Edit network configuration
   sudo nano /etc/dhcpcd.conf
   
   # Add static IP configuration:
   interface eth0
   static ip_address=192.168.1.100/24
   static routers=192.168.1.1
   static domain_name_servers=8.8.8.8
   ```

### WiFi Configuration

1. **WiFi Setup**
   ```bash
   # Configure WiFi
   sudo raspi-config
   # Navigate to System Options > Wireless LAN
   
   # Or edit manually:
   sudo nano /etc/wpa_supplicant/wpa_supplicant.conf
   ```

2. **WiFi Optimization**
   ```bash
   # For stable connection:
   # - Use 5GHz band if available
   # - Position Pi close to router
   # - Consider external antenna
   ```

## Testing Hardware

### Initial System Test

1. **Boot Test**
   ```bash
   # Check successful boot
   sudo dmesg | grep -i error
   sudo dmesg | grep -i hailo
   
   # Verify all hardware detected
   lsusb  # Should show camera
   lspci  # Should show Hailo device
   ```

2. **Camera Test**
   ```bash
   # Test camera functionality
   v4l2-ctl --list-devices
   v4l2-ctl --list-formats-ext
   
   # Capture test image
   fswebcam -r 1280x720 --no-banner test.jpg
   ```

3. **Hailo AI Kit Test**
   ```bash
   # Verify Hailo runtime
   hailortcli fw-control identify
   
   # Check temperature and status
   hailortcli monitor
   ```

### Performance Benchmarks

1. **System Performance**
   ```bash
   # CPU and memory test
   htop
   free -h
   df -h
   
   # Temperature monitoring
   vcgencmd measure_temp
   ```

2. **Network Performance**
   ```bash
   # Network speed test
   wget -O /dev/null http://speedtest.wdc01.softlayer.com/downloads/test100.zip
   
   # MQTT connectivity test
   mosquitto_pub -h broker_ip -t test -m "hello"
   ```

## Troubleshooting

### Common Hardware Issues

1. **Power Issues**
   ```bash
   # Check power supply adequacy
   vcgencmd get_throttled
   # Result: throttled=0x0 (no issues)
   # Any other value indicates power problems
   
   # Monitor voltage
   vcgencmd measure_volts
   # Should be ~5.1V consistently
   ```

2. **Camera Not Detected**
   ```bash
   # Check USB connection
   lsusb | grep -i camera
   
   # Test different USB ports
   dmesg | tail -20  # Check for connection messages
   
   # Verify camera permissions
   ls -l /dev/video*
   sudo usermod -a -G video $USER
   ```

3. **Hailo Device Issues**
   ```bash
   # Check PCIe connection
   lspci | grep -i hailo
   
   # Verify driver installation
   lsmod | grep hailo
   
   # Check device status
   hailortcli scan
   ```

4. **Thermal Issues**
   ```bash
   # Monitor temperatures
   vcgencmd measure_temp
   # Pi 5: Should stay below 80°C
   # Add cooling if consistently above 70°C
   
   # Check for thermal throttling
   vcgencmd get_throttled
   ```

5. **Network Connectivity**
   ```bash
   # Test basic connectivity
   ping -c 4 8.8.8.8
   
   # Check WiFi signal strength
   iwconfig wlan0
   
   # MQTT broker connection
   nc -zv broker_ip 1883
   ```

### Hardware Diagnostics Script

```bash
#!/bin/bash
# hardware_check.sh - Comprehensive hardware diagnostic

echo "=== VisionAI4SchoolBus Hardware Diagnostics ==="

echo "1. System Information:"
uname -a
cat /proc/device-tree/model

echo "2. Power Status:"
vcgencmd measure_volts
vcgencmd measure_temp
vcgencmd get_throttled

echo "3. USB Devices:"
lsusb

echo "4. PCIe Devices:"
lspci

echo "5. Camera Detection:"
v4l2-ctl --list-devices 2>/dev/null || echo "No cameras detected"

echo "6. Network Status:"
ip addr show
iwconfig 2>/dev/null | grep -E "(ESSID|Signal)"

echo "7. Hailo Status:"
hailortcli scan 2>/dev/null || echo "Hailo device not found"

echo "8. Disk Usage:"
df -h

echo "9. Memory Usage:"
free -h

echo "=== Diagnostics Complete ==="
```

Save this script and run with:
```bash
chmod +x hardware_check.sh
./hardware_check.sh > hardware_diagnostics.txt
```

## Next Steps

After completing the hardware setup:

1. **Proceed to Software Installation**
   - Follow the [Installation Guide](installation-guide.md)
   - Install required software packages
   - Configure the detection system

2. **System Configuration**
   - Review [Configuration Guide](configuration.md)
   - Customize settings for your environment
   - Set up Home Assistant integration

3. **Testing and Calibration**
   - Run system tests
   - Calibrate detection parameters
   - Verify automation functionality

For additional support, see the [Troubleshooting Guide](troubleshooting.md) or open an issue on the project repository.