"""
Email parser for extracting and processing email content.
Handles email headers, body content, and attachments.
"""

import email
from email import policy
from email.parser import BytesParser
from email.header import decode_header
from email.utils import parseaddr
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from src.utils import format_email_address, parse_date_string
import html2text


class MailParser:
    """
    Parser for email messages with filtering and extraction capabilities.
    """
    
    def __init__(self):
        """Initialize the mail parser."""
        self.logger = logging.getLogger(__name__)
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = False
    
    def parse_email(self, raw_email: bytes) -> Optional[Dict[str, Any]]:
        """
        Parse raw email content into structured dictionary.
        
        Args:
            raw_email: Raw email bytes
            
        Returns:
            Dictionary with email information or None if parsing fails
        """
        try:
            # Parse email
            msg = BytesParser(policy=policy.default).parsebytes(raw_email)
            
            # Extract basic information
            email_data = {
                "message_id": self._get_header(msg, 'Message-ID'),
                "subject": self._decode_header(msg.get('Subject', '')),
                "from": self._parse_email_address(msg.get('From', '')),
                "to": self._parse_email_addresses(msg.get('To', '')),
                "cc": self._parse_email_addresses(msg.get('Cc', '')),
                "date": self._parse_date(msg.get('Date', '')),
                "body": self._extract_body(msg),
                "has_attachments": self._has_attachments(msg),
                "attachments_info": []
            }
            
            return email_data
            
        except Exception as e:
            self.logger.error(f"Error parsing email: {e}")
            return None
    
    def _decode_header(self, header: str) -> str:
        """
        Decode email header that may be encoded.
        
        Args:
            header: Header string
            
        Returns:
            Decoded header string
        """
        if not header:
            return ""
        
        try:
            decoded_parts = decode_header(header)
            decoded_str = ""
            
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    decoded_str += part.decode(encoding or 'utf-8', errors='replace')
                else:
                    decoded_str += part
            
            return decoded_str
        except Exception as e:
            self.logger.warning(f"Error decoding header: {e}")
            return str(header)
    
    def _get_header(self, msg, header_name: str) -> str:
        """Get and decode email header."""
        header_value = msg.get(header_name, '')
        if header_value:
            return self._decode_header(header_value)
        return ''
    
    def _parse_email_address(self, address_str: str) -> Dict[str, str]:
        """
        Parse email address string.
        
        Args:
            address_str: Email address string
            
        Returns:
            Dictionary with name and email
        """
        if not address_str:
            return {"name": "", "email": ""}
        
        try:
            name, email_addr = parseaddr(address_str)
            name = self._decode_header(name)
            return {"name": name, "email": email_addr}
        except Exception as e:
            self.logger.warning(f"Error parsing email address: {e}")
            return {"name": "", "email": address_str}
    
    def _parse_email_addresses(self, addresses_str: str) -> List[Dict[str, str]]:
        """Parse multiple email addresses."""
        if not addresses_str:
            return []
        
        addresses = []
        for addr in addresses_str.split(','):
            addr = addr.strip()
            if addr:
                addresses.append(self._parse_email_address(addr))
        
        return addresses
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """
        Parse email date.
        
        Args:
            date_str: Date string from email
            
        Returns:
            ISO format date string or None
        """
        dt = parse_date_string(date_str)
        return dt.isoformat() if dt else None
    
    def _extract_body(self, msg) -> Dict[str, str]:
        """
        Extract email body content.
        
        Args:
            msg: Email message object
            
        Returns:
            Dictionary with text and html versions of body
        """
        body = {
            "text": "",
            "html": ""
        }
        
        try:
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition", ""))
                    
                    # Skip attachments
                    if "attachment" in content_disposition:
                        continue
                    
                    if content_type == "text/plain":
                        body["text"] = part.get_content()
                    elif content_type == "text/html":
                        html_content = part.get_content()
                        body["html"] = html_content
                        # Convert HTML to text if no plain text available
                        if not body["text"]:
                            body["text"] = self.html_converter.handle(html_content)
            else:
                content_type = msg.get_content_type()
                if content_type == "text/plain":
                    body["text"] = msg.get_content()
                elif content_type == "text/html":
                    html_content = msg.get_content()
                    body["html"] = html_content
                    body["text"] = self.html_converter.handle(html_content)
        
        except Exception as e:
            self.logger.error(f"Error extracting body: {e}")
        
        return body
    
    def _has_attachments(self, msg) -> bool:
        """Check if email has attachments."""
        if msg.is_multipart():
            for part in msg.walk():
                content_disposition = str(part.get("Content-Disposition", ""))
                if "attachment" in content_disposition:
                    return True
        return False
    
    def get_message_object(self, raw_email: bytes):
        """
        Get email message object for further processing.
        
        Args:
            raw_email: Raw email bytes
            
        Returns:
            Email message object
        """
        return BytesParser(policy=policy.default).parsebytes(raw_email)
    
    @staticmethod
    def build_search_criteria(
        from_addr: Optional[str] = None,
        subject: Optional[str] = None,
        since_date: Optional[datetime] = None,
        before_date: Optional[datetime] = None,
        days_back: Optional[int] = None
    ) -> str:
        """
        Build IMAP search criteria string.
        
        Args:
            from_addr: Filter by sender email
            subject: Filter by subject keyword
            since_date: Filter emails since this date
            before_date: Filter emails before this date
            days_back: Filter emails from last N days
            
        Returns:
            IMAP search criteria string
        """
        criteria_parts = []
        
        if from_addr:
            criteria_parts.append(f'FROM "{from_addr}"')
        
        if subject:
            criteria_parts.append(f'SUBJECT "{subject}"')
        
        if days_back:
            since_date = datetime.now() - timedelta(days=days_back)
        
        if since_date:
            date_str = since_date.strftime("%d-%b-%Y")
            criteria_parts.append(f'SINCE {date_str}')
        
        if before_date:
            date_str = before_date.strftime("%d-%b-%Y")
            criteria_parts.append(f'BEFORE {date_str}')
        
        if not criteria_parts:
            return 'ALL'
        
        return ' '.join(criteria_parts)
    
    def filter_by_keywords(self, email_data: Dict[str, Any], keywords: List[str]) -> bool:
        """
        Check if email contains any of the keywords in subject or body.
        
        Args:
            email_data: Parsed email data
            subject_keywords: List of keywords to search for
            
        Returns:
            True if any keyword found, False otherwise
        """
        if not keywords:
            return True
        
        search_text = (
            email_data.get('subject', '').lower() + ' ' +
            email_data.get('body', {}).get('text', '').lower()
        )
        
        return any(keyword.lower() in search_text for keyword in keywords)
