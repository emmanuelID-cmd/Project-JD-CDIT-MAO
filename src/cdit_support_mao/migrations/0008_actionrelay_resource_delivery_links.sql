ALTER TABLE actionrelay_ticket_outcomes ADD COLUMN delivery_links_json TEXT NOT NULL DEFAULT '[]';
ALTER TABLE actionrelay_ticket_outcomes ADD COLUMN resolution_basis_case_id TEXT REFERENCES synthetic_cases(case_id);
