import math

from src.metric_guardrails import safe_ratio


def test_safe_ratio_basic():
    assert safe_ratio(10.0, 100.0) == 0.1


def test_safe_ratio_zero_or_negative_denominator():
    assert safe_ratio(10.0, 0.0) is None
    assert safe_ratio(10.0, -1.0) is None


def test_safe_ratio_none_inputs():
    assert safe_ratio(None, 100.0) is None
    assert safe_ratio(10.0, None) is None


def test_safe_ratio_non_finite():
    assert safe_ratio(float("nan"), 100.0) is None
    assert safe_ratio(10.0, float("nan")) is None
    assert safe_ratio(10.0, float("inf")) is None
    r = safe_ratio(1.0, 3.0)
    assert r is not None and math.isfinite(r)
