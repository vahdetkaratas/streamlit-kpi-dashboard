from __future__ import annotations

import pandas as pd


def compute_previous_period(start_date: pd.Timestamp, end_date: pd.Timestamp) -> tuple[pd.Timestamp, pd.Timestamp]:
    days = (end_date - start_date).days + 1
    prev_end = start_date - pd.Timedelta(days=1)
    prev_start = prev_end - pd.Timedelta(days=days - 1)
    return prev_start, prev_end
