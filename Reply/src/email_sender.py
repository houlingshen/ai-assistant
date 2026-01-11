#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Weekly Report System - Email Sender Module
Send weekly report via Gmail
"""

import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
import os
from dotenv import load_dotenv

try:
    import markdown2
    MARKDOWN2_AVAILABLE = True
except ImportError:
    MARKDOWN2_AVAILABLE = False
    logging.warning("markdown2 not installed, HTML conversion will be basic")

logger = logging.getLogger(__name__)


class EmailSender:
    """Send weekly report via Gmail"""
    
    def __init__(self, config: dict = None):
        """
        Initialize email sender
        
        Args:
            config: Email configuration dictionary
        """
        # Load email config from MailAPI/.env
        mailapi_env = Path(__file__).parent.parent.parent / "MailAPI/config/.env"
        if mailapi_env.exists():
            load_dotenv(mailapi_env)
            logger.info(f"Loaded email credentials from {mailapi_env}")
        else:
            logger.warning(f"MailAPI .env file not found at {mailapi_env}")
        
        self.sender_email = os.getenv("EMAIL_ADDRESS")
        self.sender_password = os.getenv("EMAIL_PASSWORD")
        
        # Use config if provided, otherwise use defaults
        if config:
            self.smtp_server = config.get('smtp_server', 'smtp.gmail.com')
            self.smtp_port = config.get('smtp_port', 587)
            self.use_html = config.get('use_html', True)
            self.attach_markdown = config.get('attach_markdown', True)
        else:
            self.smtp_server = "smtp.gmail.com"
            self.smtp_port = 587
            self.use_html = True
            self.attach_markdown = True
        
        if not self.sender_email or not self.sender_password:
            raise ValueError("Email credentials not found. Please check MailAPI/config/.env")
        
        logger.info(f"Initialized email sender: {self.sender_email}")
    
    def _markdown_to_html(self, markdown_content: str) -> str:
        """
        Convert Markdown to HTML
        
        Args:
            markdown_content: Markdown content
            
        Returns:
            str: HTML content
        """
        if MARKDOWN2_AVAILABLE:
            try:
                html = markdown2.markdown(
                    markdown_content,
                    extras=["tables", "fenced-code-blocks", "strike", "task_list"]
                )
                # Add CSS styling
                styled_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <style>
                        body {{
                            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
                            line-height: 1.6;
                            color: #333;
                            max-width: 900px;
                            margin: 0 auto;
                            padding: 20px;
                            background-color: #f5f5f5;
                        }}
                        h1 {{
                            color: #2c3e50;
                            border-bottom: 3px solid #3498db;
                            padding-bottom: 10px;
                        }}
                        h2 {{
                            color: #34495e;
                            border-bottom: 2px solid #95a5a6;
                            padding-bottom: 8px;
                            margin-top: 30px;
                        }}
                        h3 {{
                            color: #7f8c8d;
                            margin-top: 20px;
                        }}
                        ul, ol {{
                            line-height: 1.8;
                        }}
                        li {{
                            margin-bottom: 8px;
                        }}
                        code {{
                            background-color: #f4f4f4;
                            padding: 2px 6px;
                            border-radius: 3px;
                            font-family: 'Courier New', monospace;
                        }}
                        pre {{
                            background-color: #f4f4f4;
                            padding: 15px;
                            border-radius: 5px;
                            overflow-x: auto;
                        }}
                        hr {{
                            border: none;
                            border-top: 1px solid #ddd;
                            margin: 30px 0;
                        }}
                        table {{
                            border-collapse: collapse;
                            width: 100%;
                            margin: 20px 0;
                        }}
                        th, td {{
                            border: 1px solid #ddd;
                            padding: 12px;
                            text-align: left;
                        }}
                        th {{
                            background-color: #3498db;
                            color: white;
                        }}
                        tr:nth-child(even) {{
                            background-color: #f2f2f2;
                        }}
                        .content {{
                            background-color: white;
                            padding: 30px;
                            border-radius: 8px;
                            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        }}
                    </style>
                </head>
                <body>
                    <div class="content">
                        {html}
                    </div>
                </body>
                </html>
                """
                return styled_html
            except Exception as e:
                logger.error(f"Error converting Markdown to HTML: {e}")
        
        # Fallback: basic HTML with line breaks
        html = markdown_content.replace('\n', '<br>\n')
        return f"<html><body><pre>{html}</pre></body></html>"
    
    def send_weekly_report(
        self,
        report_filepath: Path,
        recipient_email: str = None,
        subject: str = None
    ) -> bool:
        """
        Send weekly report email
        
        Args:
            report_filepath: Path to the Markdown report file
            recipient_email: Recipient's email address (defaults to sender)
            subject: Email subject (auto-generated if None)
            
        Returns:
            bool: True if email sent successfully
        """
        try:
            # Default recipient is sender
            if not recipient_email:
                recipient_email = self.sender_email
            
            # Read Markdown content
            with open(report_filepath, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
            
            # Generate subject
            if not subject:
                # Extract date from filename: weekly_report_YYYYMMDD.md
                date_str = report_filepath.stem.split('_')[-1]
                try:
                    from datetime import datetime
                    date_obj = datetime.strptime(date_str, '%Y%m%d')
                    subject = f"📊 Weekly Report - Week of {date_obj.strftime('%B %d, %Y')}"
                except:
                    subject = "📊 Weekly Report"
            
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            msg['Subject'] = subject
            
            # Add plain text version
            text_part = MIMEText(markdown_content, 'plain', 'utf-8')
            msg.attach(text_part)
            
            # Add HTML version if enabled
            if self.use_html:
                html_content = self._markdown_to_html(markdown_content)
                html_part = MIMEText(html_content, 'html', 'utf-8')
                msg.attach(html_part)
            
            # Attach Markdown file if enabled
            if self.attach_markdown:
                with open(report_filepath, 'rb') as f:
                    attachment = MIMEBase('application', 'octet-stream')
                    attachment.set_payload(f.read())
                    encoders.encode_base64(attachment)
                    attachment.add_header(
                        'Content-Disposition',
                        f'attachment; filename="{report_filepath.name}"'
                    )
                    msg.attach(attachment)
            
            # Send email
            logger.info(f"Connecting to {self.smtp_server}:{self.smtp_port}")
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                logger.info("TLS connection established")
                
                server.login(self.sender_email, self.sender_password)
                logger.info("Login successful")
                
                server.send_message(msg)
                logger.info(f"Email sent successfully to {recipient_email}")
            
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed: {e}")
            logger.error("Please check EMAIL_ADDRESS and EMAIL_PASSWORD in MailAPI/config/.env")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending email: {e}", exc_info=True)
            return False
    
    def send_test_email(self, recipient_email: str = None) -> bool:
        """
        Send a test email
        
        Args:
            recipient_email: Recipient's email address (defaults to sender)
            
        Returns:
            bool: True if email sent successfully
        """
        try:
            if not recipient_email:
                recipient_email = self.sender_email
            
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            msg['Subject'] = "🧪 Weekly Report System - Test Email"
            
            body = """
            This is a test email from the Weekly Report System.
            
            If you receive this email, the email configuration is working correctly!
            
            ---
            Weekly Report System
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            logger.info(f"Test email sent successfully to {recipient_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending test email: {e}")
            return False
