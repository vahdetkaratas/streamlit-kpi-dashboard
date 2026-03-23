from __future__ import annotations

import json

from src.observability import LOG_FILE, log_event, new_error_id


def test_new_error_id_has_expected_shape():
    err = new_error_id()
    assert isinstance(err, str)
    assert len(err) == 8


def test_log_event_writes_json_line():
    log_event("test_event", marker="ok")
    content = LOG_FILE.read_text(encoding="utf-8").strip().splitlines()
    assert len(content) >= 1
    payload = json.loads(content[-1])
    assert payload["event"] == "test_event"
    assert payload["marker"] == "ok"
    assert "ts" in payload

