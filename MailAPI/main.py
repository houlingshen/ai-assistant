"""
Main entry point for the MailAPI email processing system.
Command-line interface for retrieving, parsing, and organizing emails.
"""

import argparse
import logging
import sys
from datetime import datetime
from typing import List, Dict, Any

from src.utils import setup_logging
from src.mail_client import MailClient
from src.mail_parser import MailParser
from src.attachment_handler import AttachmentHandler
from src.schedule_extractor import ScheduleExtractor
from src.document_generator import DocumentGenerator


class MailAPIProcessor:
    """
    Main processor for email retrieval and document generation.
    """
    
    def __init__(self):
        """Initialize the processor with all components."""
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.client = MailClient()
        self.parser = MailParser()
        self.attachment_handler = AttachmentHandler()
        self.schedule_extractor = ScheduleExtractor()
        self.document_generator = DocumentGenerator()
        
        self.processed_emails = []
    
    def process_emails(self, args: argparse.Namespace):
        """
        Main email processing workflow.
        
        Args:
            args: Command line arguments
        """
        try:
            # Connect to mail server
            print("\n" + "="*60)
            print("📧 正在连接邮箱服务器...")
            print("="*60)
            self.logger.info("Connecting to email server...")
            if not self.client.connect():
                print("\n❌ 连接失败！请检查：")
                print("   1. 网络连接是否正常")
                print("   2. 邮箱地址是否正确")
                print("   3. 是否使用了应用专用密码（而非账号密码）")
                print("   4. 查看 TROUBLESHOOTING.md 获取详细帮助\n")
                self.logger.error("Failed to connect to email server")
                return
            
            print("✅ 连接成功！\n")
            
            # Select folder
            folder = args.folder if hasattr(args, 'folder') and args.folder else "INBOX"
            print(f"📁 选择邮件文件夹: {folder}")
            if not self.client.select_folder(folder):
                print(f"❌ 无法选择文件夹: {folder}\n")
                self.logger.error(f"Failed to select folder: {folder}")
                return
            
            # Build search criteria
            search_criteria = MailParser.build_search_criteria(
                from_addr=args.from_addr if hasattr(args, 'from_addr') else None,
                subject=args.subject[0] if hasattr(args, 'subject') and args.subject else None,
                days_back=args.days if hasattr(args, 'days') else None,
                since_date=args.start_date if hasattr(args, 'start_date') else None,
                before_date=args.end_date if hasattr(args, 'end_date') else None
            )
            
            print(f"🔍 搜索条件: {search_criteria}")
            print("⏳ 正在搜索邮件...\n")
            self.logger.info(f"Searching emails with criteria: {search_criteria}")
            
            # Search for emails
            email_ids = self.client.search_emails(search_criteria)
            
            if not email_ids:
                print("\n⚠️  未找到符合条件的邮件")
                print("提示: 可以尝试调整搜索条件（扩大日期范围、减少关键词等）\n")
                self.logger.info("No emails found matching criteria")
                return
            
            print(f"✅ 找到 {len(email_ids)} 封邮件\n")
            print("="*60)
            print("📝 开始处理邮件...")
            print("="*60 + "\n")
            self.logger.info(f"Found {len(email_ids)} emails to process")
            
            # Process each email
            for i, email_id in enumerate(email_ids, 1):
                print(f"\n[{i}/{len(email_ids)}] 正在处理第 {i} 封邮件...")
                self.logger.info(f"Processing email {i}/{len(email_ids)}")
                self._process_single_email(email_id, args)
                print(f"✓ 完成")
            
            # Generate summary report
            if self.processed_emails:
                print("\n" + "="*60)
                print("📊 正在生成摘要报告...")
                self.logger.info("Generating summary report...")
                summary_path = self.document_generator.generate_summary_report(self.processed_emails)
                print(f"✅ 摘要报告已保存: {summary_path}")
                self.logger.info(f"Summary report saved to: {summary_path}")
            
            print("\n" + "="*60)
            print(f"🎉 成功处理 {len(self.processed_emails)} 封邮件！")
            print("="*60)
            print(f"\n📂 文档保存位置: SavedDocuments/")
            print(f"💾 附件保存位置: SavedDocuments/attachments/\n")
            self.logger.info(f"Successfully processed {len(self.processed_emails)} emails")
            
        except Exception as e:
            self.logger.error(f"Error during email processing: {e}", exc_info=True)
        
        finally:
            # Disconnect from server
            self.client.disconnect()
    
    def _process_single_email(self, email_id: bytes, args: argparse.Namespace):
        """Process a single email."""
        try:
            # Fetch raw email
            raw_email = self.client.fetch_email(email_id)
            if not raw_email:
                self.logger.warning(f"Failed to fetch email {email_id}")
                return
            
            # Parse email
            email_data = self.parser.parse_email(raw_email)
            if not email_data:
                self.logger.warning(f"Failed to parse email {email_id}")
                return
            
            # Apply keyword filter if specified
            if hasattr(args, 'subject') and args.subject:
                if not self.parser.filter_by_keywords(email_data, args.subject):
                    self.logger.info(f"Email filtered out by keywords: {email_data.get('subject', 'N/A')}")
                    return
            
            subject = email_data.get('subject', 'N/A')
            print(f"   📧 主题: {subject[:60]}{'...' if len(subject) > 60 else ''}")
            self.logger.info(f"Processing: {email_data.get('subject', 'N/A')}")
            
            # Process attachments
            attachments = []
            if email_data.get('has_attachments'):
                print(f"   📎 处理附件...")
                msg = self.parser.get_message_object(raw_email)
                message_id = email_data.get('message_id', str(email_id.decode()))
                # Create safe email ID for folder name
                safe_email_id = message_id.replace('<', '').replace('>', '').replace('/', '_')[:50]
                attachments = self.attachment_handler.process_attachments(msg, safe_email_id)
                if attachments:
                    print(f"   ✓ 已保存 {len(attachments)} 个附件")
            
            # Extract schedules
            schedules = self.schedule_extractor.extract_schedules(email_data)
            if schedules:
                print(f"   📅 提取到 {len(schedules)} 个日程安排")
            
            # Generate document
            output_format = args.format if hasattr(args, 'format') and args.format else "markdown"
            document_path = self.document_generator.generate_document(
                email_data, schedules, attachments, format=output_format
            )
            print(f"   💾 已生成文档: {document_path}")
            
            # Store processing result
            email_data['schedules'] = schedules
            email_data['attachments'] = attachments
            email_data['document_path'] = document_path
            self.processed_emails.append(email_data)
            
        except Exception as e:
            self.logger.error(f"Error processing email {email_id}: {e}")


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="MailAPI - Email Processing System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Retrieve all emails from last 7 days
  python main.py --days 7
  
  # Retrieve emails from specific sender
  python main.py --from teacher@school.edu
  
  # Retrieve emails with subject keywords
  python main.py --subject "作业" "考试"
  
  # Retrieve emails in date range
  python main.py --start-date 2024-01-01 --end-date 2024-01-31
  
  # Combined filters
  python main.py --from teacher@school.edu --days 7 --subject "作业"
  
  # Output as JSON
  python main.py --days 7 --format json
        """
    )
    
    # Search filters
    parser.add_argument('--from', dest='from_addr', type=str,
                       help='Filter by sender email address')
    parser.add_argument('--subject', nargs='+',
                       help='Filter by subject keywords (multiple keywords allowed)')
    parser.add_argument('--days', type=int,
                       help='Retrieve emails from last N days')
    parser.add_argument('--start-date', type=lambda s: datetime.strptime(s, '%Y-%m-%d'),
                       help='Start date for email retrieval (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=lambda s: datetime.strptime(s, '%Y-%m-%d'),
                       help='End date for email retrieval (YYYY-MM-DD)')
    
    # Folder selection
    parser.add_argument('--folder', type=str, default='INBOX',
                       help='Email folder to search (default: INBOX)')
    
    # Output options
    parser.add_argument('--format', type=str, choices=['markdown', 'json'], default='markdown',
                       help='Output format for generated documents (default: markdown)')
    
    # Logging
    parser.add_argument('--log-level', type=str, default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                       help='Logging level (default: INFO)')
    
    return parser.parse_args()


def main():
    """Main entry point."""
    # Parse arguments
    args = parse_arguments()
    
    # Setup logging
    logger = setup_logging(args.log_level)
    
    print("\n" + "="*60)
    print("        MailAPI Email Processing System")
    print("        智能邮件处理与日程提取系统")
    print("="*60)
    print(f"📅 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔧 日志级别: {args.log_level}")
    print("="*60 + "\n")
    
    try:
        # Create processor and run
        processor = MailAPIProcessor()
        processor.process_emails(args)
        
        logger.info("="*60)
        logger.info("Processing completed successfully")
        logger.info("="*60)
        print("\n✅ 处理完成！")
        print(f"📝 日志文件: mailapi.log\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  程序被用户中断")
        logger.info("\nProcessing interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        print(f"📝 详细信息请查看日志文件: mailapi.log\n")
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
