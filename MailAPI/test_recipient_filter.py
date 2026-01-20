#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for recipient filter feature
Demonstrates how to configure and use SAVE_RECIPIENTS
"""

import os
from pathlib import Path

def show_config_examples():
    """Show configuration examples"""
    print("\n" + "="*70)
    print("📧 MailAPI Recipient Filter Configuration")
    print("="*70)
    
    print("\n1️⃣  Save ALL emails (default behavior):")
    print("-" * 70)
    print("SAVE_RECIPIENTS=")
    print("\nResult: All emails will be processed and saved")
    
    print("\n\n2️⃣  Save emails from SPECIFIC senders only:")
    print("-" * 70)
    print("SAVE_RECIPIENTS=teacher@school.edu,boss@company.com,friend@gmail.com")
    print("\nResult: Only emails from these 3 addresses will be saved")
    print("        All other emails will be skipped")
    
    print("\n\n3️⃣  Save emails from a single sender:")
    print("-" * 70)
    print("SAVE_RECIPIENTS=important@example.com")
    print("\nResult: Only emails from important@example.com will be saved")
    
    print("\n" + "="*70)
    print("⚙️  Configuration Steps")
    print("="*70)
    
    steps = [
        ("1", "Open MailAPI/config/.env file"),
        ("2", "Find the SAVE_RECIPIENTS line"),
        ("3", "Add comma-separated email addresses"),
        ("4", "Save the file"),
        ("5", "Run MailAPI normally")
    ]
    
    for num, step in steps:
        print(f"\n{num}. {step}")
    
    print("\n" + "="*70)
    print("📝 Example Usage")
    print("="*70)
    
    print("\n# Edit .env file:")
    print("SAVE_RECIPIENTS=teacher@school.edu,mentor@university.edu")
    
    print("\n# Run MailAPI:")
    print("python3 main.py --days 7")
    
    print("\n# Console output will show:")
    print("INFO - Recipient filter enabled: 2 addresses")
    print("INFO - Saving emails from: teacher@school.edu, mentor@university.edu")
    print("\n# When processing emails:")
    print("✅ Email from teacher@school.edu → SAVED")
    print("✅ Email from mentor@university.edu → SAVED")
    print("⏩ Email from spam@random.com → SKIPPED (not in list)")
    
    print("\n" + "="*70)
    print("💡 Tips")
    print("="*70)
    
    tips = [
        "Email addresses are case-insensitive (Teacher@SCHOOL.edu = teacher@school.edu)",
        "Whitespace around emails is automatically trimmed",
        "Leave SAVE_RECIPIENTS empty to disable filtering",
        "Check logs for detailed filtering information",
        "Use --log-level DEBUG for verbose output"
    ]
    
    for i, tip in enumerate(tips, 1):
        print(f"\n{i}. {tip}")
    
    print("\n" + "="*70)
    print("🔍 Verifying Configuration")
    print("="*70)
    
    print("\nCheck your current .env file:")
    env_path = Path(__file__).parent / "config" / ".env"
    
    if env_path.exists():
        print(f"\n📄 File: {env_path}")
        with open(env_path, 'r') as f:
            for line in f:
                if 'SAVE_RECIPIENTS' in line and not line.strip().startswith('#'):
                    print(f"\n{line.strip()}")
                    
                    if '=' in line:
                        value = line.split('=', 1)[1].strip()
                        if value:
                            recipients = [r.strip() for r in value.split(',') if r.strip()]
                            print(f"\n✅ Filter enabled: {len(recipients)} recipient(s)")
                            for r in recipients:
                                print(f"   - {r}")
                        else:
                            print("\n⚪ Filter disabled: saving ALL emails")
                    break
    else:
        print(f"\n⚠️  .env file not found at: {env_path}")
        print("   Please create it from .env.example")
    
    print("\n" + "="*70)
    print("✅ Configuration Guide Complete!")
    print("="*70 + "\n")


def test_recipient_matching():
    """Test recipient matching logic"""
    print("\n" + "="*70)
    print("🧪 Testing Recipient Matching Logic")
    print("="*70)
    
    # Simulate the matching logic
    test_cases = [
        {
            "saved": ["teacher@school.edu", "boss@company.com"],
            "sender": "teacher@school.edu",
            "expected": True,
            "reason": "Exact match"
        },
        {
            "saved": ["teacher@school.edu"],
            "sender": "TEACHER@SCHOOL.EDU",
            "expected": True,
            "reason": "Case-insensitive match"
        },
        {
            "saved": ["teacher@school.edu"],
            "sender": "student@school.edu",
            "expected": False,
            "reason": "Different address"
        },
        {
            "saved": [],
            "sender": "anyone@example.com",
            "expected": True,
            "reason": "No filter (empty list)"
        },
        {
            "saved": ["  teacher@school.edu  "],
            "sender": "teacher@school.edu",
            "expected": True,
            "reason": "Whitespace trimmed"
        }
    ]
    
    print("\nRunning test cases...\n")
    
    for i, test in enumerate(test_cases, 1):
        saved = test["saved"]
        sender = test["sender"]
        expected = test["expected"]
        
        # Simulate should_save_email logic
        if not saved:
            result = True
        else:
            sender_lower = sender.lower().strip()
            result = any(sender_lower == r.lower().strip() for r in saved)
        
        status = "✅ PASS" if result == expected else "❌ FAIL"
        action = "SAVE" if result else "SKIP"
        
        print(f"Test {i}: {status}")
        print(f"  Saved list: {saved if saved else '(empty - save all)'}")
        print(f"  Sender: {sender}")
        print(f"  Result: {action}")
        print(f"  Reason: {test['reason']}")
        print()
    
    print("="*70 + "\n")


if __name__ == "__main__":
    print("\n🚀 MailAPI Recipient Filter - Configuration & Testing Tool\n")
    
    show_config_examples()
    test_recipient_matching()
    
    print("📚 For more information, see:")
    print("   - MailAPI/README.md")
    print("   - MailAPI/config/.env.example")
    print("\n✨ Happy filtering! ✨\n")
