from __future__ import annotations

import pandas as pd

from src.ai_insight import _fmt_number, openai_system_prompt_for_tone, rule_based_what_changed
from src.kpis import PeriodKpiSummary


def _summary(
    *,
    profile: str,
    start: str,
    end: str,
    totals: dict,
    breakdown_rows: list[dict] | None = None,
) -> PeriodKpiSummary:
    breakdown = None
    if breakdown_rows is not None:
        breakdown = pd.DataFrame(breakdown_rows)
    return PeriodKpiSummary(
        profile=profile,
        start_date=pd.to_datetime(start),
        end_date=pd.to_datetime(end),
        totals=totals,
        trend=pd.DataFrame({"date": [], "value": []}),
        breakdown=breakdown,
    )


def test_rule_based_what_changed_mentions_up_when_current_is_higher():
    current = _summary(
        profile="sales",
        start="2026-01-08",
        end="2026-01-14",
        totals={"Revenue": 1200.0, "Volume": 30.0, "Orders": 5.0},
        breakdown_rows=[{"dimension": "A", "value": 700.0}],
    )
    previous = _summary(
        profile="sales",
        start="2026-01-01",
        end="2026-01-07",
        totals={"Revenue": 1000.0, "Volume": 25.0, "Orders": 4.0},
        breakdown_rows=[{"dimension": "A", "value": 600.0}],
    )
    text = rule_based_what_changed(current, previous)
    assert "up by" in text
    assert "Compared with" in text


def test_fmt_number_utility():
    assert _fmt_number(None) == "N/A"
    assert _fmt_number(1200.0).endswith("K")
    assert _fmt_number(2_500_000.0).endswith("M")


def test_rule_based_executive_starts_with_summary():
    current = _summary(
        profile="sales",
        start="2026-01-08",
        end="2026-01-14",
        totals={"Revenue": 1200.0, "Volume": 30.0, "Orders": 5.0},
    )
    previous = _summary(
        profile="sales",
        start="2026-01-01",
        end="2026-01-07",
        totals={"Revenue": 1000.0, "Volume": 25.0, "Orders": 4.0},
    )
    text = rule_based_what_changed(current, previous, tone="executive")
    assert text.startswith("Summary:")


def test_rule_based_brief_shorter_than_neutral():
    current = _summary(
        profile="sales",
        start="2026-01-08",
        end="2026-01-14",
        totals={"Revenue": 1200.0, "Volume": 30.0, "Orders": 5.0},
        breakdown_rows=[{"dimension": "North", "value": 700.0}],
    )
    previous = _summary(
        profile="sales",
        start="2026-01-01",
        end="2026-01-07",
        totals={"Revenue": 1000.0, "Volume": 25.0, "Orders": 4.0},
        breakdown_rows=[{"dimension": "North", "value": 600.0}],
    )
    neutral = rule_based_what_changed(current, previous, tone="neutral")
    brief = rule_based_what_changed(current, previous, tone="brief")
    assert len(brief) < len(neutral)


def test_openai_system_prompts_differ_by_tone():
    n = openai_system_prompt_for_tone("neutral")
    b = openai_system_prompt_for_tone("brief")
    assert "90 words" in b
    assert n != b
