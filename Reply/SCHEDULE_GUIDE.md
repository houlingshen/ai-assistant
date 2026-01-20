# 📅 Weekly Report Schedule Configuration Guide

This guide explains how to configure when your weekly reports are automatically generated and sent.

## 🎯 Quick Start

### Method 1: Edit Configuration File (Recommended)

Edit `Reply/config/config.yaml`:

```yaml
scheduler:
  weekly_report:
    day_of_week: "sun"  # Change to: mon, tue, wed, thu, fri, sat, sun
    hour: 20            # Change to: 0-23 (24-hour format)
    minute: 0           # Change to: 0-59
  enabled: true         # Set to false to disable scheduling
```

### Method 2: Command-Line Override (Temporary)

```bash
# Override schedule for this run only
python3 main.py --mode daemon --day fri --hour 18 --minute 30
```

## 📋 Configuration Options

### Day of Week

Valid values: `mon`, `tue`, `wed`, `thu`, `fri`, `sat`, `sun`

**Examples:**
- `day_of_week: "mon"` → Every Monday
- `day_of_week: "fri"` → Every Friday
- `day_of_week: "sun"` → Every Sunday (default)

### Hour (24-hour format)

Valid values: `0` to `23`

**Examples:**
- `hour: 9` → 9:00 AM
- `hour: 14` → 2:00 PM
- `hour: 20` → 8:00 PM (default)
- `hour: 0` → Midnight

### Minute

Valid values: `0` to `59`

**Examples:**
- `minute: 0` → On the hour (default)
- `minute: 15` → 15 minutes past the hour
- `minute: 30` → 30 minutes past the hour

## 💡 Usage Examples

### Example 1: Friday Evening Reports
```yaml
scheduler:
  weekly_report:
    day_of_week: "fri"
    hour: 18
    minute: 0
```
📧 Reports will be sent every **Friday at 6:00 PM**

### Example 2: Monday Morning Reports
```yaml
scheduler:
  weekly_report:
    day_of_week: "mon"
    hour: 9
    minute: 30
```
📧 Reports will be sent every **Monday at 9:30 AM**

### Example 3: Sunday Night Reports (Default)
```yaml
scheduler:
  weekly_report:
    day_of_week: "sun"
    hour: 20
    minute: 0
```
📧 Reports will be sent every **Sunday at 8:00 PM**

## 🔧 Command-Line Tools

### Check Current Schedule
```bash
python3 main.py --show-schedule
```

### Test with Different Schedule
```bash
# Test Friday at 6:30 PM
python3 main.py --mode daemon --day fri --hour 18 --minute 30
```

### Generate Report Immediately (Skip Schedule)
```bash
# Generate and send report right now
python3 main.py --mode once
```

## 📊 Time Zone Information

- All times use your **local system time**
- The scheduler uses 24-hour format internally
- Display shows both 24-hour and 12-hour formats

## ⚠️ Common Mistakes

### ❌ Wrong Day Format
```yaml
day_of_week: "Monday"  # WRONG - use lowercase abbreviation
day_of_week: "mon"     # CORRECT
```

### ❌ Hour Out of Range
```yaml
hour: 24  # WRONG - valid range is 0-23
hour: 0   # CORRECT (midnight)
```

### ❌ Using 12-hour Format
```yaml
hour: 8   # This is 8:00 AM, not 8:00 PM
hour: 20  # CORRECT for 8:00 PM
```

## 🎛️ Disable Scheduling

To disable automatic reports:

```yaml
scheduler:
  enabled: false
```

You can still generate reports manually:
```bash
python3 main.py --mode once
```

## 🔍 Troubleshooting

### Scheduler Not Running?

1. **Check if enabled:**
   ```bash
   python3 main.py --show-schedule
   ```

2. **Verify configuration:**
   ```bash
   cat config/config.yaml
   ```

3. **Check logs:**
   ```bash
   tail -f logs/reply.log
   ```

### Wrong Time?

- Verify your system time: `date`
- Check time zone settings
- Confirm 24-hour format usage

### Schedule Not Updating?

- Restart the scheduler after editing config
- Press `Ctrl+C` to stop, then restart

## 📚 Advanced Usage

### Multiple Schedules

Want to send reports twice a week? Run two separate instances:

**Terminal 1: Friday reports**
```bash
python3 main.py --mode daemon --day fri --hour 17
```

**Terminal 2: Monday reports**
```bash
python3 main.py --mode daemon --day mon --hour 9
```

### Dry Run (Testing)

Test your schedule configuration without actually sending:
```bash
# Just check the schedule
python3 main.py --show-schedule --day fri --hour 18

# Generate report but don't send
# (Edit email config to disable sending temporarily)
```

## 🆘 Need Help?

1. Check current configuration: `python3 main.py --show-schedule`
2. View logs: `cat logs/reply.log`
3. Test email: `python3 main.py --test-email`
4. Generate once: `python3 main.py --mode once`

---

**Happy Scheduling! 📅✨**
