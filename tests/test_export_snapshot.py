from __future__ import annotations

import json
import zipfile
from io import BytesIO

import pandas as pd

from src.data_model import infer_mapping, parse_and_clean_dates
from src.export_snapshot import (
    build_snapshot_summary_markdown,
    export_snapshot_package,
    snapshot_directory_to_zip_bytes,
)
from src.kpis import compute_period_summary


def test_export_snapshot_package_writes_core_files():
    df = pd.DataFrame(
        {
            "order_date": ["2026-01-01", "2026-01-02", "2026-01-03"],
            "sales": [10.0, 20.0, 15.0],
            "quantity": [1, 2, 1],
            "category": ["A", "B", "A"],
            "order_id": [1, 2, 3],
        }
    )
    mapping = infer_mapping(df)
    df = parse_and_clean_dates(df, mapping)
    current = compute_period_summary(df, mapping, pd.to_datetime("2026-01-02"), pd.to_datetime("2026-01-03"))
    previous = compute_period_summary(df, mapping, pd.to_datetime("2025-12-31"), pd.to_datetime("2026-01-01"))

    out_dir = export_snapshot_package(
        current=current,
        previous=previous,
        mapping=mapping,
        ai_text="Test insight",
        compare_enabled=True,
        app_version="1.2.0",
        validation_report={"status": "ok", "rows_input": 3},
    )

    assert (out_dir / "snapshot.json").exists()
    assert (out_dir / "validation_report.json").exists()
    assert (out_dir / "trend.csv").exists()
    assert (out_dir / "insight.txt").exists()
    assert (out_dir / "SNAPSHOT_SUMMARY.md").exists()
    summary_text = (out_dir / "SNAPSHOT_SUMMARY.md").read_text(encoding="utf-8")
    assert "KPI Dashboard" in summary_text
    assert "What changed?" in summary_text

    payload = json.loads((out_dir / "snapshot.json").read_text(encoding="utf-8"))
    assert payload["profile"] == "sales"
    assert payload["compare_enabled"] is True
    assert payload["app_version"] == "1.2.0"
    assert "kpi_guardrails" in payload
    assert payload["kpi_guardrails"]["min_rows_for_kpis"] == 1

    zip_bytes = snapshot_directory_to_zip_bytes(out_dir)
    with zipfile.ZipFile(BytesIO(zip_bytes)) as zf:
        names = set(zf.namelist())
    assert "snapshot.json" in names
    assert "SNAPSHOT_SUMMARY.md" in names
    assert "trend.csv" in names
    assert "insight.txt" in names


def test_export_snapshot_marketing_profile_payload_and_files():
    df = pd.DataFrame(
        {
            "campaign_date": ["2026-01-01", "2026-01-02", "2026-01-03"],
            "spend": [50.0, 60.0, 55.0],
            "impressions": [1000, 1200, 1100],
            "clicks": [50, 60, 55],
            "conversions": [2, 3, 2],
            "channel": ["Email", "Search", "Email"],
        }
    )
    mapping = infer_mapping(df)
    df = parse_and_clean_dates(df, mapping)
    current = compute_period_summary(df, mapping, pd.to_datetime("2026-01-02"), pd.to_datetime("2026-01-03"))
    previous = compute_period_summary(df, mapping, pd.to_datetime("2025-12-31"), pd.to_datetime("2026-01-01"))

    out_dir = export_snapshot_package(
        current=current,
        previous=previous,
        mapping=mapping,
        ai_text="Marketing insight",
        compare_enabled=False,
        app_version="1.6.0",
        validation_report=None,
    )

    payload = json.loads((out_dir / "snapshot.json").read_text(encoding="utf-8"))
    assert payload["profile"] == "marketing"
    assert payload["compare_enabled"] is False
    assert "Spend" in payload["totals_current"]
    assert "Conversions" in payload["totals_current"]
    assert "CTR" in payload["totals_current"]
    assert (out_dir / "breakdown.csv").exists()


def test_build_snapshot_summary_markdown_includes_totals():
    payload = {
        "app_version": "1.0.0",
        "profile": "sales",
        "date_range": {"start": "2026-01-01", "end": "2026-01-07"},
        "previous_period": {"start": "2025-12-25", "end": "2025-12-31"},
        "compare_enabled": True,
        "trend_metric_label": "Revenue",
        "totals_current": {"Revenue": 100.0, "Volume": None},
        "totals_previous": {"Revenue": 90.0, "Volume": 5.0},
        "dimension_column": "region",
        "kpi_guardrails": {
            "min_rows_for_kpis": 1,
            "current": {"period_row_count": 10, "kpis_suppressed": False},
            "previous": {"period_row_count": 8, "kpis_suppressed": False},
        },
    }
    md = build_snapshot_summary_markdown(snapshot_payload=payload, ai_text="Hello insight")
    assert "| Revenue |" in md
    assert "Hello insight" in md
    assert "region" in md

