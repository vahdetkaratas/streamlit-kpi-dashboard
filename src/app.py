"""
Streamlit entrypoint. Orchestration lives in `app_flow.py` to keep this file minimal.
Run: streamlit run src/app.py
"""

import streamlit as st

# Must run before any other Streamlit command (including imports that might touch st).
st.set_page_config(
    page_title="KPI Dashboard — Sales & Marketing CSV",
    layout="wide",
    page_icon="📊",
)

from src.app_flow import run_dashboard_app

run_dashboard_app()
