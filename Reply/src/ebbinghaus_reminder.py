#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ebbinghaus Forgetting Curve Review Reminder Module
Implements spaced repetition based on Ebbinghaus forgetting curve
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class EbbinghausReviewReminder:
    """
    Ebbinghaus forgetting curve based review reminder system
    
    Review intervals based on scientific research:
    - 1st review: 1 day after learning
    - 2nd review: 2 days after 1st review
    - 3rd review: 4 days after 2nd review
    - 4th review: 7 days after 3rd review
    - 5th review: 15 days after 4th review
    - 6th review: 30 days after 5th review
    """
    
    # Standard Ebbinghaus intervals (in days)
    REVIEW_INTERVALS = [1, 2, 4, 7, 15, 30]
    
    def __init__(self, data_collector, storage_path: str = "data/review_schedule.json"):
        """
        Initialize review reminder system
        
        Args:
            data_collector: Data collector instance for fetching learning content
            storage_path: Path to store review schedules
        """
        self.data_collector = data_collector
        self.storage_path = Path(storage_path)
        self.review_schedules = self._load_schedules()
        
        logger.info("Ebbinghaus review reminder initialized")
    
    def _load_schedules(self) -> Dict[str, Any]:
        """Load existing review schedules from storage"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    schedules = json.load(f)
                    logger.info(f"Loaded {len(schedules)} review schedules")
                    return schedules
            except Exception as e:
                logger.error(f"Error loading review schedules: {e}")
                return {}
        return {}
    
    def _save_schedules(self):
        """Save review schedules to storage"""
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(self.review_schedules, f, indent=2, ensure_ascii=False)
            logger.debug(f"Saved {len(self.review_schedules)} review schedules")
        except Exception as e:
            logger.error(f"Error saving review schedules: {e}")
    
    def add_learning_content(self, content_id: str, content_title: str, 
                            content_summary: str, learning_date: Optional[datetime] = None,
                            course_name: Optional[str] = None, content_type: Optional[str] = None):
        """
        Add new learning content to review schedule
        
        Args:
            content_id: Unique identifier for the content
            content_title: Title of the learning content
            content_summary: Summary of the content
            learning_date: When the content was learned (default: now)
            course_name: Name of the course (e.g., "Mathematics", "English")
            content_type: Type of content (e.g., "lesson", "assignment", "reading")
        """
        if learning_date is None:
            learning_date = datetime.now()
        
        # Calculate all review dates
        review_dates = []
        current_date = learning_date
        
        for interval in self.REVIEW_INTERVALS:
            current_date = current_date + timedelta(days=interval)
            review_dates.append(current_date.isoformat())
        
        # Store schedule
        self.review_schedules[content_id] = {
            'title': content_title,
            'summary': content_summary,
            'learning_date': learning_date.isoformat(),
            'review_dates': review_dates,
            'completed_reviews': [],
            'current_review_index': 0,
            'status': 'active',
            'course_name': course_name or '未分类',  # Default: "Uncategorized"
            'content_type': content_type or 'general'
        }
        
        self._save_schedules()
        logger.info(f"Added review schedule for: {content_title}")
    
    def get_due_reviews(self, reference_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Get all reviews due on or before the reference date
        
        Args:
            reference_date: Date to check against (default: today)
            
        Returns:
            List of due review items
        """
        if reference_date is None:
            reference_date = datetime.now()
        
        due_reviews = []
        
        for content_id, schedule in self.review_schedules.items():
            if schedule['status'] != 'active':
                continue
            
            current_index = schedule['current_review_index']
            
            # Check if all reviews are completed
            if current_index >= len(schedule['review_dates']):
                schedule['status'] = 'completed'
                continue
            
            # Get next review date
            next_review_date = datetime.fromisoformat(schedule['review_dates'][current_index])
            
            # Check if review is due
            if next_review_date.date() <= reference_date.date():
                due_reviews.append({
                    'content_id': content_id,
                    'title': schedule['title'],
                    'summary': schedule['summary'],
                    'learning_date': schedule['learning_date'],
                    'due_date': schedule['review_dates'][current_index],
                    'review_number': current_index + 1,
                    'total_reviews': len(self.REVIEW_INTERVALS),
                    'days_overdue': (reference_date.date() - next_review_date.date()).days,
                    'course_name': schedule.get('course_name', '未分类'),
                    'content_type': schedule.get('content_type', 'general')
                })
        
        # Save any status changes
        self._save_schedules()
        
        # Sort by most overdue first
        due_reviews.sort(key=lambda x: x['days_overdue'], reverse=True)
        
        logger.info(f"Found {len(due_reviews)} due reviews")
        return due_reviews
    
    def mark_review_completed(self, content_id: str) -> bool:
        """
        Mark a review as completed and advance to next review
        
        Args:
            content_id: ID of the content that was reviewed
            
        Returns:
            bool: True if successful
        """
        if content_id not in self.review_schedules:
            logger.warning(f"Content ID not found: {content_id}")
            return False
        
        schedule = self.review_schedules[content_id]
        
        if schedule['status'] != 'active':
            logger.warning(f"Content is not active: {content_id}")
            return False
        
        # Record completion
        completion_time = datetime.now().isoformat()
        schedule['completed_reviews'].append({
            'review_number': schedule['current_review_index'] + 1,
            'completed_at': completion_time
        })
        
        # Move to next review
        schedule['current_review_index'] += 1
        
        # Check if all reviews completed
        if schedule['current_review_index'] >= len(schedule['review_dates']):
            schedule['status'] = 'completed'
            logger.info(f"All reviews completed for: {schedule['title']}")
        else:
            logger.info(f"Review {schedule['current_review_index']} completed for: {schedule['title']}")
        
        self._save_schedules()
        return True
    
    def get_upcoming_reviews(self, days_ahead: int = 7) -> List[Dict[str, Any]]:
        """
        Get reviews scheduled in the next N days
        
        Args:
            days_ahead: Number of days to look ahead
            
        Returns:
            List of upcoming review items
        """
        today = datetime.now()
        end_date = today + timedelta(days=days_ahead)
        
        upcoming = []
        
        for content_id, schedule in self.review_schedules.items():
            if schedule['status'] != 'active':
                continue
            
            current_index = schedule['current_review_index']
            
            if current_index >= len(schedule['review_dates']):
                continue
            
            next_review_date = datetime.fromisoformat(schedule['review_dates'][current_index])
            
            # Check if within range
            if today.date() <= next_review_date.date() <= end_date.date():
                days_until = (next_review_date.date() - today.date()).days
                
                upcoming.append({
                    'content_id': content_id,
                    'title': schedule['title'],
                    'summary': schedule['summary'],
                    'review_date': schedule['review_dates'][current_index],
                    'review_number': current_index + 1,
                    'total_reviews': len(self.REVIEW_INTERVALS),
                    'days_until': days_until,
                    'course_name': schedule.get('course_name', '未分类'),
                    'content_type': schedule.get('content_type', 'general')
                })
        
        # Sort by soonest first
        upcoming.sort(key=lambda x: x['days_until'])
        
        return upcoming
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get review statistics
        
        Returns:
            Dictionary with various statistics
        """
        total = len(self.review_schedules)
        active = sum(1 for s in self.review_schedules.values() if s['status'] == 'active')
        completed = sum(1 for s in self.review_schedules.values() if s['status'] == 'completed')
        
        due_today = len(self.get_due_reviews())
        upcoming_week = len(self.get_upcoming_reviews(7))
        
        # Calculate completion rate
        total_reviews_done = sum(
            len(s['completed_reviews']) 
            for s in self.review_schedules.values()
        )
        total_reviews_scheduled = sum(
            len(s['review_dates']) 
            for s in self.review_schedules.values()
        )
        
        completion_rate = (
            (total_reviews_done / total_reviews_scheduled * 100) 
            if total_reviews_scheduled > 0 else 0
        )
        
        return {
            'total_contents': total,
            'active_schedules': active,
            'completed_schedules': completed,
            'due_today': due_today,
            'upcoming_this_week': upcoming_week,
            'total_reviews_completed': total_reviews_done,
            'total_reviews_scheduled': total_reviews_scheduled,
            'completion_rate': round(completion_rate, 2)
        }
    
    def generate_review_reminder_text(self) -> str:
        """
        Generate formatted review reminder text for email
        
        Returns:
            Formatted text with review reminders
        """
        due_reviews = self.get_due_reviews()
        upcoming_reviews = self.get_upcoming_reviews(7)
        stats = self.get_statistics()
        
        lines = []
        lines.append("# 📚 艾宾浩斯复习提醒 (Ebbinghaus Review Reminder)")
        lines.append("")
        lines.append("根据艾宾浩斯遗忘曲线，以下是您的复习计划：")
        lines.append("")
        
        # Statistics
        lines.append("## 📊 复习统计")
        lines.append("")
        lines.append(f"- **活跃学习内容**: {stats['active_schedules']} 项")
        lines.append(f"- **已完成复习**: {stats['completed_schedules']} 项")
        lines.append(f"- **完成率**: {stats['completion_rate']}%")
        lines.append(f"- **今日待复习**: {stats['due_today']} 项")
        lines.append(f"- **本周即将到期**: {stats['upcoming_this_week']} 项")
        lines.append("")
        
        # Due reviews - Group by course
        if due_reviews:
            lines.append("⚠️ 待复习内容 (需要立即复习)")
            lines.append("")
                    
            # Group reviews by course
            reviews_by_course = {}
            for review in due_reviews:
                course_name = review.get('course_name', '未分类')
                if course_name not in reviews_by_course:
                    reviews_by_course[course_name] = []
                reviews_by_course[course_name].append(review)
                    
            # Display reviews grouped by course
            for course_name, course_reviews in sorted(reviews_by_course.items()):
                lines.append(f"### 📚 课程: {course_name}")
                lines.append("")
                        
                for review in course_reviews:
                    content_type_icon = "📖" if review.get('content_type') == 'lesson' else "📝" if review.get('content_type') == 'assignment' else "📚"
                    lines.append(f"#### {content_type_icon} {review['title']}")
                    lines.append("")
                    lines.append(f"- **复习次数**: 第 {review['review_number']}/{review['total_reviews']} 次")
                    lines.append(f"- **应复习日期**: {review['due_date'][:10]}")
                            
                    if review['days_overdue'] > 0:
                        lines.append(f"- **已逾期**: {review['days_overdue']} 天 ⚠️")
                    else:
                        lines.append(f"- **状态**: 今日到期")
                            
                    if review['summary']:
                        lines.append(f"- **内容摘要**: {review['summary'][:100]}...")
                            
                    lines.append("")
                        
                lines.append("")
        else:
            lines.append("## ✅ 无待复习内容")
            lines.append("")
            lines.append("太棒了！您目前没有逾期的复习任务。")
            lines.append("")
        
        # Upcoming reviews - Group by course
        if upcoming_reviews:
            lines.append("📅 本周复习计划")
            lines.append("")
                    
            # Group by course
            upcoming_by_course = {}
            for review in upcoming_reviews:
                course_name = review.get('course_name', '未分类')
                if course_name not in upcoming_by_course:
                    upcoming_by_course[course_name] = []
                upcoming_by_course[course_name].append(review)
                    
            # Display by course
            for course_name, course_reviews in sorted(upcoming_by_course.items()):
                lines.append(f"### 📚 {course_name}")
                lines.append("")
                        
                for review in course_reviews:
                    days_text = "今天" if review['days_until'] == 0 else f"{review['days_until']} 天后"
                    content_type_icon = "📖" if review.get('content_type') == 'lesson' else "📝" if review.get('content_type') == 'assignment' else "📚"
                    lines.append(f"- {content_type_icon} **{review['title']}** - {days_text} ({review['review_date'][:10]})")
                    lines.append(f"  - 第 {review['review_number']}/{review['total_reviews']} 次复习")
                        
                lines.append("")
                    
            lines.append("")
        
        return "\n".join(lines)
    
    def scan_minecontext_for_learning_content(self, days_back: int = 7) -> int:
        """
        Scan MineContext for new learning content and add to review schedule
        
        Args:
            days_back: Number of days to look back for new content
            
        Returns:
            Number of new items added to review schedule
        """
        try:
            from datetime import datetime, timedelta
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            # Get daily reports (learning content)
            daily_reports = self.data_collector.get_daily_reports(start_date, end_date)
            
            added_count = 0
            
            for report in daily_reports:
                content_id = f"daily_report_{report['id']}"
                
                # Skip if already in schedule
                if content_id in self.review_schedules:
                    continue
                
                # Add to review schedule
                learning_date = datetime.fromisoformat(report['created_at'].replace('Z', '+00:00'))
                
                self.add_learning_content(
                    content_id=content_id,
                    content_title=report.get('title', 'Daily Report'),
                    content_summary=report.get('summary', report.get('content', '')[:200]),
                    learning_date=learning_date
                )
                
                added_count += 1
            
            logger.info(f"Added {added_count} new learning items from MineContext")
            return added_count
            
        except Exception as e:
            logger.error(f"Error scanning MineContext: {e}")
            return 0
    
    def scan_email_documents_for_courses(self, email_documents: List[Dict[str, Any]]) -> int:
        """
        Scan email documents (course schedules) and add to review schedule
        
        Args:
            email_documents: List of email documents from data_collector
            
        Returns:
            Number of items added to review schedule
        """
        import re
        
        added_count = 0
        
        for doc in email_documents:
            body = doc.get('body', '')
            attachments = doc.get('attachments', [])
            doc_date_str = doc.get('date', '')
            
            if not doc_date_str:
                continue
            
            try:
                doc_date = datetime.fromisoformat(doc_date_str)
            except:
                continue
            
            # Extract course names from body and attachments
            courses = set()
            
            # Common course keywords
            course_patterns = [
                r'(Mathematics|Math|\u6570\u5b66)',
                r'(English|\u82f1\u8bed)',
                r'(Science|\u79d1\u5b66)',
                r'(History|\u5386\u53f2)',
                r'(Geography|\u5730\u7406)',
                r'(Physics|\u7269\u7406)',
                r'(Chemistry|\u5316\u5b66)',
                r'(Biology|\u751f\u7269)',
                r'(Chinese|\u8bed\u6587)',
            ]
            
            # Search in body
            for pattern in course_patterns:
                matches = re.findall(pattern, body, re.IGNORECASE)
                courses.update(matches)
            
            # Search in attachment names
            for att in attachments:
                for pattern in course_patterns:
                    matches = re.findall(pattern, att, re.IGNORECASE)
                    courses.update(matches)
            
            # If no courses identified, use a default
            if not courses:
                courses = {'通用课程'}
            
            # Create review items for each course mentioned
            for course_name in courses:
                content_id = f"course_{course_name}_{doc_date.strftime('%Y%m%d')}"
                
                # Skip if already exists
                if content_id in self.review_schedules:
                    continue
                
                # Extract week number or lesson info from body
                week_match = re.search(r'week\s+(\d+)|\u7b2c(\d+)\u5468', body, re.IGNORECASE)
                lesson_match = re.search(r'lesson\s+(\d+)|\u7b2c(\d+)\u8bfe', body, re.IGNORECASE)
                
                if week_match:
                    week_num = week_match.group(1) or week_match.group(2)
                    content_title = f"{course_name} - Week {week_num}"
                    content_type = 'lesson'
                elif lesson_match:
                    lesson_num = lesson_match.group(1) or lesson_match.group(2)
                    content_title = f"{course_name} - Lesson {lesson_num}"
                    content_type = 'lesson'
                else:
                    content_title = f"{course_name} - Course Material"
                    content_type = 'reading'
                
                # Add to review schedule
                self.add_learning_content(
                    content_id=content_id,
                    content_title=content_title,
                    content_summary=body[:150] if body else 'Course schedule received',
                    learning_date=doc_date,
                    course_name=course_name,
                    content_type=content_type
                )
                
                added_count += 1
                logger.info(f"Added course review: {content_title}")
        
        return added_count
