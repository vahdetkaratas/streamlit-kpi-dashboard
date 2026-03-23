"""
Optional theming hook — kept minimal so Streamlit’s default theme drives contrast and widgets.

Plotly charts use the built-in light template for readability on the default app background.
"""

from __future__ import annotations

import plotly.graph_objects as go


def inject_vercel_demo_theme() -> None:
    """No-op: rely on Streamlit default styling (Settings → Theme) for colors and typography."""
    pass


def apply_plotly_dashboard_theme(fig: go.Figure, *, height: int, margin: dict) -> None:
    """Light, readable Plotly layout — no custom dark palette."""
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=margin,
    )
