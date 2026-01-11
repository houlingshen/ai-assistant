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
        
        # Load config
        if config:
            self.day_of_week = config.get('day_of_week', 'sun')
            self.hour = config.get('hour', 20)
            self.minute = config.get('minute', 0)
            self.enabled = config.get('enabled', True)
        else:
            self.day_of_week = 'sun'
            self.hour = 20
            self.minute = 0
            self.enabled = True
        
        logger.info(f"Scheduler initialized: {self.day_of_week} at {self.hour}:{self.minute:02d}")
    
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
        
        logger.info("="*60)
        logger.info("Weekly Report Scheduler Started")
        logger.info("="*60)
        logger.info(f"Next run: Every {self.day_of_week.upper()} at {self.hour}:{self.minute:02d}")
        logger.info("Press Ctrl+C to stop")
        logger.info("="*60)
        
        try:
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("\nScheduler stopped by user")
            self.scheduler.shutdown()
    
    def run_once(self):
        """Run the job once immediately (for testing)"""
        logger.info("Running job once (test mode)")
        self.generate_and_send_weekly_report()
