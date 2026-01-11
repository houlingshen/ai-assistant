# MailAPI 快速开始指南

## 快速设置（5分钟）

### 步骤 1: 安装依赖

```bash
cd MailAPI
pip install -r requirements.txt
```

### 步骤 2: 配置邮箱

```bash
# 复制配置模板
cp config/.env.example config/.env

# 编辑配置文件
nano config/.env  # 或使用其他编辑器
```

填写以下信息：
```
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_PROVIDER=gmail
```

### 步骤 3: 运行测试

```bash
# 获取最近7天的邮件
python main.py --days 7
```

## 常用命令速查

```bash
# 基础查询
python main.py --days 7                    # 最近7天
python main.py --from teacher@school.edu   # 特定发件人
python main.py --subject "作业"             # 包含关键词

# 高级查询
python main.py --days 30 --subject "作业" "考试"  # 组合条件
python main.py --start-date 2024-01-01 --end-date 2024-01-31  # 日期范围

# 输出选项
python main.py --days 7 --format json      # JSON格式输出
python main.py --days 7 --log-level DEBUG  # 调试模式
```

## 获取应用专用密码

### Gmail
1. 访问: https://myaccount.google.com/security
2. 启用两步验证
3. 生成应用专用密码
4. 将密码填入 `.env` 文件

### QQ邮箱
1. 登录QQ邮箱
2. 设置 → 账户 → POP3/IMAP/SMTP
3. 开启IMAP服务
4. 生成授权码
5. 使用授权码作为密码

### Outlook
1. 访问: https://account.microsoft.com/security
2. 启用两步验证
3. 生成应用密码
4. 使用该密码

## 检查安装

```bash
# 检查Python版本（需要3.10+）
python --version

# 检查依赖安装
pip list | grep -E "PyPDF2|python-docx|PyYAML"

# 测试配置
python -c "from src.utils import load_env_credentials; print(load_env_credentials())"
```

## 故障排查

### 问题: 认证失败
```bash
# 检查配置
cat config/.env

# 确保使用应用专用密码，不是账号密码
```

### 问题: 找不到模块
```bash
# 重新安装依赖
pip install -r requirements.txt --force-reinstall
```

### 问题: 权限错误
```bash
# 创建必要的目录
mkdir -p SavedDocuments/attachments
chmod 755 SavedDocuments
```

## 下一步

1. 查看生成的文档: `ls SavedDocuments/`
2. 阅读完整文档: `README.md`
3. 查看日志: `cat mailapi.log`

## 帮助

```bash
# 查看所有命令选项
python main.py --help
```
