"""
Portfolio demo copy and layout: hero text, step guidance, quick dataset picks.
Uses Streamlit primitives only (no custom HTML shells).
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from .data_model import ColumnMapping


def render_empty_state_welcome(sources: dict[str, Path]) -> None:
    """Full-width onboarding when no CSV is loaded."""
    demo_names = list(sources.keys())
    first = demo_names[0] if demo_names else "Demo Sales"

    _render_hero_streamlit(compact=False, mode="empty", profile_caption=None)

    st.markdown("### How to use this demo")
    _render_guide_columns(mode="empty")

    st.markdown("")
    if st.button("Use sample data", type="primary", use_container_width=True, key="welcome_sample_primary"):
        st.session_state["kpi_dataset_choice"] = first
        st.rerun()

    st.caption("Or open the sidebar → **Dataset** to pick a demo or **Upload CSV**.")


def render_main_hero(*, mapping: ColumnMapping, compact: bool) -> None:
    """Top of dashboard when data is loaded."""
    cap = f"Profile: **{mapping.profile.capitalize()}** · Trend metric: **{mapping.trend_metric_label}**"
    _render_hero_streamlit(compact=compact, mode="loaded", profile_caption=cap)


def render_how_to_and_quick_demos(*, demo_labels: list[str]) -> None:
    """Guidance strip + visible sample switches (main column)."""
    st.markdown("### How to use this demo")
    _render_guide_columns(mode="loaded")

    if demo_labels:
        st.markdown("")
        st.caption("**Try another sample** (reloads instantly)")
        cols = st.columns(min(len(demo_labels), 3))
        for i, name in enumerate(demo_labels[:3]):
            with cols[i]:
                if st.button(name, key=f"quick_demo_{name}", use_container_width=True):
                    st.session_state["kpi_dataset_choice"] = name
                    st.rerun()


def _render_hero_streamlit(
    *,
    compact: bool,
    mode: str,
    profile_caption: str | None,
) -> None:
    if compact:
        st.markdown("### KPI Dashboard Demo")
    else:
        st.title("KPI Dashboard Demo")

    if mode == "empty":
        st.markdown(
            "Upload a CSV or load a sample to explore **KPIs**, **trends**, and a **“what changed?”** summary—"
            "so business performance is clear without a separate BI stack."
        )
        st.caption(
            "Ideal for **sales** and **marketing** exports: one date column plus metrics is enough to get started."
        )
    else:
        st.markdown(
            "Track **money**, **volume or conversions**, and **orders or CTR** for the selected period, "
            "with optional **compare to the previous period** so you see direction, not just a snapshot."
        )
        st.caption(
            "Leaders get a single screen for how we did—then use **Export snapshot** in the sidebar to share numbers."
        )

    if profile_caption:
        st.caption(profile_caption)


def _render_guide_columns(*, mode: str) -> None:
    if mode == "empty":
        cards = [
            ("1 · Data", "Use **Use sample data** above or the sidebar **Dataset** (demos or **Upload CSV**)."),
            ("2 · Explore", "After load, use sidebar mapping and **date range**; KPIs and charts update on each run."),
            ("3 · Share", "**Export snapshot** builds a ZIP with CSV extracts, summary, and optional chart PNGs."),
        ]
    else:
        cards = [
            ("1 · Refine", "Sidebar: **dates**, **compare previous period**, **minimum rows** guardrails."),
            ("2 · View", "Scan **KPI summary** below, then **Trend** and **Breakdown** charts."),
            ("3 · Optional", "**Compact layout** for demos; **OpenAI** (if configured) enriches the insight text."),
        ]
    c1, c2, c3 = st.columns(3)
    for col, (title, body) in zip((c1, c2, c3), cards):
        with col:
            st.markdown(f"**{title}**")
            st.markdown(body)
