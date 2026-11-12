CREATE TABLE synthetic_case_responses (
    response_id TEXT PRIMARY KEY CHECK(length(response_id) BETWEEN 3 AND 96),
    case_id TEXT NOT NULL REFERENCES synthetic_cases(case_id) ON DELETE CASCADE,
    case_version TEXT NOT NULL,
    author_account_id TEXT NOT NULL REFERENCES synthetic_accounts(account_id) ON DELETE RESTRICT,
    response_text TEXT NOT NULL CHECK(length(response_text) BETWEEN 1 AND 4000),
    created_at TEXT NOT NULL
);
CREATE INDEX synthetic_case_responses_case_time_idx
    ON synthetic_case_responses(case_id, created_at);
