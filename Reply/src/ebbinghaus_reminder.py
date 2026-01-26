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
        Generate actionable review reminder text focused on helping users study effectively
        
        Returns:
            Formatted text with clear action items for review
        """
        due_reviews = self.get_due_reviews()
        upcoming_reviews = self.get_upcoming_reviews(7)
        
        lines = []
        lines.append("# 📚 今日复习计划 (Today's Review Plan)")
        lines.append("")
        lines.append("*基于艾宾浩斯遗忘曲线的科学复习提醒*")
        lines.append("")
        
        # Priority: Due reviews (what needs to be reviewed NOW)
        if due_reviews:
            # Group by course
            reviews_by_course = {}
            for review in due_reviews:
                course_name = review.get('course_name', '其他内容')
                if course_name not in reviews_by_course:
                    reviews_by_course[course_name] = []
                reviews_by_course[course_name].append(review)
            
            lines.append("## 🎯 今日必做 - 需要立即复习的内容")
            lines.append("")
            
            for course_name, course_reviews in sorted(reviews_by_course.items()):
                # Count overdue days
                max_overdue = max(r['days_overdue'] for r in course_reviews)
                urgency_icon = "🔴" if max_overdue > 3 else "🟡" if max_overdue > 0 else "🟢"
                
                lines.append(f"### {urgency_icon} {course_name}")
                lines.append("")
                lines.append(f"**共 {len(course_reviews)} 个知识点需要复习**")
                lines.append("")
                
                # List what to review
                lines.append("**复习内容：**")
                for i, review in enumerate(course_reviews, 1):
                    # Simplify: just show what needs to be reviewed
                    title = review['title']
                    review_num = review['review_number']
                    
                    # Show status icon
                    if review['days_overdue'] > 3:
                        status = "⚠️ 紧急"
                    elif review['days_overdue'] > 0:
                        status = "⏰ 逾期"
                    else:
                        status = "📅 今天"
                    
                    lines.append(f"{i}. {title} - {status} (第{review_num}次复习)")
                
                lines.append("")
                
                # Action guidance
                if max_overdue > 3:
                    lines.append("💡 **建议**: 这门课程复习严重滞后，建议今天优先完成！")
                elif max_overdue > 0:
                    lines.append("💡 **建议**: 尽快完成复习，巩固记忆。")
                else:
                    lines.append("💡 **建议**: 按计划复习，保持学习节奏。")
                
                lines.append("")
                lines.append("---")
                lines.append("")
        else:
            lines.append("## ✅ 今日无待复习内容")
            lines.append("")
            lines.append("🎉 太棒了！今天没有需要复习的内容，继续保持！")
            lines.append("")
        
        # Upcoming reviews this week
        if upcoming_reviews:
            lines.append("## 📅 本周复习计划")
            lines.append("")
            lines.append("*提前规划，从容应对*")
            lines.append("")
            
            # Group by date then by course
            reviews_by_date = {}
            for review in upcoming_reviews:
                date = review['review_date'][:10]
                if date not in reviews_by_date:
                    reviews_by_date[date] = {}
                
                course_name = review.get('course_name', '其他内容')
                if course_name not in reviews_by_date[date]:
                    reviews_by_date[date][course_name] = []
                reviews_by_date[date][course_name].append(review)
            
            # Display by date
            for date in sorted(reviews_by_date.keys()):
                # Parse date to show day of week
                from datetime import datetime
                date_obj = datetime.fromisoformat(date)
                weekday_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
                weekday = weekday_names[date_obj.weekday()]
                
                # Calculate days until
                today = datetime.now().date()
                days_until = (date_obj.date() - today).days
                
                if days_until == 0:
                    date_display = f"今天 ({date})"  
                elif days_until == 1:
                    date_display = f"明天 {weekday} ({date})"
                else:
                    date_display = f"{days_until}天后 {weekday} ({date})"
                
                lines.append(f"### 📆 {date_display}")
                lines.append("")
                
                # List courses for this date
                for course_name, course_reviews in sorted(reviews_by_date[date].items()):
                    lines.append(f"**{course_name}** - {len(course_reviews)} 个知识点")
                    for review in course_reviews:
                        lines.append(f"  - {review['title']} (第{review['review_number']}次)")
                
                lines.append("")
        
        # Study tips based on Ebbinghaus curve
        lines.append("---")
        lines.append("")
        lines.append("## 💡 复习小贴士")
        lines.append("")
        lines.append("**艾宾浩斯遗忘曲线复习时间点：**")
        lines.append("- 第1次复习：学习后1天 (巩固初次记忆)")
        lines.append("- 第2次复习：学习后2天 (强化记忆)")
        lines.append("- 第3次复习：学习后4天 (加深印象)")
        lines.append("- 第4次复习：学习后7天 (长期记忆)")
        lines.append("- 第5次复习：学习后15天 (考试准备)")
        lines.append("- 第6次复习：学习后30天 (永久记忆)")
        lines.append("")
        lines.append("**复习建议：**")
        lines.append("- ✅ 按时复习比一次性突击更有效")
        lines.append("- ✅ 每次复习15-30分钟即可，不需要重新完整学习")
        lines.append("- ✅ 重点回顾关键概念、公式和例题")
        lines.append("- ✅ 做相关练习题检验掌握程度")
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
        Scan email documents for course schedules/plans and add to review schedule
        Only processes emails that contain actual schedule/plan indicators
            
        Args:
            email_documents: List of email documents from data_collector
                
        Returns:
            Number of items added to review schedule
        """
        import re
            
        added_count = 0
            
        # Keywords that indicate this is a course schedule/plan email
        schedule_indicators = [
            r'schedule',
            r'timetable',
            r'time table',
            r'syllabus',
            r'teaching plan',
            r'lesson plan',
            r'curriculum',
            r'course plan',
            r'outline',
            r'课程表',
            r'课表',
            r'教学计划',
            r'课程大纲',
            r'课程安排',
            r'教案',
            r'学习计划',
            r'week\s*\d+',  # Week 1, Week 2, etc.
            r'第\s*\d+\s*周',  # 第1周, 第2周, etc.
        ]
            
        for doc in email_documents:
            body = doc.get('body', '')
            subject = doc.get('subject', '')
            attachments = doc.get('attachments', [])
            doc_date_str = doc.get('date', '')
                
            if not doc_date_str:
                continue
                
            try:
                doc_date = datetime.fromisoformat(doc_date_str)
            except:
                continue
                
            # First check: Does this email contain schedule/plan indicators?
            is_schedule_email = False
            combined_text = f"{subject} {body} {' '.join(attachments)}".lower()
                
            for indicator in schedule_indicators:
                if re.search(indicator, combined_text, re.IGNORECASE):
                    is_schedule_email = True
                    logger.info(f"Found schedule indicator '{indicator}' in email")
                    break
                
            # Skip if not a schedule/plan email
            if not is_schedule_email:
                logger.debug(f"Skipping email - no schedule indicators found")
                continue
                
            # Extract course names from body and attachments
            courses = set()
                
            # Common course keywords
            course_patterns = [
                r'(Mathematics|Math|数学)',
                r'(English|英语)',
                r'(Science|科学)',
                r'(History|历史)',
                r'(Geography|地理)',
                r'(Physics|物理)',
                r'(Chemistry|化学)',
                r'(Biology|生物)',
                r'(Chinese|语文)',
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
                
            # If no specific courses identified but it's a schedule email, use subject/attachment as course
            if not courses:
                # Try to extract from subject or first attachment
                if attachments:
                    # Use attachment filename as course name
                    att_name = attachments[0].replace('.pdf', '').replace('.docx', '').replace('.xlsx', '')
                    courses.add(att_name[:50])  # Limit length
                elif subject:
                    courses.add(subject[:50])
                else:
                    courses = {'课程计划'}
                
            # Create review items for each course mentioned
            for course_name in courses:
                content_id = f"course_{course_name}_{doc_date.strftime('%Y%m%d')}"
                    
                # Skip if already exists
                if content_id in self.review_schedules:
                    continue
                    
                # Extract week number or lesson info from body
                week_match = re.search(r'week\s+(\d+)|第(\d+)周', body, re.IGNORECASE)
                lesson_match = re.search(r'lesson\s+(\d+)|第(\d+)课', body, re.IGNORECASE)
                    
                if week_match:
                    week_num = week_match.group(1) or week_match.group(2)
                    content_title = f"{course_name} - Week {week_num}"
                    content_type = 'lesson'
                elif lesson_match:
                    lesson_num = lesson_match.group(1) or lesson_match.group(2)
                    content_title = f"{course_name} - Lesson {lesson_num}"
                    content_type = 'lesson'
                else:
                    content_title = f"{course_name} - 课程计划"
                    content_type = 'reading'
                    
                # Use a concise summary - just indicate it's a schedule
                summary = f"收到课程计划，请按时复习课程内容"
                    
                # Add to review schedule
                self.add_learning_content(
                    content_id=content_id,
                    content_title=content_title,
                    content_summary=summary,
                    learning_date=doc_date,
                    course_name=course_name,
                    content_type=content_type
                )
                    
                added_count += 1
                logger.info(f"Added course review: {content_title}")
            
        return added_count
