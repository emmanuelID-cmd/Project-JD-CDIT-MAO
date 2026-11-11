ALTER TABLE synthetic_accounts ADD COLUMN auditor_access INTEGER NOT NULL DEFAULT 0
    CHECK (auditor_access IN (0, 1));

CREATE TABLE actionrelay_runs (
    run_id TEXT PRIMARY KEY,
    case_id TEXT NOT NULL REFERENCES synthetic_cases(case_id) ON DELETE CASCADE,
    case_version TEXT NOT NULL,
    actor_account_id TEXT NOT NULL REFERENCES synthetic_accounts(account_id),
    status TEXT NOT NULL CHECK (status IN ('running', 'human_review', 'blocked', 'stale')),
    started_at TEXT NOT NULL,
    completed_at TEXT,
    provider_attempts INTEGER NOT NULL DEFAULT 0 CHECK (provider_attempts IN (0, 1)),
    result_json TEXT NOT NULL DEFAULT '{}',
    UNIQUE (case_id, case_version)
);

CREATE TABLE actionrelay_auditor_feedback (
    feedback_id TEXT PRIMARY KEY,
    decision_id TEXT NOT NULL REFERENCES synthetic_auditor_decisions(decision_id) ON DELETE CASCADE,
    author_account_id TEXT NOT NULL REFERENCES synthetic_accounts(account_id),
    note TEXT NOT NULL CHECK (length(note) <= 2000),
    flagged INTEGER NOT NULL CHECK (flagged IN (0, 1)),
    created_at TEXT NOT NULL
);

CREATE INDEX actionrelay_feedback_decision_time
    ON actionrelay_auditor_feedback(decision_id, created_at);
