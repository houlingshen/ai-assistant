#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Weekly Report System - Utility Functions
Common utility functions and helpers
"""

import logging
import yaml
from pathlib import Path
from typing import Dict, Any


def setup_logging(log_file: str = "logs/reply.log", log_level: str = "INFO"):
    """
    Setup logging configuration
    
    Args:
        log_file: Path to log file
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    # Create logs directory if it doesn't exist
    log_path = Path(log_file)
    log_path.parent.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized: {log_file} (level: {log_level})")


def load_config(config_path: str = "config/config.yaml") -> Dict[str, Any]:
    """
    Load configuration from YAML file
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        dict: Configuration dictionary
    """
    try:
        config_file = Path(__file__).parent.parent / config_path
        
        if not config_file.exists():
            logging.warning(f"Config file not found: {config_file}")
            return {}
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        logging.info(f"Configuration loaded from: {config_file}")
        return config if config else {}
        
    except Exception as e:
        logging.error(f"Error loading configuration: {e}")
        return {}


def format_date_range(start_date, end_date) -> str:
    """
    Format date range as string
    
    Args:
        start_date: Start datetime
        end_date: End datetime
        
    Returns:
        str: Formatted date range
    """
    return f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"


def get_next_monday():
    """
    Get the date of next Monday
    
    Returns:
        datetime: Next Monday at 00:00:00
    """
    from datetime import datetime, timedelta
    
    today = datetime.now()
    days_until_monday = (7 - today.weekday()) % 7
    if days_until_monday == 0:
        days_until_monday = 7
    
    next_monday = today + timedelta(days=days_until_monday)
    return next_monday.replace(hour=0, minute=0, second=0, microsecond=0)


def get_current_week_monday():
    """
    Get the Monday of current week
    
    Returns:
        datetime: Current week's Monday at 00:00:00
    """
    from datetime import datetime, timedelta
    
    today = datetime.now()
    days_since_monday = today.weekday()
    
    current_monday = today - timedelta(days=days_since_monday)
    return current_monday.replace(hour=0, minute=0, second=0, microsecond=0)


def validate_email(email: str) -> bool:
    """
    Validate email address format
    
    Args:
        email: Email address string
        
    Returns:
        bool: True if valid email format
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def ensure_directory(directory: str):
    """
    Ensure directory exists, create if not
    
    Args:
        directory: Directory path
    """
    Path(directory).mkdir(parents=True, exist_ok=True)
