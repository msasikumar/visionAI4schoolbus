"""
MQTT Client
Handles MQTT communication for Home Assistant integration and notifications
"""

import json
import time
import threading
from typing import Dict, Any, Optional, Callable
from ..utils.logger import get_logger

try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False


class MQTTClient:
    """MQTT client for Home Assistant integration and messaging"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_logger('mqtt')
        
        # MQTT Configuration
        self.broker_host = config.get('broker_host', 'localhost')
        self.broker_port = config.get('broker_port', 1883)
        self.username = config.get('username', '')
        self.password = config.get('password', '')
        self.client_id = config.get('client_id', 'visionai4schoolbus')
        self.topic_prefix = config.get('topic_prefix', 'schoolbus')
        self.qos = config.get('qos', 1)
        self.retain = config.get('retain', True)
        self.keepalive = config.get('keepalive', 60)
        
        # MQTT Client
        self.client = None
        self.connected = False
        self.reconnect_delay = 5  # seconds
        
        # Message callbacks
        self.message_callbacks = {}
        
        # Connection monitoring
        self.last_heartbeat = 0
        self.heartbeat_interval = 30  # seconds
        
        if not MQTT_AVAILABLE:
            self.logger.error("paho-mqtt library not available")
            
    def connect(self) -> bool:
        """Connect to MQTT broker"""
        if not MQTT_AVAILABLE:
            return False
            
        try:
            self.logger.info(f"Connecting to MQTT broker at {self.broker_host}:{self.broker_port}")
            
            # Create MQTT client
            self.client = mqtt.Client(client_id=self.client_id)
            
            # Set credentials if provided
            if self.username and self.password:
                self.client.username_pw_set(self.username, self.password)
            
            # Set callbacks
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_message = self._on_message
            self.client.on_publish = self._on_publish
            
            # Connect to broker
            result = self.client.connect(self.broker_host, self.broker_port, self.keepalive)
            
            if result == 0:
                # Start network loop in background thread
                self.client.loop_start()
                
                # Wait for connection to be established
                timeout = 10
                while not self.connected and timeout > 0:
                    time.sleep(0.1)
                    timeout -= 0.1
                
                if self.connected:
                    self.logger.info("Successfully connected to MQTT broker")
                    self._setup_discovery()
                    return True
                else:
                    self.logger.error("Failed to establish MQTT connection within timeout")
                    return False
            else:
                self.logger.error(f"Failed to connect to MQTT broker, result code: {result}")
                return False
                
        except Exception as e:
            self.logger.error(f"MQTT connection error: {e}")
            return False
    
    def disconnect(self) -> None:
        """Disconnect from MQTT broker"""
        if self.client:
            self.logger.info("Disconnecting from MQTT broker")
            self.client.loop_stop()
            self.client.disconnect()
            self.connected = False
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback for when client connects to broker"""
        if rc == 0:
            self.connected = True
            self.logger.info("MQTT client connected")
            
            # Subscribe to command topics
            command_topic = f"{self.topic_prefix}/command/+"
            client.subscribe(command_topic, self.qos)
            
        else:
            self.logger.error(f"MQTT connection failed with code {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback for when client disconnects from broker"""
        self.connected = False
        if rc != 0:
            self.logger.warning(f"MQTT client disconnected unexpectedly (code: {rc})")
        else:
            self.logger.info("MQTT client disconnected")
    
    def _on_message(self, client, userdata, msg):
        """Callback for when message is received"""
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            
            self.logger.debug(f"Received message on {topic}: {payload}")
            
            # Handle command messages
            if topic.startswith(f"{self.topic_prefix}/command/"):
                command = topic.split('/')[-1]
                self._handle_command(command, payload)
            
            # Call registered callbacks
            for topic_pattern, callback in self.message_callbacks.items():
                if topic.startswith(topic_pattern):
                    callback(topic, payload)
                    
        except Exception as e:
            self.logger.error(f"Error processing MQTT message: {e}")
    
    def _on_publish(self, client, userdata, mid):
        """Callback for when message is published"""
        self.logger.debug(f"Message published with ID: {mid}")
    
    def _handle_command(self, command: str, payload: str):
        """Handle incoming commands"""
        try:
            if command == "status":
                self._publish_status()
            elif command == "restart":
                self.logger.info("Restart command received")
                # This would trigger an application restart
            elif command == "test_detection":
                self._publish_test_detection()
            else:
                self.logger.warning(f"Unknown command received: {command}")
                
        except Exception as e:
            self.logger.error(f"Error handling command {command}: {e}")
    
    def publish(self, topic: str, payload: Any, qos: Optional[int] = None, retain: Optional[bool] = None) -> bool:
        """Publish message to MQTT topic"""
        if not self.connected or not self.client:
            return False
        
        try:
            # Use default QoS and retain if not specified
            if qos is None:
                qos = self.qos
            if retain is None:
                retain = self.retain
            
            # Convert payload to JSON if it's a dict
            if isinstance(payload, dict):
                payload = json.dumps(payload)
            elif not isinstance(payload, str):
                payload = str(payload)
            
            # Publish message
            result = self.client.publish(topic, payload, qos, retain)
            
            if result.rc == 0:
                self.logger.debug(f"Published to {topic}: {payload}")
                return True
            else:
                self.logger.error(f"Failed to publish to {topic}, rc: {result.rc}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error publishing to {topic}: {e}")
            return False
    
    def publish_detection(self, detection: Dict[str, Any]) -> bool:
        """Publish school bus detection event"""
        topic = f"{self.topic_prefix}/detection"
        
        detection_data = {
            'timestamp': time.time(),
            'detected': True,
            'confidence': detection.get('confidence', 0),
            'class_name': detection.get('class_name', 'unknown'),
            'bbox': detection.get('bbox', []),
            'message': 'School bus detected'
        }
        
        return self.publish(topic, detection_data)
    
    def publish_status(self, status: Dict[str, Any]) -> bool:
        """Publish system status"""
        topic = f"{self.topic_prefix}/status"
        
        status_data = {
            'timestamp': time.time(),
            'online': True,
            **status
        }
        
        return self.publish(topic, status_data)
    
    def _publish_status(self) -> None:
        """Publish current system status (internal)"""
        status = {
            'uptime': time.time(),  # This would be actual uptime
            'mqtt_connected': self.connected
        }
        self.publish_status(status)
    
    def _publish_test_detection(self) -> None:
        """Publish test detection for debugging"""
        test_detection = {
            'confidence': 0.95,
            'class_name': 'bus',
            'bbox': [100, 100, 200, 150],
        }
        self.publish_detection(test_detection)
    
    def publish_device_command(self, device_type: str, device_id: str, command: str, value: Any = None) -> bool:
        """Publish device command"""
        topic = f"{self.topic_prefix}/device/{device_type}/{device_id}/set"
        
        command_data = {
            'command': command,
            'timestamp': time.time()
        }
        
        if value is not None:
            command_data['value'] = value
        
        return self.publish(topic, command_data)
    
    def publish_announcement(self, message: str, priority: str = 'normal') -> bool:
        """Publish voice announcement request"""
        topic = f"{self.topic_prefix}/announcement"
        
        announcement_data = {
            'message': message,
            'priority': priority,
            'timestamp': time.time()
        }
        
        return self.publish(topic, announcement_data)
    
    def subscribe_to_topic(self, topic: str, callback: Callable[[str, str], None]) -> bool:
        """Subscribe to a topic with callback"""
        if not self.connected or not self.client:
            return False
        
        try:
            result = self.client.subscribe(topic, self.qos)
            if result[0] == 0:
                self.message_callbacks[topic] = callback
                self.logger.info(f"Subscribed to topic: {topic}")
                return True
            else:
                self.logger.error(f"Failed to subscribe to {topic}, rc: {result[0]}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error subscribing to {topic}: {e}")
            return False
    
    def _setup_discovery(self) -> None:
        """Setup Home Assistant MQTT discovery"""
        try:
            # Device information
            device_info = {
                "identifiers": ["visionai4schoolbus"],
                "name": "School Bus Detector",
                "model": "VisionAI4SchoolBus",
                "manufacturer": "Custom",
                "sw_version": "1.0.0"
            }
            
            # Binary sensor for bus detection
            sensor_config = {
                "name": "School Bus Detected",
                "unique_id": "schoolbus_detector_detected",
                "state_topic": f"{self.topic_prefix}/detection",
                "value_template": "{{ value_json.detected }}",
                "payload_on": True,
                "payload_off": False,
                "device_class": "motion",
                "device": device_info
            }
            
            discovery_topic = f"homeassistant/binary_sensor/schoolbus_detector/detected/config"
            self.publish(discovery_topic, sensor_config, retain=True)
            
            # Sensor for confidence level
            confidence_config = {
                "name": "School Bus Detection Confidence",
                "unique_id": "schoolbus_detector_confidence",
                "state_topic": f"{self.topic_prefix}/detection",
                "value_template": "{{ value_json.confidence | round(2) }}",
                "unit_of_measurement": "%",
                "device": device_info
            }
            
            discovery_topic = f"homeassistant/sensor/schoolbus_detector/confidence/config"
            self.publish(discovery_topic, confidence_config, retain=True)
            
            self.logger.info("Home Assistant MQTT discovery configured")
            
        except Exception as e:
            self.logger.error(f"Error setting up MQTT discovery: {e}")
    
    def is_connected(self) -> bool:
        """Check if client is connected to broker"""
        return self.connected and self.client is not None
    
    def get_status(self) -> Dict[str, Any]:
        """Get MQTT client status"""
        return {
            'connected': self.connected,
            'broker_host': self.broker_host,
            'broker_port': self.broker_port,
            'client_id': self.client_id,
            'topic_prefix': self.topic_prefix
        }
