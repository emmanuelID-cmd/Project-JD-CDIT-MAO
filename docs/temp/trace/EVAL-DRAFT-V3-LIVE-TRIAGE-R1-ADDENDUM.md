# R1 span-coverage correction

**Status:** Diagnostic correction; the original R1 manifest, results, and report remain unchanged.

The original R1 report states 94/94 matching spans. A later review found that its span denominator was incorrectly derived from items with a non-null category comparison, excluding three items whose provider output was rejected even though their segmentation spans were available.

Rechecking the frozen R1 results gives **97/97 observed item spans matching**. The remaining **8 of 105 expected spans were unavailable** because those cases stopped at intake checkpoint A1. This correction does not establish whether those eight stops were necessary under the safe-minimization rule; that remains unresolved. The corrected evaluator now reports observed span matches separately from unavailable spans.

This is a diagnostic metric correction, not an accuracy score or a Phase 2 completion claim. The dataset remains `DRAFT_NOT_APPROVED`, and scoring remains unauthorized.
