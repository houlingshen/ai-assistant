#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Connect System - Main Entry Point
Bridge between MailAPI, MineContext, and Reply
"""

import logging
import sys
import time
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.email_reader import EmailDocumentReader
from src.minecontext_client import MineContextClient
from src.reply_trigger import ReplyTrigger
from src.file_watcher import FileWatcher
from src.sync_manager import SyncManager
from src.utils import setup_logging, load_config, load_env_variables, get_absolute_path, print_banner


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Connect System - Bridge MailAPI, MineContext, and Reply",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Sync all documents once
  python3 main.py --mode once
  
  # Run with file watcher (daemon mode)
  python3 main.py --mode daemon
  
  # Trigger weekly report generation
  python3 main.py --trigger-report
  
  # Test MineContext connection
  python3 main.py --test-connection
  
  # Show sync statistics
  python3 main.py --stats
        """
    )
    
    parser.add_argument(
        '--mode',
        choices=['once', 'daemon'],
        default='daemon',
        help='Run mode: once (sync once) or daemon (watch directory)'
    )
    
    parser.add_argument(
        '--trigger-report',
        action='store_true',
        help='Trigger weekly report generation and sending'
    )
    
    parser.add_argument(
        '--test-connection',
        action='store_true',
        help='Test MineContext API connection'
    )
    
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show synchronization statistics'
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
    
    return parser.parse_args()


def main():
    """Main entry point"""
    args = parse_arguments()
    
    # Load environment variables
    load_env_variables()
    
    # Load configuration
    config = load_config(args.config)
    
    # Setup logging
    log_config = config.get('logging', {})
    log_file = log_config.get('file', 'logs/connect.log')
    log_level = args.log_level or log_config.get('level', 'INFO')
    setup_logging(log_file, log_level)
    
    logger = logging.getLogger(__name__)
    
    # Print banner
    print_banner("Connect System")
    print("MailAPI ↔ MineContext ↔ Reply Bridge")
    print(f"Mode: {args.mode}")
    print(f"Config: {args.config}")
    print("=" * 60)
    print()
    
    logger.info("=" * 60)
    logger.info("        Connect System Starting")
    logger.info("=" * 60)
    logger.info(f"Mode: {args.mode}")
    logger.info(f"Config: {args.config}")
    logger.info(f"Log Level: {log_level}")
    logger.info("=" * 60)
    
    try:
        # Get configuration
        sync_config = config.get('sync', {})
        minecontext_config = config.get('minecontext', {})
        reply_config = config.get('reply', {})
        data_config = config.get('data', {})
        
        # Resolve paths
        mail_docs_dir = get_absolute_path(
            sync_config.get('mail_documents_dir', '../MailAPI/SavedDocuments')
        )
        reply_dir = get_absolute_path(
            reply_config.get('reply_dir', '../Reply')
        )
        processed_file = get_absolute_path(
            data_config.get('processed_files', 'data/processed_files.json')
        )
        
        logger.info(f"Mail documents directory: {mail_docs_dir}")
        logger.info(f"Reply directory: {reply_dir}")
        logger.info(f"Processed files tracking: {processed_file}")
        
        # Initialize components
        logger.info("Initializing components...")
        
        email_reader = EmailDocumentReader(str(mail_docs_dir))
        
        minecontext_client = MineContextClient(
            api_url=minecontext_config.get('api_url', 'http://localhost:8765'),
            auth_token=minecontext_config.get('auth_token', 'default_token')
        )
        
        reply_trigger = ReplyTrigger(str(reply_dir))
        
        sync_manager = SyncManager(
            email_reader,
            minecontext_client,
            reply_trigger,
            str(processed_file)
        )
        
        logger.info("All components initialized successfully")
        
        # Test connection mode
        if args.test_connection:
            logger.info("Testing MineContext API connection...")
            print("\n🔍 Testing MineContext API connection...")
            
            if minecontext_client.check_connection():
                print("✅ MineContext API connection successful!")
                logger.info("MineContext API connection successful")
            else:
                print("❌ Failed to connect to MineContext API")
                print("   Please ensure MineContext web server is running at:")
                print(f"   {minecontext_config.get('api_url', 'http://localhost:8765')}")
                logger.error("Failed to connect to MineContext API")
            
            # Also test Reply
            print("\n🔍 Testing Reply system...")
            if reply_trigger.test_reply_connection():
                print("✅ Reply system is accessible!")
            else:
                print("❌ Reply system not accessible")
            
            return
        
        # Show statistics mode
        if args.stats:
            logger.info("Retrieving synchronization statistics...")
            stats = sync_manager.get_sync_stats()
            
            print("\n📊 Synchronization Statistics")
            print("=" * 40)
            print(f"Total files:      {stats['total_files']}")
            print(f"Email files:      {stats['email_files']}")
            print(f"Summary files:    {stats['summary_files']}")
            print(f"Processed:        {stats['processed_count']}")
            print(f"Pending:          {stats['pending']}")
            print("=" * 40)
            
            return
        
        # Trigger report mode
        if args.trigger_report:
            logger.info("Triggering weekly report generation...")
            print("\n📧 Triggering weekly report generation...")
            
            success = sync_manager.trigger_weekly_report_generation()
            
            if success:
                print("✅ Weekly report generated and sent!")
                logger.info("Weekly report generated and sent successfully")
            else:
                print("❌ Failed to generate/send weekly report")
                logger.error("Failed to generate/send weekly report")
            
            return
        
        # Sync mode
        if args.mode == 'once':
            logger.info("Starting one-time sync...")
            print("\n🔄 Starting one-time sync...")
            
            # Check MineContext connection first
            if not minecontext_client.check_connection():
                print("❌ Cannot connect to MineContext API")
                print("   Please ensure MineContext web server is running")
                logger.error("Cannot sync: MineContext not accessible")
                sys.exit(1)
            
            # Sync all documents
            count = sync_manager.sync_all_documents()
            
            print(f"\n✅ Synced {count} email documents to MineContext")
            logger.info(f"One-time sync complete: {count} documents synced")
        
        else:
            # Daemon mode with file watcher
            logger.info("Starting daemon mode with file watcher...")
            print("\n🚀 Starting daemon mode...")
            
            # Check MineContext connection first
            if not minecontext_client.check_connection():
                print("⚠️  Warning: Cannot connect to MineContext API")
                print("   Please ensure MineContext web server is running")
                logger.warning("Starting without MineContext connection")
            
            # Initial sync
            print("📂 Performing initial sync...")
            count = sync_manager.sync_all_documents()
            print(f"   Synced {count} documents")
            logger.info(f"Initial sync: {count} documents")
            
            # Start file watcher
            print("\n👁️  Watching for new email documents...")
            print(f"   Directory: {mail_docs_dir}")
            print("   Press Ctrl+C to stop\n")
            
            watcher = FileWatcher(str(mail_docs_dir), sync_manager)
            watcher.start()
            
            if not watcher.is_alive():
                print("❌ Failed to start file watcher")
                logger.error("File watcher failed to start")
                sys.exit(1)
            
            try:
                while True:
                    time.sleep(1)
                    
                    # Check if watcher is still alive
                    if not watcher.is_alive():
                        logger.error("File watcher stopped unexpectedly")
                        print("\n❌ File watcher stopped unexpectedly")
                        break
                        
            except KeyboardInterrupt:
                logger.info("Stopping file watcher...")
                print("\n\n⏹️  Stopping file watcher...")
                watcher.stop()
                print("✅ File watcher stopped")
    
    except KeyboardInterrupt:
        logger.info("Program interrupted by user")
        print("\n\n⚠️  Program stopped by user")
        sys.exit(0)
    
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\n❌ Fatal error: {e}")
        print("   Check logs for details")
        sys.exit(1)
    
    logger.info("Connect system shutdown complete")
    print("\n✅ Connect system shutdown complete")


if __name__ == "__main__":
    main()
