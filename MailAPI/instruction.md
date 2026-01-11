# Background（背景）
当前项目 ai-assistant 是一个帮助学生从邮件中整理并规划日程安排及信息的智能执行系统。

我们目前位于 `ai-assistant/MailAPI` 目录下。

现在的任务是读取用户所指定的某一类或几类邮件及其附件，并将其转化为文档保存在 `ai-assistant/MailAPI/SavedDocuments` 中，便于后续读取和处理。

# Role（角色）
 你是一位精通python的参加ai创新大赛的大学生

# Goals（目标）

## 核心功能

1. **邮件连接与认证**
   - 支持多种邮件协议（IMAP/POP3）
   - 安全的身份验证机制
   - 支持主流邮箱服务（Gmail, Outlook, QQ邮箱等）

2. **邮件检索与过滤**
   - 按发件人筛选邮件
   - 按主题关键词筛选邮件
   - 按日期范围筛选邮件
   - 按标签/文件夹筛选邮件
   - 支持组合条件查询

3. **邮件内容提取**
   - 提取邮件主题（Subject）
   - 提取发件人信息（From）
   - 提取收件人信息（To, Cc, Bcc）
   - 提取邮件正文（纯文本和HTML格式）
   - 提取邮件发送/接收时间
   - 识别并提取日程安排信息（时间、地点、事项）

4. **附件处理**
   - 识别所有附件类型
   - 下载并保存附件到指定目录
   - 支持常见文档格式（PDF, DOCX, XLSX, TXT等）
   - 支持图片格式（JPG, PNG, GIF等）
   - 附件内容文本提取（OCR for images, text extraction for documents）

5. **文档生成与保存**
   - 为每封邮件生成结构化文档
   - 文档格式：Markdown 或 JSON
   - 文件命名规则：`{date}_{sender}_{subject}.md` 或 `.json`
   - 保存到 `SavedDocuments/` 目录
   - 附件保存到 `SavedDocuments/attachments/{email_id}/`

6. **日程信息提取与结构化**
   - 使用 NLP 识别时间表达（如："明天下午3点"、"2024年1月15日"）
   - 提取会议/活动标题
   - 提取地点信息
   - 提取参与者信息
   - 生成日历事件格式（iCalendar .ics 文件）

# Technical Requirements（技术要求）

## 必需的 Python 库

```python
# 邮件处理
imaplib          # IMAP 协议
poplib           # POP3 协议
email            # 邮件解析
smtplib          # 邮件发送（可选）

# 附件和文档处理
PyPDF2           # PDF 文件处理
python-docx      # Word 文档处理
openpyxl         # Excel 文件处理
Pillow           # 图片处理
pytesseract      # OCR 文字识别

# 日期和时间处理
dateutil         # 智能日期解析
pytz             # 时区处理

# NLP 和文本处理
re               # 正则表达式
nltk             # 自然语言处理（可选）
spacy            # 高级 NLP（可选）

# 文件和路径
os, pathlib      # 文件系统操作
shutil           # 文件复制和移动

# 数据处理
json             # JSON 格式处理
pyyaml           # YAML 配置文件
pandas           # 数据结构（可选）

# 配置和安全
python-dotenv    # 环境变量管理
keyring          # 安全凭证存储
```

## 项目结构

```
MailAPI/
├── instruction.md           # 本文件
├── config/
│   ├── email_config.yaml   # 邮箱配置
│   └── .env                # 敏感信息（不提交到git）
├── src/
│   ├── __init__.py
│   ├── mail_client.py      # 邮件客户端
│   ├── mail_parser.py      # 邮件解析器
│   ├── attachment_handler.py # 附件处理
│   ├── schedule_extractor.py # 日程提取
│   ├── document_generator.py # 文档生成
│   └── utils.py            # 工具函数
├── SavedDocuments/          # 保存的文档
│   └── attachments/        # 附件存储
├── tests/
│   └── test_*.py           # 单元测试
├── main.py                  # 主程序入口
├── requirements.txt         # 依赖列表
└── README.md               # 使用说明
```

# Implementation Steps（实现步骤）

## Phase 1: 基础邮件连接（必须实现）

1. 创建 `mail_client.py`
   - 实现 `MailClient` 类
   - 支持 IMAP 连接
   - 实现登录/登出功能
   - 错误处理和重连机制

2. 创建配置文件
   - `email_config.yaml`: 邮箱服务器配置
   - `.env`: 存储邮箱账号密码（使用环境变量）

## Phase 2: 邮件检索与解析（必须实现）

1. 创建 `mail_parser.py`
   - 实现邮件搜索功能（按条件筛选）
   - 解析邮件头信息
   - 提取邮件正文（支持纯文本和HTML）
   - 识别邮件中的附件

2. 实现过滤器
   - 按发件人过滤
   - 按主题关键词过滤
   - 按日期范围过滤

## Phase 3: 附件处理（必须实现）

1. 创建 `attachment_handler.py`
   - 下载附件到本地
   - 按邮件ID组织附件目录
   - 提取附件元数据（文件名、大小、类型）
   - 文本提取功能（PDF、Word、Excel）

## Phase 4: 日程信息提取（核心功能）

1. 创建 `schedule_extractor.py`
   - 使用正则表达式识别时间表达
   - 提取日期和时间信息
   - 识别地点关键词
   - 提取事件描述
   - 生成结构化日程数据

2. 支持多种时间格式
   - 绝对时间："2024年1月15日下午3点"
   - 相对时间："明天下午"、"下周一"
   - 时间范围："3点到5点"、"全天"

## Phase 5: 文档生成（必须实现）

1. 创建 `document_generator.py`
   - 生成 Markdown 格式文档
   - 包含邮件基本信息
   - 包含提取的日程信息
   - 包含附件列表和链接
   - 生成文件名和保存路径

2. 文档模板示例
```markdown
# 邮件信息

- **主题**: {subject}
- **发件人**: {sender}
- **收件人**: {recipients}
- **日期**: {date}
- **邮件ID**: {message_id}

## 正文内容

{body_content}

## 提取的日程安排

### 事件 1
- **标题**: 项目会议
- **时间**: 2024-01-15 15:00-17:00
- **地点**: 会议室A
- **参与者**: 张三, 李四

## 附件列表

1. [项目计划.pdf](./attachments/{email_id}/项目计划.pdf)
2. [数据表格.xlsx](./attachments/{email_id}/数据表格.xlsx)
```

## Phase 6: 主程序和CLI（必须实现）

1. 创建 `main.py`
   - 命令行参数解析
   - 执行流程控制
   - 日志记录
   - 进度显示

2. 支持的命令
```bash
# 检索最近7天的所有邮件
python main.py --days 7

# 按发件人检索
python main.py --from "teacher@school.edu"

# 按主题关键词检索
python main.py --subject "作业" "考试"

# 按日期范围检索
python main.py --start-date "2024-01-01" --end-date "2024-01-31"

# 组合条件
python main.py --from "teacher@school.edu" --days 7 --subject "作业"
```

# Output Format（输出格式）

## JSON 格式示例

```json
{
  "email_id": "<message-id@mail.server>",
  "subject": "关于下周项目会议的通知",
  "from": {
    "name": "张老师",
    "email": "teacher@school.edu"
  },
  "to": ["student@school.edu"],
  "date": "2024-01-10T10:30:00+08:00",
  "body": {
    "text": "邮件正文...",
    "html": "<html>...</html>"
  },
  "schedules": [
    {
      "title": "项目会议",
      "start_time": "2024-01-15T15:00:00+08:00",
      "end_time": "2024-01-15T17:00:00+08:00",
      "location": "会议室A",
      "participants": ["张三", "李四"],
      "description": "讨论项目进展"
    }
  ],
  "attachments": [
    {
      "filename": "项目计划.pdf",
      "filepath": "./attachments/msg001/项目计划.pdf",
      "size": 1024000,
      "type": "application/pdf"
    }
  ],
  "saved_at": "2024-01-10T11:00:00+08:00"
}
```

# Error Handling（错误处理）

1. **网络错误**: 自动重试机制（最多3次）
2. **认证失败**: 提示用户检查凭证
3. **邮件解析失败**: 记录日志，跳过该邮件继续处理
4. **附件下载失败**: 记录错误，保存邮件信息但标注附件缺失
5. **文件写入失败**: 检查目录权限，提示用户

# Security Considerations（安全考虑）

1. 不要在代码中硬编码密码
2. 使用 `.env` 文件存储敏感信息
3. `.env` 文件必须加入 `.gitignore`
4. 考虑使用应用专用密码（App Password）
5. 支持 OAuth2 认证（可选，用于 Gmail）

# Testing Requirements（测试要求）

1. 单元测试覆盖核心功能
2. 测试数据使用示例邮件
3. Mock 邮件服务器进行测试
4. 测试各种边界情况和异常

# Success Criteria（成功标准）

- [ ] 能成功连接到邮箱服务器
- [ ] 能按照指定条件检索邮件
- [ ] 能正确解析邮件内容和附件
- [ ] 能提取日程安排信息
- [ ] 能生成格式规范的文档
- [ ] 所有文档正确保存到 SavedDocuments 目录
- [ ] 附件正确保存到对应子目录
- [ ] 错误处理完善，程序稳定运行
- [ ] 代码注释完整，易于维护
- [ ] 提供清晰的使用文档

# Deliverables（交付物）

1. 完整的 Python 代码实现
2. `requirements.txt` 文件
3. 配置文件模板
4. README.md 使用说明
5. 至少3个测试用例
6. 运行演示视频或截图（可选）

# Timeline Suggestion（时间建议）

- Day 1-2: Phase 1 & 2（邮件连接和解析）
- Day 3-4: Phase 3 & 4（附件处理和日程提取）
- Day 5: Phase 5（文档生成）
- Day 6: Phase 6（主程序和CLI）
- Day 7: 测试、文档和优化

# Additional Features（附加功能，可选）

1. Web UI 界面
2. 数据库存储邮件索引
3. 全文搜索功能
4. 邮件分类和标签
5. 自动回复功能
6. 日程冲突检测
7. 日历集成（导出 .ics 文件）
8. 邮件摘要生成（使用 AI）
9. 多语言支持
10. 邮件模板功能