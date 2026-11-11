ALTER TABLE actionrelay_ticket_outcomes RENAME TO actionrelay_ticket_outcomes_v6;

CREATE TABLE actionrelay_ticket_outcomes (
    case_id TEXT PRIMARY KEY REFERENCES synthetic_cases(case_id) ON DELETE CASCADE,
    case_version TEXT NOT NULL,
    route TEXT NOT NULL CHECK (route IN ('routine_form', 'resource_link', 'human_review')),
    reason TEXT NOT NULL,
    recorded_at TEXT NOT NULL,
    actor_account_id TEXT NOT NULL REFERENCES synthetic_accounts(account_id),
    reply TEXT NOT NULL,
    source_url TEXT,
    pdf_digest TEXT,
    pdf BLOB,
    CHECK (
        (route = 'routine_form' AND source_url IS NOT NULL AND pdf_digest IS NOT NULL AND pdf IS NOT NULL)
        OR (route = 'resource_link' AND source_url IS NOT NULL AND pdf_digest IS NULL AND pdf IS NULL)
        OR (route = 'human_review' AND pdf IS NULL AND pdf_digest IS NULL)
    )
);

INSERT INTO actionrelay_ticket_outcomes
    (case_id, case_version, route, reason, recorded_at, actor_account_id,
     reply, source_url, pdf_digest, pdf)
SELECT case_id, case_version, route, reason, recorded_at, actor_account_id,
       reply, source_url, pdf_digest, pdf
FROM actionrelay_ticket_outcomes_v6;

DROP TABLE actionrelay_ticket_outcomes_v6;
