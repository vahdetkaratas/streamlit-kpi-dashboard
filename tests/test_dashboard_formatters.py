"""Compare-toggle behavior is implemented via empty previous totals → None deltas."""

from __future__ import annotations

from src.dashboard import _format_delta, _format_money, _format_percent


def test_format_delta_returns_none_when_previous_missing_compare_off_semantics():
    """When compare is off, app passes no previous value → delta hidden."""
    assert _format_delta(100.0, None, kind="money") is None
    assert _format_delta(None, 50.0, kind="money") is None


def test_format_delta_shows_change_when_previous_present():
    s = _format_delta(110.0, 100.0, kind="money")
    assert s is not None
    assert "+10" in s
    assert "%" in s


def test_format_delta_previous_zero_uses_na_percent():
    s = _format_delta(10.0, 0.0, kind="count")
    assert s is not None
    assert "n/a" in s


def test_format_delta_ctr_percent_points():
    s = _format_delta(0.02, 0.01, kind="percent_point")
    assert s is not None
    assert "pp" in s


def test_format_money_and_percent_none():
    assert _format_money(None) == "N/A"
    assert _format_percent(None) == "N/A"
