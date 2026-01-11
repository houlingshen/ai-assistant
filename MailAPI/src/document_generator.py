"""
Document generator for creating structured documents from email data.
Supports both Markdown and JSON output formats.
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
from src.utils import sanitize_filename, ensure_directory


class DocumentGenerator:
    """
    Generator for creating structured documents from processed emails.
    """
    
    def __init__(self, output_dir: str = "SavedDocuments"):
        """
        Initialize document generator.
        
        Args:
            output_dir: Directory for saving generated documents
        """
        self.logger = logging.getLogger(__name__)
        self.output_dir = output_dir
        ensure_directory(output_dir)
    
    def generate_document(self,
                         email_data: Dict[str, Any],
                         schedules: List[Dict[str, Any]],
                         attachments: List[Dict[str, Any]],
                         format: str = "markdown") -> str:
        """
        Generate document from email data.
        
        Args:
            email_data: Parsed email data
            schedules: Extracted schedule information
            attachments: Attachment information
            format: Output format ('markdown' or 'json')
            
        Returns:
            Path to generated document
        """
        # Generate filename
        filename = self._generate_filename(email_data, format)
        filepath = Path(self.output_dir) / filename
        
        try:
            if format.lower() == "json":
                self._generate_json(filepath, email_data, schedules, attachments)
            else:
                self._generate_markdown(filepath, email_data, schedules, attachments)
            
            self.logger.info(f"Generated document: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Error generating document: {e}")
            raise
    
    def _generate_filename(self, email_data: Dict[str, Any], format: str) -> str:
        """Generate filename from email data."""
        # Parse date
        date_str = email_data.get('date', '')
        try:
            if date_str:
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                date_part = dt.strftime("%Y%m%d_%H%M%S")
            else:
                date_part = datetime.now().strftime("%Y%m%d_%H%M%S")
        except:
            date_part = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Get sender
        sender = email_data.get('from', {}).get('email', 'unknown')
        sender_part = sender.split('@')[0] if '@' in sender else sender
        
        # Get subject
        subject = email_data.get('subject', 'no_subject')
        subject_part = subject[:50]  # Limit length
        
        # Combine parts
        filename = f"{date_part}_{sender_part}_{subject_part}"
        filename = sanitize_filename(filename)
        
        # Add extension
        ext = '.json' if format.lower() == 'json' else '.md'
        return filename + ext
    
    def _generate_markdown(self,
                          filepath: Path,
                          email_data: Dict[str, Any],
                          schedules: List[Dict[str, Any]],
                          attachments: List[Dict[str, Any]]):
        """Generate Markdown format document."""
        with open(filepath, 'w', encoding='utf-8') as f:
            # Write header
            f.write("# 邮件信息\n\n")
            
            # Basic information
            f.write(f"- **主题**: {email_data.get('subject', 'N/A')}\n")
            f.write(f"- **发件人**: {self._format_contact(email_data.get('from', {}))}\n")
            f.write(f"- **收件人**: {self._format_contacts(email_data.get('to', []))}\n")
            
            cc = email_data.get('cc', [])
            if cc:
                f.write(f"- **抄送**: {self._format_contacts(cc)}\n")
            
            f.write(f"- **日期**: {email_data.get('date', 'N/A')}\n")
            f.write(f"- **邮件ID**: `{email_data.get('message_id', 'N/A')}`\n")
            f.write("\n")
            
            # Email body
            f.write("## 正文内容\n\n")
            body_text = email_data.get('body', {}).get('text', '')
            if body_text:
                f.write(body_text)
                f.write("\n\n")
            else:
                f.write("*无正文内容*\n\n")
            
            # Schedules
            if schedules:
                f.write("## 提取的日程安排\n\n")
                for i, schedule in enumerate(schedules, 1):
                    f.write(f"### 事件 {i}\n\n")
                    f.write(f"- **标题**: {schedule.get('title', 'N/A')}\n")
                    
                    start_time = schedule.get('start_time', 'N/A')
                    end_time = schedule.get('end_time', 'N/A')
                    if schedule.get('all_day'):
                        f.write(f"- **时间**: 全天\n")
                    else:
                        f.write(f"- **开始时间**: {start_time}\n")
                        f.write(f"- **结束时间**: {end_time}\n")
                    
                    location = schedule.get('location', '')
                    if location:
                        f.write(f"- **地点**: {location}\n")
                    
                    participants = schedule.get('participants', [])
                    if participants:
                        f.write(f"- **参与者**: {', '.join(participants[:5])}\n")
                    
                    description = schedule.get('description', '')
                    if description:
                        f.write(f"- **描述**: {description}\n")
                    
                    f.write("\n")
            
            # Attachments
            if attachments:
                f.write("## 附件列表\n\n")
                for i, att in enumerate(attachments, 1):
                    filename = att.get('filename', 'unknown')
                    filepath_rel = att.get('filepath', '')
                    size = att.get('size_readable', 'N/A')
                    file_type = att.get('type', 'N/A')
                    
                    f.write(f"{i}. [{filename}]({filepath_rel}) - {size} ({file_type})\n")
                
                f.write("\n")
            else:
                f.write("## 附件列表\n\n*无附件*\n\n")
            
            # Footer
            f.write("---\n")
            f.write(f"*文档生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
    
    def _generate_json(self,
                      filepath: Path,
                      email_data: Dict[str, Any],
                      schedules: List[Dict[str, Any]],
                      attachments: List[Dict[str, Any]]):
        """Generate JSON format document."""
        document = {
            "email_id": email_data.get('message_id', ''),
            "subject": email_data.get('subject', ''),
            "from": email_data.get('from', {}),
            "to": email_data.get('to', []),
            "cc": email_data.get('cc', []),
            "date": email_data.get('date', ''),
            "body": email_data.get('body', {}),
            "schedules": schedules,
            "attachments": attachments,
            "saved_at": datetime.now().isoformat()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(document, f, ensure_ascii=False, indent=2)
    
    def _format_contact(self, contact: Dict[str, str]) -> str:
        """Format a single contact."""
        name = contact.get('name', '')
        email = contact.get('email', '')
        
        if name and email:
            return f"{name} <{email}>"
        elif email:
            return email
        elif name:
            return name
        return "N/A"
    
    def _format_contacts(self, contacts: List[Dict[str, str]]) -> str:
        """Format multiple contacts."""
        if not contacts:
            return "N/A"
        
        formatted = [self._format_contact(c) for c in contacts]
        return ", ".join(formatted)
    
    def generate_summary_report(self, processed_emails: List[Dict[str, Any]]) -> str:
        """
        Generate a summary report of processed emails.
        
        Args:
            processed_emails: List of processed email data
            
        Returns:
            Path to summary report
        """
        summary_path = Path(self.output_dir) / f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        try:
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write("# 邮件处理摘要报告\n\n")
                f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"**处理邮件数**: {len(processed_emails)}\n\n")
                
                f.write("## 邮件列表\n\n")
                
                for i, email in enumerate(processed_emails, 1):
                    f.write(f"### {i}. {email.get('subject', 'N/A')}\n\n")
                    f.write(f"- **发件人**: {self._format_contact(email.get('from', {}))}\n")
                    f.write(f"- **日期**: {email.get('date', 'N/A')}\n")
                    
                    schedules = email.get('schedules', [])
                    if schedules:
                        f.write(f"- **日程事件**: {len(schedules)} 个\n")
                    
                    attachments = email.get('attachments', [])
                    if attachments:
                        f.write(f"- **附件**: {len(attachments)} 个\n")
                    
                    f.write(f"- **文档路径**: {email.get('document_path', 'N/A')}\n")
                    f.write("\n")
            
            self.logger.info(f"Generated summary report: {summary_path}")
            return str(summary_path)
            
        except Exception as e:
            self.logger.error(f"Error generating summary report: {e}")
            raise
