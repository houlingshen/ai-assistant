#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sync Manager Module
Manage email document synchronization between MailAPI and MineContext
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Set, Optional

logger = logging.getLogger(__name__)


class SyncManager:
    """Manage email document synchronization"""
    
    def __init__(self, email_reader, minecontext_client, reply_trigger, processed_file: str):
        """
        Initialize sync manager
        
        Args:
            email_reader: EmailDocumentReader instance
            minecontext_client: MineContextClient instance
            reply_trigger: ReplyTrigger instance
            processed_file: Path to processed files tracking file
        """
        self.email_reader = email_reader
        self.minecontext_client = minecontext_client
        self.reply_trigger = reply_trigger
        self.processed_file = Path(processed_file)
        self.processed_files = self._load_processed_files()
        
        logger.info("Initialized SyncManager")
    
    def _load_processed_files(self) -> Set[str]:
        """
        Load list of already processed files
        
        Returns:
            Set[str]: Set of processed file paths
        """
        if self.processed_file.exists():
            try:
                with open(self.processed_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    files = set(data.get('files', []))
                    logger.info(f"Loaded {len(files)} processed files from tracking")
                    return files
            except Exception as e:
                logger.error(f"Error loading processed files: {e}")
                return set()
        else:
            logger.info("No processed files tracking found, starting fresh")
            return set()
    
    def _save_processed_files(self):
        """Save processed files list to disk"""
        try:
            # Create directory if it doesn't exist
            self.processed_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                'files': list(self.processed_files),
                'last_updated': datetime.now().isoformat(),
                'total_count': len(self.processed_files)
            }
            
            with open(self.processed_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Saved {len(self.processed_files)} processed files to tracking")
            
        except Exception as e:
            logger.error(f"Error saving processed files: {e}")
    
    def sync_single_document(self, filepath: Path) -> bool:
        """
        Sync a single email document to MineContext
        
        Args:
            filepath: Path to email document
            
        Returns:
            bool: True if successful
        """
        # Check if already processed
        filepath_str = str(filepath)
        if filepath_str in self.processed_files:
            logger.info(f"File already processed: {filepath.name}")
            return True
        
        try:
            logger.info(f"Processing new email document: {filepath.name}")
            
            # Parse email document
            email_data = self.email_reader.parse_email_document(filepath)
            
            if not email_data:
                logger.error(f"Failed to parse email document: {filepath.name}")
                return False
            
            # Import to MineContext
            doc_id = self.minecontext_client.import_email_document(email_data)
            
            if doc_id:
                logger.info(f"✓ Successfully imported: {filepath.name} (ID: {doc_id})")
                
                # Mark as processed
                self.processed_files.add(filepath_str)
                self._save_processed_files()
                
                return True
            else:
                logger.error(f"✗ Failed to import: {filepath.name}")
                return False
                
        except Exception as e:
            logger.error(f"Error syncing {filepath.name}: {e}", exc_info=True)
            return False
    
    def sync_all_documents(self) -> int:
        """
        Sync all unprocessed documents
        
        Returns:
            int: Number of documents successfully synced
        """
        logger.info("Starting batch sync of all documents...")
        
        # Get unprocessed documents
        unprocessed = self.email_reader.get_unprocessed_documents(self.processed_files)
        
        if not unprocessed:
            logger.info("No new documents to sync")
            return 0
        
        logger.info(f"Found {len(unprocessed)} unprocessed documents")
        
        success_count = 0
        
        for filepath in unprocessed:
            if self.sync_single_document(filepath):
                success_count += 1
        
        logger.info(f"Batch sync complete: {success_count}/{len(unprocessed)} documents synced")
        
        return success_count
    
    def trigger_weekly_report_generation(self, week: str = "current") -> bool:
        """
        Trigger weekly report generation and sending
        
        Args:
            week: Which week to generate report for ('current' or 'next')
            
        Returns:
            bool: True if successful
        """
        logger.info(f"Triggering weekly report generation for {week} week...")
        
        # Step 1: Optionally trigger MineContext to generate report
        # (MineContext may generate reports automatically, so this is optional)
        try:
            self.minecontext_client.trigger_report_generation("weekly")
        except Exception as e:
            logger.warning(f"Could not trigger MineContext report generation: {e}")
        
        # Step 2: Trigger Reply to send the report
        success = self.reply_trigger.trigger_weekly_report(week=week)
        
        if success:
            logger.info("✓ Weekly report generated and sent successfully")
        else:
            logger.error("✗ Failed to generate/send weekly report")
        
        return success
    
    def get_sync_stats(self) -> dict:
        """
        Get synchronization statistics
        
        Returns:
            dict: Statistics about sync status
        """
        total_files = len(list(self.email_reader.documents_dir.glob('*.md')))
        summary_files = len([f for f in self.email_reader.documents_dir.glob('*.md') 
                            if self.email_reader.is_summary_file(f)])
        
        return {
            'processed_count': len(self.processed_files),
            'total_files': total_files,
            'summary_files': summary_files,
            'email_files': total_files - summary_files,
            'pending': max(0, total_files - summary_files - len(self.processed_files))
        }
