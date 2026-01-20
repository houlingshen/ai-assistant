# -*- coding: utf-8 -*-

# Copyright (c) 2025 Beijing Volcano Engine Technology Co., Ltd.
# SPDX-License-Identifier: Apache-2.0

"""
Analysis routes - Historical data analysis and retrieval
Provides endpoints for analyzing past two weeks of data
"""

import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Body, Depends, Query
from pydantic import BaseModel

from opencontext.server.middleware.auth import auth_dependency
from opencontext.server.opencontext import OpenContext
from opencontext.server.utils import convert_resp, get_context_lab
from opencontext.storage.global_storage import get_storage
from opencontext.utils.logging_utils import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["analysis"])


class AnalysisResultModel(BaseModel):
    """Analysis result model"""
    analysis_type: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None


@router.get("/api/analysis/two-weeks-data")
async def get_two_weeks_data(
    opencontext: OpenContext = Depends(get_context_lab),
    _auth: str = auth_dependency,
):
    """
    Get all data from the past two weeks for analysis
    
    Returns aggregated data including:
    - Reports (daily summaries)
    - Activities
    - Todos
    - Tips
    """
    try:
        now = datetime.now()
        two_weeks_ago = now - timedelta(days=14)
        
        logger.info(f"Fetching data from {two_weeks_ago.date()} to {now.date()}")
        
        # Get reports from past 2 weeks
        reports = get_storage().get_reports(limit=100, offset=0, is_deleted=False)
        reports_filtered = [
            r for r in reports 
            if r.get('created_at') and datetime.fromisoformat(r['created_at'].replace('Z', '+00:00')) >= two_weeks_ago
        ]
        
        # Get activities from past 2 weeks
        activities = get_storage().get_activities(
            start_time=two_weeks_ago,
            end_time=now,
            limit=200,
            offset=0
        )
        
        # Parse JSON fields
        for activity in activities:
            if activity.get("resources"):
                try:
                    activity["resources"] = json.loads(activity["resources"])
                except (json.JSONDecodeError, TypeError):
                    activity["resources"] = None
            if activity.get("metadata"):
                try:
                    activity["metadata"] = json.loads(activity["metadata"])
                except (json.JSONDecodeError, TypeError):
                    activity["metadata"] = None
        
        # Get todos from past 2 weeks
        todos = get_storage().get_todos(status=None, limit=100, offset=0)
        todos_filtered = [
            t for t in todos 
            if t.get('created_at') and datetime.fromisoformat(t['created_at'].replace('Z', '+00:00')) >= two_weeks_ago
        ]
        
        # Get tips from past 2 weeks
        tips = get_storage().get_tips(limit=100, offset=0)
        tips_filtered = [
            t for t in tips 
            if t.get('created_at') and datetime.fromisoformat(t['created_at'].replace('Z', '+00:00')) >= two_weeks_ago
        ]
        
        # Aggregate statistics
        stats = {
            "total_reports": len(reports_filtered),
            "total_activities": len(activities),
            "total_todos": len(todos_filtered),
            "completed_todos": len([t for t in todos_filtered if t.get('status') == 1]),
            "pending_todos": len([t for t in todos_filtered if t.get('status') == 0]),
            "total_tips": len(tips_filtered),
            "date_range": {
                "start": two_weeks_ago.isoformat(),
                "end": now.isoformat()
            }
        }
        
        logger.info(f"Retrieved two weeks data: {stats}")
        
        return convert_resp(data={
            "reports": reports_filtered,
            "activities": activities,
            "todos": todos_filtered,
            "tips": tips_filtered,
            "statistics": stats
        })
        
    except Exception as e:
        logger.exception(f"Error fetching two weeks data: {e}")
        return convert_resp(
            code=500,
            status=500,
            message=f"Failed to fetch two weeks data: {str(e)}"
        )


@router.get("/api/analysis/daily-summary")
async def get_daily_summary(
    days: int = Query(14, ge=1, le=30, description="Number of days to retrieve"),
    opencontext: OpenContext = Depends(get_context_lab),
    _auth: str = auth_dependency,
):
    """
    Get daily summary for the past N days
    Groups data by day for easier analysis
    """
    try:
        now = datetime.now()
        start_date = now - timedelta(days=days)
        
        logger.info(f"Fetching daily summary from {start_date.date()} to {now.date()}")
        
        # Get all data
        reports = get_storage().get_reports(limit=100, offset=0, is_deleted=False)
        activities = get_storage().get_activities(
            start_time=start_date,
            end_time=now,
            limit=500,
            offset=0
        )
        todos = get_storage().get_todos(status=None, limit=100, offset=0)
        tips = get_storage().get_tips(limit=100, offset=0)
        
        # Group by day
        daily_data = {}
        
        for i in range(days):
            day = (now - timedelta(days=i)).date()
            day_str = day.isoformat()
            daily_data[day_str] = {
                "date": day_str,
                "reports": [],
                "activities": [],
                "todos": [],
                "tips": []
            }
        
        # Categorize reports
        for report in reports:
            if report.get('created_at'):
                report_date = datetime.fromisoformat(report['created_at'].replace('Z', '+00:00')).date()
                day_str = report_date.isoformat()
                if day_str in daily_data:
                    daily_data[day_str]["reports"].append(report)
        
        # Categorize activities
        for activity in activities:
            if activity.get('start_time'):
                activity_date = datetime.fromisoformat(activity['start_time'].replace('Z', '+00:00')).date()
                day_str = activity_date.isoformat()
                if day_str in daily_data:
                    # Parse JSON fields
                    if activity.get("resources"):
                        try:
                            activity["resources"] = json.loads(activity["resources"])
                        except (json.JSONDecodeError, TypeError):
                            activity["resources"] = None
                    daily_data[day_str]["activities"].append(activity)
        
        # Categorize todos
        for todo in todos:
            if todo.get('created_at'):
                todo_date = datetime.fromisoformat(todo['created_at'].replace('Z', '+00:00')).date()
                day_str = todo_date.isoformat()
                if day_str in daily_data:
                    daily_data[day_str]["todos"].append(todo)
        
        # Categorize tips
        for tip in tips:
            if tip.get('created_at'):
                tip_date = datetime.fromisoformat(tip['created_at'].replace('Z', '+00:00')).date()
                day_str = tip_date.isoformat()
                if day_str in daily_data:
                    daily_data[day_str]["tips"].append(tip)
        
        # Convert to sorted list
        daily_list = sorted(daily_data.values(), key=lambda x: x['date'], reverse=True)
        
        logger.info(f"Generated daily summary for {len(daily_list)} days")
        
        return convert_resp(data={
            "daily_summary": daily_list,
            "total_days": len(daily_list)
        })
        
    except Exception as e:
        logger.exception(f"Error generating daily summary: {e}")
        return convert_resp(
            code=500,
            status=500,
            message=f"Failed to generate daily summary: {str(e)}"
        )


@router.post("/api/analysis/save-result")
async def save_analysis_result(
    result: AnalysisResultModel = Body(...),
    opencontext: OpenContext = Depends(get_context_lab),
    _auth: str = auth_dependency,
):
    """
    Save analysis result to database for future reference
    Creates a new vault document with the analysis
    """
    try:
        logger.info(f"Saving analysis result: {result.analysis_type}")
        
        # Create metadata
        metadata = result.metadata or {}
        metadata["analysis_type"] = result.analysis_type
        if result.start_time:
            metadata["start_time"] = result.start_time
        if result.end_time:
            metadata["end_time"] = result.end_time
        
        # Save as vault document
        doc_id = get_storage().insert_vaults(
            title=f"Analysis - {result.analysis_type} - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            summary=f"Automated analysis: {result.analysis_type}",
            content=result.content,
            document_type="analysis",
            tags=f"analysis,{result.analysis_type},automated"
        )
        
        logger.info(f"Analysis result saved with ID: {doc_id}")
        
        return convert_resp(data={
            "message": "Analysis result saved successfully",
            "doc_id": doc_id
        })
        
    except Exception as e:
        logger.exception(f"Error saving analysis result: {e}")
        return convert_resp(
            code=500,
            status=500,
            message=f"Failed to save analysis result: {str(e)}"
        )


@router.get("/api/analysis/weekly-stats")
async def get_weekly_stats(
    weeks: int = Query(2, ge=1, le=8, description="Number of weeks to analyze"),
    opencontext: OpenContext = Depends(get_context_lab),
    _auth: str = auth_dependency,
):
    """
    Get weekly statistics for comparison and trend analysis
    """
    try:
        now = datetime.now()
        start_date = now - timedelta(weeks=weeks)
        
        logger.info(f"Calculating weekly stats for {weeks} weeks")
        
        # Get all relevant data
        activities = get_storage().get_activities(
            start_time=start_date,
            end_time=now,
            limit=1000,
            offset=0
        )
        
        todos = get_storage().get_todos(status=None, limit=200, offset=0)
        todos_filtered = [
            t for t in todos 
            if t.get('created_at') and datetime.fromisoformat(t['created_at'].replace('Z', '+00:00')) >= start_date
        ]
        
        reports = get_storage().get_reports(limit=100, offset=0, is_deleted=False)
        reports_filtered = [
            r for r in reports 
            if r.get('created_at') and datetime.fromisoformat(r['created_at'].replace('Z', '+00:00')) >= start_date
        ]
        
        # Group by week
        weekly_stats = []
        
        for i in range(weeks):
            week_start = now - timedelta(weeks=i+1)
            week_end = now - timedelta(weeks=i)
            
            week_activities = [
                a for a in activities 
                if a.get('start_time') and 
                week_start <= datetime.fromisoformat(a['start_time'].replace('Z', '+00:00')) < week_end
            ]
            
            week_todos = [
                t for t in todos_filtered 
                if t.get('created_at') and 
                week_start <= datetime.fromisoformat(t['created_at'].replace('Z', '+00:00')) < week_end
            ]
            
            week_reports = [
                r for r in reports_filtered 
                if r.get('created_at') and 
                week_start <= datetime.fromisoformat(r['created_at'].replace('Z', '+00:00')) < week_end
            ]
            
            # Calculate total activity time
            total_hours = 0
            for activity in week_activities:
                if activity.get('start_time') and activity.get('end_time'):
                    try:
                        start = datetime.fromisoformat(activity['start_time'].replace('Z', '+00:00'))
                        end = datetime.fromisoformat(activity['end_time'].replace('Z', '+00:00'))
                        duration = (end - start).total_seconds() / 3600
                        total_hours += duration
                    except:
                        pass
            
            weekly_stats.append({
                "week_number": i + 1,
                "week_start": week_start.isoformat(),
                "week_end": week_end.isoformat(),
                "total_activities": len(week_activities),
                "total_activity_hours": round(total_hours, 2),
                "total_reports": len(week_reports),
                "total_todos": len(week_todos),
                "completed_todos": len([t for t in week_todos if t.get('status') == 1]),
                "pending_todos": len([t for t in week_todos if t.get('status') == 0]),
                "completion_rate": round(
                    len([t for t in week_todos if t.get('status') == 1]) / len(week_todos) * 100, 2
                ) if week_todos else 0
            })
        
        logger.info(f"Generated weekly stats for {len(weekly_stats)} weeks")
        
        return convert_resp(data={
            "weekly_stats": weekly_stats,
            "total_weeks": len(weekly_stats)
        })
        
    except Exception as e:
        logger.exception(f"Error calculating weekly stats: {e}")
        return convert_resp(
            code=500,
            status=500,
            message=f"Failed to calculate weekly stats: {str(e)}"
        )
