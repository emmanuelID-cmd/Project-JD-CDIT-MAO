CREATE TABLE synthetic_auditor_decisions (
    decision_id TEXT PRIMARY KEY CHECK(length(decision_id) BETWEEN 3 AND 96),
    case_id TEXT NOT NULL REFERENCES synthetic_cases(case_id) ON DELETE RESTRICT,
    item_id TEXT NOT NULL CHECK(length(item_id) BETWEEN 1 AND 128),
    decision_version INTEGER NOT NULL CHECK(decision_version >= 1),
    item_index INTEGER NOT NULL CHECK(item_index BETWEEN 1 AND 8),
    item_count INTEGER NOT NULL CHECK(item_count BETWEEN 1 AND 8 AND item_index <= item_count),
    case_version TEXT NOT NULL CHECK(length(case_version) BETWEEN 1 AND 64),
    source_id TEXT NOT NULL CHECK(length(source_id) BETWEEN 1 AND 128),
    source_version TEXT NOT NULL CHECK(length(source_version) BETWEEN 1 AND 64),
    source_start INTEGER NOT NULL CHECK(source_start >= 0),
    source_end INTEGER NOT NULL CHECK(source_end > source_start),
    source_digest_sha256 TEXT NOT NULL CHECK(length(source_digest_sha256) = 64),
    policy_version TEXT NOT NULL CHECK(length(policy_version) BETWEEN 1 AND 64),
    category TEXT NOT NULL CHECK(length(category) BETWEEN 1 AND 120),
    urgency_band TEXT NOT NULL CHECK(urgency_band IN ('low', 'medium', 'high')),
    destination TEXT NOT NULL CHECK(length(destination) BETWEEN 1 AND 120),
    rationale TEXT NOT NULL CHECK(length(rationale) BETWEEN 1 AND 2000),
    evidence TEXT NOT NULL CHECK(length(evidence) BETWEEN 1 AND 2000),
    conditions_json TEXT NOT NULL CHECK(json_valid(conditions_json)),
    exceptions_json TEXT NOT NULL CHECK(json_valid(exceptions_json)),
    reviewer_account_id TEXT NOT NULL REFERENCES synthetic_accounts(account_id) ON DELETE RESTRICT,
    recorded_at TEXT NOT NULL,
    is_synthetic INTEGER NOT NULL CHECK(is_synthetic = 1),
    UNIQUE(case_id, item_id, decision_version)
);
CREATE INDEX synthetic_auditor_decisions_case_item_version_idx
    ON synthetic_auditor_decisions(case_id, item_id, decision_version DESC);
CREATE INDEX synthetic_auditor_decisions_recorded_at_idx
    ON synthetic_auditor_decisions(recorded_at DESC);

CREATE TRIGGER synthetic_auditor_decisions_no_update
BEFORE UPDATE ON synthetic_auditor_decisions
BEGIN
    SELECT RAISE(ABORT, 'Auditor decisions are append-only');
END;
