# MailAPI - Email Processing System

一个智能邮件处理系统，用于帮助学生从邮件中整理并规划日程安排及信息。

## 功能特性

- ✅ **邮件连接与认证** - 支持多种邮箱服务（Gmail, Outlook, QQ邮箱等）
- ✅ **邮件检索与过滤** - 按发件人、主题、日期范围等条件筛选邮件
- ✅ **邮件内容提取** - 提取主题、正文、发件人、收件人等信息
- ✅ **附件处理** - 自动下载并保存附件，支持PDF、Word、Excel等格式
- ✅ **日程信息提取** - 智能识别邮件中的时间、地点、事件信息
- ✅ **文档生成** - 自动生成Markdown或JSON格式的结构化文档

## 项目结构

```
MailAPI/
├── config/              # 配置文件目录
│   ├── email_config.yaml   # 邮箱服务器配置
│   └── .env.example        # 环境变量模板
├── src/                 # 源代码目录
│   ├── mail_client.py      # 邮件客户端
│   ├── mail_parser.py      # 邮件解析器
│   ├── attachment_handler.py # 附件处理器
│   ├── schedule_extractor.py # 日程提取器
│   ├── document_generator.py # 文档生成器
│   └── utils.py            # 工具函数
├── SavedDocuments/      # 保存的文档目录
│   └── attachments/        # 附件存储目录
├── main.py              # 主程序入口
├── requirements.txt     # Python依赖
└── README.md           # 本文件
```

## 安装说明

### 1. 环境要求

- Python 3.10 或更高版本
- pip 包管理器

### 2. 安装依赖

```bash
cd MailAPI
pip install -r requirements.txt
```

### 3. 配置邮箱账号

复制配置模板并填写你的邮箱信息：

```bash
cp config/.env.example config/.env
```

编辑 `config/.env` 文件：

```bash
EMAIL_ADDRESS=your_email@example.com
EMAIL_PASSWORD=your_password_or_app_password
EMAIL_PROVIDER=gmail  # 可选: gmail, outlook, qq, 163
```

**重要提示**：
- 建议使用应用专用密码（App Password）而不是账号密码
- Gmail用户需要启用"允许不够安全的应用"或使用OAuth2
- QQ邮箱需要开启IMAP/SMTP服务并获取授权码

## 使用方法

### 基本用法

```bash
# 检索最近7天的所有邮件
python main.py --days 7

# 按发件人检索
python main.py --from teacher@school.edu

# 按主题关键词检索
python main.py --subject "作业" "考试"

# 按日期范围检索
python main.py --start-date 2024-01-01 --end-date 2024-01-31

# 组合多个条件
python main.py --from teacher@school.edu --days 7 --subject "作业"

# 输出JSON格式
python main.py --days 7 --format json
```

### 命令行参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `--from` | 按发件人筛选 | `--from teacher@school.edu` |
| `--subject` | 按主题关键词筛选 | `--subject "作业" "考试"` |
| `--days` | 检索最近N天的邮件 | `--days 7` |
| `--start-date` | 起始日期 | `--start-date 2024-01-01` |
| `--end-date` | 结束日期 | `--end-date 2024-01-31` |
| `--folder` | 指定邮件文件夹 | `--folder INBOX` |
| `--format` | 输出格式 | `--format json` |
| `--log-level` | 日志级别 | `--log-level DEBUG` |

## 输出说明

### Markdown格式示例

```markdown
# 邮件信息

- **主题**: 关于下周项目会议的通知
- **发件人**: 张老师 <teacher@school.edu>
- **收件人**: student@school.edu
- **日期**: 2024-01-10T10:30:00+08:00

## 正文内容

各位同学好，下周一下午3点在会议室A召开项目讨论会...

## 提取的日程安排

### 事件 1

- **标题**: 项目讨论会
- **开始时间**: 2024-01-15T15:00:00+08:00
- **结束时间**: 2024-01-15T17:00:00+08:00
- **地点**: 会议室A

## 附件列表

1. [项目计划.pdf](./attachments/msg001/项目计划.pdf)
```

### JSON格式示例

```json
{
  "email_id": "<message-id@mail.server>",
  "subject": "关于下周项目会议的通知",
  "from": {
    "name": "张老师",
    "email": "teacher@school.edu"
  },
  "schedules": [
    {
      "title": "项目讨论会",
      "start_time": "2024-01-15T15:00:00+08:00",
      "end_time": "2024-01-15T17:00:00+08:00",
      "location": "会议室A"
    }
  ]
}
```

## 文件保存规则

- **邮件文档**: `SavedDocuments/{日期}_{发件人}_{主题}.md`
- **附件**: `SavedDocuments/attachments/{邮件ID}/{附件名}`
- **摘要报告**: `SavedDocuments/summary_{时间戳}.md`

## 常见问题

### 1. 连接失败

**问题**: `Authentication failed` 或连接超时

**解决方案**:
- 检查 `.env` 文件中的邮箱地址和密码是否正确
- Gmail用户使用应用专用密码
- QQ邮箱使用授权码而不是登录密码
- 检查网络连接和防火墙设置

### 2. 找不到邮件

**问题**: 搜索结果为空

**解决方案**:
- 确认邮件确实存在于指定文件夹
- 调整搜索条件（扩大日期范围、减少关键词等）
- 尝试使用 `--folder` 参数指定其他文件夹

### 3. 附件下载失败

**问题**: 附件保存失败或为空

**解决方案**:
- 检查 `SavedDocuments/attachments` 目录的写入权限
- 确保有足够的磁盘空间
- 查看日志文件 `mailapi.log` 了解详细错误信息

### 4. 日程提取不准确

**问题**: 无法识别邮件中的时间信息

**解决方案**:
- 当前支持常见的中文时间表达
- 可以在 `schedule_extractor.py` 中自定义时间匹配规则
- 考虑使用更高级的NLP库（如spacy）提高准确率

## 开发说明

### 运行测试

```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试
python -m pytest tests/test_mail_parser.py
```

### 调试模式

```bash
python main.py --days 7 --log-level DEBUG
```

### 扩展功能

1. **添加新的邮箱提供商**: 编辑 `config/email_config.yaml`
2. **自定义时间匹配规则**: 修改 `schedule_extractor.py`
3. **添加新的文档格式**: 扩展 `document_generator.py`

## 安全建议

1. ✅ 使用应用专用密码而不是账号密码
2. ✅ 不要将 `.env` 文件提交到版本控制系统
3. ✅ 定期更换密码和授权码
4. ✅ 限制程序的文件系统访问权限
5. ✅ 在生产环境中使用 OAuth2 认证

## 许可证

Apache License 2.0

## 作者

AI Assistant Team - 为AI创新大赛开发

## 更新日志

### v1.0.0 (2024-01-06)
- ✨ 初始版本发布
- ✅ 支持IMAP邮件检索
- ✅ 智能日程信息提取
- ✅ 自动附件下载和文本提取
- ✅ Markdown和JSON文档生成

## 技术支持

遇到问题？请查看：
1. 日志文件: `mailapi.log`
2. 配置文件: `config/email_config.yaml`
3. 环境变量: `config/.env`

## 未来计划

- [ ] Web UI界面
- [ ] 数据库支持
- [ ] 邮件分类和标签
- [ ] 日历集成(.ics导出)
- [ ] 多语言支持
- [ ] OAuth2认证