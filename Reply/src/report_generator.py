#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Weekly Report System - Report Generator Module
Generate weekly report in Markdown format
"""

import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List
import json

logger = logging.getLogger(__name__)


class WeeklyReportGenerator:
    """Generate weekly report in Markdown format"""
    
    def __init__(self, data_collector, output_dir: str = "ReplyDocuments", 
                 ebbinghaus_reminder=None):
        """
        Initialize report generator
        
        Args:
            data_collector: Instance of MineContextDataCollector
            output_dir: Directory to save generated reports
            ebbinghaus_reminder: Optional EbbinghausReviewReminder instance
        """
        self.data_collector = data_collector
        self.output_dir = Path(__file__).parent.parent / output_dir
        self.output_dir.mkdir(exist_ok=True)
        self.ebbinghaus_reminder = ebbinghaus_reminder
        logger.info(f"Initialized report generator, output dir: {self.output_dir}")
    
    def generate_weekly_report(self, week_start_date: datetime) -> str:
        """
        Generate weekly report for the specified week
        
        Args:
            week_start_date: Monday of the week (datetime)
        
        Returns:
            str: Markdown content of the weekly report
        """
        logger.info(f"Generating weekly report for week starting {week_start_date.date()}")
        
        # Collect data
        week_data = self.data_collector.get_week_data(week_start_date)
        
        # Generate Markdown content
        markdown_content = self._build_markdown(week_data)
        
        logger.info("Weekly report generated successfully")
        return markdown_content
    
    def _build_markdown(self, week_data: Dict[str, Any]) -> str:
        """
        Build Markdown content from collected data
        
        Args:
            week_data: Dictionary containing week's data
            
        Returns:
            str: Formatted Markdown content
        """
        week_start = week_data['week_start']
        week_end = week_data['week_end']
        
        md_lines = []
        
        # Header
        md_lines.append(f"# Weekly Report - Week Starting {week_start.strftime('%B %d, %Y')}")
        md_lines.append("")
        
        # Overview
        md_lines.append("## 概览 (Overview)")
        md_lines.append("")
        md_lines.append(f"- **报告周期**: {week_start.strftime('%Y-%m-%d')} - {week_end.strftime('%Y-%m-%d')}")
        md_lines.append(f"- **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        md_lines.append(f"- **数据来源**: MineContext AI Assistant")
        md_lines.append("")
        md_lines.append("---")
        md_lines.append("")
        
        # Daily Summaries
        daily_reports = week_data.get('daily_reports', [])
        if daily_reports:
            md_lines.append("## 每日总结 (Daily Summaries)")
            md_lines.append("")
            for report in daily_reports:
                report_date = datetime.fromisoformat(report['created_at'].replace('Z', '+00:00'))
                day_name = report_date.strftime('%A')
                md_lines.append(f"### {report_date.strftime('%Y-%m-%d')} - {day_name}")
                md_lines.append("")
                if report['content']:
                    md_lines.append(report['content'])
                else:
                    md_lines.append("*No summary available for this day.*")
                md_lines.append("")
            md_lines.append("---")
            md_lines.append("")
        
        # Weekly Highlights
        md_lines.append("## 本周亮点 (Weekly Highlights)")
        md_lines.append("")
        
        # Extract highlights from daily reports
        if daily_reports:
            md_lines.append("### 主要活动")
            activities = week_data.get('activities', [])
            if activities:
                for activity in activities[:5]:  # Top 5 activities
                    md_lines.append(f"- **{activity['title']}**")
                    if activity.get('content'):
                        # Take first line or summary
                        summary = activity['content'].split('\n')[0][:100]
                        md_lines.append(f"  {summary}...")
            else:
                md_lines.append("- *No significant activities recorded*")
            md_lines.append("")
        
        md_lines.append("---")
        md_lines.append("")
        
        # Todos Summary
        todos = week_data.get('todos', [])
        if todos:
            md_lines.append("## 待办事项 (Todos Summary)")
            md_lines.append("")
            
            completed_todos = [t for t in todos if t['status'] == 1]
            pending_todos = [t for t in todos if t['status'] == 0]
            
            if completed_todos:
                md_lines.append("### ✅ 已完成 (Completed)")
                md_lines.append("")
                for todo in completed_todos:
                    urgency = "🔴 高" if todo['urgency'] == 2 else "🟡 中" if todo['urgency'] == 1 else "🟢 低"
                    md_lines.append(f"- [x] {todo['content']} - [{urgency}]")
                    if todo.get('reason'):
                        md_lines.append(f"  *Reason: {todo['reason']}*")
                md_lines.append("")
            
            if pending_todos:
                md_lines.append("### ⏳ 未完成 (Pending)")
                md_lines.append("")
                for todo in pending_todos:
                    urgency = "🔴 高" if todo['urgency'] == 2 else "🟡 中" if todo['urgency'] == 1 else "🟢 低"
                    deadline = ""
                    if todo.get('end_time'):
                        deadline = f" (截止: {todo['end_time'][:10]})"
                    md_lines.append(f"- [ ] {todo['content']} - [{urgency}]{deadline}")
                    if todo.get('reason'):
                        md_lines.append(f"  *Reason: {todo['reason']}*")
                md_lines.append("")
            
            md_lines.append("---")
            md_lines.append("")
        
        # Tips & Insights
        tips = week_data.get('tips', [])
        if tips:
            md_lines.append("## 智能提示 (Tips & Insights)")
            md_lines.append("")
            for i, tip in enumerate(tips, 1):
                md_lines.append(f"{i}. {tip['content']}")
            md_lines.append("")
            md_lines.append("---")
            md_lines.append("")
        
        # Activity Statistics
        activities = week_data.get('activities', [])
        if activities:
            md_lines.append("## 活动统计 (Activity Statistics)")
            md_lines.append("")
            md_lines.append(f"- **总活动数**: {len(activities)}")
            
            # Calculate total time
            total_hours = 0
            for activity in activities:
                if activity.get('start_time') and activity.get('end_time'):
                    try:
                        start = datetime.fromisoformat(activity['start_time'].replace('Z', '+00:00'))
                        end = datetime.fromisoformat(activity['end_time'].replace('Z', '+00:00'))
                        duration = (end - start).total_seconds() / 3600
                        total_hours += duration
                    except:
                        pass
            
            md_lines.append(f"- **总活动时间**: {total_hours:.1f} 小时")
            md_lines.append("")
            
            # Category distribution (if metadata exists)
            categories = {}
            for activity in activities:
                if activity.get('metadata'):
                    try:
                        metadata = json.loads(activity['metadata']) if isinstance(activity['metadata'], str) else activity['metadata']
                        category = metadata.get('category', 'Other')
                        categories[category] = categories.get(category, 0) + 1
                    except:
                        pass
            
            if categories:
                md_lines.append("### 活动类别分布")
                for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                    md_lines.append(f"- {category}: {count} 次")
                md_lines.append("")
            
            md_lines.append("---")
            md_lines.append("")
        
        # Next Week Plan
        md_lines.append("## 下周计划 (Next Week Plan)")
        md_lines.append("")
        
        # Extract pending todos for next week
        pending_todos = [t for t in todos if t['status'] == 0]
        if pending_todos:
            md_lines.append("### 待完成任务")
            for todo in pending_todos[:10]:  # Top 10 pending tasks
                urgency = "🔴 高优先级" if todo['urgency'] == 2 else "🟡 中优先级" if todo['urgency'] == 1 else "🟢 低优先级"
                md_lines.append(f"- {todo['content']} - [{urgency}]")
            md_lines.append("")
        else:
            md_lines.append("*暂无待完成任务*")
            md_lines.append("")
        
        # Important deadlines
        upcoming_deadlines = []
        for todo in pending_todos:
            if todo.get('end_time'):
                try:
                    deadline = datetime.fromisoformat(todo['end_time'].replace('Z', '+00:00'))
                    if deadline > datetime.now():
                        upcoming_deadlines.append((todo['content'], deadline))
                except:
                    pass
        
        if upcoming_deadlines:
            upcoming_deadlines.sort(key=lambda x: x[1])
            md_lines.append("### ⚠️ 重要截止日期提醒")
            for content, deadline in upcoming_deadlines[:5]:
                md_lines.append(f"- **{deadline.strftime('%Y-%m-%d')}**: {content}")
            md_lines.append("")
        
        md_lines.append("---")
        md_lines.append("")
        
        # Ebbinghaus Review Reminder (if enabled)
        if self.ebbinghaus_reminder:
            try:
                # Scan for new learning content
                self.ebbinghaus_reminder.scan_minecontext_for_learning_content(days_back=7)
                
                # Generate review reminder section
                review_text = self.ebbinghaus_reminder.generate_review_reminder_text()
                md_lines.append(review_text)
                md_lines.append("---")
                md_lines.append("")
                logger.info("Added Ebbinghaus review reminder to report")
            except Exception as e:
                logger.error(f"Failed to add review reminder: {e}")
        
        # Footer
        md_lines.append("*此报告由 AI Assistant 自动生成*")
        md_lines.append("")
        
        return '\n'.join(md_lines)
    
    def save_report(self, markdown_content: str, week_start_date: datetime) -> Path:
        """
        Save report to ReplyDocuments/
        
        Args:
            markdown_content: The Markdown content to save
            week_start_date: Monday of the week
            
        Returns:
            Path: Path to the saved file
        """
        filename = f"weekly_report_{week_start_date.strftime('%Y%m%d')}.md"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        logger.info(f"Report saved to: {filepath}")
        return filepath
