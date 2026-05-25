# 当前已实现功能

本文档记录项目当前已经实现并保留的功能。

## Telegram 命令

### `/start`

返回基础欢迎文案。

当前展示的可用命令：

```text
/start - 查看基础说明
/chat - 开启对话
```

欢迎语会根据北京时间自动变化：

- 05:00-11:59: 上午好
- 12:00-17:59: 下午好
- 18:00-04:59: 夜深了，注意休息

### `/chat`

在 Telegram 私聊中开启 GPT 对话模式。

限制：

- 只允许在私聊中使用。
- 群聊中使用会提示用户去私聊。
- 无法识别用户时会返回简短错误提示。

开启后，用户在私聊中发送普通文本，会进入 GPT 对话流程。

## GPT 对话

项目通过 OpenAI Responses API 调用配置的模型。

相关配置：

- `OPENAI_API_KEY`: OpenAI API Key
- `OPENAI_MODEL`: 使用的模型，默认 `gpt-4.1-mini`
- `CHAT_SESSION_TTL_SECONDS`: 会话无消息过期时间，默认 3600 秒
- `CHAT_CONTEXT_MESSAGE_LIMIT`: 每次请求携带的最近消息数量，默认 20
- `CHAT_MAX_INPUT_CHARS`: 单条用户输入最大字符数，默认 4000

处理流程：

1. 获取或创建当前用户的活跃聊天会话。
2. 如果会话超过 TTL 未更新，则关闭旧会话并创建新会话。
3. 截断过长输入，保存用户消息。
4. 创建一条请求记录。
5. 读取最近上下文消息并请求 OpenAI。
6. 保存助手回复。
7. 标记请求成功并记录 OpenAI request id。
8. 如果回复超过 Telegram 单条消息限制，会自动拆分发送。

## 数据库存储

PostgreSQL 用于保存聊天相关数据。

当前表：

- `chat_sessions`: 聊天会话
- `chat_messages`: 用户和助手消息
- `chat_requests`: 每次模型请求记录
- `chat_error_logs`: 模型调用失败等错误记录

数据库迁移入口：

```powershell
wsl.exe -d Ubuntu-24.04 -- bash -lc "cd /mnt/c/Users/altscherzxu/Desktop/telegram_bot && .venv-wsl/bin/python -m app.storage.migrate"
```

SQL 文件位置：

- `migrations/001_chat_tables.sql`: 程序迁移实际读取的 SQL
- `sql/chat_tables.sql`: 当前表结构的归档副本

## 错误处理

用户侧错误提示保持简短。

OpenAI 调用失败时：

- 用户收到：`抱歉，当前无法回复。`
- 请求记录会标记为 `failed`
- 错误类型、错误信息、上下文片段会写入 `chat_error_logs`
- Python 日志会记录异常堆栈，便于排查

## 配置加载

配置通过环境变量或 `.env` 文件读取。

读取顺序：

```python
.env
```

## 启动与维护

项目当前只需要启动 bot 进程。

一键重启脚本：

```powershell
powershell -ExecutionPolicy Bypass -File .\Docs\restart-wsl.ps1
```

脚本会：

1. 停止旧 bot 进程。
2. 确认 PostgreSQL 可用。
3. 执行数据库迁移。
4. 后台启动 bot。
5. 打印当前 bot 进程。

