# Phase 4 — Shawn Lane Evidence and Handoff

**Status:** Optional guide; Shawn chooses whether and how to use it.

## Suggested activity

- Run or update Shawn's lane harness for its component role, keeping stand-in upstreams where appropriate.
- Record Python version, command, counts, expected/observed outcomes, and limitations. Python 3.12 results are historical; the project target is Python 3.13.
- Publish proposed/accepted contract version, examples, agent versions, known limits, and open interface questions.
- Route agent-internal findings to Shawn; route connector/schema transport defects to Shared Lane.

## Boundary and evidence

The combined workflow harness is separate Shared Lane test infrastructure. It may call Shawn's approved contracts and report internal defects, but it may not edit her agents or lane harness. Shawn's choice not to follow this guide is never a failed acceptance criterion.
