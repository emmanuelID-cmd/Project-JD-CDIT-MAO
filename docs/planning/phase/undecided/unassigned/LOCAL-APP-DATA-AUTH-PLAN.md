# Local App, SQL Foundation, Authentication, and Role Showcase Plan

**Status:** Scope approved. Manny owns the SQL foundation; app/auth/UI ownership remains unassigned pending project-lead assignment. Shared reviews only cross-agent data/event contracts. This plan does not change Manny/Shawn agent ownership.
**Requirements source:** [`PRD-v4.md`](../../../../requirements/PRD-v4.md). PRD-v3 is retained as historical context.
**Branch rule:** The authorized local branch `manny/sql-foundation` was created from Manny's verified lane tip `a363724` on 2026-11-08. While Manny is the sole SQL author, keep this branch and connected local Manny lanes linear and fast-forwarded to the same commit before switching. Never merge/rebase/reset divergent work to force alignment. No push is authorized by this plan.

## Context

The project already selects SQLite and lists logical entities, including synthetic accounts, cases, workflow runs, evaluation results, and Product Health events. The current scaffold has no durable schema or role-specific user interface; the PRD describes intended account categories and local Admin controls. The new role showcase is separate from the authenticated app and must contain no protected resources or operative privileged actions. The existing six-agent phase work continues under the agent owners; this track adds application persistence/auth/UI and connects only through approved contracts.

## Approach

Build a local-only application foundation around the existing Python 3.13/FastAPI/Pydantic stack and SQLite, with server-side role checks at every page/API/data boundary. Keep the unauthenticated role showcase isolated and static/mock. Use an allowlisted metadata contract so Product Health can inspect operational signals without retaining ticket bodies, credentials, or real identities. An alternative - using the public showcase as a role-switching view of the actual app - is rejected because it would conflate presentation with authorization and risk exposing protected data.

## Steps

1. **PRD-v4 and source pointers** - Create the approved v4 requirements document, preserve PRD-v3 unchanged, and update current instructions/indexes to name v4 as the source of truth. Keep dated historical reviews and handoff evidence accurate as historical records.
2. **SQL foundation** - On `manny/sql-foundation`, translate the logical entity list into a versioned SQLite schema. Define keys, foreign keys, constraints, indexes, migration versioning, synthetic seed/reset data, and local recovery behavior. Proposed entities: `synthetic_accounts`, `synthetic_cases`, `knowledge_documents`, `knowledge_chunks`, `policy_versions`, `workflow_runs`, `agent_handoffs`, `evaluation_cases`, `evaluation_results`, `product_health_events`, and `account_access_events`. Confirm which agent event fields may persist with Shared before implementing any cross-agent record shape.
3. **Data minimization and Product Health contract** - Define an allowlist for synthetic run/event IDs, timestamps, stage/status, bounded category/reason codes, component/model/policy/source versions, performance measurements, and account-access-change metadata. Explicitly exclude real identities, raw ticket text, attachments, credentials, arbitrary prompts/model payloads, and unrestricted free text. Add synthetic-only seeds and prohibited-field tests.
4. **Local synthetic authentication and authorization** - Implement seeded prototype accounts and the session lifecycle; route each role to its view. Enforce role and record scope in server-side dependencies/repositories, not only in navigation. Admin-only synthetic account role/status controls emit auditable before/after events. No production identity provider, public registration, or real credentials.
5. **Authenticated interfaces** - Implement the client-facing User view and shared Staff/Admin back end. Admin-specific account and Product Health controls appear only after server authorization. Add login, logout, denied, expired, empty, database unavailable, and safe-recovery states.
6. **Unauthenticated role showcase** - Build three linked User/Staff/Admin preview pages with fabricated static data, a visible preview notice, accessible navigation, and inert controls. Keep it unable to create sessions, call protected APIs, or query the app database.
7. **Security and UX verification** - Test the complete role x route x action matrix, direct URL/API access, account-change audit records, prohibited persistence, SQL parameterization, and zero protected-resource access from the showcase. Review keyboard access, responsive layout, loading/empty/error/denied/recovery states, and consistent navigation. Test only synthetic fixtures.
8. **Integration and handoff** - Connect Product Health metadata to the existing workflow only after Shared approves event fields and versions. Run focused database/auth/UI tests and the affected integration checks. Record evidence and unresolved retention/session policy decisions; update the checklist only for verified results.

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

## Unknowns

- Unknown: Owner for app/auth/UI implementation.
  Recommendation: Keep only the app/auth/UI portion in `phase/undecided/unassigned` until the project lead assigns it; Manny remains the SQL owner and Shared coordinates cross-agent event contracts.
  Basis: The project lead authorized the Manny-owned `manny/sql-foundation` branch, while existing lane assignment does not assign general application UI ownership.
  Verification action: Project lead assigns app/auth/UI owner before that implementation starts.
- Unknown: Exact schema columns, retention interval, and deletion/reset cadence for Product Health metadata.
  Recommendation: Allowlist fields from PRD-v4; use local project-lifetime retention with a reset/purge path until a shorter duration is approved.
  Basis: PRD-v4 permits minimal metadata but sets no exact duration or finalized DDL.
  Verification action: Review schema and retention statement before first persistent record is written.
- Unknown: Local synthetic credential provisioning and session expiry details.
  Recommendation: Seed synthetic accounts, disable public registration, hash synthetic passwords, use server-side authorization, and provide explicit logout/reset; never use real credentials.
  Basis: PRD-v4 excludes production authentication while requiring local synthetic account identity.
  Verification action: Approve the local auth configuration and session policy during implementation design.
