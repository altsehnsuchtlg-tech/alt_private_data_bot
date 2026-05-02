# Telegram Bot Skeleton

- Python 负责路由、业务编排、队列生产/消费
- C++ 负责可替换的高性能计算模块（通过 `pybind11` 暴露给 Python）
- Redis Stream 作为异步任务队列
- PostgreSQL 作为主数据存储（当前仅保留存储层占位）

## 架构分层

- `app/bot/`: Telegram 命令路由与 handler（薄 handler）
- `app/services/`: 业务服务层（native 调用、队列封装）
- `app/workers/`: 后台任务消费
- `app/storage/`: 数据库连接与后续 repository 扩展位
- `app/infra/`: Redis 等基础设施适配
- `native/src/`: C++ 扩展源码

## 已内置命令

- `/start`: 显示说明
- `/native <text>`: 提交一个 native 评分任务
- `/job_result <job_id>`: 查询任务结果

## 快速启动（本地）

1. 准备环境变量：
   - `Copy-Item .env.example .env`
   - 把 `.env` 里的 `BOT_TOKEN` 改成真实 token
2. 启动依赖：
   - `docker compose up -d redis postgres`
3. 安装依赖并编译扩展：
   - `python -m venv .venv`
   - `.venv\Scripts\Activate.ps1`
   - `pip install -U pip`
   - `pip install -e .`
4. 启动 bot：
   - `python -m app.main`
5. 另开一个终端启动 worker：
   - `python -m app.workers.worker`

## 快速启动（Docker Compose）

1. `Copy-Item .env.example .env`
2. 修改 `.env` 里的 `BOT_TOKEN`
3. `docker compose up --build`

## 关键环境变量

- `BOT_TOKEN`: Telegram bot token
- `BOT_ADMIN_IDS`: 管理员 ID，逗号分隔（可留空）
- `REDIS_URL`: Redis 连接串
- `POSTGRES_DSN`: PostgreSQL DSN
- `JOB_RESULT_TTL_SECONDS`: job 结果在 Redis 的保留秒数
