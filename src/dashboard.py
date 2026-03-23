from __future__ import annotations

import html
from typing import Optional

import plotly.express as px
import streamlit as st

from .data_model import ColumnMapping
from .kpis import PeriodKpiSummary
from .ui_theme import ACCENT, apply_plotly_dashboard_theme


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
) -> None:
    chart_h = 220 if compact else 320
    _sec_cls = "vd-section compact" if compact else "vd-section"

    if compact:
        st.markdown("### KPI Dashboard Demo")
    else:
        st.title("KPI Dashboard Demo")
    st.markdown(
        "See **revenue or spend**, **volume / conversions**, and **orders or CTR** at a glance, "
        "with trends and a plain-language **“what changed?”** vs the prior period."
    )
    st.caption(f"**Profile:** {mapping.profile.capitalize()} · **Trend metric:** {mapping.trend_metric_label}")

    with st.expander("How to use this demo", expanded=False):
        st.markdown(
            "- Use the **sidebar** for **dates**, **period compare**, and **minimum rows** guardrails.\n"
            "- Toggle **Compact layout** for denser screens; enable **OpenAI** (if configured) for richer insight text.\n"
            "- **Export snapshot** packages KPIs, CSV extracts, and summaries for sharing."
        )

    st.divider()
    st.markdown(f'<p class="{_sec_cls}">Key metrics</p>', unsafe_allow_html=True)

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
    st.markdown(f'<p class="{_sec_cls}">Trend</p>', unsafe_allow_html=True)
    if not current.trend.empty:
        trend_fig = px.line(current.trend, x="date", y="value", markers=False)
        trend_fig.update_traces(line=dict(color=ACCENT, width=2))
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
    st.markdown(f'<p class="{_sec_cls}">{bd_title}</p>', unsafe_allow_html=True)

    if mapping.dimension_col:
        if current.breakdown is not None and not current.breakdown.empty:
            fig = px.bar(
                current.breakdown,
                x="dimension",
                y="value",
                title=None if compact else f"Top {mapping.dimension_col} by {mapping.trend_metric_label}",
            )
            fig.update_traces(marker_color=ACCENT, marker_line_width=0)
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
    st.markdown(f'<p class="{_sec_cls}">What changed?</p>', unsafe_allow_html=True)
    _insight_safe = html.escape(ai_text).replace("\n", "<br/>")
    st.markdown(f'<div class="vd-insight">{_insight_safe}</div>', unsafe_allow_html=True)
