from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import pandas as pd

from .data_model import ColumnMapping, filter_date_range
from .metric_guardrails import safe_ratio


@dataclass(frozen=True)
class PeriodKpiSummary:
    profile: str
    start_date: pd.Timestamp
    end_date: pd.Timestamp
    totals: dict[str, Optional[float]]
    trend: pd.DataFrame
    breakdown: Optional[pd.DataFrame]
    period_row_count: int = 0
    min_rows_for_kpis: int = 1
    kpis_suppressed: bool = False


def _safe_sum(series: pd.Series) -> float:
    coerced = pd.to_numeric(series, errors="coerce")
    return float(coerced.fillna(0).sum())


def _safe_nunique(series: pd.Series) -> Optional[float]:
    if series is None:
        return None
    if len(series) == 0:
        return None
    return float(series.nunique(dropna=True))


def compute_period_summary(
    df: pd.DataFrame,
    mapping: ColumnMapping,
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
    *,
    min_rows_for_kpis: int = 1,
) -> PeriodKpiSummary:
    period_df = filter_date_range(df, mapping.date_col, start_date, end_date)
    row_count = len(period_df)
    suppressed = min_rows_for_kpis > 0 and row_count < min_rows_for_kpis

    totals: dict[str, Optional[float]] = {}
    breakdown: Optional[pd.DataFrame] = None

    # Trend: always group by day
    trend_metric = mapping.trend_metric_col
    trend_df = (
        period_df.groupby(period_df[mapping.date_col].dt.normalize())[trend_metric]
        .apply(_safe_sum)
        .reset_index()
        .rename(columns={"date_col": "date", mapping.date_col: "date", 0: trend_metric})
    )
    trend_df = trend_df.rename(columns={trend_df.columns[0]: "date", trend_metric: "value"})

    if mapping.profile == "sales":
        revenue = _safe_sum(period_df[mapping.revenue_col]) if mapping.revenue_col else None
        volume = _safe_sum(period_df[mapping.volume_col]) if mapping.volume_col else None
        order_count = (
            _safe_nunique(period_df[mapping.order_id_col]) if mapping.order_id_col else float(len(period_df))
        )

        totals = {
            "Revenue": revenue,
            "Volume": volume,
            "Orders": order_count,
        }

        if mapping.dimension_col:
            breakdown_metric = mapping.revenue_col
            breakdown = (
                period_df.groupby(mapping.dimension_col)[breakdown_metric]
                .apply(_safe_sum)
                .reset_index()
                .rename(columns={mapping.dimension_col: "dimension", breakdown_metric: "value"})
                .sort_values("value", ascending=False)
                .head(6)
            )

    else:
        spend = _safe_sum(period_df[mapping.spend_col]) if mapping.spend_col else None
        conversions = (
            _safe_sum(period_df[mapping.conversions_col]) if mapping.conversions_col else None
        )
        clicks = _safe_sum(period_df[mapping.clicks_col]) if mapping.clicks_col else None
        impressions = (
            _safe_sum(period_df[mapping.impressions_col]) if mapping.impressions_col else None
        )
        ctr = safe_ratio(clicks, impressions) if (mapping.clicks_col and mapping.impressions_col) else None

        totals = {
            "Spend": spend,
            "Conversions": conversions,
            "CTR": ctr,
        }

        if mapping.dimension_col:
            breakdown_metric = mapping.spend_col
            breakdown = (
                period_df.groupby(mapping.dimension_col)[breakdown_metric]
                .apply(_safe_sum)
                .reset_index()
                .rename(columns={mapping.dimension_col: "dimension", breakdown_metric: "value"})
                .sort_values("value", ascending=False)
                .head(6)
            )

    if suppressed:
        totals = {k: None for k in totals}
        trend_df = pd.DataFrame(columns=["date", "value"])
        breakdown = None

    return PeriodKpiSummary(
        profile=mapping.profile,
        start_date=pd.to_datetime(start_date),
        end_date=pd.to_datetime(end_date),
        totals=totals,
        trend=trend_df,
        breakdown=breakdown,
        period_row_count=row_count,
        min_rows_for_kpis=min_rows_for_kpis,
        kpis_suppressed=suppressed,
    )

