"""
Streamlit entrypoint. Orchestration lives in `app_flow.py` to keep this file minimal.
Run: streamlit run src/app.py
"""

from src.app_flow import run_dashboard_app

run_dashboard_app()
