#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Email Document Reader Module
Read and parse email documents from MailAPI SavedDocuments
"""

import re
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class EmailDocumentReader:
    """Read and parse email documents from SavedDocuments"""
    
    def __init__(self, documents_dir: str):
        """
        Initialize email document reader
        
        Args:
            documents_dir: Path to SavedDocuments directory
        """
        self.documents_dir = Path(documents_dir).resolve()
        
        if not self.documents_dir.exists():
            logger.warning(f"Documents directory not found: {self.documents_dir}")
        else:
            logger.info(f"Initialized email reader for: {self.documents_dir}")
    
    def parse_email_document(self, filepath: Path) -> Optional[Dict[str, Any]]:
        """
        Parse email Markdown document
        
        Args:
            filepath: Path to email Markdown file
            
        Returns:
            dict: Parsed email data or None if parsing fails
                {
                    'subject': str,
                    'from': str,
                    'to': str,
                    'date': str (ISO format),
                    'message_id': str,
                    'content': str,
                    'attachments': List[str],
                    'schedules': List[Dict],
                    'filepath': str,
                    'filename': str
                }
        """
        try:
            if not filepath.exists():
                logger.error(f"File not found: {filepath}")
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract metadata
            metadata = self.extract_metadata(content)
            
            # Extract body content
            body = self.extract_body_content(content)
            
            # Extract attachments
            attachments = self.extract_attachments(content)
            
            # Extract schedules if available
            schedules = self.extract_schedules(content)
            
            email_data = {
                'subject': metadata.get('subject', 'No Subject'),
                'from': metadata.get('from', 'Unknown'),
                'to': metadata.get('to', 'Unknown'),
                'date': metadata.get('date', ''),
                'message_id': metadata.get('message_id', ''),
                'content': body,
                'attachments': attachments,
                'schedules': schedules,
                'filepath': str(filepath),
                'filename': filepath.name
            }
            
            logger.debug(f"Parsed email: {email_data['subject']}")
            return email_data
            
        except Exception as e:
            logger.error(f"Failed to parse email document {filepath}: {e}")
            return None
    
    def extract_metadata(self, content: str) -> Dict[str, str]:
        """
        Extract email metadata from Markdown
        
        Args:
            content: Markdown content
            
        Returns:
            dict: Extracted metadata
        """
        metadata = {}
        
        # Pattern: - **主题**: xxx or - **Subject**: xxx
        patterns = {
            'subject': r'-\s*\*\*(?:主题|Subject)\*\*:\s*(.+)',
            'from': r'-\s*\*\*(?:发件人|From)\*\*:\s*(.+)',
            'to': r'-\s*\*\*(?:收件人|To)\*\*:\s*(.+)',
            'date': r'-\s*\*\*(?:日期|Date)\*\*:\s*(.+)',
            'message_id': r'-\s*\*\*(?:邮件ID|Message ID)\*\*:\s*(.+)',
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, content)
            if match:
                metadata[key] = match.group(1).strip()
        
        return metadata
    
    def extract_body_content(self, content: str) -> str:
        """
        Extract email body from ## 正文内容 section
        
        Args:
            content: Markdown content
            
        Returns:
            str: Email body content
        """
        # Find content between ## 正文内容 and next ##
        pattern = r'##\s*正文内容\s*\n(.*?)(?=\n##|\Z)'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            return match.group(1).strip()
        
        # Fallback: try English version
        pattern = r'##\s*Body Content\s*\n(.*?)(?=\n##|\Z)'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            return match.group(1).strip()
        
        return ""
    
    def extract_attachments(self, content: str) -> List[str]:
        """
        Extract attachments from ## 附件列表 section
        
        Args:
            content: Markdown content
            
        Returns:
            List[str]: List of attachment filenames
        """
        attachments = []
        
        # Find attachments section
        pattern = r'##\s*附件列表\s*\n(.*?)(?=\n##|\Z)'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            section = match.group(1)
            
            # Check if no attachments
            if '无附件' in section or 'No attachments' in section:
                return []
            
            # Extract attachment filenames (usually in list format)
            lines = section.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('-') or line.startswith('*'):
                    # Remove list markers
                    attachment = re.sub(r'^[-*]\s*', '', line).strip()
                    if attachment:
                        attachments.append(attachment)
        
        return attachments
    
    def extract_schedules(self, content: str) -> List[Dict[str, Any]]:
        """
        Extract schedules from ## 日程安排 section if exists
        
        Args:
            content: Markdown content
            
        Returns:
            List[Dict]: List of schedule items
        """
        schedules = []
        
        # Find schedules section
        pattern = r'##\s*日程安排\s*\n(.*?)(?=\n##|\Z)'
        match = re.search(pattern, content, re.DOTALL)
        
        if not match:
            return []
        
        section = match.group(1)
        
        # Parse schedule items (assuming format like: - **时间**: xxx, **地点**: xxx)
        # This is a simplified parser, adjust based on actual format
        lines = section.split('\n')
        current_schedule = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_schedule:
                    schedules.append(current_schedule)
                    current_schedule = {}
                continue
            
            # Extract time, location, event, etc.
            time_match = re.search(r'(?:时间|Time)[:：]\s*(.+?)(?:,|$)', line)
            location_match = re.search(r'(?:地点|Location)[:：]\s*(.+?)(?:,|$)', line)
            event_match = re.search(r'(?:事件|Event)[:：]\s*(.+?)(?:,|$)', line)
            
            if time_match:
                current_schedule['time'] = time_match.group(1).strip()
            if location_match:
                current_schedule['location'] = location_match.group(1).strip()
            if event_match:
                current_schedule['event'] = event_match.group(1).strip()
        
        if current_schedule:
            schedules.append(current_schedule)
        
        return schedules
    
    def is_summary_file(self, filepath: Path) -> bool:
        """
        Check if file is a summary file (skip these)
        
        Args:
            filepath: Path to file
            
        Returns:
            bool: True if it's a summary file
        """
        return 'summary_' in filepath.name.lower()
    
    def get_unprocessed_documents(self, processed_files: set) -> List[Path]:
        """
        Get list of unprocessed email documents
        
        Args:
            processed_files: Set of already processed file paths
            
        Returns:
            List[Path]: List of unprocessed document paths
        """
        unprocessed = []
        
        if not self.documents_dir.exists():
            return unprocessed
        
        for filepath in self.documents_dir.glob('*.md'):
            # Skip summary files
            if self.is_summary_file(filepath):
                continue
            
            # Skip already processed files
            if str(filepath) in processed_files:
                continue
            
            unprocessed.append(filepath)
        
        return unprocessed
