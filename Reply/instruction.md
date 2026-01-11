# Background（背景）
当前项目 ai-assistant 是一个帮助学生从邮件中整理并规划日程安排及信息的智能执行系统。
我们目前位于 `ai-assistant/Reply` 目录下。

**核心任务**：
1. 从 MineContext-main 收集生成的内容（daily reports, weekly reports, tips, todos, activities）
2. 整理成结构化的周报文档
3. 保存到 ReplyDocuments 目录，按日期命名
4. 每周日自动发送下周的周报给 MailAPI 中的用户邮箱

---

# Role（角色）
你是一位精通 Python 开发的 AI 创新大赛参赛大学生，擅长：
- Python 异步编程和定时任务
- SQLite/数据库查询和数据处理
- Gmail API 集成和邮件发送
- Markdown 文档生成和格式化
- 系统集成和模块化设计

---

# Goals（目标）

## 主要功能

### 1. 数据收集模块 (Data Collection)
从 MineContext 的本地数据库中收集以下内容：
- **Daily Reports**: 每日总结（存储在 vaults 表，document_type='daily_report'）
- **Weekly Reports**: 每周总结（存储在 vaults 表，document_type='weekly_report'）
- **Tips**: 智能提示（存储在 tips 表）
- **Todos**: 待办事项（存储在 todos 表，包含状态、优先级、截止时间）
- **Activities**: 活动记录（存储在 activities 表）

**数据库位置**：`~/Library/Application Support/MineContext/Data/minecontext.db`

### 2. 周报生成模块 (Weekly Report Generator)
整合收集到的数据，生成结构化的周报文档：

**周报结构**：
```markdown
# Weekly Report - [Week Starting Date]

## 概述 (Overview)
- 报告周期：[Start Date] - [End Date]
- 生成时间：[Generation Timestamp]
- 数据来源：MineContext AI Assistant

## 每日总结 (Daily Summaries)
### [Date 1 - Monday]
[Daily report content]

### [Date 2 - Tuesday]
[Daily report content]
...

## 本周亮点 (Weekly Highlights)
- 主要成就
- 重要事件
- 学习进展

## 待办事项 (Todos Summary)
### 已完成 (Completed)
- [ ] Task 1 - [优先级] [完成日期]

### 进行中 (In Progress)
- [ ] Task 2 - [优先级] [截止日期]

### 未完成 (Pending)
- [ ] Task 3 - [优先级] [截止日期]

## 智能提示 (Tips & Insights)
1. [Tip 1]
2. [Tip 2]
...

## 活动统计 (Activity Statistics)
- 总活动时间：[X hours]
- 主要活动类别：
  - 学习：[X hours]
  - 工作：[Y hours]
  - 其他：[Z hours]

## 下周计划 (Next Week Plan)
- 从待办事项中提取下周需要完成的任务
- 重要截止日期提醒
```

**文件命名**：`weekly_report_YYYYMMDD.md`（使用周一的日期）
**保存位置**：`Reply/ReplyDocuments/weekly_report_YYYYMMDD.md`

### 3. 邮件发送模块 (Email Sender)
使用 Gmail API 发送周报邮件给用户：

**邮件配置**：
- 发件人：从 MailAPI 的 `config/.env` 读取 Gmail 账户
- 收件人：从 MailAPI 的 `config/.env` 读取 `EMAIL_ADDRESS`
- 主题：`Weekly Report - Week of [Date]`
- 内容：将 Markdown 周报转换为 HTML 格式发送
- 附件：原始 Markdown 文件

### 4. 定时任务模块 (Scheduler)
使用 `schedule` 或 `APScheduler` 实现：
- **周报生成**：每周日 20:00 生成下周的周报
- **邮件发送**：每周日 20:30 发送生成的周报
- **数据收集**：每天 19:00 同步 MineContext 数据

---

# Technical Requirements（技术要求）

## 1. 技术栈
- **语言**：Python 3.8+
- **数据库**：SQLite3（读取 MineContext 数据库）
- **定时任务**：`APScheduler` 或 `schedule`
- **邮件发送**：`smtplib` + `email` 或 Gmail API
- **Markdown 处理**：`markdown2` 或 `mistune`
- **日志**：`logging`
- **配置管理**：`python-dotenv` + YAML

## 2. Python 库依赖
```txt
APScheduler>=3.10.0
python-dotenv>=1.0.0
markdown2>=2.4.0
PyYAML>=6.0
pytz>=2024.1
```

## 3. 项目结构
```
Reply/
├── config/
│   ├── config.yaml          # 系统配置
│   └── .env.example         # 环境变量示例
├── src/
│   ├── __init__.py
│   ├── data_collector.py    # 从 MineContext 收集数据
│   ├── report_generator.py  # 生成周报 Markdown
│   ├── email_sender.py      # 发送邮件
│   ├── scheduler.py         # 定时任务管理
│   └── utils.py             # 工具函数
├── ReplyDocuments/          # 存储生成的周报
├── logs/                    # 日志文件
├── main.py                  # 主程序入口
├── requirements.txt         # Python 依赖
├── README.md                # 项目说明
└── instruction.md          # 本文档
```

## 4. 核心功能实现要点

### 4.1 数据收集 (data_collector.py)
```python
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import os

class MineContextDataCollector:
    """Collect data from MineContext database"""
    
    def __init__(self):
        # MineContext database path
        self.db_path = Path.home() / "Library/Application Support/MineContext/Data/minecontext.db"
    
    def get_daily_reports(self, start_date, end_date):
        """Get daily reports from vaults table"""
        # Query: SELECT * FROM vaults WHERE document_type='daily_report' AND created_at BETWEEN start_date AND end_date
        pass
    
    def get_weekly_reports(self, start_date, end_date):
        """Get weekly reports"""
        pass
    
    def get_tips(self, start_date, end_date):
        """Get tips from tips table"""
        pass
    
    def get_todos(self, start_date, end_date):
        """Get todos with status from todos table"""
        pass
    
    def get_activities(self, start_date, end_date):
        """Get activities from activities table"""
        pass
```

### 4.2 周报生成 (report_generator.py)
```python
from datetime import datetime, timedelta
import markdown2

class WeeklyReportGenerator:
    """Generate weekly report in Markdown format"""
    
    def __init__(self, data_collector):
        self.data_collector = data_collector
    
    def generate_weekly_report(self, week_start_date):
        """
        Generate weekly report for the specified week
        
        Args:
            week_start_date: Monday of the week (datetime)
        
        Returns:
            str: Markdown content of the weekly report
        """
        week_end_date = week_start_date + timedelta(days=6)
        
        # Collect data
        daily_reports = self.data_collector.get_daily_reports(week_start_date, week_end_date)
        tips = self.data_collector.get_tips(week_start_date, week_end_date)
        todos = self.data_collector.get_todos(week_start_date, week_end_date)
        activities = self.data_collector.get_activities(week_start_date, week_end_date)
        
        # Generate Markdown content
        markdown_content = self._build_markdown(
            week_start_date, week_end_date,
            daily_reports, tips, todos, activities
        )
        
        return markdown_content
    
    def _build_markdown(self, start_date, end_date, daily_reports, tips, todos, activities):
        """Build Markdown content"""
        pass
    
    def save_report(self, markdown_content, week_start_date):
        """Save report to ReplyDocuments/"""
        filename = f"weekly_report_{week_start_date.strftime('%Y%m%d')}.md"
        filepath = Path(__file__).parent.parent / "ReplyDocuments" / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        return filepath
```

### 4.3 邮件发送 (email_sender.py)
```python
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import markdown2
from pathlib import Path
import os
from dotenv import load_dotenv

class EmailSender:
    """Send weekly report via Gmail"""
    
    def __init__(self):
        # Load email config from MailAPI/.env
        mailapi_env = Path(__file__).parent.parent.parent / "MailAPI/config/.env"
        load_dotenv(mailapi_env)
        
        self.sender_email = os.getenv("EMAIL_ADDRESS")
        self.sender_password = os.getenv("EMAIL_PASSWORD")
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
    
    def send_weekly_report(self, report_filepath, recipient_email):
        """
        Send weekly report email
        
        Args:
            report_filepath: Path to the Markdown report file
            recipient_email: Recipient's email address
        """
        # Read Markdown content
        with open(report_filepath, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        # Convert Markdown to HTML
        html_content = markdown2.markdown(markdown_content, extras=["tables", "fenced-code-blocks"])
        
        # Create email message
        msg = MIMEMultipart('alternative')
        msg['From'] = self.sender_email
        msg['To'] = recipient_email
        msg['Subject'] = f"Weekly Report - Week of {report_filepath.stem.split('_')[-1]}"
        
        # Attach HTML content
        msg.attach(MIMEText(html_content, 'html'))
        
        # Attach Markdown file
        with open(report_filepath, 'rb') as f:
            attachment = MIMEBase('application', 'octet-stream')
            attachment.set_payload(f.read())
            encoders.encode_base64(attachment)
            attachment.add_header('Content-Disposition', f'attachment; filename={report_filepath.name}')
            msg.attach(attachment)
        
        # Send email
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.send_message(msg)
```

### 4.4 定时任务 (scheduler.py)
```python
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
import logging

class WeeklyReportScheduler:
    """Schedule weekly report generation and email sending"""
    
    def __init__(self, report_generator, email_sender):
        self.scheduler = BlockingScheduler()
        self.report_generator = report_generator
        self.email_sender = email_sender
        self.logger = logging.getLogger(__name__)
    
    def generate_and_send_weekly_report(self):
        """Generate and send weekly report for next week"""
        try:
            # Calculate next Monday
            today = datetime.now()
            days_until_monday = (7 - today.weekday()) % 7
            if days_until_monday == 0:
                days_until_monday = 7
            next_monday = today + timedelta(days=days_until_monday)
            next_monday = next_monday.replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Generate report
            self.logger.info(f"Generating weekly report for week starting {next_monday.date()}")
            markdown_content = self.report_generator.generate_weekly_report(next_monday)
            report_filepath = self.report_generator.save_report(markdown_content, next_monday)
            
            # Send email
            self.logger.info("Sending weekly report email")
            recipient_email = os.getenv("EMAIL_ADDRESS")  # From MailAPI config
            self.email_sender.send_weekly_report(report_filepath, recipient_email)
            
            self.logger.info("Weekly report generated and sent successfully")
        except Exception as e:
            self.logger.error(f"Error generating/sending weekly report: {e}")
    
    def start(self):
        """Start the scheduler"""
        # Schedule weekly report generation: Every Sunday at 20:00
        self.scheduler.add_job(
            self.generate_and_send_weekly_report,
            CronTrigger(day_of_week='sun', hour=20, minute=0),
            id='weekly_report_job'
        )
        
        self.logger.info("Scheduler started. Waiting for scheduled tasks...")
        self.scheduler.start()
```

## 5. 配置文件

### config/config.yaml
```yaml
# Weekly Report System Configuration

data_collection:
  minecontext_db_path: "~/Library/Application Support/MineContext/Data/minecontext.db"
  sync_interval: 3600  # seconds

report_generation:
  output_dir: "ReplyDocuments"
  format: "markdown"
  include_sections:
    - daily_summaries
    - todos
    - tips
    - activities
    - next_week_plan

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
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "logs/reply.log"
```

### config/.env.example
```env
# This file is automatically read from ../MailAPI/config/.env
# No need to duplicate configuration

# Optionally override recipient email
# RECIPIENT_EMAIL=student@example.com
```

## 6. 主程序 (main.py)
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import sys
from pathlib import Path
import argparse

from src.data_collector import MineContextDataCollector
from src.report_generator import WeeklyReportGenerator
from src.email_sender import EmailSender
from src.scheduler import WeeklyReportScheduler
from src.utils import setup_logging, load_config

def main():
    """Main entry point for Weekly Report System"""
    parser = argparse.ArgumentParser(description="Weekly Report System")
    parser.add_argument('--mode', choices=['daemon', 'once'], default='daemon',
                       help='Run mode: daemon (scheduled) or once (generate and send immediately)')
    parser.add_argument('--config', default='config/config.yaml',
                       help='Path to configuration file')
    args = parser.parse_args()
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("="*60)
    logger.info("Weekly Report System Starting")
    logger.info("="*60)
    
    try:
        # Load configuration
        config = load_config(args.config)
        
        # Initialize components
        data_collector = MineContextDataCollector()
        report_generator = WeeklyReportGenerator(data_collector)
        email_sender = EmailSender()
        
        if args.mode == 'once':
            # Generate and send report immediately
            logger.info("Running in 'once' mode - generating report now")
            scheduler = WeeklyReportScheduler(report_generator, email_sender)
            scheduler.generate_and_send_weekly_report()
            logger.info("Report generated and sent successfully")
        else:
            # Run as daemon with scheduler
            logger.info("Running in 'daemon' mode - starting scheduler")
            scheduler = WeeklyReportScheduler(report_generator, email_sender)
            scheduler.start()
    
    except KeyboardInterrupt:
        logger.info("\nShutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

---

# Implementation Steps（实施步骤）

## Phase 1: 项目初始化
1. 创建项目结构
2. 生成 `requirements.txt`
3. 创建配置文件 (`config.yaml`, `.env.example`)
4. 设置日志系统

## Phase 2: 数据收集模块
1. 实现 `MineContextDataCollector`
2. 测试从 MineContext 数据库读取数据
3. 处理日期范围和数据过滤

## Phase 3: 周报生成模块
1. 实现 `WeeklyReportGenerator`
2. 设计 Markdown 模板
3. 生成测试周报
4. 保存到 `ReplyDocuments/`

## Phase 4: 邮件发送模块
1. 实现 `EmailSender`
2. 测试 Gmail SMTP 连接
3. 实现 Markdown 到 HTML 转换
4. 测试发送邮件功能

## Phase 5: 定时任务模块
1. 实现 `WeeklyReportScheduler`
2. 配置定时任务（每周日 20:00）
3. 测试定时任务执行

## Phase 6: 集成测试
1. 端到端测试
2. 错误处理和日志记录
3. 性能优化
4. 编写 README.md

---

# Error Handling（错误处理）

1. **数据库连接失败**
   - 检查 MineContext 是否安装和运行
   - 验证数据库路径是否正确
   - 记录错误日志

2. **邮件发送失败**
   - 重试机制（最多 3 次）
   - 检查网络连接
   - 验证 Gmail 凭据

3. **周报生成失败**
   - 记录失败原因
   - 保留部分生成的内容
   - 发送通知邮件

4. **数据为空**
   - 检查日期范围
   - 生成空报告提示
   - 记录警告日志

---

# Testing（测试）

## 单元测试
1. 测试数据收集函数
2. 测试周报生成逻辑
3. 测试邮件发送功能

## 集成测试
1. 端到端流程测试
2. 模拟定时任务执行

## 手动测试命令
```bash
# 立即生成和发送周报
python3 main.py --mode once

# 启动守护进程（定时任务模式）
python3 main.py --mode daemon
```

---

# Success Criteria（成功标准）

1. ✅ 能够从 MineContext 数据库成功读取数据
2. ✅ 生成结构化的 Markdown 周报文档
3. ✅ 周报文件正确保存到 `ReplyDocuments/`
4. ✅ 能够通过 Gmail 发送 HTML 格式邮件
5. ✅ 定时任务每周日自动执行
6. ✅ 错误处理和日志记录完善
7. ✅ 代码模块化、可维护、有注释

---

# Deliverables（交付物）

1. 完整的 Python 项目代码
2. `requirements.txt` 文件
3. 配置文件（`config.yaml`, `.env.example`）
4. README.md（包含安装、配置、使用说明）
5. 示例周报文档
6. 测试脚本

---

# Additional Notes（附加说明）

## 与其他模块的集成

### MailAPI 集成
- 读取 `MailAPI/config/.env` 获取 Gmail 凭据
- 使用相同的邮件账户发送周报

### MineContext 集成
- 直接访问 `~/Library/Application Support/MineContext/Data/minecontext.db`
- 只读模式，不修改数据库
- 支持实时同步最新数据

## 未来扩展
1. 支持多个收件人
2. 自定义周报模板
3. 添加图表和可视化
4. 支持 PDF 导出
5. Web 界面管理后台

