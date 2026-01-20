#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Weekly Report System - Main Entry Point
Generate and send weekly reports based on MineContext data
"""

import logging
import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.data_collector import MineContextDataCollector
from src.report_generator import WeeklyReportGenerator
from src.email_sender import EmailSender
from src.scheduler import WeeklyReportScheduler
from src.ebbinghaus_reminder import EbbinghausReviewReminder
from src.utils import setup_logging, load_config, get_next_monday, get_current_week_monday


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Weekly Report System - Generate and send weekly reports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run once immediately (test mode)
  python3 main.py --mode once
  
  # Run as daemon with scheduler (default)
  python3 main.py --mode daemon
  
  # Generate report for current week
  python3 main.py --mode once --week current
  
  # Generate report for next week
  python3 main.py --mode once --week next
  
  # Test email configuration
  python3 main.py --test-email
  
  # Use custom config file
  python3 main.py --config custom_config.yaml
  
  # Use custom MineContext API
  python3 main.py --api-url http://localhost:8080 --auth-token your_token
  
  # Override schedule settings
  python3 main.py --mode daemon --day fri --hour 18 --minute 30
  
  # Check current schedule
  python3 main.py --show-schedule
  
  # Generate report in English
  python3 main.py --mode once --language en
  
  # Generate report in Chinese (default)
  python3 main.py --mode once --language zh
        """
    )
    
    parser.add_argument(
        '--mode',
        choices=['daemon', 'once'],
        default='daemon',
        help='Run mode: daemon (scheduled) or once (generate immediately)'
    )
    
    parser.add_argument(
        '--week',
        choices=['current', 'next'],
        default='next',
        help='Which week to generate report for (only used with --mode once)'
    )
    
    parser.add_argument(
        '--config',
        default='config/config.yaml',
        help='Path to configuration file'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level'
    )
    
    parser.add_argument(
        '--test-email',
        action='store_true',
        help='Send a test email and exit'
    )
    
    parser.add_argument(
        '--api-url',
        help='MineContext API URL (e.g., http://localhost:8765)'
    )
    
    parser.add_argument(
        '--auth-token',
        help='MineContext API authentication token'
    )
    
    # Schedule override options
    parser.add_argument(
        '--day',
        choices=['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'],
        help='Override day of week for scheduled reports'
    )
    
    parser.add_argument(
        '--hour',
        type=int,
        help='Override hour (0-23) for scheduled reports'
    )
    
    parser.add_argument(
        '--minute',
        type=int,
        help='Override minute (0-59) for scheduled reports'
    )
    
    parser.add_argument(
        '--show-schedule',
        action='store_true',
        help='Show current schedule configuration and exit'
    )
    
    # Language option
    parser.add_argument(
        '--language',
        '--lang',
        choices=['zh', 'en'],
        help='Report language: zh (Chinese) or en (English)'
    )
    
    return parser.parse_args()


def main():
    """Main entry point for Weekly Report System"""
    args = parse_arguments()
    
    # Load configuration
    config = load_config(args.config)
    
    # Show schedule mode
    if args.show_schedule:
        scheduler_config = config.get('scheduler', {}).get('weekly_report', {})
        day = args.day or scheduler_config.get('day_of_week', 'sun')
        hour = args.hour if args.hour is not None else scheduler_config.get('hour', 20)
        minute = args.minute if args.minute is not None else scheduler_config.get('minute', 0)
        enabled = config.get('scheduler', {}).get('enabled', True)
        
        day_names = {
            'mon': 'Monday', 'tue': 'Tuesday', 'wed': 'Wednesday',
            'thu': 'Thursday', 'fri': 'Friday', 'sat': 'Saturday', 'sun': 'Sunday'
        }
        day_full = day_names.get(day, day.upper())
        period = "AM" if hour < 12 else "PM"
        hour_12 = hour if hour <= 12 else hour - 12
        hour_12 = 12 if hour_12 == 0 else hour_12
        
        print("\n" + "="*60)
        print("📅 Weekly Report Schedule Configuration")
        print("="*60)
        print(f"\n📌 Config File: {args.config}")
        print(f"⏰ Schedule: Every {day_full} at {hour}:{minute:02d} ({hour_12}:{minute:02d} {period})")
        print(f"✅ Enabled: {'Yes' if enabled else 'No'}")
        print(f"\n💡 Valid days: {', '.join(['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'])}")
        print("💡 Valid hours: 0-23 (24-hour format)")
        print("💡 Valid minutes: 0-59")
        print(f"\n⚙️  To change: Edit {args.config} or use command-line options")
        print("   Example: python3 main.py --day fri --hour 18 --minute 30")
        print("="*60 + "\n")
        return
    
    # Setup logging
    log_config = config.get('logging', {})
    log_file = log_config.get('file', 'logs/reply.log')
    log_level = args.log_level or log_config.get('level', 'INFO')
    setup_logging(log_file, log_level)
    
    logger = logging.getLogger(__name__)
    
    logger.info("="*60)
    logger.info("        Weekly Report System")
    logger.info("        智能周报生成与发送系统")
    logger.info("="*60)
    logger.info(f"Mode: {args.mode}")
    logger.info(f"Config: {args.config}")
    logger.info(f"Log Level: {log_level}")
    logger.info("="*60)
    
    try:
        # Initialize components
        logger.info("Initializing components...")
        
        # Data collector with API configuration
        api_url = args.api_url or config.get('data_collection', {}).get('minecontext_api_url')
        auth_token = args.auth_token or config.get('data_collection', {}).get('minecontext_auth_token')
        
        data_collector = MineContextDataCollector(api_url=api_url, auth_token=auth_token)
        
        # Ebbinghaus Review Reminder (optional)
        enable_review_reminder = config.get('review_reminder', {}).get('enabled', True)
        ebbinghaus_reminder = None
        
        if enable_review_reminder:
            try:
                storage_path = config.get('review_reminder', {}).get('storage_path', 'data/review_schedule.json')
                ebbinghaus_reminder = EbbinghausReviewReminder(data_collector, storage_path)
                logger.info("✓ Ebbinghaus review reminder enabled")
            except Exception as e:
                logger.warning(f"Failed to initialize review reminder: {e}")
        
        # Report generator
        output_dir = config.get('report_generation', {}).get('output_dir', 'ReplyDocuments')
        language = args.language or config.get('language', {}).get('default', 'zh')
        logger.info(f"Report language: {language}")
        report_generator = WeeklyReportGenerator(data_collector, output_dir, ebbinghaus_reminder, language)
        
        # Email sender
        email_config = config.get('email', {})
        email_sender = EmailSender(email_config)
        
        # Test email mode
        if args.test_email:
            logger.info("\n🧪 Testing email configuration...")
            success = email_sender.send_test_email()
            if success:
                logger.info("✅ Test email sent successfully!")
                print("\n✅ Test email sent successfully! Check your inbox.")
            else:
                logger.error("❌ Failed to send test email")
                print("\n❌ Failed to send test email. Check logs for details.")
            return
        
        # Run mode
        if args.mode == 'once':
            # Generate and send report immediately
            logger.info(f"\nRunning in 'once' mode - generating {args.week} week report")
            
            # Determine which week
            if args.week == 'current':
                target_monday = get_current_week_monday()
                logger.info("Generating report for CURRENT week")
            else:
                target_monday = get_next_monday()
                logger.info("Generating report for NEXT week")
            
            logger.info(f"Target week: {target_monday.date()}")
            
            # Generate report
            markdown_content = report_generator.generate_weekly_report(target_monday)
            report_filepath = report_generator.save_report(markdown_content, target_monday)
            
            logger.info(f"\n📄 Report saved to: {report_filepath}")
            print(f"\n📄 Report saved to: {report_filepath}")
            
            # Send email
            import os
            recipient = os.getenv("EMAIL_ADDRESS")
            if recipient:
                logger.info(f"\n📧 Sending report to: {recipient}")
                print(f"\n📧 Sending report to: {recipient}")
                
                success = email_sender.send_weekly_report(report_filepath, recipient)
                
                if success:
                    logger.info("✅ Report sent successfully!")
                    print("\n✅ Report generated and sent successfully!")
                else:
                    logger.error("❌ Failed to send email")
                    print("\n❌ Failed to send email. Check logs for details.")
            else:
                logger.warning("No recipient email found, skipping email send")
                print("\n⚠️  No recipient email configured, report saved only")
        
        else:
            # Run as daemon with scheduler
            logger.info("\nRunning in 'daemon' mode - starting scheduler")
            print("\n🕒 Starting scheduler...")
            print("The system will generate and send reports automatically.")
            print("Press Ctrl+C to stop.\n")
            
            scheduler_config = config.get('scheduler', {}).get('weekly_report', {})
            
            # Override with command-line arguments if provided
            if args.day:
                scheduler_config['day_of_week'] = args.day
                logger.info(f"Override: day_of_week = {args.day}")
            if args.hour is not None:
                scheduler_config['hour'] = args.hour
                logger.info(f"Override: hour = {args.hour}")
            if args.minute is not None:
                scheduler_config['minute'] = args.minute
                logger.info(f"Override: minute = {args.minute}")
            
            scheduler = WeeklyReportScheduler(
                report_generator,
                email_sender,
                scheduler_config
            )
            scheduler.start()
    
    except KeyboardInterrupt:
        logger.info("\n\n⚠️  Program interrupted by user")
        print("\n\n⚠️  Program stopped by user")
        sys.exit(0)
    
    except FileNotFoundError as e:
        logger.error(f"\n❌ File not found: {e}")
        print(f"\n❌ Error: {e}")
        print("\nPlease ensure MineContext web server is running.")
        print("Default API URL: http://localhost:8765")
        print("You can start MineContext server with: python3 -m opencontext.server.opencontext")
        sys.exit(1)
    
    except ValueError as e:
        logger.error(f"\n❌ Configuration error: {e}")
        print(f"\n❌ Configuration error: {e}")
        print("\nPlease check your configuration files:")
        print("  - Reply/config/config.yaml")
        print("  - MailAPI/config/.env")
        sys.exit(1)
    
    except Exception as e:
        logger.error(f"\n❌ Fatal error: {e}", exc_info=True)
        print(f"\n❌ Fatal error: {e}")
        print(f"Check log file for details: {log_file}")
        sys.exit(1)


if __name__ == "__main__":
    main()
