"""
Portfolio demo chrome: hero, guidance cards, quick dataset picks.
Streamlit-native; minimal HTML wrappers (single divs) styled in ui_theme.py.
"""

from __future__ import annotations

import html
from pathlib import Path

import streamlit as st

from .data_model import ColumnMapping


def render_empty_state_welcome(sources: dict[str, Path]) -> None:
    """Full-width onboarding when no CSV is loaded."""
    demo_names = list(sources.keys())
    first = demo_names[0] if demo_names else "Demo Sales"

    _render_hero(
        compact=False,
        mode="empty",
        profile_line=None,
    )
    st.markdown("### How to use this demo")
    _render_guide_columns(mode="empty")

    st.markdown("")
    if st.button("Use sample data", type="primary", use_container_width=True, key="welcome_sample_primary"):
        st.session_state["kpi_dataset_choice"] = first
        st.rerun()

    st.caption("Or open the **sidebar** → **Dataset** to pick **Demo Sales**, **Demo Marketing**, or **Upload CSV**.")


def render_main_hero(*, mapping: ColumnMapping, compact: bool) -> None:
    """Top of dashboard when data is loaded."""
    profile_line = (
        f"<strong>Profile:</strong> {mapping.profile.capitalize()} · "
        f"<strong>Trend metric:</strong> {html.escape(mapping.trend_metric_label)}"
    )
    _render_hero(compact=compact, mode="loaded", profile_line=profile_line)


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


def _render_hero(
    *,
    compact: bool,
    mode: str,
    profile_line: str | None,
) -> None:
    title_tag = "h3" if compact else "h1"
    if mode == "empty":
        lead = (
            "Upload a CSV or load a sample to explore **KPIs**, **trends**, and a **“what changed?”** summary—"
            "so business performance is clear without a separate BI stack."
        )
        sub = (
            "Ideal for **sales** and **marketing** exports: one date column plus metrics is enough to get started."
        )
    else:
        lead = (
            "Track **money**, **volume or conversions**, and **orders or CTR** for the selected period, "
            "with optional **compare to the previous period** so you see direction, not just a snapshot."
        )
        sub = (
            "Leaders get a single screen for “how did we do?”—then use **Export snapshot** in the sidebar to share numbers."
        )

    meta = ""
    if profile_line:
        meta = f'<p class="vd-hero-meta">{profile_line}</p>'

    st.markdown(
        f"""
<div class="vd-hero">
  <{title_tag} class="vd-hero-title">KPI Dashboard Demo</{title_tag}>
  <p class="vd-hero-lead">{lead}</p>
  <p class="vd-hero-sub">{sub}</p>
  {meta}
</div>
        """,
        unsafe_allow_html=True,
    )


def _render_guide_columns(*, mode: str) -> None:
    if mode == "empty":
        cards = [
            ("1 · Data", "Use <strong>Use sample data</strong> above or the sidebar <strong>Dataset</strong> (demos or <strong>Upload CSV</strong>)."),
            ("2 · Explore", "After load, use sidebar mapping and <strong>date range</strong>; KPIs and charts update on each run."),
            ("3 · Share", "<strong>Export snapshot</strong> builds a ZIP with CSV extracts, summary, and optional chart PNGs."),
        ]
    else:
        cards = [
            ("1 · Refine", "Sidebar: <strong>dates</strong>, <strong>compare previous period</strong>, <strong>minimum rows</strong> guardrails."),
            ("2 · View", "Scan <strong>KPI summary</strong> below, then <strong>Trend</strong> and <strong>Breakdown</strong> charts."),
            ("3 · Optional", "<strong>Compact layout</strong> for demos; <strong>OpenAI</strong> (if configured) enriches the insight text."),
        ]
    c1, c2, c3 = st.columns(3)
    for col, (title, body) in zip((c1, c2, c3), cards):
        with col:
            st.markdown(
                f'<div class="vd-guide-col"><p class="vd-guide-title">{html.escape(title)}</p>'
                f'<p class="vd-guide-body">{body}</p></div>',
                unsafe_allow_html=True,
            )
