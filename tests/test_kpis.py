from __future__ import annotations

import pandas as pd

from src.data_model import infer_mapping, parse_and_clean_dates
from src.kpis import compute_period_summary


def test_compute_period_sales_totals():
    df = pd.DataFrame(
        {
            "order_date": ["2026-01-01", "2026-01-02"],
            "sales": [10.0, 20.0],
            "quantity": [1, 2],
            "category": ["A", "A"],
            "order_id": [1, 1],
        }
    )
    mapping = infer_mapping(df)
    df = parse_and_clean_dates(df, mapping)
    start = pd.to_datetime("2026-01-01")
    end = pd.to_datetime("2026-01-02")
    summary = compute_period_summary(df, mapping, start, end)
    assert summary.totals["Revenue"] == 30.0
    assert summary.totals["Volume"] == 3.0
    # order_id has one unique value (1)
    assert summary.totals["Orders"] == 1.0


def test_marketing_ctr_none_when_impressions_zero():
    df = pd.DataFrame(
        {
            "campaign_date": ["2026-01-01", "2026-01-02"],
            "spend": [100.0, 120.0],
            "impressions": [0, 0],
            "clicks": [10, 12],
            "conversions": [1, 2],
            "channel": ["Email", "Search"],
        }
    )
    mapping = infer_mapping(df)
    df = parse_and_clean_dates(df, mapping)
    summary = compute_period_summary(df, mapping, pd.to_datetime("2026-01-01"), pd.to_datetime("2026-01-02"))
    assert summary.profile == "marketing"
    assert summary.totals["CTR"] is None


def test_min_rows_suppresses_totals_and_charts():
    df = pd.DataFrame(
        {
            "order_date": ["2026-01-01", "2026-01-02"],
            "sales": [10.0, 20.0],
            "quantity": [1, 2],
            "category": ["A", "B"],
            "order_id": [1, 2],
        }
    )
    mapping = infer_mapping(df)
    df = parse_and_clean_dates(df, mapping)
    summary = compute_period_summary(
        df,
        mapping,
        pd.to_datetime("2026-01-01"),
        pd.to_datetime("2026-01-02"),
        min_rows_for_kpis=5,
    )
    assert summary.period_row_count == 2
    assert summary.kpis_suppressed is True
    assert summary.totals["Revenue"] is None
    assert summary.trend.empty
    assert summary.breakdown is None


def test_min_rows_zero_never_suppresses():
    df = pd.DataFrame(
        {
            "order_date": ["2026-01-01"],
            "sales": [10.0],
            "quantity": [1],
            "category": ["A"],
            "order_id": [1],
        }
    )
    mapping = infer_mapping(df)
    df = parse_and_clean_dates(df, mapping)
    summary = compute_period_summary(
        df,
        mapping,
        pd.to_datetime("2026-01-01"),
        pd.to_datetime("2026-01-01"),
        min_rows_for_kpis=0,
    )
    assert summary.kpis_suppressed is False
    assert summary.totals["Revenue"] == 10.0


def test_breakdown_none_when_dimension_missing():
    df = pd.DataFrame(
        {
            "order_date": ["2026-01-01", "2026-01-02"],
            "sales": [10.0, 20.0],
            "quantity": [1, 2],
            "order_id": [1, 2],
        }
    )
    mapping = infer_mapping(df)
    assert mapping.dimension_col is None
    df = parse_and_clean_dates(df, mapping)
    summary = compute_period_summary(df, mapping, pd.to_datetime("2026-01-01"), pd.to_datetime("2026-01-02"))
    assert summary.breakdown is None

