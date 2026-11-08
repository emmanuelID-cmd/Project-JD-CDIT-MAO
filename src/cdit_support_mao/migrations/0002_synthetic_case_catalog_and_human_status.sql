CREATE TABLE synthetic_case_catalog (
    catalog_id TEXT PRIMARY KEY CHECK(length(catalog_id) = 11),
    row_number INTEGER NOT NULL UNIQUE CHECK(row_number BETWEEN 1 AND 80),
    category TEXT NOT NULL CHECK(length(category) BETWEEN 1 AND 120),
    example_query TEXT NOT NULL CHECK(length(example_query) BETWEEN 1 AND 12000),
    default_band TEXT NOT NULL CHECK(default_band IN ('low', 'medium', 'high')),
    rationale TEXT NOT NULL CHECK(length(rationale) BETWEEN 1 AND 2000),
    source_document TEXT NOT NULL CHECK(source_document = 'CASE-SCENARIOS.md'),
    source_version TEXT NOT NULL CHECK(length(source_version) BETWEEN 1 AND 64),
    is_synthetic INTEGER NOT NULL CHECK(is_synthetic = 1)
);
CREATE INDEX synthetic_case_catalog_band_idx ON synthetic_case_catalog(default_band, row_number);

ALTER TABLE synthetic_cases
    ADD COLUMN record_kind TEXT NOT NULL DEFAULT 'user_request'
    CHECK(record_kind IN ('user_request', 'development_example'));
ALTER TABLE synthetic_cases
    ADD COLUMN category TEXT CHECK(category IS NULL OR length(category) BETWEEN 1 AND 120);
ALTER TABLE synthetic_cases
    ADD COLUMN catalog_id TEXT REFERENCES synthetic_case_catalog(catalog_id) ON DELETE RESTRICT;
ALTER TABLE synthetic_cases
    ADD COLUMN closure_reason TEXT
    CHECK(closure_reason IS NULL OR closure_reason IN (
        'requester_cancelled_unresolved', 'staff_closed', 'admin_closed'
    ));
CREATE UNIQUE INDEX synthetic_cases_catalog_id_uq
    ON synthetic_cases(catalog_id) WHERE catalog_id IS NOT NULL;
CREATE INDEX synthetic_cases_kind_status_idx ON synthetic_cases(record_kind, status, updated_at DESC);

CREATE TABLE synthetic_case_change_events (
    event_id TEXT PRIMARY KEY CHECK(length(event_id) BETWEEN 3 AND 96),
    case_id TEXT NOT NULL REFERENCES synthetic_cases(case_id) ON DELETE CASCADE,
    actor_account_id TEXT NOT NULL REFERENCES synthetic_accounts(account_id) ON DELETE RESTRICT,
    action TEXT NOT NULL CHECK(action IN (
        'example_seeded', 'user_submitted', 'user_edited', 'requester_cancelled',
        'staff_edited', 'staff_status_updated', 'admin_edited', 'admin_status_updated'
    )),
    before_status TEXT CHECK(before_status IS NULL OR before_status IN (
        'submitted', 'in_progress', 'waiting_on_customer', 'under_investigation',
        'escalated', 'resolved', 'closed'
    )),
    after_status TEXT NOT NULL CHECK(after_status IN (
        'submitted', 'in_progress', 'waiting_on_customer', 'under_investigation',
        'escalated', 'resolved', 'closed'
    )),
    subject_changed INTEGER NOT NULL DEFAULT 0 CHECK(subject_changed IN (0, 1)),
    request_text_changed INTEGER NOT NULL DEFAULT 0 CHECK(request_text_changed IN (0, 1)),
    reason_code TEXT NOT NULL CHECK(reason_code IN (
        'initial_submission', 'content_correction', 'requester_cancellation',
        'human_status_change', 'synthetic_catalog_seed'
    )),
    occurred_at TEXT NOT NULL
);
CREATE INDEX synthetic_case_change_events_case_time_idx
    ON synthetic_case_change_events(case_id, occurred_at DESC);

CREATE TRIGGER synthetic_case_catalog_kind_insert
BEFORE INSERT ON synthetic_cases
WHEN (NEW.record_kind = 'development_example' AND NEW.catalog_id IS NULL)
  OR (NEW.record_kind = 'user_request' AND NEW.catalog_id IS NOT NULL)
BEGIN
    SELECT RAISE(ABORT, 'catalog reference must match synthetic case record kind');
END;

CREATE TRIGGER synthetic_case_catalog_kind_update
BEFORE UPDATE OF record_kind, catalog_id ON synthetic_cases
WHEN (NEW.record_kind = 'development_example' AND NEW.catalog_id IS NULL)
  OR (NEW.record_kind = 'user_request' AND NEW.catalog_id IS NOT NULL)
BEGIN
    SELECT RAISE(ABORT, 'catalog reference must match synthetic case record kind');
END;
