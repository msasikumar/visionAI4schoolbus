#!/bin/bash
# VisionAI4SchoolBus Quick Start Script

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}VisionAI4SchoolBus Quick Start${NC}"
echo "==============================="

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    echo -e "${YELLOW}Running as root. For installation, this is correct.${NC}"
else
    echo -e "${YELLOW}Running as regular user. This is for post-installation setup.${NC}"
fi

echo
echo "Available options:"
echo "1. Full Installation (requires root)"
echo "2. Test System"
echo "3. Start Service"
echo "4. Stop Service"
echo "5. View Logs"
echo "6. Check Status"
echo "7. Configuration Help"
echo "8. Exit"
echo

read -p "Select option (1-8): " choice

case $choice in
    1)
        if [[ $EUID -ne 0 ]]; then
            echo "Please run with sudo for installation"
            exit 1
        fi
        echo -e "${GREEN}Starting installation...${NC}"
        ./install.sh
        ;;
    2)
        echo -e "${GREEN}Running system tests...${NC}"
        python3 test_system.py
        ;;
    3)
        echo -e "${GREEN}Starting VisionAI4SchoolBus service...${NC}"
        sudo systemctl start visionai4schoolbus
        echo "Service started. Use option 6 to check status."
        ;;
    4)
        echo -e "${GREEN}Stopping VisionAI4SchoolBus service...${NC}"
        sudo systemctl stop visionai4schoolbus
        echo "Service stopped."
        ;;
    5)
        echo -e "${GREEN}Showing recent logs (Ctrl+C to exit)...${NC}"
        sudo journalctl -u visionai4schoolbus -f
        ;;
    6)
        echo -e "${GREEN}Service status:${NC}"
        sudo systemctl status visionai4schoolbus
        ;;
    7)
        echo -e "${GREEN}Configuration Help:${NC}"
        echo
        echo "1. Edit configuration file:"
        echo "   sudo nano /opt/visionai4schoolbus/config/config.yaml"
        echo
        echo "2. Key settings to configure:"
        echo "   - Camera device ID (usually 0)"
        echo "   - MQTT broker settings"
        echo "   - Home Assistant device entities"
        echo "   - Detection confidence threshold"
        echo "   - Device activation duration"
        echo
        echo "3. Test configuration:"
        echo "   python3 test_system.py"
        echo
        echo "4. After changes, restart service:"
        echo "   sudo systemctl restart visionai4schoolbus"
        ;;
    8)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo "Invalid option"
        exit 1
        ;;
esac
