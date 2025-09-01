"""
Home Assistant Controller
Manages Home Assistant device integration and automation
"""

import time
import json
from typing import Dict, Any, List, Optional
from ..utils.logger import get_logger


class HomeAssistantController:
    """Controls Home Assistant devices via MQTT"""
    
    def __init__(self, mqtt_client, config: Dict[str, Any]):
        self.mqtt_client = mqtt_client
        self.config = config
        self.logger = get_logger('home_assistant')
        
        # Home Assistant configuration
        self.discovery_prefix = config.get('discovery_prefix', 'homeassistant')
        self.device_name = config.get('device_name', 'School Bus Detector')
        
        # Device lists
        self.lights = config.get('devices', {}).get('lights', [])
        self.switches = config.get('devices', {}).get('switches', [])
        self.voice_announcements = config.get('voice_announcements', True)
        self.announcement_message = config.get('announcement_message', 'School bus detected in front of the house')
        
        # State tracking
        self.activated_devices = set()
        self.activation_time = None
        
        self.logger.info(f"Home Assistant controller initialized with {len(self.lights)} lights and {len(self.switches)} switches")
    
    def activate_devices(self) -> bool:
        """Activate all configured devices when school bus is detected"""
        try:
            self.logger.info("Activating Home Assistant devices")
            success_count = 0
            total_devices = len(self.lights) + len(self.switches)
            
            # Turn on lights
            for light in self.lights:
                if self._turn_on_light(light):
                    self.activated_devices.add(light)
                    success_count += 1
                else:
                    self.logger.warning(f"Failed to turn on light: {light}")
            
            # Turn on switches
            for switch in self.switches:
                if self._turn_on_switch(switch):
                    self.activated_devices.add(switch)
                    success_count += 1
                else:
                    self.logger.warning(f"Failed to turn on switch: {switch}")
            
            # Send voice announcement if enabled
            if self.voice_announcements:
                self._send_voice_announcement()
            
            # Send notification
            self._send_notification("School Bus Detected", "A school bus has been detected in front of the house. Smart devices have been activated.")
            
            self.activation_time = time.time()
            
            if success_count > 0:
                self.logger.info(f"Successfully activated {success_count}/{total_devices} devices")
                return True
            else:
                self.logger.error("Failed to activate any devices")
                return False
                
        except Exception as e:
            self.logger.error(f"Error activating devices: {e}")
            return False
    
    def deactivate_devices(self) -> bool:
        """Deactivate all previously activated devices"""
        try:
            self.logger.info("Deactivating Home Assistant devices")
            success_count = 0
            
            # Create a copy of activated devices to iterate over
            devices_to_deactivate = self.activated_devices.copy()
            
            for device in devices_to_deactivate:
                if device in self.lights:
                    if self._turn_off_light(device):
                        self.activated_devices.remove(device)
                        success_count += 1
                elif device in self.switches:
                    if self._turn_off_switch(device):
                        self.activated_devices.remove(device)
                        success_count += 1
            
            # Send deactivation notification
            if success_count > 0:
                self._send_notification("Devices Deactivated", f"School bus detection timeout reached. {success_count} devices have been deactivated.")
            
            self.activation_time = None
            
            if success_count > 0:
                self.logger.info(f"Successfully deactivated {success_count} devices")
                return True
            else:
                self.logger.warning("No devices were deactivated")
                return False
                
        except Exception as e:
            self.logger.error(f"Error deactivating devices: {e}")
            return False
    
    def _turn_on_light(self, light_entity: str) -> bool:
        """Turn on a specific light entity"""
        try:
            # Remove 'light.' prefix if present for topic
            entity_id = light_entity.replace('light.', '')
            topic = f"{light_entity}/set"
            
            command = {
                'state': 'ON',
                'brightness': 255,
                'transition': 1
            }
            
            if self.mqtt_client and self.mqtt_client.is_connected():
                result = self.mqtt_client.publish(topic, command)
                if result:
                    self.logger.debug(f"Turned on light: {light_entity}")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error turning on light {light_entity}: {e}")
            return False
    
    def _turn_off_light(self, light_entity: str) -> bool:
        """Turn off a specific light entity"""
        try:
            entity_id = light_entity.replace('light.', '')
            topic = f"{light_entity}/set"
            
            command = {
                'state': 'OFF',
                'transition': 2
            }
            
            if self.mqtt_client and self.mqtt_client.is_connected():
                result = self.mqtt_client.publish(topic, command)
                if result:
                    self.logger.debug(f"Turned off light: {light_entity}")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error turning off light {light_entity}: {e}")
            return False
    
    def _turn_on_switch(self, switch_entity: str) -> bool:
        """Turn on a specific switch entity"""
        try:
            entity_id = switch_entity.replace('switch.', '')
            topic = f"{switch_entity}/set"
            
            command = {'state': 'ON'}
            
            if self.mqtt_client and self.mqtt_client.is_connected():
                result = self.mqtt_client.publish(topic, command)
                if result:
                    self.logger.debug(f"Turned on switch: {switch_entity}")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error turning on switch {switch_entity}: {e}")
            return False
    
    def _turn_off_switch(self, switch_entity: str) -> bool:
        """Turn off a specific switch entity"""
        try:
            entity_id = switch_entity.replace('switch.', '')
            topic = f"{switch_entity}/set"
            
            command = {'state': 'OFF'}
            
            if self.mqtt_client and self.mqtt_client.is_connected():
                result = self.mqtt_client.publish(topic, command)
                if result:
                    self.logger.debug(f"Turned off switch: {switch_entity}")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error turning off switch {switch_entity}: {e}")
            return False
    
    def _send_voice_announcement(self) -> bool:
        """Send voice announcement via MQTT"""
        try:
            if self.mqtt_client and self.mqtt_client.is_connected():
                return self.mqtt_client.publish_announcement(self.announcement_message, 'high')
            return False
            
        except Exception as e:
            self.logger.error(f"Error sending voice announcement: {e}")
            return False
    
    def _send_notification(self, title: str, message: str) -> bool:
        """Send notification to Home Assistant"""
        try:
            topic = "homeassistant/notify"
            
            notification = {
                'title': title,
                'message': message,
                'data': {
                    'tag': 'schoolbus_detection',
                    'group': 'security',
                    'timestamp': time.time()
                }
            }
            
            if self.mqtt_client and self.mqtt_client.is_connected():
                return self.mqtt_client.publish(topic, notification)
            return False
            
        except Exception as e:
            self.logger.error(f"Error sending notification: {e}")
            return False
    
    def test_devices(self) -> Dict[str, bool]:
        """Test all configured devices"""
        results = {}
        
        # Test lights
        for light in self.lights:
            self.logger.info(f"Testing light: {light}")
            turn_on = self._turn_on_light(light)
            time.sleep(1)
            turn_off = self._turn_off_light(light)
            results[light] = turn_on and turn_off
        
        # Test switches
        for switch in self.switches:
            self.logger.info(f"Testing switch: {switch}")
            turn_on = self._turn_on_switch(switch)
            time.sleep(1)
            turn_off = self._turn_off_switch(switch)
            results[switch] = turn_on and turn_off
        
        return results
    
    def get_device_status(self) -> Dict[str, Any]:
        """Get current device status"""
        return {
            'total_lights': len(self.lights),
            'total_switches': len(self.switches),
            'activated_devices': list(self.activated_devices),
            'activation_time': self.activation_time,
            'voice_announcements_enabled': self.voice_announcements,
            'mqtt_connected': self.mqtt_client.is_connected() if self.mqtt_client else False
        }
    
    def add_device(self, device_type: str, entity_id: str) -> bool:
        """Add a new device to control"""
        try:
            if device_type == 'light':
                if entity_id not in self.lights:
                    self.lights.append(entity_id)
                    self.logger.info(f"Added light device: {entity_id}")
                    return True
            elif device_type == 'switch':
                if entity_id not in self.switches:
                    self.switches.append(entity_id)
                    self.logger.info(f"Added switch device: {entity_id}")
                    return True
            else:
                self.logger.error(f"Unknown device type: {device_type}")
                return False
                
            self.logger.warning(f"Device {entity_id} already exists")
            return False
            
        except Exception as e:
            self.logger.error(f"Error adding device {entity_id}: {e}")
            return False
    
    def remove_device(self, device_type: str, entity_id: str) -> bool:
        """Remove a device from control"""
        try:
            if device_type == 'light' and entity_id in self.lights:
                self.lights.remove(entity_id)
                if entity_id in self.activated_devices:
                    self.activated_devices.remove(entity_id)
                self.logger.info(f"Removed light device: {entity_id}")
                return True
            elif device_type == 'switch' and entity_id in self.switches:
                self.switches.remove(entity_id)
                if entity_id in self.activated_devices:
                    self.activated_devices.remove(entity_id)
                self.logger.info(f"Removed switch device: {entity_id}")
                return True
            else:
                self.logger.warning(f"Device {entity_id} not found in {device_type} list")
                return False
                
        except Exception as e:
            self.logger.error(f"Error removing device {entity_id}: {e}")
            return False
    
    def update_configuration(self, config: Dict[str, Any]) -> None:
        """Update controller configuration"""
        try:
            self.lights = config.get('devices', {}).get('lights', self.lights)
            self.switches = config.get('devices', {}).get('switches', self.switches)
            self.voice_announcements = config.get('voice_announcements', self.voice_announcements)
            self.announcement_message = config.get('announcement_message', self.announcement_message)
            
            self.logger.info("Home Assistant controller configuration updated")
            
        except Exception as e:
            self.logger.error(f"Error updating configuration: {e}")
    
    def emergency_stop(self) -> bool:
        """Emergency stop - deactivate all devices immediately"""
        try:
            self.logger.warning("Emergency stop initiated - deactivating all devices")
            
            # Force deactivate all devices
            success = self.deactivate_devices()
            
            # Clear activation state
            self.activated_devices.clear()
            self.activation_time = None
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error during emergency stop: {e}")
            return False
