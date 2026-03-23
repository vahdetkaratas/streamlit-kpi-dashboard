from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal, Optional

import pandas as pd

Profile = Literal["sales", "marketing"]


@dataclass(frozen=True)
class ColumnMapping:
    profile: Profile
    date_col: str

    # Sales profile fields
    revenue_col: Optional[str] = None
    volume_col: Optional[str] = None
    order_id_col: Optional[str] = None

    # Marketing profile fields
    spend_col: Optional[str] = None
    conversions_col: Optional[str] = None
    clicks_col: Optional[str] = None
    impressions_col: Optional[str] = None

    # Shared
    dimension_col: Optional[str] = None

    # Which metric drives the trend chart (fixed for MVP)
    trend_metric_col: str = ""
    trend_metric_label: str = ""


DATE_ALIASES = ["date", "order_date", "created_at", "campaign_date", "ds", "timestamp"]

REVENUE_ALIASES = ["revenue", "sales", "amount"]
VOLUME_ALIASES = ["quantity", "qty", "units"]
ORDER_ID_ALIASES = ["order_id", "orderid", "id"]

SPEND_ALIASES = ["spend", "cost", "amount"]
CONVERSIONS_ALIASES = ["conversions", "conversion", "converted"]
CLICKS_ALIASES = ["clicks", "click"]
IMPRESSIONS_ALIASES = ["impressions", "impr"]

# Dimension used for breakdown charts
DIMENSION_ALIASES = ["category", "product_type", "product", "region", "channel"]


def _lower_to_original(columns: Iterable[str]) -> dict[str, str]:
    return {str(c).strip().lower(): c for c in columns}


def _pick_first_alias(columns_lower_map: dict[str, str], aliases: list[str]) -> Optional[str]:
    for a in aliases:
        if a in columns_lower_map:
            return columns_lower_map[a]
    return None


def infer_profile(df: pd.DataFrame) -> Profile:
    cols = _lower_to_original(df.columns)
    has_marketing_signals = any(a in cols for a in SPEND_ALIASES) and any(
        a in cols for a in IMPRESSIONS_ALIASES
    )
    if has_marketing_signals:
        return "marketing"
    return "sales"


def infer_mapping(df: pd.DataFrame) -> ColumnMapping:
    profile = infer_profile(df)
    cols = _lower_to_original(df.columns)

    date_col = _pick_first_alias(cols, DATE_ALIASES)
    if not date_col:
        raise ValueError(
            "Could not detect a date column. Expected one of: " + ", ".join(DATE_ALIASES)
        )

    dimension_col = _pick_first_alias(cols, DIMENSION_ALIASES)

    if profile == "sales":
        revenue_col = _pick_first_alias(cols, REVENUE_ALIASES)
        if not revenue_col:
            raise ValueError(
                "Could not detect a revenue metric column for sales profile. "
                "Expected one of: " + ", ".join(REVENUE_ALIASES)
            )
        volume_col = _pick_first_alias(cols, VOLUME_ALIASES)
        order_id_col = _pick_first_alias(cols, ORDER_ID_ALIASES)

        return ColumnMapping(
            profile=profile,
            date_col=date_col,
            revenue_col=revenue_col,
            volume_col=volume_col,
            order_id_col=order_id_col,
            dimension_col=dimension_col,
            trend_metric_col=revenue_col,
            trend_metric_label="Revenue",
        )

    # marketing
    spend_col = _pick_first_alias(cols, SPEND_ALIASES)
    conversions_col = _pick_first_alias(cols, CONVERSIONS_ALIASES)
    clicks_col = _pick_first_alias(cols, CLICKS_ALIASES)
    impressions_col = _pick_first_alias(cols, IMPRESSIONS_ALIASES)

    if not spend_col:
        raise ValueError(
            "Could not detect a spend metric column for marketing profile. "
            "Expected one of: " + ", ".join(SPEND_ALIASES)
        )

    return ColumnMapping(
        profile=profile,
        date_col=date_col,
        spend_col=spend_col,
        conversions_col=conversions_col,
        clicks_col=clicks_col,
        impressions_col=impressions_col,
        dimension_col=dimension_col if dimension_col != clicks_col else dimension_col,
        trend_metric_col=spend_col,
        trend_metric_label="Spend",
    )


def parse_and_clean_dates(df: pd.DataFrame, mapping: ColumnMapping) -> pd.DataFrame:
    out = df.copy()
    out[mapping.date_col] = pd.to_datetime(out[mapping.date_col], errors="coerce")
    out = out.dropna(subset=[mapping.date_col])
    return out


def filter_date_range(
    df: pd.DataFrame,
    date_col: str,
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
) -> pd.DataFrame:
    start_ts = pd.to_datetime(start_date)
    end_ts = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1)
    mask = (df[date_col] >= start_ts) & (df[date_col] <= end_ts)
    return df.loc[mask].copy()


def build_manual_mapping(
    *,
    profile: Profile,
    date_col: str,
    primary_metric_col: str,
    dimension_col: Optional[str] = None,
    volume_col: Optional[str] = None,
    order_id_col: Optional[str] = None,
    conversions_col: Optional[str] = None,
    clicks_col: Optional[str] = None,
    impressions_col: Optional[str] = None,
) -> ColumnMapping:
    """
    Build a mapping from user-provided column choices.

    `primary_metric_col` means:
    - sales profile -> revenue column
    - marketing profile -> spend column
    """
    if profile == "sales":
        return ColumnMapping(
            profile=profile,
            date_col=date_col,
            revenue_col=primary_metric_col,
            volume_col=volume_col,
            order_id_col=order_id_col,
            dimension_col=dimension_col,
            trend_metric_col=primary_metric_col,
            trend_metric_label="Revenue",
        )

    return ColumnMapping(
        profile=profile,
        date_col=date_col,
        spend_col=primary_metric_col,
        conversions_col=conversions_col,
        clicks_col=clicks_col,
        impressions_col=impressions_col,
        dimension_col=dimension_col,
        trend_metric_col=primary_metric_col,
        trend_metric_label="Spend",
    )

