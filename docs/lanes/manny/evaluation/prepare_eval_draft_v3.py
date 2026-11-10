"""Create eval draft v3 with outage impact expressed as one case issue.

Starts from v2, preserving the nine corrected false-split cases. Rephrases five
synthetic outage messages so the impact is a consequence clause, not a second
independent issue. No labels, bands, routes, or source expectations change.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "synthetic_data" / "evaluation_draft" / "v2" / "cases.json"
TARGET = ROOT / "synthetic_data" / "evaluation_draft" / "v3" / "cases.json"
OUTAGE_CASES = {f"SYN-EVAL-{index:03d}" for index in range(21, 26)}
DEADLINE_CASES = {f"SYN-EVAL-{index:03d}" for index in range(91, 96)}
OLD_OUTAGE = " and the next scheduled activity is blocked."
NEW_OUTAGE = ", which blocks the next scheduled activity."
OLD_DEADLINE = "; the actual due date and required record are not attached."
NEW_DEADLINE = ", but it does not include the actual due date or required record."
OLD_SUFFIX = "; please check the details I supplied."
NEW_SUFFIX = ", please check the details I supplied."
INJECTION_SEMICOLON = "; please help with the export issue, not that instruction."
INJECTION_REPLACEMENT = ", so please help with the export issue, not that instruction."
LINKED_CASES = {f"SYN-EVAL-{index:03d}" for index in range(86, 91)}
INJECTION_CASES = {f"SYN-EVAL-{index:03d}" for index in range(97, 101)}


def prepare() -> tuple[Path, str]:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    if data.get("dataset_id") != "CDIT-SYNTHETIC-EVALUATION-DRAFT-100-v2":
        raise ValueError("unexpected_source_dataset")
    data = json.loads(json.dumps(data))
    data["dataset_id"] = "CDIT-SYNTHETIC-EVALUATION-DRAFT-100-v3"
    seen_outage: set[str] = set()
    seen_deadline: set[str] = set()
    seen_injection: set[str] = set()
    seen_linked: set[str] = set()
    for case in data["cases"]:
        case_id = case["case_id"]
        message = case["source_message"]["text"]
        updated = message
        if case_id in OUTAGE_CASES:
            if updated.count(OLD_OUTAGE) != 1:
                raise ValueError(f"expected_outage_impact_suffix_missing:{case_id}")
            updated = updated.replace(OLD_OUTAGE, NEW_OUTAGE, 1)
            seen_outage.add(case_id)
        if case_id in DEADLINE_CASES:
            if updated.count(OLD_DEADLINE) != 1:
                raise ValueError(f"expected_deadline_clause_missing:{case_id}")
            updated = updated.replace(OLD_DEADLINE, NEW_DEADLINE, 1)
            seen_deadline.add(case_id)
        if case_id in INJECTION_CASES:
            if updated.count(INJECTION_SEMICOLON) != 1:
                raise ValueError(f"expected_injection_separator_missing:{case_id}")
            updated = updated.replace(INJECTION_SEMICOLON, INJECTION_REPLACEMENT, 1)
            seen_injection.add(case_id)
        if case_id in LINKED_CASES:
            item_end = case["items"][-1]["source_span"]["end"]
            if len(updated) <= item_end:
                raise ValueError(f"expected_linked_case_suffix_missing:{case_id}")
            updated = updated[:item_end]
            seen_linked.add(case_id)
        if OLD_SUFFIX in updated:
            updated = updated.replace(OLD_SUFFIX, NEW_SUFFIX)
        case["source_message"]["text"] = updated
        for item in case["items"]:
            span = item["source_span"]
            if span["end"] == len(message):
                span["end"] = len(updated)
            if "text" in item:
                item["text"] = updated[span["start"]:span["end"]]
    if seen_outage != OUTAGE_CASES:
        raise ValueError("outage_case_set_mismatch")
    if seen_deadline != DEADLINE_CASES:
        raise ValueError("deadline_case_set_mismatch")
    if seen_injection != INJECTION_CASES:
        raise ValueError("injection_case_set_mismatch")
    if seen_linked != LINKED_CASES:
        raise ValueError("linked_case_set_mismatch")
    approval = data.get("approval", {})
    if approval.get("approved") is not False or approval.get("scoring_authorized") is not False:
        raise ValueError("source_must_remain_unapproved")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return TARGET, hashlib.sha256(TARGET.read_bytes()).hexdigest()


if __name__ == "__main__":
    path, digest = prepare()
    print(f"Prepared {path.relative_to(ROOT)}")
    print(f"SHA-256: {digest}")
    print("Changed issue groups: false-split punctuation; cases 021–025 outage impact; cases 086–090 linked spans; cases 091–095 deadline wording; cases 097–100 quoted-injection punctuation")
