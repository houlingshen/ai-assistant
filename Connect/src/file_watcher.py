#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
File Watcher Module
Watch SavedDocuments directory for new email files
"""

import time
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileModifiedEvent

logger = logging.getLogger(__name__)


class EmailDocumentHandler(FileSystemEventHandler):
    """Handle new email document events"""
    
    def __init__(self, sync_manager):
        """
        Initialize email document handler
        
        Args:
            sync_manager: SyncManager instance
        """
        self.sync_manager = sync_manager
        super().__init__()
    
    def on_created(self, event):
        """
        Handle file creation event
        
        Args:
            event: File system event
        """
        if event.is_directory:
            return
        
        filepath = Path(event.src_path)
        
        # Only process .md files
        if filepath.suffix != '.md':
            return
        
        # Skip summary files
        if 'summary_' in filepath.name.lower():
            logger.debug(f"Skipping summary file: {filepath.name}")
            return
        
        logger.info(f"New email document detected: {filepath.name}")
        
        # Wait a bit for file to be fully written
        time.sleep(1)
        
        # Trigger sync
        try:
            self.sync_manager.sync_single_document(filepath)
        except Exception as e:
            logger.error(f"Error syncing new document {filepath.name}: {e}")
    
    def on_modified(self, event):
        """
        Handle file modification event
        
        Args:
            event: File system event
        """
        # Optionally handle file modifications
        # For now, we'll skip this to avoid duplicate processing
        pass


class FileWatcher:
    """Watch SavedDocuments directory for new files"""
    
    def __init__(self, watch_dir: str, sync_manager):
        """
        Initialize file watcher
        
        Args:
            watch_dir: Directory to watch
            sync_manager: SyncManager instance
        """
        self.watch_dir = Path(watch_dir).resolve()
        self.sync_manager = sync_manager
        self.observer = Observer()
        self.is_running = False
        
        if not self.watch_dir.exists():
            logger.warning(f"Watch directory not found: {self.watch_dir}")
        else:
            logger.info(f"Initialized file watcher for: {self.watch_dir}")
    
    def start(self):
        """Start watching directory"""
        if not self.watch_dir.exists():
            logger.error(f"Cannot start watcher: directory not found: {self.watch_dir}")
            return
        
        try:
            event_handler = EmailDocumentHandler(self.sync_manager)
            self.observer.schedule(event_handler, str(self.watch_dir), recursive=False)
            self.observer.start()
            self.is_running = True
            logger.info(f"Started watching directory: {self.watch_dir}")
            
        except Exception as e:
            logger.error(f"Failed to start file watcher: {e}")
            self.is_running = False
    
    def stop(self):
        """Stop watching directory"""
        if self.is_running:
            try:
                self.observer.stop()
                self.observer.join(timeout=5)
                self.is_running = False
                logger.info("File watcher stopped")
            except Exception as e:
                logger.error(f"Error stopping file watcher: {e}")
    
    def is_alive(self) -> bool:
        """
        Check if watcher is still running
        
        Returns:
            bool: True if watcher is running
        """
        return self.is_running and self.observer.is_alive()
