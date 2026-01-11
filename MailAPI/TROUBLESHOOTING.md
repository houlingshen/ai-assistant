# MailAPI 故障排查指南

## 问题: 邮件没有保存到 SavedDocuments 文件夹

### 原因分析

根据日志显示，程序运行但无法连接到邮箱服务器：

```
ERROR - IMAP error: BasicAuthBlocked
LOGIN failed
```

**根本原因**: Microsoft Outlook 已经禁用了基本身份验证（Basic Authentication），需要使用应用专用密码。

---

## 解决方案

### 方案 1: 为 Outlook 生成应用专用密码（推荐）

#### 步骤：

1. **访问 Microsoft 账户安全页面**
   - 打开: https://account.microsoft.com/security
   - 登录您的 Outlook 账号

2. **启用两步验证（如果未启用）**
   - 点击 "高级安全选项"
   - 启用 "两步验证"
   - 按照提示完成设置

3. **生成应用密码**
   - 在安全页面，找到 "应用密码" 部分
   - 点击 "创建新的应用密码"
   - 选择 "邮件" 作为应用类型
   - 复制生成的密码（16位字符，类似: `abcd-efgh-ijkl-mnop`）

4. **更新配置文件**
   - 打开 `config/.env` 文件
   - 将 `EMAIL_PASSWORD` 改为应用专用密码：
   
   ```env
   EMAIL_ADDRESS=TestingHollynLaura@outlook.com
   EMAIL_PASSWORD=abcd-efgh-ijkl-mnop
   EMAIL_PROVIDER=outlook
   ```

5. **重新运行程序**
   ```bash
   python3 main.py --days 7
   ```

---

### 方案 2: 使用 Gmail（如果有Gmail账号）

Gmail 对 IMAP 访问的支持更好：

1. **启用 Gmail IMAP**
   - 登录 Gmail
   - 设置 → 查看所有设置 → 转发和 POP/IMAP
   - 启用 IMAP

2. **生成应用专用密码**
   - 访问: https://myaccount.google.com/security
   - 启用两步验证
   - 生成应用密码（选择"邮件"和"其他设备"）

3. **更新配置**
   ```env
   EMAIL_ADDRESS=your_gmail@gmail.com
   EMAIL_PASSWORD=your_app_password
   EMAIL_PROVIDER=gmail
   ```

---

### 方案 3: 使用 QQ 邮箱

QQ邮箱仍然支持 IMAP 基本认证：

1. **开启 IMAP 服务**
   - 登录 QQ 邮箱
   - 设置 → 账户 → POP3/IMAP/SMTP/Exchange
   - 开启 IMAP/SMTP 服务

2. **生成授权码**
   - 在同一页面生成授权码
   - 这个授权码就是您的 EMAIL_PASSWORD

3. **更新配置**
   ```env
   EMAIL_ADDRESS=your_qq@qq.com
   EMAIL_PASSWORD=your_authorization_code
   EMAIL_PROVIDER=qq
   ```

---

## 验证配置

### 快速测试连接

运行以下命令测试邮箱连接：

```bash
python3 -c "
from src.mail_client import MailClient
client = MailClient()
if client.connect():
    print('✅ 连接成功！')
    client.disconnect()
else:
    print('❌ 连接失败，请检查配置')
"
```

### 测试完整流程

```bash
# 获取最近7天的邮件
python3 main.py --days 7

# 检查是否生成了文档
ls -lh SavedDocuments/
```

---

## 常见错误和解决方法

### 错误 1: `Authentication failed`

**原因**: 密码错误或未使用应用专用密码

**解决**:
- 确认使用应用专用密码，不是账号密码
- 重新生成应用密码
- 检查 `.env` 文件中没有多余的空格

### 错误 2: `Connection timeout`

**原因**: 网络问题或防火墙阻止

**解决**:
- 检查网络连接
- 尝试关闭 VPN
- 检查防火墙设置

### 错误 3: `IMAP not enabled`

**原因**: 邮箱未开启 IMAP 服务

**解决**:
- 登录邮箱网页版
- 在设置中启用 IMAP
- Gmail: 设置 → 转发和 POP/IMAP
- Outlook: 设置 → 邮件 → 同步电子邮件

### 错误 4: `Permission denied` 写入文件失败

**原因**: SavedDocuments 目录无写入权限

**解决**:
```bash
chmod 755 SavedDocuments
chmod 755 SavedDocuments/attachments
```

---

## 调试技巧

### 1. 启用详细日志

```bash
python3 main.py --days 7 --log-level DEBUG
```

### 2. 查看日志文件

```bash
tail -f mailapi.log
```

### 3. 测试单个模块

```python
# 测试邮件解析
from src.mail_parser import MailParser
parser = MailParser()
criteria = parser.build_search_criteria(days_back=7)
print(f"搜索条件: {criteria}")
```

---

## 成功标志

当程序成功运行时，您应该看到：

```
✅ 连接成功并认证
✅ 搜索到 X 封邮件
✅ 处理邮件 1/X
✅ 生成文档: SavedDocuments/20240109_sender_subject.md
✅ 生成摘要报告
```

并且 `SavedDocuments/` 目录中会有新生成的文件：

```bash
$ ls SavedDocuments/
20240109_143022_teacher_关于作业的通知.md
20240109_150133_admin_会议通知.md
summary_20240109_151000.md
attachments/
```

---

## 获取帮助

如果以上方法都无法解决问题：

1. 检查完整的错误日志: `cat mailapi.log`
2. 确认 Python 版本 ≥ 3.10: `python3 --version`
3. 确认依赖已安装: `pip3 list | grep -E "PyPDF2|PyYAML"`
4. 查看 README.md 了解更多信息

---

## 下一步

配置成功后，您可以：

1. **浏览生成的文档**
   ```bash
   cat SavedDocuments/*.md
   ```

2. **尝试其他查询条件**
   ```bash
   python3 main.py --from teacher@school.edu
   python3 main.py --subject "作业" "考试"
   ```

3. **生成 JSON 格式**
   ```bash
   python3 main.py --days 7 --format json
   ```

---

**最后更新**: 2026-01-09
