"""
Utility functions for the MailAPI system.
"""

import os
import re
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional
import yaml
from dotenv import load_dotenv


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """
    Set up logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        Configured logger instance
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('mailapi.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger('MailAPI')


def load_config(config_path: str = "config/email_config.yaml") -> dict:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Configuration dictionary
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing configuration file: {e}")


def load_env_credentials():
    """
    Load email credentials from environment variables.
    
    Returns:
        tuple: (email_address, email_password, provider)
    """
    load_dotenv('config/.env')
    
    email_address = os.getenv('EMAIL_ADDRESS')
    email_password = os.getenv('EMAIL_PASSWORD')
    provider = os.getenv('EMAIL_PROVIDER', 'gmail')
    
    if not email_address or not email_password:
        raise ValueError(
            "Email credentials not found. Please create config/.env file "
            "with EMAIL_ADDRESS and EMAIL_PASSWORD"
        )
    
    return email_address, email_password, provider


def sanitize_filename(filename: str, max_length: int = 200) -> str:
    """
    Sanitize filename to remove invalid characters.
    
    Args:
        filename: Original filename
        max_length: Maximum length of the filename
        
    Returns:
        Sanitized filename
    """
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip('. ')
    
    # Limit length
    if len(filename) > max_length:
        name, ext = os.path.splitext(filename)
        filename = name[:max_length-len(ext)] + ext
    
    return filename or 'unnamed'


def ensure_directory(directory: str) -> Path:
    """
    Ensure directory exists, create if not.
    
    Args:
        directory: Directory path
        
    Returns:
        Path object
    """
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path


def format_email_address(email_tuple: tuple) -> dict:
    """
    Format email address tuple to dictionary.
    
    Args:
        email_tuple: (name, email) tuple from email parser
        
    Returns:
        Dictionary with 'name' and 'email' keys
    """
    if not email_tuple or len(email_tuple) < 2:
        return {"name": "", "email": ""}
    
    name = email_tuple[0] if email_tuple[0] else ""
    email = email_tuple[1] if email_tuple[1] else ""
    
    return {"name": name, "email": email}


def parse_date_string(date_str: str) -> Optional[datetime]:
    """
    Parse date string to datetime object.
    
    Args:
        date_str: Date string in various formats
        
    Returns:
        datetime object or None if parsing fails
    """
    from email.utils import parsedate_to_datetime
    
    try:
        return parsedate_to_datetime(date_str)
    except Exception as e:
        logging.warning(f"Failed to parse date: {date_str}, Error: {e}")
        return None


def get_file_size_readable(size_bytes: int) -> str:
    """
    Convert file size in bytes to human-readable format.
    
    Args:
        size_bytes: File size in bytes
        
    Returns:
        Readable file size string
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to specified length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix
