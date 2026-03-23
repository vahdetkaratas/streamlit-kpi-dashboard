"""
Visual tokens aligned with `layout-shell/styles.css` (portfolio shell):
Poppins, dark surfaces, amber accent — without embedding the left info-bar layout.
"""

from __future__ import annotations

import plotly.graph_objects as go

# layout-shell :root (hex/rgb equivalents)
DEEP = "#191923"
CONTENT_BG = "#1e1e28"
INFO_BAR_BG = "#20202a"
CARD_A = "#2d2d3a"
CARD_B = "#2b2b35"
TEXT_PRIMARY = "#fafafc"
TEXT_SECONDARY = "#8c8c8e"
TEXT_TERTIARY = "#646466"
BORDER_SOFT = "rgba(255, 255, 255, 0.08)"
SHADOW_1 = "0 3px 8px 0 rgba(15, 15, 20, 0.2)"
SHADOW_2 = "0 1px 4px 0 rgba(15, 15, 20, 0.1)"
ACCENT = "#ffc107"
ACCENT_HOVER = "#e0ac06"
ACCENT_ON = "#1a1a1f"
SUCCESS = "#22c55e"
WARNING = "#eab308"
DANGER = "#ef4444"

FONT_SANS = '"Poppins", system-ui, sans-serif'


def inject_vercel_demo_theme() -> None:
    """Inject fonts + global CSS (Streamlit). Call once after set_page_config."""
    import streamlit as st

    st.markdown(
        f"""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root {{
    --vd-deep: {DEEP};
    --vd-content: {CONTENT_BG};
    --vd-sidebar: {INFO_BAR_BG};
    --vd-card-a: {CARD_A};
    --vd-card-b: {CARD_B};
    --vd-text: {TEXT_PRIMARY};
    --vd-muted: {TEXT_SECONDARY};
    --vd-muted2: {TEXT_TERTIARY};
    --vd-border: {BORDER_SOFT};
    --vd-accent: {ACCENT};
    --vd-accent-hover: {ACCENT_HOVER};
    --vd-accent-on: {ACCENT_ON};
    --vd-shadow-1: {SHADOW_1};
    --vd-shadow-2: {SHADOW_2};
    --vd-success: {SUCCESS};
    --vd-warning: {WARNING};
    --vd-danger: {DANGER};
  }}
  .stApp, [data-testid="stHeader"] {{
    background-color: var(--vd-deep) !important;
  }}
  [data-testid="stAppViewContainer"] {{
    background-color: var(--vd-deep) !important;
  }}
  section.main {{
    background-color: var(--vd-content) !important;
  }}
  section.main > div {{
    max-width: 1200px;
    margin-left: auto;
    margin-right: auto;
  }}
  .block-container {{
    padding-top: 1.25rem;
    padding-bottom: 2.75rem;
    font-family: {FONT_SANS};
    font-weight: 400;
    font-size: 15px;
    letter-spacing: normal;
    color: var(--vd-text);
    -webkit-font-smoothing: subpixel-antialiased;
  }}
  h1, h2, h3, h4, h5, h6 {{
    font-family: {FONT_SANS} !important;
    color: var(--vd-text) !important;
    letter-spacing: normal !important;
    font-weight: 600 !important;
  }}
  h1 {{
    font-weight: 700 !important;
  }}
  .stMarkdown, .stMarkdown p, .stCaption, [data-testid="stCaption"] {{
    color: var(--vd-text);
  }}
  [data-testid="stCaption"] {{
    color: var(--vd-muted) !important;
    font-size: 0.9rem !important;
    font-weight: 300 !important;
  }}
  hr {{
    border-color: var(--vd-border) !important;
    opacity: 1 !important;
    margin: 2rem 0 !important;
  }}
  .vd-hero {{
    background: linear-gradient(159deg, rgba(45, 45, 58, 0.65) 0%, rgba(43, 43, 53, 0.45) 100%);
    border: 1px solid var(--vd-border);
    border-radius: 14px;
    padding: 1.5rem 1.75rem 1.6rem;
    margin-bottom: 1.5rem;
    box-shadow: var(--vd-shadow-2);
  }}
  .vd-hero .vd-hero-title {{
    font-family: {FONT_SANS} !important;
    margin: 0 0 0.65rem 0 !important;
    padding: 0 !important;
    color: var(--vd-text) !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
    line-height: 1.2 !important;
  }}
  .vd-hero h3.vd-hero-title {{
    font-size: 1.35rem !important;
  }}
  .vd-hero .vd-hero-lead {{
    font-family: {FONT_SANS};
    margin: 0 0 0.5rem 0;
    font-size: 1.02rem;
    font-weight: 500;
    line-height: 1.55;
    color: var(--vd-text);
  }}
  .vd-hero .vd-hero-sub {{
    font-family: {FONT_SANS};
    margin: 0;
    font-size: 0.92rem;
    font-weight: 300;
    line-height: 1.55;
    color: var(--vd-muted);
  }}
  .vd-hero .vd-hero-meta {{
    font-family: {FONT_SANS};
    margin: 1rem 0 0 0;
    font-size: 0.82rem;
    font-weight: 400;
    color: var(--vd-muted2);
    padding-top: 0.85rem;
    border-top: 1px solid var(--vd-border);
  }}
  .vd-guide-col {{
    border: 1px solid var(--vd-border);
    border-radius: 12px;
    padding: 1rem 1.15rem;
    background: rgba(25, 25, 35, 0.45);
    box-shadow: var(--vd-shadow-2);
    min-height: 6.5rem;
  }}
  .vd-guide-col .vd-guide-title {{
    font-family: {FONT_SANS};
    margin: 0 0 0.45rem 0;
    font-size: 0.9rem;
    font-weight: 600;
    color: var(--vd-text);
    line-height: 1.35;
  }}
  .vd-guide-col .vd-guide-body {{
    font-family: {FONT_SANS};
    margin: 0;
    font-size: 0.82rem;
    font-weight: 300;
    line-height: 1.5;
    color: var(--vd-muted);
  }}
  p.vd-section-kpi {{
    margin-top: 0.25rem !important;
    padding-bottom: 0.35rem;
    border-bottom: 2px solid var(--vd-accent);
    display: inline-block;
    width: 100%;
    box-sizing: border-box;
  }}
  a {{
    color: var(--vd-accent) !important;
    font-weight: 500;
  }}
  a:hover {{
    color: var(--vd-accent-hover) !important;
    text-shadow: 0 0 3px rgba(250, 250, 252, 0.25);
  }}
  [data-testid="stSidebar"] {{
    background: var(--vd-sidebar) !important;
    border-right: 1px solid var(--vd-border) !important;
    box-shadow: var(--vd-shadow-1);
  }}
  [data-testid="stSidebar"] .block-container {{
    font-family: {FONT_SANS};
    font-size: 13px;
    font-weight: 300;
    letter-spacing: 0.5px;
    line-height: 1.5;
    color: var(--vd-muted);
  }}
  [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{
    font-size: 1rem !important;
    font-weight: 600 !important;
    text-transform: none !important;
    letter-spacing: normal !important;
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
    font-size: 13px !important;
    font-weight: 300 !important;
  }}
  [data-testid="stMetric"] {{
    background: linear-gradient(159deg, rgba(45, 45, 58, 0.95) 0%, rgba(43, 43, 53, 0.95) 100%) !important;
    border: 1px solid var(--vd-border) !important;
    border-left: 3px solid var(--vd-accent) !important;
    border-radius: 8px !important;
    padding: 0.85rem 1rem !important;
    box-shadow: var(--vd-shadow-2);
  }}
  [data-testid="stMetricLabel"] {{
    color: var(--vd-muted) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.04em !important;
    font-size: 0.7rem !important;
    font-weight: 600 !important;
  }}
  [data-testid="stMetricValue"] {{
    font-family: {FONT_SANS} !important;
    color: var(--vd-text) !important;
    font-size: 1.1rem !important;
    font-weight: 600 !important;
  }}
  section.main [data-testid="stMetric"] {{
    padding: 1rem 1.15rem !important;
  }}
  section.main [data-testid="stMetricValue"] {{
    font-size: 1.6rem !important;
    line-height: 1.2 !important;
  }}
  [data-testid="stMetricDelta"] {{
    font-family: {FONT_SANS} !important;
    font-size: 0.8rem !important;
    font-weight: 400 !important;
  }}
  .stButton > button {{
    font-family: {FONT_SANS} !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    border: 1px solid var(--vd-border) !important;
    background: linear-gradient(159deg, rgba(45, 45, 58, 0.9) 0%, rgba(43, 43, 53, 0.9) 100%) !important;
    color: var(--vd-muted) !important;
  }}
  .stButton > button:hover {{
    border-color: rgba(255, 255, 255, 0.15) !important;
    color: var(--vd-text) !important;
  }}
  .stButton > button[kind="primary"],
  div[data-testid="stButton"] > button[kind="primary"] {{
    background-color: var(--vd-accent) !important;
    color: var(--vd-accent-on) !important;
    border: none !important;
  }}
  .stButton > button[kind="primary"]:hover {{
    background-color: var(--vd-accent-hover) !important;
    color: var(--vd-accent-on) !important;
  }}
  div[data-testid="stDownloadButton"] > button {{
    font-family: {FONT_SANS} !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    background-color: var(--vd-accent) !important;
    color: var(--vd-accent-on) !important;
    border: none !important;
  }}
  div[data-testid="stDownloadButton"] > button:hover {{
    background-color: var(--vd-accent-hover) !important;
    color: var(--vd-accent-on) !important;
  }}
  [data-baseweb="input"], [data-baseweb="select"] > div {{
    border-radius: 8px !important;
    border-color: var(--vd-border) !important;
    background-color: rgba(25, 25, 35, 0.55) !important;
  }}
  [data-testid="stSidebar"] input, [data-testid="stSidebar"] textarea {{
    color: var(--vd-text) !important;
  }}
  .stExpander {{
    border: 1px solid var(--vd-border) !important;
    border-radius: 12px !important;
    background: rgba(25, 25, 35, 0.35) !important;
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
    background: var(--vd-content);
    box-shadow: var(--vd-shadow-2);
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
    font-weight: 300;
    font-size: 14px;
    color: var(--vd-text);
    line-height: 1.65;
    padding: 1rem 1.25rem;
    background: linear-gradient(159deg, rgba(45, 45, 58, 0.55) 0%, rgba(43, 43, 53, 0.55) 100%);
    border: 1px solid var(--vd-border);
    border-radius: 12px;
    margin-top: 0.25rem;
    box-shadow: var(--vd-shadow-2);
  }}
</style>
        """,
        unsafe_allow_html=True,
    )


def apply_plotly_dashboard_theme(fig: go.Figure, *, height: int, margin: dict) -> None:
    """Plotly styling to match layout-shell dark content area."""
    fig.update_layout(
        height=height,
        margin=margin,
        paper_bgcolor=CONTENT_BG,
        plot_bgcolor=DEEP,
        font=dict(color=TEXT_PRIMARY, family="Poppins, sans-serif", size=12),
        xaxis=dict(
            gridcolor=BORDER_SOFT,
            linecolor=BORDER_SOFT,
            zerolinecolor=BORDER_SOFT,
            tickfont=dict(color=TEXT_SECONDARY, size=11),
            title_font=dict(color=TEXT_SECONDARY),
        ),
        yaxis=dict(
            gridcolor=BORDER_SOFT,
            linecolor=BORDER_SOFT,
            zerolinecolor=BORDER_SOFT,
            tickfont=dict(color=TEXT_SECONDARY, size=11),
            title_font=dict(color=TEXT_SECONDARY),
        ),
        legend=dict(font=dict(color=TEXT_SECONDARY), bgcolor="rgba(0,0,0,0)", borderwidth=0),
        hoverlabel=dict(
            bgcolor=CARD_A,
            bordercolor=BORDER_SOFT,
            font=dict(family="Poppins, sans-serif", size=12, color=TEXT_PRIMARY),
        ),
    )
    fig.update_layout(title_font=dict(size=13, color=TEXT_SECONDARY, family="Poppins, sans-serif"))
