from __future__ import annotations

from typing import Optional

import plotly.express as px
import streamlit as st

from .data_model import ColumnMapping
from .demo_ux import render_how_to_and_quick_demos, render_main_hero
from .kpis import PeriodKpiSummary
from .ui_theme import apply_plotly_dashboard_theme


def _format_money(x: Optional[float]) -> str:
    if x is None:
        return "N/A"
    return f"${x:,.0f}"


def _format_percent(x: Optional[float]) -> str:
    if x is None:
        return "N/A"
    return f"{x*100:.1f}%"


def _format_delta(
    current_value: Optional[float],
    previous_value: Optional[float],
    *,
    kind: str,
) -> Optional[str]:
    if current_value is None or previous_value is None:
        return None

    delta_abs = current_value - previous_value
    if previous_value == 0:
        delta_pct_text = "n/a"
    else:
        delta_pct = (delta_abs / previous_value) * 100.0
        delta_pct_text = f"{delta_pct:+.1f}%"

    if kind == "money":
        return f"{delta_abs:+,.0f} ({delta_pct_text})"
    if kind == "percent_point":
        # x is ratio value (e.g., 0.019), show pp as % points
        return f"{delta_abs*100:+.1f}pp ({delta_pct_text})"
    return f"{delta_abs:+,.0f} ({delta_pct_text})"


def render_dashboard(
    current: PeriodKpiSummary,
    mapping: ColumnMapping,
    ai_text: str,
    previous: Optional[PeriodKpiSummary] = None,
    compare_enabled: bool = False,
    *,
    compact: bool = False,
    demo_quick_labels: Optional[list[str]] = None,
) -> None:
    chart_h = 220 if compact else 320

    render_main_hero(mapping=mapping, compact=compact)
    render_how_to_and_quick_demos(demo_labels=list(demo_quick_labels or []))

    st.divider()

    st.subheader("KPI summary")
    st.caption("Primary metrics for the selected date range (deltas show when **Compare with previous period** is on).")

    if current.kpis_suppressed:
        st.warning(
            f"Current period KPIs are hidden: **{current.period_row_count}** row(s) in range, "
            f"below the minimum of **{current.min_rows_for_kpis}**. "
            "Lower the threshold in the sidebar or widen the date range."
        )
    if compare_enabled and previous is not None and previous.kpis_suppressed:
        st.warning(
            f"Previous period KPIs are hidden: **{previous.period_row_count}** row(s), "
            f"below **{previous.min_rows_for_kpis}** — compare deltas may show N/A."
        )

    c1, c2, c3 = st.columns(3)
    prev_totals = previous.totals if (compare_enabled and previous is not None) else {}
    if mapping.profile == "sales":
        c1.metric(
            "Revenue",
            _format_money(current.totals.get("Revenue")),
            _format_delta(current.totals.get("Revenue"), prev_totals.get("Revenue"), kind="money"),
            help="Total revenue summed over the selected date range.",
        )
        c2.metric(
            "Volume",
            None if current.totals.get("Volume") is None else f"{current.totals.get('Volume'):,.0f}",
            _format_delta(current.totals.get("Volume"), prev_totals.get("Volume"), kind="count"),
            help="Sum of the mapped volume column (e.g. units), if present.",
        )
        c3.metric(
            "Orders",
            None if current.totals.get("Orders") is None else f"{current.totals.get('Orders'):,.0f}",
            _format_delta(current.totals.get("Orders"), prev_totals.get("Orders"), kind="count"),
            help="Distinct order IDs if mapped; otherwise row count in range.",
        )
    else:
        c1.metric(
            "Spend",
            _format_money(current.totals.get("Spend")),
            _format_delta(current.totals.get("Spend"), prev_totals.get("Spend"), kind="money"),
            help="Total advertising or campaign spend in the selected period.",
        )
        c2.metric(
            "Conversions",
            None if current.totals.get("Conversions") is None else f"{current.totals.get('Conversions'):,.0f}",
            _format_delta(current.totals.get("Conversions"), prev_totals.get("Conversions"), kind="count"),
            help="Conversion count (e.g. leads or purchases) from your mapped column.",
        )
        ctr = current.totals.get("CTR")
        c3.metric(
            "CTR (conversion rate from clicks)",
            _format_percent(ctr),
            _format_delta(ctr, prev_totals.get("CTR"), kind="percent_point"),
            help="Clicks ÷ impressions when both columns are available and impressions > 0.",
        )

    st.divider()
    st.subheader("Charts")
    st.caption("Hover points and bars for exact values.")
    st.markdown("#### Trend")
    if not current.trend.empty:
        trend_fig = px.line(current.trend, x="date", y="value", markers=False)
        trend_fig.update_traces(line=dict(width=2))
        apply_plotly_dashboard_theme(
            trend_fig,
            height=chart_h,
            margin=dict(l=0, r=0, t=8 if compact else 16, b=0),
        )
        st.plotly_chart(trend_fig, use_container_width=True)
    else:
        st.info(
            "No trend series for this range — often because there are no rows in the selected dates, "
            "KPIs are suppressed by the **Minimum rows** setting, or the trend metric column is empty. "
            "Try widening **Date range** in the sidebar or lowering the row threshold."
        )

    bd_title = "Breakdown" if mapping.dimension_col else "Breakdown (not available)"
    st.markdown(f"#### {bd_title}")

    if mapping.dimension_col:
        if current.breakdown is not None and not current.breakdown.empty:
            fig = px.bar(
                current.breakdown,
                x="dimension",
                y="value",
                title=None if compact else f"Top {mapping.dimension_col} by {mapping.trend_metric_label}",
            )
            fig.update_traces(marker_line_width=0)
            # Few categories → default bars look like full-width slabs; add gap so reads as a proper bar chart.
            fig.update_layout(bargap=0.45)
            apply_plotly_dashboard_theme(
                fig,
                height=chart_h,
                margin=dict(l=20, r=20, t=12 if compact else 36, b=20),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(
                f"A breakdown column (**{mapping.dimension_col}**) is mapped, but there is no data in the "
                "current date range. Adjust the range or check the CSV."
            )
    else:
        st.caption(
            "No breakdown column is mapped. Use **Manual mapping** in the sidebar and set "
            "**Breakdown dimension** to enable the bar chart."
        )

    st.divider()
    st.subheader("What changed?")
    st.write(ai_text)
