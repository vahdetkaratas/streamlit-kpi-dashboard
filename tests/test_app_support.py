import pandas as pd

from src.app_support import compute_previous_period


def test_compute_previous_period_symmetric_length():
    start = pd.to_datetime("2026-01-10")
    end = pd.to_datetime("2026-01-12")
    p0, p1 = compute_previous_period(start, end)
    assert (end - start).days == (p1 - p0).days
    assert p1 < start
