from __future__ import annotations

import json
from types import SimpleNamespace

from cdit_support_mao.evaluation_live import run_batch


CASE_TEXT = "Where do I find the transcript for a completed training course?"


class FakeMessages:
    def __init__(self):
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        output = {
            "items": [
                {
                    "item_index": 1,
                    "category": "Product how-to / documentation request",
                    "category_label": "inference",
                    "evidence_quote": CASE_TEXT,
                    "rationale": "The request asks where to find a training transcript.",
                    "missing_questions": [],
                    "urgency": "unknown",
                    "urgency_label": "unknown",
                    "destination": "unknown",
                    "destination_label": "unknown",
                    "human_review_required": True,
                    "downstream_allowed": False,
                }
            ],
            "human_review_required": True,
            "parent_complete": False,
            "downstream_allowed": False,
            "dispatched": False,
        }
        return SimpleNamespace(
            stop_reason="end_turn",
            content=[SimpleNamespace(type="text", text=json.dumps(output))],
            model="claude-sonnet-5-5",
            usage=SimpleNamespace(input_tokens=111, output_tokens=51),
        )


class FakeClient:
    def __init__(self):
        self.messages = FakeMessages()
        self.options = None

    def with_options(self, **kwargs):
        self.options = kwargs
        return self


def _case_file(tmp_path):
    item = {
        "item_index": 1,
        "source_span": {"start": 0, "end": len(CASE_TEXT)},
        "triage_proposal": {
            "category": "Product how-to / documentation request",
            "label": "inference",
        },
    }
    data = {
        "dataset_id": "SYNTHETIC-TEST",
        "case_count": 1,
        "scope": {"synthetic_only": True},
        "approval": {"approved": False, "scoring_authorized": False},
        "cases": [
            {
                "case_id": "SYN-EVAL-067",
                "source_message": {"text": CASE_TEXT},
                "items": [item],
            }
        ],
    }
    path = tmp_path / "cases.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def test_live_evaluation_scores_validated_synthetic_triage_with_injected_client(tmp_path):
    client = FakeClient()

    result = run_batch(
        _case_file(tmp_path),
        case_ids={"SYN-EVAL-067"},
        max_cases=1,
        client=client,
        billable_call_authorized=True,
    )

    assert result["diagnostic_only"] is True
    assert result["model_calls"] == 1
    assert result["cases"][0]["trace_id"].startswith("TRACE-")
    assert result["cases"][0]["items"][0]["category_match"] is True
    assert result["cases"][0]["urgency_contract_pass"] is True
    assert result["cases"][0]["human_review_contract_pass"] is True
    assert result["ticket_writes"] == 0
    assert result["external_dispatches"] == 0
    assert len(client.messages.calls) == 1
    assert client.options == {"max_retries": 0, "timeout": 60}


def test_live_evaluation_without_billable_authorization_fails_closed(tmp_path):
    client = FakeClient()

    result = run_batch(
        _case_file(tmp_path),
        case_ids={"SYN-EVAL-067"},
        max_cases=1,
        client=client,
        billable_call_authorized=False,
    )

    assert result["model_calls"] == 0
    assert result["triage_category"]["scored_items"] == 0
    assert result["triage_category"]["unscored_items"] == 1
    assert client.messages.calls == []
