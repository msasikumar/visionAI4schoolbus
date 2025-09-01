"""
Logging System
Centralized logging configuration for the application
"""

import logging
import logging.handlers
import os
from pathlib import Path
from typing import Dict, Any


def setup_logging(config: Dict[str, Any]) -> logging.Logger:
    """Setup logging configuration"""
    
    # Get configuration values with defaults
    log_level = config.get('level', 'INFO').upper()
    log_file = config.get('file_path', 'logs/visionai4schoolbus.log')
    max_file_size = config.get('max_file_size', 10485760)  # 10MB
    backup_count = config.get('backup_count', 5)
    log_format = config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_output = config.get('console_output', True)
    
    # Create logs directory if it doesn't exist
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger('visionai4schoolbus')
    logger.setLevel(getattr(logging, log_level, logging.INFO))
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter(log_format)
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_file_size,
        backupCount=backup_count
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a child logger"""
    return logging.getLogger(f'visionai4schoolbus.{name}')
