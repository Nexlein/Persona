-- ─── USERS ───
-- Verified users. Uses soft-delete (deleted_at) for GDPR compliance.
CREATE TABLE users (
    id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email              VARCHAR(255) UNIQUE NOT NULL,
    interests          TEXT ARRAY DEFAULT '{}',
    schedule_hour      INT DEFAULT 8 CHECK (schedule_hour BETWEEN 0 AND 23),
    schedule_timezone  VARCHAR(64) DEFAULT 'Europe/Paris',
    custom_prompt      TEXT,
    consent_given_at   TIMESTAMPTZ,         -- GDPR: consent timestamp
    created_at         TIMESTAMPTZ DEFAULT now(),
    updated_at         TIMESTAMPTZ DEFAULT now(),
    password_hash      VARCHAR(64),          -- SHA-256 hex of password
    deleted_at         TIMESTAMPTZ          -- soft delete (GDPR-friendly)
);

CREATE INDEX idx_users_email_active
    ON users(email) WHERE deleted_at IS NULL;

CREATE INDEX idx_users_schedule
    ON users(schedule_hour) WHERE deleted_at IS NULL;


-- ─── CHAT_SESSIONS ───
-- Links an N8N Chat Trigger sessionId to an authenticated user.
-- Core auth table: no entry here means the user is not connected.
CREATE TABLE chat_sessions (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id        VARCHAR(128) NOT NULL UNIQUE,
    user_id           UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    authenticated_at  TIMESTAMPTZ DEFAULT now(),
    last_activity     TIMESTAMPTZ DEFAULT now(),
    expires_at        TIMESTAMPTZ NOT NULL DEFAULT (now() + INTERVAL '7 days')
);

CREATE INDEX idx_sessions_user ON chat_sessions(user_id);
CREATE INDEX idx_sessions_expires ON chat_sessions(expires_at);


-- Enable Row Level Security (RLS) on all tables.
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_sessions ENABLE ROW LEVEL SECURITY;


-- ─── VIEWS & FUNCTIONS FOR N8N SCHEDULER ───

-- View to retrieve active users scheduled for the current hour in their timezone
CREATE OR REPLACE VIEW users_to_schedule AS
SELECT id, email, interests, schedule_hour, schedule_timezone
FROM users
WHERE deleted_at IS NULL
  AND interests IS NOT NULL
  AND array_length(interests, 1) > 0
  AND schedule_hour = EXTRACT(HOUR FROM NOW() AT TIME ZONE schedule_timezone)::int;
