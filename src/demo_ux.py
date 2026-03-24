"""
Portfolio demo copy and layout: hero text, step guidance, quick dataset picks.
Uses Streamlit primitives only (no custom HTML shells).
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from .data_model import ColumnMapping

# Apply in app_flow *before* st.radio(..., key="kpi_dataset_choice") — cannot set that key after the radio exists.
KPI_DATASET_PENDING_KEY = "_kpi_pending_dataset"


def _request_dataset_switch(label: str) -> None:
    st.session_state[KPI_DATASET_PENDING_KEY] = label
    st.rerun()


def render_empty_state_welcome(sources: dict[str, Path]) -> None:
    """Full-width onboarding when no CSV is loaded."""
    demo_names = list(sources.keys())
    first = demo_names[0] if demo_names else "Demo Sales"

    _render_hero_streamlit(compact=False, mode="empty", profile_caption=None)

    st.markdown("### How to use this demo")
    _render_guide_columns(mode="empty")

    st.markdown("")
    if st.button("Use sample data", type="primary", use_container_width=True, key="welcome_sample_primary"):
        _request_dataset_switch(first)

    st.caption("Or open the sidebar → **1 · Data source** to pick a demo or **Upload CSV**.")


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
                # Stable widget key (no spaces) — label still shows full name e.g. "Demo Marketing"
                key_slug = name.replace(" ", "_")
                if st.button(name, key=f"quick_demo_{key_slug}", use_container_width=True):
                    _request_dataset_switch(name)


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
            "**What this is:** a small demo that turns a sales or marketing CSV into **KPI cards**, **two charts**, "
            "and a short **“what changed vs last period?”** paragraph—so you can explain performance in one screen."
        )
        st.caption(
            "You don’t need every sidebar option on day one: pick data → leave column detection on Auto → choose dates. "
            "Presets, layout, AI wording, and export are for later or for repeating the same file shape."
        )
    else:
        st.markdown(
            "The numbers below follow **sidebar steps 1–3**: data source, **which column is what**, then **dates + compare**. "
            "Open the optional expanders only if you need tighter layout, different insight wording, or a shareable ZIP."
        )
        st.caption(
            "Default path: scroll the dashboard; change the date range to tell a different story. Export is step **4** when you need artifacts."
        )

    if profile_caption:
        st.caption(profile_caption)


def _render_guide_columns(*, mode: str) -> None:
    if mode == "empty":
        cards = [
            ("1 · Data", "**Use sample data** here or sidebar **1 · Data source** (demo or **Upload CSV**)."),
            ("2 · Meaning", "After load, sidebar **2 · Column meaning**—usually keep **Auto-detect**."),
            ("3 · Read & share", "Sidebar **3** sets the story (dates / compare). **4 · Export** when you need a ZIP."),
        ]
    else:
        cards = [
            ("1 · Story", "Sidebar **3 · Dates & comparison** defines the period; optional guardrail lives in its expander."),
            ("2 · Read", "KPI strip → **Trend** → **Breakdown**; the text block summarizes vs the previous period."),
            ("3 · When needed", "Optional expanders: **layout & insight wording**, **OpenAI** if configured, **4 · Export** for files."),
        ]
    c1, c2, c3 = st.columns(3)
    for col, (title, body) in zip((c1, c2, c3), cards):
        with col:
            st.markdown(f"**{title}**")
            st.markdown(body)
