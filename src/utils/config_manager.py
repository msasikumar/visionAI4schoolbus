"""
Configuration Management System
Handles loading and accessing configuration from YAML files
"""

import yaml
import os
from pathlib import Path
from typing import Any, Dict, Optional


class ConfigManager:
    """Manages application configuration from YAML files"""
    
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.config_data = {}
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from YAML file"""
        try:
            if not self.config_path.exists():
                raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
            
            with open(self.config_path, 'r') as file:
                self.config_data = yaml.safe_load(file) or {}
                
        except Exception as e:
            print(f"Error loading configuration: {e}")
            # Load default configuration if file load fails
            self.config_data = self._get_default_config()
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation
        e.g., 'camera.resolution' -> config['camera']['resolution']
        """
        keys = key.split('.')
        value = self.config_data
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration if file loading fails"""
        return {
            'camera': {
                'device_id': 0,
                'resolution': {'width': 1280, 'height': 720},
                'fps': 30
            },
            'detection': {
                'model_path': 'models/yolov8n_hailo.hef',
                'min_confidence': 0.7,
                'cooldown_seconds': 30
            },
            'mqtt': {
                'broker_host': 'localhost',
                'broker_port': 1883,
                'topic_prefix': 'schoolbus'
            }
        }
