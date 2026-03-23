from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import pandas as pd

from src.data_model import ColumnMapping


@dataclass
class ValidationError(Exception):
    message: str
    report: dict

    def __str__(self) -> str:
        return self.message


def _required_columns(mapping: ColumnMapping) -> list[str]:
    cols = [mapping.date_col, mapping.trend_metric_col]
    if mapping.profile == "sales" and mapping.revenue_col:
        cols.append(mapping.revenue_col)
    if mapping.profile == "marketing" and mapping.spend_col:
        cols.append(mapping.spend_col)
    return list(dict.fromkeys(cols))


def _optional_numeric_columns(mapping: ColumnMapping) -> list[str]:
    candidates = [
        mapping.volume_col,
        mapping.conversions_col,
        mapping.clicks_col,
        mapping.impressions_col,
    ]
    return [c for c in candidates if c]


def validate_and_prepare_dataset(
    df: pd.DataFrame,
    mapping: ColumnMapping,
    *,
    min_date_parse_ratio: float = 0.8,
) -> tuple[pd.DataFrame, dict]:
    report: dict = {
        "profile": mapping.profile,
        "rows_input": int(len(df)),
        "missing_columns": [],
        "date_parse_ratio": None,
        "rows_after_date_parse": None,
        "numeric_columns": {},
        "min_date_parse_ratio": float(min_date_parse_ratio),
    }

    required_cols = _required_columns(mapping)
    missing = [c for c in required_cols if c not in df.columns]
    report["missing_columns"] = missing
    if missing:
        raise ValidationError(
            f"Missing required column(s): {', '.join(missing)}.",
            report,
        )

    out = df.copy()
    parsed_dates = pd.to_datetime(out[mapping.date_col], errors="coerce", format="mixed")
    valid_date_count = int(parsed_dates.notna().sum())
    date_ratio = (valid_date_count / len(out)) if len(out) else 0.0
    report["date_parse_ratio"] = float(date_ratio)

    if date_ratio < min_date_parse_ratio:
        raise ValidationError(
            (
                f"Date parsing coverage is too low ({date_ratio:.1%}). "
                f"Required at least {min_date_parse_ratio:.0%} valid dates."
            ),
            report,
        )

    out[mapping.date_col] = parsed_dates
    out = out.dropna(subset=[mapping.date_col]).copy()
    report["rows_after_date_parse"] = int(len(out))

    numeric_required = [mapping.trend_metric_col]
    numeric_optional = _optional_numeric_columns(mapping)
    numeric_all = list(dict.fromkeys(numeric_required + numeric_optional))

    for col in numeric_all:
        if col not in out.columns:
            continue
        coerced = pd.to_numeric(out[col], errors="coerce")
        valid_count = int(coerced.notna().sum())
        ratio = (valid_count / len(out)) if len(out) else 0.0
        report["numeric_columns"][col] = {
            "valid_ratio": float(ratio),
            "valid_count": valid_count,
            "total": int(len(out)),
        }
        out[col] = coerced

    # Trend metric is required to be numerically valid for at least one row.
    trend_stats = report["numeric_columns"].get(mapping.trend_metric_col)
    if trend_stats is None or trend_stats["valid_count"] == 0:
        raise ValidationError(
            (
                f"Primary metric column '{mapping.trend_metric_col}' has no valid numeric values "
                "after coercion."
            ),
            report,
        )

    report["status"] = "ok"
    return out, report

