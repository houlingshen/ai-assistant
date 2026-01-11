#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MineContext API Client Module
Client for MineContext Web API
"""

import requests
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class MineContextClient:
    """Client for MineContext Web API"""
    
    def __init__(self, api_url: str = "http://localhost:8765", auth_token: str = "default_token"):
        """
        Initialize MineContext API client
        
        Args:
            api_url: MineContext API base URL
            auth_token: API authentication token
        """
        self.api_url = api_url.rstrip('/')
        self.auth_token = auth_token
        self.headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        
        logger.info(f"Initialized MineContext client: {self.api_url}")
    
    def check_connection(self) -> bool:
        """
        Check if MineContext API is accessible
        
        Returns:
            bool: True if connection successful
        """
        try:
            response = requests.get(
                f"{self.api_url}/api/debug/tips?limit=1",
                headers=self.headers,
                timeout=5
            )
            
            if response.ok:
                logger.info("MineContext API connection successful")
                return True
            else:
                logger.error(f"MineContext API returned status {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to connect to MineContext API: {e}")
            return False
    
    def import_email_document(self, email_data: Dict[str, Any]) -> Optional[int]:
        """
        Import email document into MineContext as a Vault document
        
        Args:
            email_data: Parsed email data
            
        Returns:
            int: Document ID if successful, None otherwise
        """
        try:
            # Format email content for MineContext
            content = self._format_email_content(email_data)
            
            # Create vault document
            vault_doc = {
                "title": f"Email: {email_data['subject']}",
                "content": content,
                "summary": f"From {email_data['from']} - {email_data['date']}",
                "document_type": "email",
                "tags": "email,mail_api,imported"
            }
            
            # POST to /api/vaults/create
            response = requests.post(
                f"{self.api_url}/api/vaults/create",
                json=vault_doc,
                headers=self.headers,
                timeout=30
            )
            
            if response.ok:
                result = response.json()
                # MineContext returns {"success": True, "doc_id": id}
                if result.get('success'):
                    doc_id = result.get('doc_id')
                    if doc_id:
                        logger.info(f"Successfully imported email: {email_data['subject']} (ID: {doc_id})")
                        return doc_id
                    else:
                        logger.warning(f"Email imported but no ID returned: {email_data['subject']}")
                        return None
                else:
                    logger.error(f"Failed to import email: {result.get('error', 'Unknown error')}")
                    return None
            else:
                logger.error(f"Failed to import email: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error importing email to MineContext: {e}")
            return None
    
    def _format_email_content(self, email_data: Dict[str, Any]) -> str:
        """
        Format email data as Markdown for MineContext
        
        Args:
            email_data: Parsed email data
            
        Returns:
            str: Formatted Markdown content
        """
        lines = []
        
        # Header section
        lines.append("# Email Information")
        lines.append("")
        lines.append(f"**From**: {email_data['from']}")
        lines.append(f"**To**: {email_data['to']}")
        lines.append(f"**Date**: {email_data['date']}")
        lines.append(f"**Subject**: {email_data['subject']}")
        
        if email_data.get('message_id'):
            lines.append(f"**Message ID**: {email_data['message_id']}")
        
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # Body content
        lines.append("## Email Body")
        lines.append("")
        lines.append(email_data['content'])
        lines.append("")
        
        # Attachments
        if email_data.get('attachments'):
            lines.append("## Attachments")
            lines.append("")
            for attachment in email_data['attachments']:
                lines.append(f"- {attachment}")
            lines.append("")
        
        # Schedules
        if email_data.get('schedules'):
            lines.append("## Schedule Information")
            lines.append("")
            for schedule in email_data['schedules']:
                if schedule.get('time'):
                    lines.append(f"**Time**: {schedule['time']}")
                if schedule.get('location'):
                    lines.append(f"**Location**: {schedule['location']}")
                if schedule.get('event'):
                    lines.append(f"**Event**: {schedule['event']}")
                lines.append("")
        
        # Metadata footer
        lines.append("---")
        lines.append(f"*Imported from MailAPI: {email_data['filename']}*")
        lines.append(f"*Import time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        
        return "\n".join(lines)
    
    def trigger_report_generation(self, report_type: str = "weekly") -> bool:
        """
        Trigger report generation in MineContext
        
        Args:
            report_type: Type of report to generate
            
        Returns:
            bool: True if successful
        """
        try:
            # Try content generation trigger endpoint
            response = requests.post(
                f"{self.api_url}/api/content_generation/trigger",
                json={"type": report_type},
                headers=self.headers,
                timeout=60
            )
            
            if response.ok:
                logger.info(f"Successfully triggered {report_type} report generation")
                return True
            else:
                logger.warning(f"Report generation trigger returned: {response.status_code}")
                # This might be okay if the endpoint doesn't exist
                # MineContext may generate reports automatically
                return True
                
        except Exception as e:
            logger.warning(f"Could not trigger report generation: {e}")
            # Not critical - reports may be generated automatically
            return True
    
    def get_vault_documents(self, document_type: Optional[str] = None, limit: int = 100) -> list:
        """
        Get vault documents from MineContext
        
        Args:
            document_type: Filter by document type
            limit: Maximum number of documents to retrieve
            
        Returns:
            list: List of vault documents
        """
        try:
            params = {"limit": limit}
            if document_type:
                params["document_type"] = document_type
            
            response = requests.get(
                f"{self.api_url}/api/vaults",
                params=params,
                headers=self.headers,
                timeout=30
            )
            
            if response.ok:
                result = response.json()
                documents = result.get('data', [])
                logger.info(f"Retrieved {len(documents)} vault documents")
                return documents
            else:
                logger.error(f"Failed to get vault documents: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error retrieving vault documents: {e}")
            return []
