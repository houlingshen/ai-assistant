"""
Schedule extractor for identifying and parsing schedule information from emails.
Uses regular expressions and NLP techniques to extract dates, times, and event details.
"""

import re
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dateutil import parser as date_parser
import pytz


class ScheduleExtractor:
    """
    Extractor for schedule and event information from email content.
    """
    
    def __init__(self, timezone: str = "Asia/Shanghai"):
        """
        Initialize schedule extractor.
        
        Args:
            timezone: Timezone for date/time interpretation
        """
        self.logger = logging.getLogger(__name__)
        self.timezone = pytz.timezone(timezone)
        
        # Chinese time patterns
        self.time_patterns = {
            'absolute_datetime': [
                r'(\d{4})年(\d{1,2})月(\d{1,2})日[^\d]*(\d{1,2})[：:点](\d{1,2})?分?',
                r'(\d{1,2})月(\d{1,2})日[^\d]*(\d{1,2})[：:点](\d{1,2})?分?',
                r'(\d{4})-(\d{1,2})-(\d{1,2})\s+(\d{1,2}):(\d{1,2})',
            ],
            'relative_time': [
                r'(今天|明天|后天|昨天|前天)',
                r'(下周|上周|本周)(一|二|三|四|五|六|日|天)',
                r'(这个|下个|上个)(周末|月初|月底)',
            ],
            'time_only': [
                r'(\d{1,2})[：:点](\d{1,2})?分?',
                r'(上午|下午|中午|晚上|早上)(\d{1,2})[：:点](\d{1,2})?分?',
            ],
            'time_range': [
                r'(\d{1,2})[：:点](\d{1,2})?分?[到至\-~](\d{1,2})[：:点](\d{1,2})?分?',
                r'(上午|下午)(\d{1,2})[：:点][到至](\d{1,2})[：:点]',
            ]
        }
        
        # Location patterns
        self.location_patterns = [
            r'(?:在|于)([^,，。\n]{2,20}?)(召开|举行|进行|开会)',
            r'(会议室|教室|办公室|大厅|礼堂)[A-Za-z0-9\-]*',
            r'地点[：:]\s*([^\n，。]{2,30})',
        ]
        
        # Event title patterns
        self.event_patterns = [
            r'(?:关于|召开|举行)([^，,。\n]{2,30}?)(?:的通知|会议|活动)',
            r'([^，,。\n]{2,30}?)(?:会议|讨论|培训|讲座|活动)',
        ]
    
    def extract_schedules(self, email_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract schedule information from email.
        
        Args:
            email_data: Parsed email data dictionary
            
        Returns:
            List of extracted schedule dictionaries
        """
        schedules = []
        
        # Get text content
        text_content = email_data.get('body', {}).get('text', '')
        subject = email_data.get('subject', '')
        
        # Combine subject and body for extraction
        full_text = f"{subject}\n{text_content}"
        
        # Extract datetime information
        datetime_matches = self._extract_datetimes(full_text)
        
        # Extract locations
        locations = self._extract_locations(full_text)
        
        # Extract event titles
        events = self._extract_event_titles(full_text, subject)
        
        # Extract participants
        participants = self._extract_participants(email_data)
        
        # Combine information into schedule objects
        if datetime_matches:
            for dt_match in datetime_matches:
                schedule = {
                    "title": events[0] if events else "邮件中的事件",
                    "start_time": dt_match.get('start_time'),
                    "end_time": dt_match.get('end_time'),
                    "location": locations[0] if locations else "",
                    "participants": participants,
                    "description": self._extract_description(full_text),
                    "all_day": dt_match.get('all_day', False)
                }
                schedules.append(schedule)
        
        self.logger.info(f"Extracted {len(schedules)} schedule(s) from email")
        return schedules
    
    def _extract_datetimes(self, text: str) -> List[Dict[str, Any]]:
        """Extract datetime information from text."""
        datetime_results = []
        
        # Try absolute datetime patterns
        for pattern in self.time_patterns['absolute_datetime']:
            matches = re.finditer(pattern, text)
            for match in matches:
                dt_info = self._parse_absolute_datetime(match)
                if dt_info:
                    datetime_results.append(dt_info)
        
        # Try relative time patterns
        for pattern in self.time_patterns['relative_time']:
            matches = re.finditer(pattern, text)
            for match in matches:
                dt_info = self._parse_relative_time(match, text)
                if dt_info:
                    datetime_results.append(dt_info)
        
        # Try time range patterns
        for pattern in self.time_patterns['time_range']:
            matches = re.finditer(pattern, text)
            for match in matches:
                dt_info = self._parse_time_range(match)
                if dt_info:
                    datetime_results.append(dt_info)
        
        return datetime_results
    
    def _parse_absolute_datetime(self, match) -> Optional[Dict[str, Any]]:
        """Parse absolute datetime from regex match."""
        try:
            groups = match.groups()
            
            # Handle different date formats
            if len(groups) >= 4:
                year = int(groups[0]) if len(groups[0]) == 4 else datetime.now().year
                month = int(groups[1]) if len(groups) > 1 else 1
                day = int(groups[2]) if len(groups) > 2 else 1
                hour = int(groups[3]) if len(groups) > 3 else 0
                minute = int(groups[4]) if len(groups) > 4 and groups[4] else 0
                
                dt = datetime(year, month, day, hour, minute)
                dt = self.timezone.localize(dt)
                
                return {
                    'start_time': dt.isoformat(),
                    'end_time': (dt + timedelta(hours=1)).isoformat(),
                    'all_day': False
                }
        except Exception as e:
            self.logger.warning(f"Error parsing absolute datetime: {e}")
        
        return None
    
    def _parse_relative_time(self, match, full_text: str) -> Optional[Dict[str, Any]]:
        """Parse relative time expressions like 'tomorrow', 'next week'."""
        try:
            time_expr = match.group(0)
            base_date = datetime.now()
            
            # Map relative time to actual date
            if '今天' in time_expr:
                target_date = base_date
            elif '明天' in time_expr:
                target_date = base_date + timedelta(days=1)
            elif '后天' in time_expr:
                target_date = base_date + timedelta(days=2)
            elif '昨天' in time_expr:
                target_date = base_date - timedelta(days=1)
            elif '下周' in time_expr:
                days_ahead = 7 + self._get_weekday_offset(time_expr)
                target_date = base_date + timedelta(days=days_ahead)
            else:
                return None
            
            # Try to find time in surrounding context
            context = full_text[max(0, match.start()-50):min(len(full_text), match.end()+50)]
            time_match = re.search(r'(\d{1,2})[：:点](\d{1,2})?分?', context)
            
            if time_match:
                hour = int(time_match.group(1))
                minute = int(time_match.group(2)) if time_match.group(2) else 0
                target_date = target_date.replace(hour=hour, minute=minute)
            else:
                target_date = target_date.replace(hour=9, minute=0)
            
            dt = self.timezone.localize(target_date)
            
            return {
                'start_time': dt.isoformat(),
                'end_time': (dt + timedelta(hours=1)).isoformat(),
                'all_day': False
            }
        except Exception as e:
            self.logger.warning(f"Error parsing relative time: {e}")
        
        return None
    
    def _get_weekday_offset(self, time_expr: str) -> int:
        """Get weekday offset from Chinese weekday expression."""
        weekday_map = {
            '一': 0, '二': 1, '三': 2, '四': 3,
            '五': 4, '六': 5, '日': 6, '天': 6
        }
        
        for char, offset in weekday_map.items():
            if char in time_expr:
                return offset
        return 0
    
    def _parse_time_range(self, match) -> Optional[Dict[str, Any]]:
        """Parse time range expressions."""
        try:
            groups = match.groups()
            
            # Parse start and end times
            start_hour = int(groups[0]) if groups else 9
            start_minute = int(groups[1]) if len(groups) > 1 and groups[1] else 0
            end_hour = int(groups[2]) if len(groups) > 2 else start_hour + 1
            end_minute = int(groups[3]) if len(groups) > 3 and groups[3] else 0
            
            # Use today's date
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            start_dt = today.replace(hour=start_hour, minute=start_minute)
            end_dt = today.replace(hour=end_hour, minute=end_minute)
            
            start_dt = self.timezone.localize(start_dt)
            end_dt = self.timezone.localize(end_dt)
            
            return {
                'start_time': start_dt.isoformat(),
                'end_time': end_dt.isoformat(),
                'all_day': False
            }
        except Exception as e:
            self.logger.warning(f"Error parsing time range: {e}")
        
        return None
    
    def _extract_locations(self, text: str) -> List[str]:
        """Extract location information from text."""
        locations = []
        
        for pattern in self.location_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                location = match.group(1) if match.lastindex >= 1 else match.group(0)
                locations.append(location.strip())
        
        return list(set(locations))[:3]  # Return up to 3 unique locations
    
    def _extract_event_titles(self, text: str, subject: str) -> List[str]:
        """Extract event titles from text."""
        events = []
        
        # First try subject line
        for pattern in self.event_patterns:
            match = re.search(pattern, subject)
            if match:
                events.append(match.group(1).strip())
        
        # Then try body text
        for pattern in self.event_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                event_title = match.group(1).strip()
                if event_title and event_title not in events:
                    events.append(event_title)
        
        return events[:5]  # Return up to 5 events
    
    def _extract_participants(self, email_data: Dict[str, Any]) -> List[str]:
        """Extract participant names from email."""
        participants = []
        
        # Add recipients
        to_recipients = email_data.get('to', [])
        for recipient in to_recipients:
            name = recipient.get('name', '') or recipient.get('email', '')
            if name:
                participants.append(name)
        
        # Add CC recipients
        cc_recipients = email_data.get('cc', [])
        for recipient in cc_recipients:
            name = recipient.get('name', '') or recipient.get('email', '')
            if name and name not in participants:
                participants.append(name)
        
        return participants
    
    def _extract_description(self, text: str, max_length: int = 200) -> str:
        """Extract event description from text."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Truncate if too long
        if len(text) > max_length:
            text = text[:max_length] + "..."
        
        return text
