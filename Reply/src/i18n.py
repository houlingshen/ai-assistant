#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Internationalization (i18n) Module
Provides multi-language support for weekly reports
"""

import logging

logger = logging.getLogger(__name__)


class I18n:
    """Internationalization handler for weekly reports"""
    
    # Language strings
    STRINGS = {
        'zh': {
            # Report sections
            'report_title': '周报',
            'week_starting': '周报 - {date}',
            'overview': '概览 (Overview)',
            'report_period': '报告周期',
            'generated_time': '生成时间',
            'data_source': '数据来源',
            
            # Daily summaries
            'daily_summaries': '每日总结 (Daily Summaries)',
            'no_summary': '*本日无总结。*',
            
            # Weekly highlights
            'weekly_highlights': '本周亮点 (Weekly Highlights)',
            'main_activities': '主要活动',
            'no_activities': '*未记录重要活动*',
            
            # Todos
            'todos_summary': '待办事项 (Todos Summary)',
            'completed': '✅ 已完成 (Completed)',
            'pending': '⏳ 未完成 (Pending)',
            'high_priority': '🔴 高',
            'medium_priority': '🟡 中',
            'low_priority': '🟢 低',
            'reason': '原因',
            'deadline': '截止',
            
            # Tips
            'tips_insights': '智能提示 (Tips & Insights)',
            
            # Activities
            'activity_statistics': '活动统计 (Activity Statistics)',
            'total_activities': '总活动数',
            'total_activity_time': '总活动时间',
            'hours': '小时',
            'activity_categories': '活动类别分布',
            'times': '次',
            
            # Next week plan
            'next_week_plan': '下周计划 (Next Week Plan)',
            'pending_tasks': '待完成任务',
            'no_pending_tasks': '*暂无待完成任务*',
            'important_deadlines': '⚠️ 重要截止日期提醒',
            
            # Course schedules
            'course_schedules': '📚 课程计划 (Course Schedules)',
            'sender': '发件人',
            'date': '日期',
            'content': '内容',
            'attachments': '附件',
            'course_tip': '请按照课程计划安排学习时间，确保按时完成教学任务。',
            
            # Ebbinghaus
            'ebbinghaus_title': '📚 艾宾浩斯复习提醒 (Ebbinghaus Review Reminder)',
            'ebbinghaus_intro': '根据艾宾浩斯遗忘曲线，以下是您的复习计划：',
            'review_statistics': '📊 复习统计',
            'active_content': '活跃学习内容',
            'completed_reviews': '已完成复习',
            'completion_rate': '完成率',
            'due_today': '今日待复习',
            'upcoming_this_week': '本周即将到期',
            'items': '项',
            'due_reviews': '⚠️ 待复习内容 (需要立即复习)',
            'no_due_reviews': '✅ 无待复习内容',
            'no_due_reviews_msg': '太棒了！您目前没有逾期的复习任务。',
            'weekly_review_plan': '📅 本周复习计划',
            'review_number': '复习次数',
            'review_date': '应复习日期',
            'days_overdue': '已逾期',
            'due_today_status': '今日到期',
            'content_summary': '内容摘要',
            'days_later': '天后',
            'today': '今天',
            
            # Footer
            'auto_generated': '*此报告由 AI Assistant 自动生成*',
            
            # Days of week
            'monday': '星期一',
            'tuesday': '星期二',
            'wednesday': '星期三',
            'thursday': '星期四',
            'friday': '星期五',
            'saturday': '星期六',
            'sunday': '星期日',
        },
        
        'en': {
            # Report sections
            'report_title': 'Weekly Report',
            'week_starting': 'Weekly Report - Week Starting {date}',
            'overview': 'Overview',
            'report_period': 'Report Period',
            'generated_time': 'Generated Time',
            'data_source': 'Data Source',
            
            # Daily summaries
            'daily_summaries': 'Daily Summaries',
            'no_summary': '*No summary available for this day.*',
            
            # Weekly highlights
            'weekly_highlights': 'Weekly Highlights',
            'main_activities': 'Main Activities',
            'no_activities': '*No significant activities recorded*',
            
            # Todos
            'todos_summary': 'Todos Summary',
            'completed': '✅ Completed',
            'pending': '⏳ Pending',
            'high_priority': '🔴 High',
            'medium_priority': '🟡 Medium',
            'low_priority': '🟢 Low',
            'reason': 'Reason',
            'deadline': 'Deadline',
            
            # Tips
            'tips_insights': 'Tips & Insights',
            
            # Activities
            'activity_statistics': 'Activity Statistics',
            'total_activities': 'Total Activities',
            'total_activity_time': 'Total Activity Time',
            'hours': 'hours',
            'activity_categories': 'Activity Category Distribution',
            'times': 'times',
            
            # Next week plan
            'next_week_plan': 'Next Week Plan',
            'pending_tasks': 'Pending Tasks',
            'no_pending_tasks': '*No pending tasks*',
            'important_deadlines': '⚠️ Important Deadlines',
            
            # Course schedules
            'course_schedules': '📚 Course Schedules',
            'sender': 'Sender',
            'date': 'Date',
            'content': 'Content',
            'attachments': 'Attachments',
            'course_tip': 'Please arrange your study time according to the course schedule to ensure timely completion of teaching tasks.',
            
            # Ebbinghaus
            'ebbinghaus_title': '📚 Ebbinghaus Review Reminder',
            'ebbinghaus_intro': 'Based on the Ebbinghaus forgetting curve, here is your review schedule:',
            'review_statistics': '📊 Review Statistics',
            'active_content': 'Active Learning Content',
            'completed_reviews': 'Completed Reviews',
            'completion_rate': 'Completion Rate',
            'due_today': 'Due Today',
            'upcoming_this_week': 'Upcoming This Week',
            'items': 'items',
            'due_reviews': '⚠️ Reviews Due (Immediate Action Required)',
            'no_due_reviews': '✅ No Reviews Due',
            'no_due_reviews_msg': 'Great! You have no overdue review tasks.',
            'weekly_review_plan': '📅 Weekly Review Plan',
            'review_number': 'Review Number',
            'review_date': 'Due Date',
            'days_overdue': 'Days Overdue',
            'due_today_status': 'Due Today',
            'content_summary': 'Content Summary',
            'days_later': 'days later',
            'today': 'today',
            
            # Footer
            'auto_generated': '*This report is automatically generated by AI Assistant*',
            
            # Days of week
            'monday': 'Monday',
            'tuesday': 'Tuesday',
            'wednesday': 'Wednesday',
            'thursday': 'Thursday',
            'friday': 'Friday',
            'saturday': 'Saturday',
            'sunday': 'Sunday',
        }
    }
    
    def __init__(self, language: str = 'zh'):
        """
        Initialize i18n with specified language
        
        Args:
            language: Language code ('zh' or 'en')
        """
        self.language = self._validate_language(language)
        logger.info(f"Language set to: {self.language}")
    
    def _validate_language(self, language: str) -> str:
        """Validate and return language code"""
        lang_lower = language.lower().strip()
        if lang_lower in self.STRINGS:
            return lang_lower
        logger.warning(f"Unsupported language '{language}', defaulting to 'zh'")
        return 'zh'
    
    def t(self, key: str, **kwargs) -> str:
        """
        Translate key to current language
        
        Args:
            key: Translation key
            **kwargs: Format parameters
            
        Returns:
            Translated string
        """
        translation = self.STRINGS.get(self.language, {}).get(key, key)
        
        # Apply formatting if kwargs provided
        if kwargs:
            try:
                return translation.format(**kwargs)
            except KeyError as e:
                logger.warning(f"Missing format parameter {e} for key '{key}'")
                return translation
        
        return translation
    
    def get_day_name(self, weekday: int) -> str:
        """
        Get day name for weekday number
        
        Args:
            weekday: 0=Monday, 6=Sunday
            
        Returns:
            Day name in current language
        """
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        if 0 <= weekday <= 6:
            return self.t(days[weekday])
        return str(weekday)
    
    def set_language(self, language: str):
        """Change current language"""
        self.language = self._validate_language(language)
        logger.info(f"Language changed to: {self.language}")
