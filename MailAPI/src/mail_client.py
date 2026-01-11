"""
Email client for connecting to and interacting with email servers.
Supports IMAP protocol with automatic retry and error handling.
"""

import imaplib
import time
import logging
from typing import Optional, List
from src.utils import load_config, load_env_credentials


class MailClient:
    """
    Email client for IMAP server connection and management.
    """
    
    def __init__(self, config_path: str = "config/email_config.yaml"):
        """
        Initialize the mail client.
        
        Args:
            config_path: Path to the configuration file
        """
        self.logger = logging.getLogger(__name__)
        self.config = load_config(config_path)
        self.email_address, self.password, self.provider = load_env_credentials()
        
        self.connection: Optional[imaplib.IMAP4_SSL] = None
        self.is_connected = False
        
        # Load server settings
        self._load_server_settings()
    
    def _load_server_settings(self):
        """Load IMAP server settings based on provider."""
        provider_config = self.config['imap'].get(self.provider)
        
        if not provider_config:
            raise ValueError(f"Provider '{self.provider}' not found in configuration")
        
        self.server = provider_config['server']
        self.port = provider_config['port']
        self.use_ssl = provider_config.get('use_ssl', True)
        self.timeout = self.config.get('connection_timeout', 30)
        self.max_retries = self.config.get('max_retries', 3)
        
        self.logger.info(f"Loaded settings for provider: {self.provider}")
    
    def connect(self) -> bool:
        """
        Connect to the IMAP server with retry mechanism.
        
        Returns:
            True if connection successful, False otherwise
        """
        for attempt in range(self.max_retries):
            try:
                self.logger.info(f"Connecting to {self.server}:{self.port} (attempt {attempt + 1}/{self.max_retries})")
                
                # Create IMAP connection
                if self.use_ssl:
                    self.connection = imaplib.IMAP4_SSL(self.server, self.port, timeout=self.timeout)
                else:
                    self.connection = imaplib.IMAP4(self.server, self.port)
                
                # Login
                self.connection.login(self.email_address, self.password)
                
                self.is_connected = True
                self.logger.info("Successfully connected and authenticated")
                return True
                
            except imaplib.IMAP4.error as e:
                self.logger.error(f"IMAP error: {e}")
                if "authentication failed" in str(e).lower():
                    self.logger.error("Authentication failed. Please check your credentials.")
                    return False
                    
            except Exception as e:
                self.logger.error(f"Connection error: {e}")
                
            # Wait before retry
            if attempt < self.max_retries - 1:
                wait_time = (attempt + 1) * 2
                self.logger.info(f"Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
        
        self.logger.error("Failed to connect after all retry attempts")
        return False
    
    def disconnect(self):
        """Disconnect from the IMAP server."""
        if self.connection and self.is_connected:
            try:
                self.connection.close()
                self.connection.logout()
                self.is_connected = False
                self.logger.info("Disconnected from server")
            except Exception as e:
                self.logger.warning(f"Error during disconnect: {e}")
    
    def select_folder(self, folder: str = "INBOX") -> bool:
        """
        Select an email folder.
        
        Args:
            folder: Folder name (default: INBOX)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected:
            self.logger.error("Not connected to server")
            return False
        
        try:
            status, messages = self.connection.select(folder)
            if status == 'OK':
                message_count = int(messages[0])
                self.logger.info(f"Selected folder '{folder}' with {message_count} messages")
                return True
            else:
                self.logger.error(f"Failed to select folder '{folder}'")
                return False
        except Exception as e:
            self.logger.error(f"Error selecting folder: {e}")
            return False
    
    def search_emails(self, criteria: str) -> List[bytes]:
        """
        Search for emails based on IMAP search criteria.
        
        Args:
            criteria: IMAP search criteria (e.g., 'ALL', 'UNSEEN', 'FROM "sender@example.com"')
            
        Returns:
            List of email IDs
        """
        if not self.is_connected:
            self.logger.error("Not connected to server")
            return []
        
        try:
            status, messages = self.connection.search(None, criteria)
            if status == 'OK':
                email_ids = messages[0].split()
                self.logger.info(f"Found {len(email_ids)} emails matching criteria: {criteria}")
                return email_ids
            else:
                self.logger.error(f"Search failed for criteria: {criteria}")
                return []
        except Exception as e:
            self.logger.error(f"Error searching emails: {e}")
            return []
    
    def fetch_email(self, email_id: bytes, parts: str = "(RFC822)") -> Optional[bytes]:
        """
        Fetch email content by ID.
        
        Args:
            email_id: Email ID
            parts: Parts to fetch (default: RFC822 for full message)
            
        Returns:
            Email content as bytes or None if failed
        """
        if not self.is_connected:
            self.logger.error("Not connected to server")
            return None
        
        try:
            status, msg_data = self.connection.fetch(email_id, parts)
            if status == 'OK':
                return msg_data[0][1]
            else:
                self.logger.error(f"Failed to fetch email {email_id}")
                return None
        except Exception as e:
            self.logger.error(f"Error fetching email: {e}")
            return None
    
    def get_folder_list(self) -> List[str]:
        """
        Get list of available folders.
        
        Returns:
            List of folder names
        """
        if not self.is_connected:
            self.logger.error("Not connected to server")
            return []
        
        try:
            status, folders = self.connection.list()
            if status == 'OK':
                folder_list = []
                for folder in folders:
                    # Parse folder name from response
                    folder_str = folder.decode()
                    # Extract folder name (usually the last quoted part)
                    parts = folder_str.split('"')
                    if len(parts) >= 3:
                        folder_list.append(parts[-2])
                return folder_list
            else:
                self.logger.error("Failed to get folder list")
                return []
        except Exception as e:
            self.logger.error(f"Error getting folder list: {e}")
            return []
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
