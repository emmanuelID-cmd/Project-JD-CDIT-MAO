# Phase 1 — Knowledge Agent (Shawn)

**Status:** Optional guide. Knowledge code is present in merged PR #2; presence is not independent acceptance.

## Suggested review/work

- Compare retrieval, source allowlist/freshness, relevance, provenance, conflict handling, abstention, and injection boundary with approved A3 and the accepted contract.
- Confirm only synthetic/local approved corpus material is used; retrieved passages remain untrusted evidence and cannot supply instructions or permissions.
- Review source IDs/versions, claim labels, uncertainty, relevance signal, and abstention reason in the output.
- If Shawn chooses, fix her own findings and record results on the project's Python 3.13 target.

## Suggested handoff and evidence

Knowledge's evidence packet and source versions go to Troubleshooting and connector review. Contract mapping defects go to Shared; Knowledge behavior fixes stay with Shawn. A reviewer should be able to check expected source/abstention behavior for selected cases.

This guide's completion is not required for Shawn to work or submit changes; product acceptance follows the approved PRD.
