CREATE TABLE IF NOT EXISTS chat_sessions (
    id SERIAL PRIMARY KEY,
    chat_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    status VARCHAR(16) NOT NULL DEFAULT 'active',
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_message_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at TIMESTAMPTZ NULL
);

CREATE INDEX IF NOT EXISTS idx_chat_sessions_chat_user_status
    ON chat_sessions (chat_id, user_id, status);

CREATE TABLE IF NOT EXISTS chat_messages (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role VARCHAR(16) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id
    ON chat_messages (session_id);

CREATE TABLE IF NOT EXISTS chat_requests (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    user_id BIGINT NOT NULL,
    model VARCHAR(64) NOT NULL,
    status VARCHAR(16) NOT NULL DEFAULT 'processing',
    request_text TEXT NOT NULL,
    response_text TEXT NULL,
    error_type VARCHAR(128) NULL,
    error_message TEXT NULL,
    openai_request_id VARCHAR(128) NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ NULL
);

CREATE INDEX IF NOT EXISTS idx_chat_requests_session_id
    ON chat_requests (session_id);

CREATE TABLE IF NOT EXISTS chat_error_logs (
    id SERIAL PRIMARY KEY,
    request_id INTEGER NULL REFERENCES chat_requests(id) ON DELETE SET NULL,
    session_id INTEGER NULL REFERENCES chat_sessions(id) ON DELETE SET NULL,
    user_id BIGINT NULL,
    event_name VARCHAR(64) NOT NULL,
    error_type VARCHAR(128) NOT NULL,
    error_message TEXT NOT NULL,
    context TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_chat_error_logs_session_id
    ON chat_error_logs (session_id);
