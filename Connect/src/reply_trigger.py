#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Reply Trigger Module
Trigger Reply system to generate and send weekly reports
"""

import subprocess
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class ReplyTrigger:
    """Trigger Reply system to generate and send weekly reports"""
    
    def __init__(self, reply_dir: str):
        """
        Initialize Reply trigger
        
        Args:
            reply_dir: Path to Reply directory
        """
        self.reply_dir = Path(reply_dir).resolve()
        self.main_py = self.reply_dir / "main.py"
        
        if not self.reply_dir.exists():
            logger.warning(f"Reply directory not found: {self.reply_dir}")
        elif not self.main_py.exists():
            logger.warning(f"Reply main.py not found: {self.main_py}")
        else:
            logger.info(f"Initialized Reply trigger: {self.reply_dir}")
    
    def trigger_weekly_report(self, week: str = "current") -> bool:
        """
        Trigger Reply to generate and send weekly report
        
        Args:
            week: 'current' or 'next'
            
        Returns:
            bool: True if successful
        """
        if not self.main_py.exists():
            logger.error(f"Reply main.py not found: {self.main_py}")
            return False
        
        try:
            logger.info(f"Triggering Reply system for {week} week...")
            
            cmd = [
                "python3",
                str(self.main_py),
                "--mode", "once",
                "--week", week
            ]
            
            logger.debug(f"Running command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                cwd=str(self.reply_dir),
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            # Log output
            if result.stdout:
                logger.info(f"Reply stdout: {result.stdout}")
            
            if result.stderr:
                logger.warning(f"Reply stderr: {result.stderr}")
            
            # Check exit code
            if result.returncode == 0:
                logger.info("Reply system completed successfully")
                return True
            else:
                logger.error(f"Reply system failed with exit code {result.returncode}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Reply system timed out (exceeded 5 minutes)")
            return False
            
        except Exception as e:
            logger.error(f"Failed to trigger Reply system: {e}")
            return False
    
    def test_reply_connection(self) -> bool:
        """
        Test if Reply system is accessible
        
        Returns:
            bool: True if Reply is accessible
        """
        if not self.main_py.exists():
            logger.error(f"Reply main.py not found: {self.main_py}")
            return False
        
        try:
            # Try to run with --help to test if it's working
            cmd = ["python3", str(self.main_py), "--help"]
            
            result = subprocess.run(
                cmd,
                cwd=str(self.reply_dir),
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                logger.info("Reply system is accessible")
                return True
            else:
                logger.error("Reply system test failed")
                return False
                
        except Exception as e:
            logger.error(f"Failed to test Reply connection: {e}")
            return False
