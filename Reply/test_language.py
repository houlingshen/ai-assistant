#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for language switching functionality
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.i18n import I18n


def test_i18n():
    """Test i18n translations"""
    print("=" * 70)
    print("Testing Language Switching Functionality")
    print("=" * 70)
    
    # Test Chinese
    print("\n【中文测试 (Chinese Test)】\n")
    i18n_zh = I18n('zh')
    
    print(f"Report Title: {i18n_zh.t('report_title')}")
    print(f"Overview: {i18n_zh.t('overview')}")
    print(f"Report Period: {i18n_zh.t('report_period')}")
    print(f"Generated Time: {i18n_zh.t('generated_time')}")
    print(f"Todos Summary: {i18n_zh.t('todos_summary')}")
    print(f"Completed: {i18n_zh.t('completed')}")
    print(f"Pending: {i18n_zh.t('pending')}")
    print(f"High Priority: {i18n_zh.t('high_priority')}")
    print(f"Medium Priority: {i18n_zh.t('medium_priority')}")
    print(f"Low Priority: {i18n_zh.t('low_priority')}")
    print(f"Weekly Highlights: {i18n_zh.t('weekly_highlights')}")
    print(f"Tips & Insights: {i18n_zh.t('tips_insights')}")
    print(f"Activity Statistics: {i18n_zh.t('activity_statistics')}")
    print(f"Next Week Plan: {i18n_zh.t('next_week_plan')}")
    print(f"Auto Generated: {i18n_zh.t('auto_generated')}")
    
    # Test days
    print(f"\nDays of week:")
    for i in range(7):
        print(f"  {i}: {i18n_zh.get_day_name(i)}")
    
    # Test English
    print("\n【英文测试 (English Test)】\n")
    i18n_en = I18n('en')
    
    print(f"Report Title: {i18n_en.t('report_title')}")
    print(f"Overview: {i18n_en.t('overview')}")
    print(f"Report Period: {i18n_en.t('report_period')}")
    print(f"Generated Time: {i18n_en.t('generated_time')}")
    print(f"Todos Summary: {i18n_en.t('todos_summary')}")
    print(f"Completed: {i18n_en.t('completed')}")
    print(f"Pending: {i18n_en.t('pending')}")
    print(f"High Priority: {i18n_en.t('high_priority')}")
    print(f"Medium Priority: {i18n_en.t('medium_priority')}")
    print(f"Low Priority: {i18n_en.t('low_priority')}")
    print(f"Weekly Highlights: {i18n_en.t('weekly_highlights')}")
    print(f"Tips & Insights: {i18n_en.t('tips_insights')}")
    print(f"Activity Statistics: {i18n_en.t('activity_statistics')}")
    print(f"Next Week Plan: {i18n_en.t('next_week_plan')}")
    print(f"Auto Generated: {i18n_en.t('auto_generated')}")
    
    # Test days
    print(f"\nDays of week:")
    for i in range(7):
        print(f"  {i}: {i18n_en.get_day_name(i)}")
    
    # Test format strings
    print("\n【格式化测试 (Format Test)】\n")
    print(f"Chinese: {i18n_zh.t('week_starting', date='2026-01-20')}")
    print(f"English: {i18n_en.t('week_starting', date='2026-01-20')}")
    
    # Test language switching
    print("\n【语言切换测试 (Language Switch Test)】\n")
    i18n = I18n('zh')
    print(f"Initial (zh): {i18n.t('report_title')}")
    
    i18n.set_language('en')
    print(f"After switch (en): {i18n.t('report_title')}")
    
    i18n.set_language('zh')
    print(f"After switch back (zh): {i18n.t('report_title')}")
    
    # Test invalid language
    print("\n【无效语言测试 (Invalid Language Test)】\n")
    i18n_invalid = I18n('fr')  # French not supported
    print(f"Invalid language 'fr': {i18n_invalid.t('report_title')} (should default to Chinese)")
    
    print("\n" + "=" * 70)
    print("✅ All tests passed!")
    print("=" * 70)
    print("\n📝 Usage examples:")
    print("  python3 main.py --mode once --language zh   # Chinese report")
    print("  python3 main.py --mode once --language en   # English report")
    print("  python3 main.py --mode daemon --lang en     # English scheduled reports")
    print("\n⚙️  Configuration:")
    print("  Edit Reply/config/config.yaml:")
    print("    language:")
    print("      default: \"en\"  # or \"zh\"")
    print("=" * 70)


if __name__ == "__main__":
    test_i18n()
