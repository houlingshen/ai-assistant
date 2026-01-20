#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Weekly Report System - Scheduler Module
Schedule weekly report generation and email sending
"""

import logging
import os
from datetime import datetime, timedelta
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv
from pathlib import Path

logger = logging.getLogger(__name__)


class WeeklyReportScheduler:
    """Schedule weekly report generation and email sending"""
    
    # Valid day of week values
    VALID_DAYS = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
    DAY_NAMES = {
        'mon': 'Monday',
        'tue': 'Tuesday',
        'wed': 'Wednesday',
        'thu': 'Thursday',
        'fri': 'Friday',
        'sat': 'Saturday',
        'sun': 'Sunday'
    }
    
    def __init__(self, report_generator, email_sender, config: dict = None):
        """
        Initialize scheduler
        
        Args:
            report_generator: Instance of WeeklyReportGenerator
            email_sender: Instance of EmailSender
            config: Scheduler configuration dictionary
        """
        self.scheduler = BlockingScheduler()
        self.report_generator = report_generator
        self.email_sender = email_sender
        
        # Load recipient email from MailAPI config
        mailapi_env = Path(__file__).parent.parent.parent / "MailAPI/config/.env"
        if mailapi_env.exists():
            load_dotenv(mailapi_env)
        
        self.recipient_email = os.getenv("EMAIL_ADDRESS")
        
        # Load and validate config
        if config:
            self.day_of_week = self._validate_day(config.get('day_of_week', 'sun'))
            self.hour = self._validate_hour(config.get('hour', 20))
            self.minute = self._validate_minute(config.get('minute', 0))
            self.enabled = config.get('enabled', True)
        else:
            self.day_of_week = 'sun'
            self.hour = 20
            self.minute = 0
            self.enabled = True
        
        day_full_name = self.DAY_NAMES.get(self.day_of_week, self.day_of_week.upper())
        logger.info(f"Scheduler initialized: Every {day_full_name} at {self.hour}:{self.minute:02d}")
    
    def _validate_day(self, day: str) -> str:
        """Validate day of week"""
        day_lower = day.lower().strip()
        if day_lower not in self.VALID_DAYS:
            logger.warning(f"Invalid day '{day}', using default 'sun'. Valid days: {', '.join(self.VALID_DAYS)}")
            return 'sun'
        return day_lower
    
    def _validate_hour(self, hour: int) -> int:
        """Validate hour (0-23)"""
        try:
            hour_int = int(hour)
            if 0 <= hour_int <= 23:
                return hour_int
            else:
                logger.warning(f"Hour {hour} out of range (0-23), using default 20")
                return 20
        except (ValueError, TypeError):
            logger.warning(f"Invalid hour '{hour}', using default 20")
            return 20
    
    def _validate_minute(self, minute: int) -> int:
        """Validate minute (0-59)"""
        try:
            minute_int = int(minute)
            if 0 <= minute_int <= 59:
                return minute_int
            else:
                logger.warning(f"Minute {minute} out of range (0-59), using default 0")
                return 0
        except (ValueError, TypeError):
            logger.warning(f"Invalid minute '{minute}', using default 0")
            return 0
    
    def generate_and_send_weekly_report(self):
        """Generate and send weekly report for next week"""
        try:
            logger.info("="*60)
            logger.info("Starting scheduled weekly report generation")
            logger.info("="*60)
            
            # Calculate next Monday
            today = datetime.now()
            days_until_monday = (7 - today.weekday()) % 7
            if days_until_monday == 0:
                days_until_monday = 7
            next_monday = today + timedelta(days=days_until_monday)
            next_monday = next_monday.replace(hour=0, minute=0, second=0, microsecond=0)
            
            logger.info(f"Generating report for week starting: {next_monday.date()}")
            
            # Generate report
            markdown_content = self.report_generator.generate_weekly_report(next_monday)
            report_filepath = self.report_generator.save_report(markdown_content, next_monday)
            
            logger.info(f"Report generated and saved to: {report_filepath}")
            
            # Send email
            if self.recipient_email:
                logger.info(f"Sending report email to: {self.recipient_email}")
                success = self.email_sender.send_weekly_report(
                    report_filepath,
                    self.recipient_email
                )
                
                if success:
                    logger.info("✅ Weekly report generated and sent successfully!")
                else:
                    logger.error("❌ Failed to send email")
            else:
                logger.warning("No recipient email configured, skipping email send")
            
            logger.info("="*60)
            
        except Exception as e:
            logger.error(f"Error in scheduled task: {e}", exc_info=True)
    
    def start(self):
        """Start the scheduler"""
        if not self.enabled:
            logger.warning("Scheduler is disabled in configuration")
            return
        
        # Schedule weekly report generation
        self.scheduler.add_job(
            self.generate_and_send_weekly_report,
            CronTrigger(
                day_of_week=self.day_of_week,
                hour=self.hour,
                minute=self.minute
            ),
            id='weekly_report_job',
            name='Generate and Send Weekly Report',
            replace_existing=True
        )
        
        day_full_name = self.DAY_NAMES.get(self.day_of_week, self.day_of_week.upper())
        time_12hr = self._format_time_12hr(self.hour, self.minute)
        
        logger.info("="*60)
        logger.info("📅 Weekly Report Scheduler Started")
        logger.info("="*60)
        logger.info(f"Schedule: Every {day_full_name} at {self.hour}:{self.minute:02d} ({time_12hr})")
        logger.info(f"Recipient: {self.recipient_email or 'Not configured'}")
        logger.info("Press Ctrl+C to stop")
        logger.info("="*60)
        
        print("\n" + "="*60)
        print("📅 Weekly Report Scheduler")
        print("="*60)
        print(f"⏰ Schedule: Every {day_full_name} at {self.hour}:{self.minute:02d} ({time_12hr})")
        print(f"📧 Recipient: {self.recipient_email or 'Not configured'}")
        print(f"\n💡 To change schedule, edit: Reply/config/config.yaml")
        print(f"   - day_of_week: {', '.join(self.VALID_DAYS)}")
        print(f"   - hour: 0-23 (24-hour format)")
        print(f"   - minute: 0-59")
        print("\n⌨️  Press Ctrl+C to stop")
        print("="*60 + "\n")
        
        try:
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("\nScheduler stopped by user")
            print("\n✋ Scheduler stopped by user")
            self.scheduler.shutdown()
    
    def _format_time_12hr(self, hour: int, minute: int) -> str:
        """Format time in 12-hour format"""
        period = "AM" if hour < 12 else "PM"
        hour_12 = hour if hour <= 12 else hour - 12
        hour_12 = 12 if hour_12 == 0 else hour_12
        return f"{hour_12}:{minute:02d} {period}"
    
    def run_once(self):
        """Run the job once immediately (for testing)"""
        logger.info("Running job once (test mode)")
        self.generate_and_send_weekly_report()
