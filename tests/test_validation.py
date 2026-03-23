from __future__ import annotations

import pandas as pd
import pytest

from src.data_model import build_manual_mapping
from src.validation import ValidationError, validate_and_prepare_dataset


def test_validation_fails_when_date_parse_ratio_below_threshold():
    df = pd.DataFrame(
        {
            "order_date": ["bad-date", "also-bad", "2026-01-01"],
            "sales": [10, 20, 30],
        }
    )
    mapping = build_manual_mapping(
        profile="sales",
        date_col="order_date",
        primary_metric_col="sales",
    )
    with pytest.raises(ValidationError) as exc:
        validate_and_prepare_dataset(df, mapping, min_date_parse_ratio=0.8)
    assert "Date parsing coverage is too low" in str(exc.value)


def test_validation_fails_when_primary_metric_not_numeric():
    df = pd.DataFrame(
        {
            "order_date": ["2026-01-01", "2026-01-02"],
            "sales": ["x", "y"],
        }
    )
    mapping = build_manual_mapping(
        profile="sales",
        date_col="order_date",
        primary_metric_col="sales",
    )
    with pytest.raises(ValidationError) as exc:
        validate_and_prepare_dataset(df, mapping)
    assert "has no valid numeric values" in str(exc.value)


def test_validation_returns_report_on_success():
    df = pd.DataFrame(
        {
            "order_date": ["2026-01-01", "2026-01-02"],
            "sales": ["10", "20"],
            "quantity": [1, 2],
        }
    )
    mapping = build_manual_mapping(
        profile="sales",
        date_col="order_date",
        primary_metric_col="sales",
        volume_col="quantity",
    )
    prepared, report = validate_and_prepare_dataset(df, mapping, min_date_parse_ratio=0.8)
    assert len(prepared) == 2
    assert report["status"] == "ok"
    assert report["numeric_columns"]["sales"]["valid_count"] == 2

