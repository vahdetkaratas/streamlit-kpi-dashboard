"""
UI tokens: light, high-contrast shell with the same indigo accent as `vercel_demo`
(#6366f1). Easier to read than the demo’s near-black page while staying visually related.
"""

from __future__ import annotations

import plotly.graph_objects as go

# Light theme — prioritise readability (WCAG-friendly contrast on body text)
BG_PAGE = "#eceff4"
SURFACE = "#ffffff"
SURFACE_SUBTLE = "#f5f7fa"
BORDER = "#d1d7e0"
TEXT = "#1a1e28"
MUTED = "#5a6270"
ACCENT = "#6366f1"
ACCENT_HOVER = "#4f52d5"
SUCCESS = "#15803d"
WARNING = "#b45309"
DANGER = "#c2410c"

FONT_SANS = "'DM Sans', system-ui, sans-serif"
FONT_MONO = "'JetBrains Mono', ui-monospace, monospace"


def inject_vercel_demo_theme() -> None:
    """Inject fonts + global CSS (Streamlit). Call once after set_page_config."""
    import streamlit as st

    st.markdown(
        f"""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,600;0,9..40,700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root {{
    --vd-bg: {BG_PAGE};
    --vd-surface: {SURFACE};
    --vd-surface-muted: {SURFACE_SUBTLE};
    --vd-border: {BORDER};
    --vd-text: {TEXT};
    --vd-muted: {MUTED};
    --vd-accent: {ACCENT};
    --vd-accent-hover: {ACCENT_HOVER};
    --vd-success: {SUCCESS};
    --vd-warning: {WARNING};
    --vd-danger: {DANGER};
  }}
  .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
    background-color: var(--vd-bg) !important;
  }}
  section.main > div {{
    max-width: 1200px;
    margin-left: auto;
    margin-right: auto;
  }}
  .block-container {{
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    font-family: {FONT_SANS};
    color: var(--vd-text);
  }}
  h1, h2, h3, h4, h5, h6 {{
    font-family: {FONT_SANS} !important;
    color: var(--vd-text) !important;
    letter-spacing: -0.02em !important;
    font-weight: 700 !important;
  }}
  .stMarkdown, .stMarkdown p, .stCaption, [data-testid="stCaption"] {{
    color: var(--vd-text);
  }}
  [data-testid="stCaption"] {{
    color: var(--vd-muted) !important;
  }}
  hr {{
    border-color: var(--vd-border) !important;
    opacity: 1 !important;
  }}
  a {{
    color: var(--vd-accent) !important;
    font-weight: 500;
  }}
  a:hover {{
    color: var(--vd-accent-hover) !important;
  }}
  [data-testid="stSidebar"] {{
    background-color: var(--vd-surface) !important;
    border-right: 1px solid var(--vd-border) !important;
  }}
  [data-testid="stSidebar"] .block-container {{
    font-family: {FONT_SANS};
    color: var(--vd-text);
  }}
  [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{
    font-size: 1rem !important;
    font-weight: 700 !important;
    text-transform: none !important;
    letter-spacing: -0.02em !important;
    color: var(--vd-text) !important;
    border-bottom: 1px solid var(--vd-border);
    padding-bottom: 0.35rem;
    margin-top: 1.25rem !important;
    margin-bottom: 0.5rem !important;
  }}
  [data-testid="stSidebar"] h1:first-of-type, [data-testid="stSidebar"] h2:first-of-type {{
    margin-top: 0 !important;
  }}
  [data-testid="stSidebar"] label, [data-testid="stSidebar"] .stMarkdown p {{
    color: var(--vd-muted) !important;
    font-size: 0.875rem;
  }}
  [data-testid="stMetric"] {{
    background-color: var(--vd-surface) !important;
    border: 1px solid var(--vd-border) !important;
    border-radius: 8px !important;
    padding: 0.85rem 1rem !important;
    box-shadow: 0 1px 2px rgba(26, 30, 40, 0.04);
  }}
  [data-testid="stMetricLabel"] {{
    color: var(--vd-muted) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.04em !important;
    font-size: 0.7rem !important;
    font-weight: 600 !important;
  }}
  [data-testid="stMetricValue"] {{
    font-family: {FONT_MONO} !important;
    color: var(--vd-text) !important;
    font-size: 1.1rem !important;
    font-weight: 600 !important;
  }}
  [data-testid="stMetricDelta"] {{
    font-family: {FONT_MONO} !important;
    font-size: 0.8rem !important;
  }}
  .stButton > button {{
    font-family: {FONT_SANS} !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    border: 1px solid var(--vd-border) !important;
    background-color: var(--vd-surface-muted) !important;
    color: var(--vd-text) !important;
  }}
  .stButton > button:hover {{
    border-color: var(--vd-muted) !important;
    background-color: var(--vd-surface) !important;
  }}
  div[data-testid="stDownloadButton"] > button {{
    font-family: {FONT_SANS} !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    background-color: var(--vd-accent) !important;
    color: #fff !important;
    border: none !important;
  }}
  div[data-testid="stDownloadButton"] > button:hover {{
    background-color: var(--vd-accent-hover) !important;
    color: #fff !important;
  }}
  [data-baseweb="input"], [data-baseweb="select"] > div {{
    border-radius: 8px !important;
    border-color: var(--vd-border) !important;
  }}
  .stExpander {{
    border: 1px solid var(--vd-border) !important;
    border-radius: 12px !important;
    background-color: var(--vd-surface) !important;
  }}
  .stAlert {{
    border-radius: 10px !important;
    border: 1px solid var(--vd-border) !important;
  }}
  [data-testid="stInfo"], [data-testid="stSuccess"], [data-testid="stWarning"], [data-testid="stError"] {{
    border-radius: 10px !important;
  }}
  iframe[title="streamlit_plotly_chart"] {{
    border-radius: 10px;
    border: 1px solid var(--vd-border);
    background: var(--vd-surface);
  }}
  p.vd-section {{
    font-family: {FONT_SANS} !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    color: var(--vd-muted) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    margin: 1.25rem 0 0.75rem 0 !important;
    line-height: 1.3 !important;
  }}
  p.vd-section.compact {{
    margin-top: 0.35rem !important;
    margin-bottom: 0.2rem !important;
    font-size: 0.8rem !important;
  }}
  .vd-insight {{
    font-family: {FONT_SANS};
    color: var(--vd-text);
    line-height: 1.65;
    padding: 1rem 1.25rem;
    background: var(--vd-surface);
    border: 1px solid var(--vd-border);
    border-radius: 12px;
    margin-top: 0.25rem;
    box-shadow: 0 1px 2px rgba(26, 30, 40, 0.04);
  }}
</style>
        """,
        unsafe_allow_html=True,
    )


def apply_plotly_dashboard_theme(fig: go.Figure, *, height: int, margin: dict) -> None:
    """Plotly styling to match the light shell."""
    fig.update_layout(
        height=height,
        margin=margin,
        paper_bgcolor=SURFACE,
        plot_bgcolor=SURFACE_SUBTLE,
        font=dict(color=TEXT, family="DM Sans, sans-serif", size=12),
        xaxis=dict(
            gridcolor=BORDER,
            linecolor=BORDER,
            zerolinecolor=BORDER,
            tickfont=dict(color=MUTED, size=11),
            title_font=dict(color=MUTED),
        ),
        yaxis=dict(
            gridcolor=BORDER,
            linecolor=BORDER,
            zerolinecolor=BORDER,
            tickfont=dict(color=MUTED, size=11),
            title_font=dict(color=MUTED),
        ),
        legend=dict(font=dict(color=MUTED), bgcolor="rgba(0,0,0,0)", borderwidth=0),
        hoverlabel=dict(
            bgcolor=SURFACE,
            bordercolor=BORDER,
            font=dict(family="JetBrains Mono, monospace", size=12, color=TEXT),
        ),
    )
    fig.update_layout(title_font=dict(size=13, color=MUTED, family="DM Sans, sans-serif"))
