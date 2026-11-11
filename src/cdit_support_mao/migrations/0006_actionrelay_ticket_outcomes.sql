ALTER TABLE synthetic_cases ADD COLUMN withdrawal_requested_at TEXT;

CREATE TABLE actionrelay_ticket_outcomes (
    case_id TEXT PRIMARY KEY REFERENCES synthetic_cases(case_id) ON DELETE CASCADE,
    case_version TEXT NOT NULL,
    route TEXT NOT NULL CHECK (route IN ('routine_form', 'human_review')),
    reason TEXT NOT NULL,
    recorded_at TEXT NOT NULL,
    actor_account_id TEXT NOT NULL REFERENCES synthetic_accounts(account_id),
    reply TEXT NOT NULL,
    source_url TEXT,
    pdf_digest TEXT,
    pdf BLOB,
    CHECK ((route = 'routine_form' AND source_url IS NOT NULL AND pdf_digest IS NOT NULL AND pdf IS NOT NULL)
        OR (route = 'human_review' AND pdf IS NULL AND pdf_digest IS NULL))
);

CREATE TABLE actionrelay_review_runs (
    decision_id TEXT PRIMARY KEY REFERENCES synthetic_auditor_decisions(decision_id) ON DELETE CASCADE,
    case_id TEXT NOT NULL REFERENCES synthetic_cases(case_id) ON DELETE CASCADE,
    case_version TEXT NOT NULL,
    run_id TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL CHECK (status IN ('running', 'human_review', 'blocked', 'stale')),
    started_at TEXT NOT NULL,
    completed_at TEXT,
    result_json TEXT NOT NULL DEFAULT '{}'
);
