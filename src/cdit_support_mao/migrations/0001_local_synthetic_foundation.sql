CREATE TABLE synthetic_accounts (
    account_id TEXT PRIMARY KEY CHECK(length(account_id) BETWEEN 3 AND 64),
    username TEXT NOT NULL UNIQUE COLLATE NOCASE CHECK(length(username) BETWEEN 3 AND 80),
    role TEXT NOT NULL CHECK(role IN ('user', 'staff', 'admin')),
    status TEXT NOT NULL CHECK(status IN ('setup_required', 'active', 'suspended', 'deactivated', 'removed')),
    password_hash TEXT CHECK(password_hash IS NULL OR length(password_hash) BETWEEN 32 AND 512),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    CHECK(status <> 'active' OR password_hash IS NOT NULL)
);

CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY CHECK(length(session_id) BETWEEN 8 AND 96),
    token_hash TEXT NOT NULL UNIQUE CHECK(length(token_hash) = 64),
    account_id TEXT NOT NULL REFERENCES synthetic_accounts(account_id) ON DELETE RESTRICT,
    issued_at TEXT NOT NULL,
    last_activity_at TEXT NOT NULL,
    absolute_expires_at TEXT NOT NULL,
    warned_15m INTEGER NOT NULL DEFAULT 0 CHECK(warned_15m IN (0, 1)),
    warned_5m INTEGER NOT NULL DEFAULT 0 CHECK(warned_5m IN (0, 1)),
    revoked_at TEXT,
    CHECK(absolute_expires_at > issued_at)
);
CREATE INDEX sessions_account_active_idx ON sessions(account_id, revoked_at, absolute_expires_at);

CREATE TABLE synthetic_cases (
    case_id TEXT PRIMARY KEY CHECK(length(case_id) BETWEEN 3 AND 96),
    owner_account_id TEXT NOT NULL REFERENCES synthetic_accounts(account_id) ON DELETE RESTRICT,
    parent_case_id TEXT REFERENCES synthetic_cases(case_id) ON DELETE RESTRICT,
    subject TEXT NOT NULL CHECK(length(subject) BETWEEN 1 AND 160),
    request_text TEXT NOT NULL CHECK(length(request_text) BETWEEN 1 AND 12000),
    status TEXT NOT NULL CHECK(status IN ('submitted', 'in_progress', 'waiting_on_customer', 'under_investigation', 'escalated', 'resolved', 'closed')),
    urgency_band TEXT NOT NULL DEFAULT 'unknown' CHECK(urgency_band IN ('low', 'medium', 'high', 'urgent', 'unknown')),
    is_synthetic INTEGER NOT NULL CHECK(is_synthetic = 1),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX synthetic_cases_owner_updated_idx ON synthetic_cases(owner_account_id, updated_at DESC);
CREATE INDEX synthetic_cases_status_urgency_idx ON synthetic_cases(status, urgency_band);

-- This table deliberately contains bounded metadata columns only: no ticket body,
-- attachment, credential, identity, prompt, or arbitrary JSON/text payload column.
CREATE TABLE product_health_events (
    event_id TEXT PRIMARY KEY CHECK(length(event_id) BETWEEN 3 AND 96),
    occurred_at TEXT NOT NULL,
    event_type TEXT NOT NULL CHECK(event_type IN ('database_seeded', 'database_reset', 'retention_purge', 'session_warning_15m', 'session_warning_5m', 'session_extension_requested', 'auth_denied', 'account_access_changed')),
    component TEXT NOT NULL CHECK(component IN ('database', 'auth', 'session', 'access_admin')),
    component_version TEXT NOT NULL CHECK(length(component_version) BETWEEN 1 AND 64),
    status_code TEXT NOT NULL CHECK(status_code IN ('ok', 'warning', 'blocked', 'failed')),
    error_code TEXT CHECK(error_code IS NULL OR (length(error_code) BETWEEN 1 AND 64 AND error_code NOT GLOB '*[^a-z0-9_.-]*')),
    duration_ms INTEGER CHECK(duration_ms IS NULL OR duration_ms >= 0)
);
CREATE INDEX product_health_events_retention_idx ON product_health_events(occurred_at);
CREATE INDEX product_health_events_component_time_idx ON product_health_events(component, occurred_at);

CREATE TABLE product_health_summaries (
    summary_id TEXT PRIMARY KEY CHECK(length(summary_id) BETWEEN 3 AND 96),
    window_started_at TEXT NOT NULL,
    window_ended_at TEXT NOT NULL,
    component TEXT NOT NULL CHECK(component IN ('database', 'auth', 'session', 'access_admin')),
    component_version TEXT NOT NULL CHECK(length(component_version) BETWEEN 1 AND 64),
    event_count INTEGER NOT NULL CHECK(event_count >= 0),
    failure_count INTEGER NOT NULL CHECK(failure_count >= 0 AND failure_count <= event_count),
    total_duration_ms INTEGER CHECK(total_duration_ms IS NULL OR total_duration_ms >= 0),
    CHECK(window_ended_at >= window_started_at),
    UNIQUE(window_started_at, window_ended_at, component, component_version)
);
CREATE INDEX product_health_summaries_retention_idx ON product_health_summaries(window_ended_at);

CREATE TABLE account_access_events (
    event_id TEXT PRIMARY KEY CHECK(length(event_id) BETWEEN 3 AND 96),
    actor_account_id TEXT NOT NULL REFERENCES synthetic_accounts(account_id) ON DELETE RESTRICT,
    target_account_id TEXT NOT NULL REFERENCES synthetic_accounts(account_id) ON DELETE RESTRICT,
    action TEXT NOT NULL CHECK(action IN ('grant_role', 'update_role', 'promote', 'demote', 'suspend', 'deactivate', 'remove', 'reactivate')),
    before_role TEXT CHECK(before_role IS NULL OR before_role IN ('user', 'staff', 'admin')),
    after_role TEXT CHECK(after_role IS NULL OR after_role IN ('user', 'staff', 'admin')),
    before_status TEXT CHECK(before_status IS NULL OR before_status IN ('setup_required', 'active', 'suspended', 'deactivated', 'removed')),
    after_status TEXT CHECK(after_status IS NULL OR after_status IN ('setup_required', 'active', 'suspended', 'deactivated', 'removed')),
    occurred_at TEXT NOT NULL
);
CREATE INDEX account_access_events_retention_idx ON account_access_events(occurred_at);
CREATE INDEX account_access_events_target_time_idx ON account_access_events(target_account_id, occurred_at DESC);

-- Extension is not implemented: this stores a request alert for Admin review only.
CREATE TABLE session_extension_alerts (
    alert_id TEXT PRIMARY KEY CHECK(length(alert_id) BETWEEN 3 AND 96),
    session_id TEXT NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    account_id TEXT NOT NULL REFERENCES synthetic_accounts(account_id) ON DELETE RESTRICT,
    requested_at TEXT NOT NULL,
    review_status TEXT NOT NULL DEFAULT 'new' CHECK(review_status IN ('new', 'reviewed')),
    reviewed_at TEXT
);
CREATE INDEX session_extension_alerts_review_idx ON session_extension_alerts(review_status, requested_at);
