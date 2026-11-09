ALTER TABLE synthetic_cases
    ADD COLUMN assigned_staff_account_id TEXT REFERENCES synthetic_accounts(account_id) ON DELETE RESTRICT;

CREATE INDEX synthetic_cases_assigned_updated_idx
    ON synthetic_cases(assigned_staff_account_id, updated_at DESC);

ALTER TABLE synthetic_auditor_decisions
    ADD COLUMN admin_override_reason TEXT CHECK(
        admin_override_reason IS NULL OR length(admin_override_reason) BETWEEN 1 AND 500
    );

CREATE TABLE synthetic_case_assignment_events (
    event_id TEXT PRIMARY KEY CHECK(length(event_id) BETWEEN 3 AND 96),
    case_id TEXT NOT NULL REFERENCES synthetic_cases(case_id) ON DELETE RESTRICT,
    actor_account_id TEXT REFERENCES synthetic_accounts(account_id) ON DELETE RESTRICT,
    previous_staff_account_id TEXT REFERENCES synthetic_accounts(account_id) ON DELETE RESTRICT,
    assigned_staff_account_id TEXT REFERENCES synthetic_accounts(account_id) ON DELETE RESTRICT,
    action TEXT NOT NULL CHECK(action IN ('seed_assigned', 'assigned', 'reassigned', 'unassigned')),
    occurred_at TEXT NOT NULL,
    CHECK(previous_staff_account_id IS NOT assigned_staff_account_id),
    CHECK((action = 'seed_assigned' AND actor_account_id IS NULL
           AND previous_staff_account_id IS NULL AND assigned_staff_account_id IS NOT NULL)
       OR (action = 'assigned' AND actor_account_id IS NOT NULL
           AND previous_staff_account_id IS NULL AND assigned_staff_account_id IS NOT NULL)
       OR (action = 'reassigned' AND actor_account_id IS NOT NULL
           AND previous_staff_account_id IS NOT NULL AND assigned_staff_account_id IS NOT NULL)
       OR (action = 'unassigned' AND actor_account_id IS NOT NULL
           AND previous_staff_account_id IS NOT NULL AND assigned_staff_account_id IS NULL))
);

CREATE INDEX synthetic_case_assignment_events_case_time_idx
    ON synthetic_case_assignment_events(case_id, occurred_at DESC);

CREATE TRIGGER synthetic_case_assignment_events_no_update
BEFORE UPDATE ON synthetic_case_assignment_events
BEGIN
    SELECT RAISE(ABORT, 'assignment history is append-only');
END;
