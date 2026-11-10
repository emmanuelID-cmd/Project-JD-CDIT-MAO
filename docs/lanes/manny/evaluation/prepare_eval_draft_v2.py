"""Create eval draft v2 with nine confirmed false splits corrected.

Only the canned suffix punctuation is normalized. Labels, bands, routes, and
source expectations are unchanged. The source v1 file remains immutable.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "synthetic_data" / "evaluation_draft" / "v1" / "cases.json"
TARGET = ROOT / "synthetic_data" / "evaluation_draft" / "v2" / "cases.json"
FALSE_SPLIT_CASES = {
    "SYN-EVAL-003", "SYN-EVAL-008", "SYN-EVAL-013", "SYN-EVAL-018",
    "SYN-EVAL-033", "SYN-EVAL-048", "SYN-EVAL-058", "SYN-EVAL-063",
    "SYN-EVAL-083",
}
OLD = "; please check the details I supplied."
NEW = ", please check the details I supplied."


def prepare() -> tuple[Path, str]:
    original = json.loads(SOURCE.read_text(encoding="utf-8"))
    if original.get("dataset_id") != "CDIT-SYNTHETIC-EVALUATION-DRAFT-100-v1":
        raise ValueError("unexpected_source_dataset")
    if len(original.get("cases", ())) != 100:
        raise ValueError("unexpected_source_case_count")
    data = json.loads(json.dumps(original))
    data["dataset_id"] = "CDIT-SYNTHETIC-EVALUATION-DRAFT-100-v2"

    seen: set[str] = set()
    for case in data["cases"]:
        case_id = case["case_id"]
        if case_id not in FALSE_SPLIT_CASES:
            continue
        message = case["source_message"]["text"]
        if message.count(OLD) != 1:
            raise ValueError(f"expected_false_split_suffix_missing:{case_id}")
        updated = message.replace(OLD, NEW, 1)
        case["source_message"]["text"] = updated
        for item in case["items"]:
            span = item["source_span"]
            if span["end"] == len(message):
                span["end"] = len(updated)
            if "text" in item:
                item["text"] = updated[span["start"]:span["end"]]
        seen.add(case_id)

    if seen != FALSE_SPLIT_CASES:
        raise ValueError("false_split_case_set_mismatch")
    approval = data.get("approval", {})
    if approval.get("approved") is not False or approval.get("scoring_authorized") is not False:
        raise ValueError("source_must_remain_unapproved")

    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return TARGET, hashlib.sha256(TARGET.read_bytes()).hexdigest()


if __name__ == "__main__":
    path, digest = prepare()
    print(f"Prepared {path.relative_to(ROOT)}")
    print(f"SHA-256: {digest}")
    print(f"Changed case IDs: {', '.join(sorted(FALSE_SPLIT_CASES))}")
