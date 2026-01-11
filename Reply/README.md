# Weekly Report System

智能周报生成与发送系统 - 基于 MineContext 数据自动生成和发送周报

## 📋 Overview

Weekly Report System 是一个自动化周报生成和发送系统，它能够：
- 📊 从 MineContext Web API 收集每周的活动、待办、提示等数据
- 📝 生成结构化的 Markdown 格式周报
- 📧 通过 Gmail 自动发送格式化的 HTML 邮件
- ⏰ 支持定时任务，每周日自动执行

**重要**: 本系统通过 HTTP API 与 MineContext Web 服务器交互，不直接访问数据库。

---

## 🚀 Features

- **数据收集**: 从 MineContext Web API 收集 daily reports, tips, todos, activities
- **智能生成**: 自动生成包含多个部分的结构化周报
- **邮件发送**: HTML 格式邮件 + Markdown 附件
- **定时任务**: 使用 APScheduler 实现自动化调度
- **灵活配置**: 支持 YAML 配置文件和环境变量

---

## 📁 Project Structure

```
Reply/
├── config/
│   ├── config.yaml          # 系统配置
│   └── .env.example         # 环境变量示例
├── src/
│   ├── __init__.py
│   ├── data_collector.py    # 数据收集模块
│   ├── report_generator.py  # 周报生成模块
│   ├── email_sender.py      # 邮件发送模块
│   ├── scheduler.py         # 定时任务模块
│   └── utils.py             # 工具函数
├── ReplyDocuments/          # 存储生成的周报
├── logs/                    # 日志文件
├── main.py                  # 主程序入口
├── requirements.txt         # Python 依赖
├── instruction.md           # 详细设计文档
└── README.md               # 本文档
```

---

## 🔧 Installation

### 1. Install Python Dependencies

```bash
cd /Users/shenli/Projects/holly/ai-assistant/Reply
pip3 install -r requirements.txt
```

### 2. Configure MineContext API

Create `config/.env` file with MineContext API settings:

```bash
cd /Users/shenli/Projects/holly/ai-assistant/Reply/config
cp .env.example .env
nano .env
```

Edit the file:
```env
# MineContext Web API Configuration
MINECONTEXT_API_URL=http://localhost:8765
MINECONTEXT_AUTH_TOKEN=default_token
```

**Note**: Ensure MineContext web server is running at the configured URL.

### 3. Configure Email Credentials

The system reads email configuration from `../MailAPI/config/.env`:

```bash
# Make sure MailAPI/.env is configured
cd ../MailAPI/config
cat .env
```

Should contain:
```env
EMAIL_ADDRESS=your-gmail@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_PROVIDER=gmail
```

**Note**: Use Gmail app-specific password, not regular password.

### 3. Verify MineContext Web Server

Ensure MineContext web server is running:
```bash
# Check if MineContext is running
curl http://localhost:8765/api/debug/tips?limit=1
```

If not running, start it:
```bash
cd /Users/shenli/Projects/holly/ai-assistant/MineContext-main
python3 -m opencontext.server.opencontext
```

---

## 🎯 Usage

### Quick Start

#### 1. Generate and Send Report Immediately (Test Mode)

```bash
python3 main.py --mode once
```

This will:
- Generate a report for **next week**
- Save it to `ReplyDocuments/`
- Send it via email

#### 2. Generate Report for Current Week

```bash
python3 main.py --mode once --week current
```

#### 3. Run as Daemon (Scheduled Mode)

```bash
python3 main.py --mode daemon
```

This will start a scheduler that automatically generates and sends reports every Sunday at 20:00.

#### 4. Test Email Configuration

```bash
python3 main.py --test-email
```

---

## 📧 API Configuration

The system uses MineContext Web API to fetch data. Configuration:

- **API Base URL**: http://localhost:8765 (default)
- **Authentication**: Bearer token authentication
- **Endpoints Used**:
  - `/api/debug/reports` - Daily/weekly reports
  - `/api/debug/tips` - Tips and insights
  - `/api/debug/todos` - Todo items
  - `/api/debug/activities` - Activity records

### API URL Configuration

You can configure the API URL in three ways:

1. **In config.yaml**:
```yaml
data_collection:
  minecontext_api_url: "http://localhost:8765"
  minecontext_auth_token: "default_token"
```

2. **In .env file**:
```env
MINECONTEXT_API_URL=http://localhost:8765
MINECONTEXT_AUTH_TOKEN=default_token
```

3. **Command line arguments**:
```bash
python3 main.py --api-url http://localhost:8080 --auth-token your_token
```

## 📧 Email Configuration

The system uses Gmail SMTP to send emails. Configuration is read from `MailAPI/config/.env`:

- **SMTP Server**: smtp.gmail.com
- **Port**: 587 (TLS)
- **Authentication**: Gmail app password

### How to Get Gmail App Password

1. Enable 2-factor authentication on your Google account
2. Visit https://myaccount.google.com/apppasswords
3. Generate a new app password
4. Update `MailAPI/config/.env` with the app password

---

## ⚙️ Configuration

### config/config.yaml

```yaml
data_collection:
  minecontext_db_path: "~/Library/Application Support/MineContext/Data/minecontext.db"

report_generation:
  output_dir: "ReplyDocuments"
  format: "markdown"

email:
  smtp_server: "smtp.gmail.com"
  smtp_port: 587
  use_html: true
  attach_markdown: true

scheduler:
  weekly_report:
    day_of_week: "sun"  # Sunday
    hour: 20
    minute: 0
  enabled: true

logging:
  level: "INFO"
  file: "logs/reply.log"
```

---

## 📊 Report Structure

Generated reports include:

1. **概览 (Overview)**
   - 报告周期、生成时间、数据来源

2. **每日总结 (Daily Summaries)**
   - 每天的 daily report 内容

3. **本周亮点 (Weekly Highlights)**
   - 主要活动和成就

4. **待办事项 (Todos)**
   - 已完成 / 未完成分类
   - 优先级标记

5. **智能提示 (Tips & Insights)**
   - MineContext 生成的建议

6. **活动统计 (Activity Statistics)**
   - 总活动时间、类别分布

7. **下周计划 (Next Week Plan)**
   - 待完成任务、重要截止日期

---

## 🔍 Command Line Options

```bash
# Run modes
--mode daemon          # Run as daemon with scheduler (default)
--mode once           # Generate and send report immediately

# Week selection (only for --mode once)
--week next           # Generate report for next week (default)
--week current        # Generate report for current week

# Configuration
--config FILE         # Use custom config file
--log-level LEVEL     # Set log level (DEBUG, INFO, WARNING, ERROR)
--db-path PATH        # Custom MineContext database path

# Testing
--test-email          # Send test email and exit
```

### Examples

```bash
# Generate next week's report now
python3 main.py --mode once --week next

# Generate current week's report
python3 main.py --mode once --week current

# Run with debug logging
python3 main.py --mode once --log-level DEBUG

# Test email configuration
python3 main.py --test-email

# Use custom database
python3 main.py --mode once --db-path /path/to/custom.db
```

---

## 🐛 Troubleshooting

### Issue 1: API Connection Failed

**Error**: `API request failed` or connection timeout

**Solution**:
- Ensure MineContext web server is running:
  ```bash
  curl http://localhost:8765/api/debug/tips?limit=1
  ```
- Start MineContext if not running:
  ```bash
  cd ../MineContext-main
  python3 -m opencontext.server.opencontext
  ```
- Check API URL in `config/config.yaml` or `config/.env`
- Verify authentication token is correct

### Issue 2: Database Not Found (Old Error)

**Note**: This error no longer applies as the system now uses HTTP API instead of direct database access.

If you see this error, you're using an old version. Pull the latest code.

### Issue 2: Email Authentication Failed

**Error**: `SMTP authentication failed`

**Solution**:
- Verify Gmail app password in `MailAPI/config/.env`
- Ensure 2FA is enabled on Google account
- Generate new app password if needed

### Issue 3: No Data in Report

**Issue**: Report is generated but mostly empty

**Solution**:
- MineContext might not have data for the selected week
- Try generating report for current week: `--week current`
- Check MineContext is actively collecting data

### Issue 4: Permission Denied (Old Error)

**Note**: This error no longer applies as the system now uses HTTP API.

No database file permissions are needed.

---

## 📝 Logs

Logs are saved to `logs/reply.log`:

```bash
# View recent logs
tail -f logs/reply.log

# Search for errors
grep ERROR logs/reply.log
```

---

## 🔄 Integration

### With MailAPI

- Reads email credentials from `../MailAPI/config/.env`
- Uses same Gmail account for sending reports

### With MineContext

- Connects to MineContext Web API (HTTP)
- Read-only access via API endpoints
- Supports real-time data synchronization
- No direct database access required

---

## 🚦 Status & Monitoring

When running in daemon mode, the scheduler logs:
- Startup confirmation
- Next scheduled run time
- Job execution status
- Email sending results

---

## 📅 Scheduled Task

Default schedule: **Every Sunday at 20:00**

The system will:
1. Collect data from MineContext for the upcoming week
2. Generate formatted Markdown report
3. Save to `ReplyDocuments/weekly_report_YYYYMMDD.md`
4. Send HTML email with Markdown attachment

---

## 🎨 Customization

### Modify Report Template

Edit `src/report_generator.py` → `_build_markdown()` method

### Change Schedule

Edit `config/config.yaml`:
```yaml
scheduler:
  weekly_report:
    day_of_week: "mon"  # Change to Monday
    hour: 9
    minute: 30
```

### Custom Sections

Modify `config/config.yaml`:
```yaml
report_generation:
  include_sections:
    - daily_summaries
    - todos
    - tips
    - activities
    - next_week_plan
    - custom_section  # Add your own
```

---

## 🛡️ Security Notes

- Email credentials stored in `.env` file (not in version control)
- Read-only access to MineContext database
- Uses TLS encryption for email transmission
- App-specific passwords instead of account passwords

---

## 📞 Support

For issues or questions:
1. Check logs in `logs/reply.log`
2. Review `instruction.md` for detailed specifications
3. Verify all configurations in `config/config.yaml`

---

## 📜 License

Part of the ai-assistant project for student schedule management.

---

**Generated by AI Assistant** 🤖
