#!/bin/bash
# VisionAI4SchoolBus Installation Script
# For Raspberry Pi 5 with Hailo AI Kit

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="/opt/visionai4schoolbus"
SERVICE_USER="visionai"
PYTHON_VERSION="3.11"

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

detect_platform() {
    print_status "Detecting platform..."
    
    if [[ ! -f /proc/device-tree/model ]]; then
        print_error "Cannot detect device model"
        exit 1
    fi
    
    MODEL=$(cat /proc/device-tree/model)
    print_status "Detected: $MODEL"
    
    if [[ "$MODEL" != *"Raspberry Pi 5"* ]]; then
        print_warning "This script is optimized for Raspberry Pi 5"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

update_system() {
    print_status "Updating system packages..."
    apt update && apt upgrade -y
    
    print_status "Installing system dependencies..."
    apt install -y \
        python3 \
        python3-pip \
        python3-venv \
        git \
        wget \
        curl \
        build-essential \
        cmake \
        pkg-config \
        libjpeg-dev \
        libpng-dev \
        libtiff-dev \
        libavcodec-dev \
        libavformat-dev \
        libswscale-dev \
        libv4l-dev \
        libxvidcore-dev \
        libx264-dev \
        libgtk-3-dev \
        libatlas-base-dev \
        gfortran \
        python3-dev \
        mosquitto \
        mosquitto-clients
        
    print_success "System packages updated and dependencies installed"
}

install_hailo_runtime() {
    print_status "Installing Hailo Runtime..."
    
    # Check if Hailo AI Kit is connected
    if lsusb | grep -q "03e7"; then
        print_success "Hailo AI Kit detected"
    else
        print_warning "Hailo AI Kit not detected. Make sure it's properly connected."
    fi
    
    # Download and install Hailo runtime
    cd /tmp
    
    # Note: The actual URLs and installation steps may vary based on Hailo's release
    # This is a placeholder for the actual Hailo installation
    print_status "Downloading Hailo Runtime (this may take a while)..."
    
    # Check if hailo-platform is already available
    if python3 -c "import hailo_platform" 2>/dev/null; then
        print_success "Hailo platform already installed"
    else
        print_status "Installing Hailo runtime packages..."
        # Add Hailo's repository and install packages
        # This would be replaced with actual Hailo installation commands
        wget -qO- https://hailo.ai/developer-zone/software-downloads/hailo-software-suite/ || true
        print_warning "Please install Hailo Runtime manually following the official documentation"
        print_warning "Visit: https://hailo.ai/developer-zone/software-downloads/"
    fi
}

create_user() {
    print_status "Creating service user..."
    
    if id "$SERVICE_USER" &>/dev/null; then
        print_status "User $SERVICE_USER already exists"
    else
        useradd -r -s /bin/false -d "$INSTALL_DIR" "$SERVICE_USER"
        usermod -a -G video,dialout "$SERVICE_USER"
        print_success "Created user $SERVICE_USER"
    fi
}

install_application() {
    print_status "Installing VisionAI4SchoolBus application..."
    
    # Create installation directory
    mkdir -p "$INSTALL_DIR"
    
    # Copy application files
    cp -r . "$INSTALL_DIR/"
    
    # Set ownership
    chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"
    
    # Create Python virtual environment
    print_status "Creating Python virtual environment..."
    cd "$INSTALL_DIR"
    
    sudo -u "$SERVICE_USER" python3 -m venv venv
    sudo -u "$SERVICE_USER" ./venv/bin/pip install --upgrade pip
    
    # Install Python dependencies
    print_status "Installing Python dependencies..."
    sudo -u "$SERVICE_USER" ./venv/bin/pip install -r requirements.txt
    
    # Create configuration from template
    if [[ ! -f "$INSTALL_DIR/config/config.yaml" ]]; then
        sudo -u "$SERVICE_USER" cp "$INSTALL_DIR/config/config.template.yaml" "$INSTALL_DIR/config/config.yaml"
        print_success "Created configuration file from template"
    fi
    
    # Create log directories
    mkdir -p "$INSTALL_DIR/logs/detections"
    chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR/logs"
    
    print_success "Application installed to $INSTALL_DIR"
}

install_systemd_service() {
    print_status "Installing systemd service..."
    
    # Create systemd service file
    cat > /etc/systemd/system/visionai4schoolbus.service << EOL
[Unit]
Description=VisionAI4SchoolBus - School Bus Detection System
After=network.target
Wants=network.target

[Service]
Type=simple
User=$SERVICE_USER
Group=$SERVICE_USER
WorkingDirectory=$INSTALL_DIR
Environment=PATH=$INSTALL_DIR/venv/bin
ExecStart=$INSTALL_DIR/venv/bin/python main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=visionai4schoolbus

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$INSTALL_DIR/logs $INSTALL_DIR/config
ProtectKernelTunables=true
ProtectControlGroups=true
RestrictRealtime=true

[Install]
WantedBy=multi-user.target
EOL

    systemctl daemon-reload
    systemctl enable visionai4schoolbus
    
    print_success "Systemd service installed and enabled"
}

setup_mqtt_broker() {
    print_status "Configuring MQTT broker..."
    
    # Start and enable mosquitto
    systemctl enable mosquitto
    systemctl start mosquitto
    
    # Create basic mosquitto configuration
    cat > /etc/mosquitto/conf.d/visionai4schoolbus.conf << EOL
# VisionAI4SchoolBus MQTT Configuration
listener 1883
allow_anonymous true
EOL

    systemctl restart mosquitto
    print_success "MQTT broker configured and started"
}

create_startup_script() {
    print_status "Creating management scripts..."
    
    # Create start script
    cat > "$INSTALL_DIR/start.sh" << EOL
#!/bin/bash
cd "$INSTALL_DIR"
./venv/bin/python main.py
EOL
    
    # Create test script
    cat > "$INSTALL_DIR/test.sh" << EOL
#!/bin/bash
cd "$INSTALL_DIR"
echo "Testing camera access..."
./venv/bin/python -c "
import cv2
cap = cv2.VideoCapture(0)
if cap.isOpened():
    print('Camera test: PASSED')
    cap.release()
else:
    print('Camera test: FAILED')
"

echo "Testing MQTT connection..."
mosquitto_pub -h localhost -t "test/topic" -m "test message"
if [ $? -eq 0 ]; then
    echo "MQTT test: PASSED"
else
    echo "MQTT test: FAILED"
fi
EOL
    
    chmod +x "$INSTALL_DIR/start.sh"
    chmod +x "$INSTALL_DIR/test.sh"
    chown "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR/start.sh"
    chown "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR/test.sh"
    
    print_success "Management scripts created"
}

print_final_instructions() {
    print_success "Installation completed!"
    echo
    echo "=== Next Steps ==="
    echo "1. Edit the configuration file:"
    echo "   sudo nano $INSTALL_DIR/config/config.yaml"
    echo
    echo "2. Download or place your Hailo model file:"
    echo "   sudo cp your_model.hef $INSTALL_DIR/models/"
    echo
    echo "3. Test the installation:"
    echo "   sudo -u $SERVICE_USER $INSTALL_DIR/test.sh"
    echo
    echo "4. Start the service:"
    echo "   sudo systemctl start visionai4schoolbus"
    echo
    echo "5. Check service status:"
    echo "   sudo systemctl status visionai4schoolbus"
    echo
    echo "6. View logs:"
    echo "   sudo journalctl -u visionai4schoolbus -f"
    echo
    echo "=== Configuration Notes ==="
    echo "- Configure your Home Assistant entities in the config file"
    echo "- Set up your MQTT broker connection details"
    echo "- Adjust detection sensitivity and timing parameters"
    echo "- Position your camera to view the street effectively"
    echo
    print_success "VisionAI4SchoolBus is ready to use!"
}

# Main installation flow
main() {
    echo "VisionAI4SchoolBus Installation Script"
    echo "======================================"
    
    check_root
    detect_platform
    update_system
    install_hailo_runtime
    create_user
    install_application
    install_systemd_service
    setup_mqtt_broker
    create_startup_script
    print_final_instructions
}

# Run main function
main "$@"
