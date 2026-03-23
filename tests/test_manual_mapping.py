from __future__ import annotations

from src.data_model import build_manual_mapping


def test_build_manual_mapping_sales():
    mapping = build_manual_mapping(
        profile="sales",
        date_col="my_date",
        primary_metric_col="my_revenue",
        dimension_col="region",
        volume_col="qty",
        order_id_col="order_id",
    )
    assert mapping.profile == "sales"
    assert mapping.date_col == "my_date"
    assert mapping.revenue_col == "my_revenue"
    assert mapping.volume_col == "qty"
    assert mapping.order_id_col == "order_id"
    assert mapping.trend_metric_label == "Revenue"


def test_build_manual_mapping_marketing():
    mapping = build_manual_mapping(
        profile="marketing",
        date_col="d",
        primary_metric_col="cost",
        dimension_col="channel",
        conversions_col="conversions",
        clicks_col="clicks",
        impressions_col="impressions",
    )
    assert mapping.profile == "marketing"
    assert mapping.date_col == "d"
    assert mapping.spend_col == "cost"
    assert mapping.conversions_col == "conversions"
    assert mapping.trend_metric_label == "Spend"


def test_build_manual_mapping_sales_minimal_optional_columns():
    """Mirrors UI path: only date + primary metric; optional pickers as (none)."""
    mapping = build_manual_mapping(
        profile="sales",
        date_col="order_date",
        primary_metric_col="sales",
        dimension_col=None,
        volume_col=None,
        order_id_col=None,
    )
    assert mapping.dimension_col is None
    assert mapping.volume_col is None
    assert mapping.order_id_col is None
    assert mapping.revenue_col == "sales"


def test_build_manual_mapping_marketing_optional_none():
    mapping = build_manual_mapping(
        profile="marketing",
        date_col="campaign_date",
        primary_metric_col="spend",
        dimension_col=None,
        conversions_col=None,
        clicks_col=None,
        impressions_col=None,
    )
    assert mapping.dimension_col is None
    assert mapping.conversions_col is None
    assert mapping.clicks_col is None
    assert mapping.impressions_col is None

