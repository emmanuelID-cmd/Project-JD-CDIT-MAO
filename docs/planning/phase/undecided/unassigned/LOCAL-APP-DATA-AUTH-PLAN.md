# Local App, SQL Foundation, Authentication, and Role Showcase Plan

**Status:** Scope approved. Manny owns SQL and app/auth/UI work in his lane unless he explicitly redirects or requests Shawn's participation. Shared reviews only cross-agent data/event contracts. This plan does not change Manny/Shawn agent ownership.
**Requirements source:** [`PRD-v4.md`](../../../../requirements/PRD-v4.md). PRD-v3 is retained as historical context.
**Branch rule:** The authorized local branch `manny/sql-foundation` was created from Manny's verified lane tip `a363724` on 2026-11-08. While Manny is the sole SQL author, keep this branch and connected local Manny lanes linear and fast-forwarded to the same commit before switching. Never merge/rebase/reset divergent work to force alignment. No push is authorized by this plan.

## Context

The project already selects SQLite and lists logical entities, including synthetic accounts, cases, workflow runs, evaluation results, and Product Health events. The current scaffold has no durable schema or role-specific user interface; the PRD describes intended account categories and local Admin controls. The new role showcase is separate from the authenticated app and must contain no protected resources or operative privileged actions. The existing six-agent phase work continues under the agent owners; this track adds application persistence/auth/UI and connects only through approved contracts.

## Approach

Build a local-only application foundation around the existing Python 3.13/FastAPI/Pydantic stack and SQLite, with server-side role checks at every page/API/data boundary. Keep the unauthenticated role showcase isolated and static/mock. Use an allowlisted metadata contract so Product Health can inspect operational signals without retaining ticket bodies, credentials, or real identities. An alternative - using the public showcase as a role-switching view of the actual app - is rejected because it would conflate presentation with authorization and risk exposing protected data.

## Steps

1. **PRD-v4 and source pointers** - Create the approved v4 requirements document, preserve PRD-v3 unchanged, and update current instructions/indexes to name v4 as the source of truth. Keep dated historical reviews and handoff evidence accurate as historical records.
2. **SQL foundation** - Initial v1 migration is implemented on `manny/sql-foundation`: `synthetic_accounts`, `sessions`, `synthetic_cases`, app-only `product_health_events` and aggregated `product_health_summaries`, `account_access_events`, and `session_extension_alerts`. It includes constraints, indexes, migration checksums, explicit synthetic seed/reset, and retention purge. Remaining proposed entities (`knowledge_documents`, `knowledge_chunks`, `policy_versions`, `workflow_runs`, `agent_handoffs`, `evaluation_cases`, and `evaluation_results`) need their lane/Shared boundaries reviewed before persistence; do not store cross-agent payloads in v1.
3. **Data minimization and Product Health contract** - Define an allowlist for synthetic run/event IDs, timestamps, stage/status, bounded category/reason codes, component/model/policy/source versions, performance measurements, and account-access-change metadata. Explicitly exclude real identities, raw ticket text, attachments, credentials, arbitrary prompts/model payloads, and unrestricted free text. Add synthetic-only seeds and prohibited-field tests.
4. **Local synthetic authentication and authorization** - Implement seeded prototype accounts and the session lifecycle; route each role to its view. Enforce role and record scope in server-side dependencies/repositories, not only in navigation. Admin-only synthetic account role/status controls emit auditable before/after events. No production identity provider, public registration, or real credentials.
5. **Authenticated interfaces** - Implement the client-facing User view and shared Staff/Admin back end. Admin-specific account and Product Health controls appear only after server authorization. Add login, logout, denied, expired, empty, database unavailable, and safe-recovery states.
6. **Unauthenticated role showcase** - Build three linked User/Staff/Admin preview pages with fabricated static data, a visible preview notice, accessible navigation, and inert controls. Keep it unable to create sessions, call protected APIs, or query the app database.
7. **Security and UX verification** - Test the complete role x route x action matrix, direct URL/API access, account-change audit records, prohibited persistence, SQL parameterization, and zero protected-resource access from the showcase. Review keyboard access, responsive layout, loading/empty/error/denied/recovery states, and consistent navigation. Test only synthetic fixtures.
8. **Integration and handoff** - Connect Product Health metadata to the existing workflow only after Shared approves event fields and versions. Run focused database/auth/UI tests and the affected integration checks. Record evidence and unresolved retention/session policy decisions; update the checklist only for verified results.

## Implementation progress

- SQL foundation v1 is implemented on the authorized local SQL branch with checksum migrations, synthetic seeds, reset, retention purge, and bounded Product Health/account-audit tables.
- Local synthetic authentication is implemented with salted scrypt hashes, no default passwords, 30-minute idle/8-hour absolute session limits, 15/5-minute reminders, logout and access-change revocation, plus an Admin review alert that never extends a session.
- Authenticated User, Staff, and Admin routes share the project shell and are authorized server-side. User sees only their own synthetic requests, edits only before review, sees In Progress as In Review, and may cancel their own unresolved request; Staff/Admin manage local synthetic case details/status and see all 80 tagged development examples plus the shared Product Health view; Admin additionally manages synthetic account role/status and reviews extension alerts. Agent writes remain prohibited.
- Static previews exist at /preview/user, /preview/staff, and /preview/admin; they are script-free, use fabricated text, disable illustrative controls, and run under a restrictive CSP.
- Before the case-catalog/status extension, the full Python suite passed 633 tests, including route-role denial, preview isolation, session behavior, access audits, user record scoping, and SQL parameterization. The current branch adds 80 tagged development examples and human-only case lifecycle controls; its verification is tracked in Checklist.md. Manual browser/accessibility review and database-unavailable recovery review remain open.

## Acceptance criteria

- PRD-v4 is the sole active requirements source; PRD-v3 remains unchanged and is labeled historical wherever it is linked as a current baseline.
- The SQL schema is versioned, migratable, seeded with synthetic data, and resettable; constraints prevent invalid role/status references.
- All defined User/Staff/Admin permissions pass the role-route-action matrix, including direct URL and API attempts; unauthorized attempts disclose no protected data.
- Every successful Admin account change has a matching actor/target/action/timestamp/before-after audit event; non-Admin changes are denied.
- Product Health records contain only approved allowlisted metadata. Synthetic tests find zero raw ticket bodies, attachments, credentials, direct real identities, or arbitrary prompts in those records.
- The three no-login preview pages are navigable and visually distinct; they issue zero authenticated API/database requests and expose no working privileged action.
- Database outage, invalid session, denied access, empty data, and reset/recovery paths are truthful and fail safely.
- Security and UX findings are recorded with exact test coverage; no production auth, live integration, or real-data use is claimed.

## Out of scope

- Production authentication/SSO, deployment, real User accounts or credentials, live Salesforce/CTMS/email/telephony integration, real tickets/PHI/confidential data, agent ticket writes or state changes, and public hosting of real Admin data.
- Changing Manny/Shawn agent internals or the six-agent workflow to fit a UI or schema; any internal behavior change returns to that lane owner.
- Adding a fourth role, separate Staff tiers, or access-only zones.
- Making showcase controls functional or using the showcase as an authorization mechanism.

## Decisions and remaining design work

- Approved: Manny owns SQL and app/auth/UI work in his lane unless he explicitly redirects or requests Shawn's participation.
  Shared review remains required before persisting cross-agent handoff/event fields.
- Open design task: Manny defines concrete SQLite columns, keys, indexes, migration mechanics, synthetic seeds/reset, and recovery behavior. The approved retention periods and reset path are specified in PRD-v4 §4d.
  Do not persist cross-agent handoff/event fields until Shared approves the contract.
- Approved: seed only synthetic accounts, disable public registration, store password hashes only, and enforce access server-side. Use 30-minute idle and 8-hour absolute session expiry with 15- and 5-minute warnings; do not extend automatically. An extension request creates an Admin review alert and timestamp only.
  Invalidate sessions on logout, suspension/deactivation/removal, or role change. Production authentication and real credentials remain out of scope.

## Approved local case lifecycle extension (2026-11-08)

- Seed the 80 CASE-SCENARIOS entries as development examples, separate from client-submitted requests and evaluation labels. Only Staff/Admin can see these examples.
- Staff/Admin can edit local synthetic case details/status. User can edit own request only while Submitted; In Progress is displayed to User as In Review, after which content edits are disabled. User can cancel own unresolved request as Closed/Requester Cancelled.
- Keep agent behavior propose-only/read-only. Record human case changes using bounded audit metadata without copying request bodies.
- The PRD-v4 §4e transition map governs prototype UI state updates; it is an app safeguard, not operational policy.