# 更新计划

## 目标

为 Telegram Bot 增加 `/chat` 功能，让单人私聊用户可以和 GPT 进行带上下文的持续对话。

## 第一阶段：最小可用聊天

1. 新增 `/chat` 命令，用于开启聊天模式。
2. 开启聊天模式后，用户发送普通文本即进入 GPT 对话流程。
3. 会话上下文保存到 PostgreSQL。
4. 会话有效期为 1 小时，超过 1 小时无消息后自动开启新会话。
5. OpenAI 调用失败时，用户只收到简短失败提示，详细错误写入数据库日志。
6. AI 回复保存到 PostgreSQL，并发送给 Telegram 用户。
7. Telegram 长回复需要分段发送。

## 第一阶段建议新增模块

- `app/bot/handlers/chat.py`: 处理 `/chat` 命令和聊天文本消息。
- `app/services/chat_service.py`: 封装 OpenAI 调用和上下文组装。
- `app/storage/models.py`: 定义聊天会话、消息、请求记录、日志表模型。
- `app/storage/repositories/`: 封装数据库读写逻辑。
- 数据库迁移目录：用于创建和升级 PostgreSQL 表结构。

## 第一阶段建议新增配置

- `OPENAI_API_KEY`: OpenAI API Key。
- `OPENAI_MODEL`: 默认聊天模型。
- `CHAT_SESSION_TTL_SECONDS`: 会话有效期，默认 3600。
- `CHAT_CONTEXT_MESSAGE_LIMIT`: 每次请求携带的最近消息数量，默认 20。
- `CHAT_MAX_INPUT_CHARS`: 单条用户输入最大字符数。

## 后续阶段

1. 增加 `/chat_reset`，清空当前会话并重新开始。
2. 增加 `/chat_end`，主动结束聊天模式。
3. 增加用户级限流和每日用量限制。
4. 记录 token 用量、模型、耗时、OpenAI request id。
5. 引入 Redis lock，避免同一用户连续发送多条消息导致上下文乱序。
6. 后续如有长耗时任务，再设计后台处理机制，避免长请求阻塞 bot update 处理。
7. 支持历史摘要，降低长会话上下文成本。
8. 支持群聊触发规则和权限控制。
