#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Weekly Report System - Data Collector Module
Collect data from MineContext Web API
"""

import logging
import os
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import requests
from dotenv import load_dotenv
from pathlib import Path

logger = logging.getLogger(__name__)


class MineContextDataCollector:
    """Collect data from MineContext Web API"""
    
    def __init__(self, api_url: Optional[str] = None, auth_token: Optional[str] = None):
        """
        Initialize data collector
        
        Args:
            api_url: MineContext API base URL. If None, reads from config.
            auth_token: API authentication token. If None, reads from config.
        """
        # Load config from Reply config or environment
        reply_env = Path(__file__).parent.parent / "config/.env"
        if reply_env.exists():
            load_dotenv(reply_env)
        
        self.api_url = api_url or os.getenv("MINECONTEXT_API_URL", "http://localhost:8765")
        self.auth_token = auth_token or os.getenv("MINECONTEXT_AUTH_TOKEN", "default_token")
        
        # Remove trailing slash
        self.api_url = self.api_url.rstrip('/')
        
        self.headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        logger.info(f"Initialized data collector with API: {self.api_url}")
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP GET request to MineContext API"""
        url = f"{self.api_url}{endpoint}"
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return {"data": {}}
    
    def get_daily_reports(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """
        Get daily reports from MineContext API
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            List of daily report dictionaries
        """
        try:
            # MineContext stores reports in vaults with document_type
            params = {
                "document_type": "daily_report",
                "limit": 100,
                "offset": 0
            }
            
            result = self._make_request("/api/debug/reports", params)
            
            all_reports = result.get("data", {}).get("reports", [])
            
            # Filter by date range
            reports = []
            for report in all_reports:
                created_at = report.get('created_at', '')
                if created_at:
                    try:
                        report_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        if start_date <= report_date <= end_date:
                            reports.append(report)
                    except:
                        pass
            
            logger.info(f"Retrieved {len(reports)} daily reports from API")
            return reports
            
        except Exception as e:
            logger.error(f"Error retrieving daily reports: {e}")
            return []
    
    def get_weekly_reports(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """
        Get weekly reports from MineContext API
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            List of weekly report dictionaries
        """
        try:
            params = {
                "document_type": "weekly_report",
                "limit": 100,
                "offset": 0
            }
            
            result = self._make_request("/api/debug/reports", params)
            
            all_reports = result.get("data", {}).get("reports", [])
            
            # Filter by date range
            reports = []
            for report in all_reports:
                created_at = report.get('created_at', '')
                if created_at:
                    try:
                        report_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        if start_date <= report_date <= end_date:
                            reports.append(report)
                    except:
                        pass
            
            logger.info(f"Retrieved {len(reports)} weekly reports from API")
            return reports
            
        except Exception as e:
            logger.error(f"Error retrieving weekly reports: {e}")
            return []
    
    def get_tips(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """
        Get tips from MineContext API
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            List of tip dictionaries
        """
        try:
            params = {
                "limit": 100,
                "offset": 0
            }
            
            result = self._make_request("/api/debug/tips", params)
            
            all_tips = result.get("data", {}).get("tips", [])
            
            # Filter by date range
            tips = []
            for tip in all_tips:
                created_at = tip.get('created_at', '')
                if created_at:
                    try:
                        tip_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        if start_date <= tip_date <= end_date:
                            tips.append(tip)
                    except:
                        pass
            
            logger.info(f"Retrieved {len(tips)} tips from API")
            return tips
            
        except Exception as e:
            logger.error(f"Error retrieving tips: {e}")
            return []
    
    def get_todos(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """
        Get todos from MineContext API
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            List of todo dictionaries
        """
        try:
            params = {
                "limit": 100,
                "offset": 0
            }
            
            result = self._make_request("/api/debug/todos", params)
            
            all_todos = result.get("data", {}).get("todos", [])
            
            # Filter by date range and add status_label
            todos = []
            for todo in all_todos:
                created_at = todo.get('created_at', '')
                if created_at:
                    try:
                        todo_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        if start_date <= todo_date <= end_date:
                            # Add status_label for compatibility
                            todo['status_label'] = 'completed' if todo.get('status') == 1 else 'pending'
                            todos.append(todo)
                    except:
                        pass
            
            # Sort by urgency and created_at
            todos.sort(key=lambda x: (-x.get('urgency', 0), x.get('created_at', '')))
            
            logger.info(f"Retrieved {len(todos)} todos from API")
            return todos
            
        except Exception as e:
            logger.error(f"Error retrieving todos: {e}")
            return []
    
    def get_activities(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """
        Get activities from MineContext API
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            List of activity dictionaries
        """
        try:
            params = {
                "start_time": start_date.isoformat(),
                "end_time": end_date.isoformat(),
                "limit": 100,
                "offset": 0
            }
            
            result = self._make_request("/api/debug/activities", params)
            
            activities = result.get("data", {}).get("activities", [])
            
            logger.info(f"Retrieved {len(activities)} activities from API")
            return activities
            
        except Exception as e:
            logger.error(f"Error retrieving activities: {e}")
            return []
    
    def get_email_documents(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """
        Get email documents from MailAPI SavedDocuments folder
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            List of email document dictionaries with course schedules
        """
        try:
            # Path to MailAPI SavedDocuments
            mailapi_docs = Path(__file__).parent.parent.parent / "MailAPI/SavedDocuments"
            
            if not mailapi_docs.exists():
                logger.warning(f"MailAPI SavedDocuments folder not found: {mailapi_docs}")
                return []
            
            email_docs = []
            
            # Keywords to identify course-related emails
            course_keywords = [
                'course', 'class', 'schedule', 'timetable', 'syllabus',
                'teaching plan', 'curriculum', 'lesson plan',
                '课程', '课表', '教学计划', '课程大纲', '教案'
            ]
            
            # Read all .md files in SavedDocuments
            for md_file in mailapi_docs.glob("*.md"):
                if md_file.name.startswith('summary_'):
                    continue  # Skip summary files
                
                try:
                    with open(md_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Extract date from filename (format: YYYYMMDD_HHMMSS_sender_subject.md)
                    match = re.match(r'(\d{8})_(\d{6})_', md_file.name)
                    if match:
                        date_str = match.group(1)
                        time_str = match.group(2)
                        doc_date = datetime.strptime(f"{date_str}{time_str}", "%Y%m%d%H%M%S")
                        
                        # Filter by date range
                        if not (start_date <= doc_date <= end_date):
                            continue
                    
                    # Check if it's course-related
                    content_lower = content.lower()
                    is_course_related = any(keyword.lower() in content_lower for keyword in course_keywords)
                    
                    if is_course_related:
                        # Extract sender and body
                        sender_match = re.search(r'^-\s*\*\*发件人\*\*:\s*(.+)$', content, re.MULTILINE)
                        body_match = re.search(r'## 正文内容\s*\n+(.+?)(?=##|---|$)', content, re.DOTALL)
                        attachments_match = re.search(r'## 附件列表(.+?)(?=---|$)', content, re.DOTALL)
                        
                        sender = sender_match.group(1).strip() if sender_match else 'Unknown'
                        body = body_match.group(1).strip() if body_match else ''
                        
                        # Use body content as subject/title
                        if body:
                            subject = body[:60] + '...' if len(body) > 60 else body
                        else:
                            subject = 'Course Schedule'
                        
                        # Extract attachment information
                        attachments = []
                        if attachments_match:
                            att_text = attachments_match.group(1)
                            # Find PDF, DOC, XLS attachments
                            att_files = re.findall(r'\[([^\]]+\.(pdf|docx?|xlsx?|pptx?))\]', att_text, re.IGNORECASE)
                            attachments = [att[0] for att in att_files]
                        
                        email_docs.append({
                            'file_path': str(md_file),
                            'subject': subject,
                            'sender': sender,
                            'body': body,
                            'attachments': attachments,
                            'date': doc_date.isoformat(),
                            'type': 'course_schedule'
                        })
                        
                        logger.info(f"Found course-related email: {subject}")
                
                except Exception as e:
                    logger.warning(f"Error reading email document {md_file}: {e}")
                    continue
            
            logger.info(f"Retrieved {len(email_docs)} course-related email documents")
            return email_docs
            
        except Exception as e:
            logger.error(f"Error retrieving email documents: {e}")
            return []
    
    def get_week_data(self, week_start_date: datetime) -> Dict[str, Any]:
        """
        Get all data for a specific week
        
        Args:
            week_start_date: Monday of the week
            
        Returns:
            Dictionary containing all collected data
        """
        week_end_date = week_start_date + timedelta(days=6, hours=23, minutes=59, seconds=59)
        
        logger.info(f"Collecting data for week: {week_start_date.date()} to {week_end_date.date()}")
        
        return {
            'daily_reports': self.get_daily_reports(week_start_date, week_end_date),
            'weekly_reports': self.get_weekly_reports(week_start_date, week_end_date),
            'tips': self.get_tips(week_start_date, week_end_date),
            'todos': self.get_todos(week_start_date, week_end_date),
            'activities': self.get_activities(week_start_date, week_end_date),
            'email_documents': self.get_email_documents(week_start_date, week_end_date),
            'week_start': week_start_date,
            'week_end': week_end_date
        }
