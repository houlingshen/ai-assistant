#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Utility Functions Module
Common utility functions for Connect system
"""

import os
import logging
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


def setup_logging(log_file: str, log_level: str = "INFO"):
    """
    Setup logging configuration
    
    Args:
        log_file: Path to log file
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    # Create logs directory if it doesn't exist
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert log level string to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Configure logging
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    logger.info(f"Logging configured: level={log_level}, file={log_file}")


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from YAML file
    
    Args:
        config_path: Path to config.yaml file
        
    Returns:
        dict: Configuration dictionary
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        logger.warning(f"Config file not found: {config_path}, using defaults")
        return get_default_config()
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        logger.info(f"Loaded configuration from: {config_path}")
        return config
        
    except Exception as e:
        logger.error(f"Error loading config file: {e}")
        return get_default_config()


def get_default_config() -> Dict[str, Any]:
    """
    Get default configuration
    
    Returns:
        dict: Default configuration
    """
    return {
        'sync': {
            'mail_documents_dir': '../MailAPI/SavedDocuments',
            'enable_watcher': True,
            'sync_interval': 300
        },
        'minecontext': {
            'api_url': 'http://localhost:8765',
            'auth_token': 'default_token',
            'document_type': 'email',
            'auto_tag': True,
            'tags': 'email,mail_api,imported'
        },
        'reply': {
            'reply_dir': '../Reply',
            'auto_trigger': True,
            'trigger_schedule': {
                'day_of_week': 'sun',
                'hour': 21,
                'minute': 0
            }
        },
        'data': {
            'processed_files': 'data/processed_files.json'
        },
        'logging': {
            'level': 'INFO',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'file': 'logs/connect.log'
        }
    }


def load_env_variables(env_file: Optional[str] = None):
    """
    Load environment variables from .env file
    
    Args:
        env_file: Path to .env file (optional)
    """
    if env_file and Path(env_file).exists():
        load_dotenv(env_file)
        logger.info(f"Loaded environment variables from: {env_file}")
    else:
        # Try to load from default location
        default_env = Path(__file__).parent.parent / "config/.env"
        if default_env.exists():
            load_dotenv(default_env)
            logger.info(f"Loaded environment variables from: {default_env}")
        else:
            logger.debug("No .env file found, using system environment variables")


def get_absolute_path(relative_path: str, base_dir: Optional[str] = None) -> Path:
    """
    Convert relative path to absolute path
    
    Args:
        relative_path: Relative path string
        base_dir: Base directory (default: Connect directory)
        
    Returns:
        Path: Absolute path
    """
    if base_dir is None:
        # Use Connect directory as base
        base_dir = Path(__file__).parent.parent
    else:
        base_dir = Path(base_dir)
    
    path = base_dir / relative_path
    return path.resolve()


def ensure_directory_exists(directory: str):
    """
    Ensure a directory exists, create if it doesn't
    
    Args:
        directory: Directory path
    """
    dir_path = Path(directory)
    if not dir_path.exists():
        dir_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {directory}")


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format
    
    Args:
        size_bytes: File size in bytes
        
    Returns:
        str: Formatted file size
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate string to maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to append if truncated
        
    Returns:
        str: Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def print_banner(title: str, width: int = 60):
    """
    Print a formatted banner
    
    Args:
        title: Banner title
        width: Banner width
    """
    print("=" * width)
    print(title.center(width))
    print("=" * width)
