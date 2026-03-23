from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from src.ai_insight import InsightTone, openai_what_changed, rule_based_what_changed
from src.app_support import compute_previous_period
from src.data_model import (
    ColumnMapping,
    build_manual_mapping,
    infer_mapping,
    infer_profile,
)
from src.dashboard import render_dashboard
from src.export_snapshot import export_snapshot_package, snapshot_directory_to_zip_bytes
from src.kpis import compute_period_summary
from src.load import get_demo_sources, load_csv_from_bytes, load_csv_from_path
from src.mapping_presets import (
    list_saved_preset_names,
    load_preset_by_name,
    load_preset_from_bytes,
    save_preset,
)
from src.observability import log_event, new_error_id
from src.upload_limits import (
    MAX_CSV_UPLOAD_BYTES,
    MAX_PRESET_JSON_BYTES,
    UploadTooLargeError,
    require_upload_under,
)
from src.validation import ValidationError, validate_and_prepare_dataset
from src.demo_ux import render_empty_state_welcome
from src.ui_theme import inject_vercel_demo_theme
from src.version import get_app_version


def _date_input_range(label: str, min_date: pd.Timestamp, max_date: pd.Timestamp) -> tuple[pd.Timestamp, pd.Timestamp]:
    value = st.date_input(
        label, value=(min_date.date(), max_date.date()), min_value=min_date.date(), max_value=max_date.date()
    )
    if isinstance(value, tuple) and len(value) == 2:
        start_date = pd.to_datetime(value[0])
        end_date = pd.to_datetime(value[1])
        if start_date > end_date:
            start_date, end_date = end_date, start_date
        return start_date, end_date

    d = pd.to_datetime(value)
    return d, d


def run_dashboard_app() -> None:
    st.set_page_config(page_title="KPI Dashboard Demo", layout="wide")
    inject_vercel_demo_theme()
    load_dotenv()
    app_version = get_app_version()
    log_event("app_started", app_version=app_version)

    st.sidebar.title("Data")
    st.sidebar.caption(f"v{app_version}")
    sources = get_demo_sources()
    _dataset_options = list(sources.keys()) + ["Upload CSV"]
    if "kpi_dataset_choice" not in st.session_state:
        st.session_state["kpi_dataset_choice"] = _dataset_options[0]
    choice = st.sidebar.radio(
        "Dataset",
        _dataset_options,
        key="kpi_dataset_choice",
        help="Built-in demos or your own CSV (max 25 MB).",
    )

    df_raw = None
    if choice in sources:
        try:
            df_raw = load_csv_from_path(sources[choice])
            log_event("csv_load_success", source="demo", dataset=choice, rows=int(len(df_raw)))
        except Exception as e:
            error_id = new_error_id()
            log_event("csv_load_failed", error_id=error_id, source="demo", dataset=choice, error=str(e))
            st.error(f"Could not load demo dataset. Error ID: {error_id}")
            st.stop()
    else:
        uploaded = st.sidebar.file_uploader("Upload a CSV", type=["csv"])
        if uploaded is not None:
            try:
                raw = uploaded.getvalue()
                require_upload_under(
                    size_bytes=len(raw), limit_bytes=MAX_CSV_UPLOAD_BYTES, label="CSV upload"
                )
                df_raw = load_csv_from_bytes(raw)
                log_event(
                    "csv_load_success",
                    source="upload",
                    filename=getattr(uploaded, "name", "unknown.csv"),
                    rows=int(len(df_raw)),
                )
            except UploadTooLargeError as e:
                error_id = new_error_id()
                log_event("csv_upload_rejected", error_id=error_id, reason=str(e))
                st.error(f"{e} Error ID: {error_id}")
                st.stop()
            except Exception as e:
                error_id = new_error_id()
                log_event(
                    "csv_load_failed",
                    error_id=error_id,
                    source="upload",
                    filename=getattr(uploaded, "name", "unknown.csv"),
                    error=str(e),
                )
                st.error(f"Could not read uploaded CSV. Error ID: {error_id}")
                st.stop()

    if df_raw is None:
        render_empty_state_welcome(sources)
        st.stop()

    columns = [str(c) for c in df_raw.columns]

    auto_mapping_error: str | None = None
    try:
        auto_mapping: ColumnMapping = infer_mapping(df_raw)
        log_event("mapping_auto_success", profile=auto_mapping.profile, date_col=auto_mapping.date_col)
    except Exception as e:
        auto_mapping_error = str(e)
        auto_mapping = None
        log_event("mapping_auto_failed", error=auto_mapping_error)

    st.sidebar.title("Column mapping")
    _mode_options = ["Auto-detect", "Manual mapping", "Upload preset (JSON)", "Saved preset"]
    _default_mode_index = 1 if auto_mapping_error else 0
    mapping_mode = st.sidebar.radio("Mapping mode", _mode_options, index=_default_mode_index)

    mapping: ColumnMapping | None = None

    if mapping_mode == "Manual mapping":
        st.sidebar.caption(
            "Map **Date** + **Primary metric** first. Optional fields add Volume/Orders (sales) or "
            "Clicks/Impressions (marketing) and enable the **Breakdown** chart when dimension is set."
        )
        profile_guess = infer_profile(df_raw)
        profile = st.sidebar.selectbox("Profile", ["sales", "marketing"], index=0 if profile_guess == "sales" else 1)
        date_col = st.sidebar.selectbox("Date column", columns, index=0)
        primary_metric_col = st.sidebar.selectbox(
            "Primary metric column" + (" (Revenue)" if profile == "sales" else " (Spend)"),
            columns,
            index=1 if len(columns) > 1 else 0,
        )

        optional_columns = ["(none)"] + columns
        dimension_pick = st.sidebar.selectbox("Breakdown dimension (optional)", optional_columns, index=0)
        dimension_col = None if dimension_pick == "(none)" else dimension_pick

        if profile == "sales":
            volume_pick = st.sidebar.selectbox("Volume column (optional)", optional_columns, index=0)
            order_id_pick = st.sidebar.selectbox("Order ID column (optional)", optional_columns, index=0)
            mapping = build_manual_mapping(
                profile="sales",
                date_col=date_col,
                primary_metric_col=primary_metric_col,
                dimension_col=dimension_col,
                volume_col=None if volume_pick == "(none)" else volume_pick,
                order_id_col=None if order_id_pick == "(none)" else order_id_pick,
            )
        else:
            conv_pick = st.sidebar.selectbox("Conversions column (optional)", optional_columns, index=0)
            clicks_pick = st.sidebar.selectbox("Clicks column (optional)", optional_columns, index=0)
            impr_pick = st.sidebar.selectbox("Impressions column (optional)", optional_columns, index=0)
            mapping = build_manual_mapping(
                profile="marketing",
                date_col=date_col,
                primary_metric_col=primary_metric_col,
                dimension_col=dimension_col,
                conversions_col=None if conv_pick == "(none)" else conv_pick,
                clicks_col=None if clicks_pick == "(none)" else clicks_pick,
                impressions_col=None if impr_pick == "(none)" else impr_pick,
            )
        log_event("mapping_manual_selected", profile=mapping.profile, date_col=mapping.date_col)

    elif mapping_mode == "Upload preset (JSON)":
        preset_upload = st.sidebar.file_uploader("Mapping preset (.json)", type=["json"])
        if preset_upload is None:
            st.info("Upload a mapping preset JSON file, or choose another mapping mode in the sidebar.")
            st.stop()
        try:
            raw = preset_upload.getvalue()
            require_upload_under(
                size_bytes=len(raw), limit_bytes=MAX_PRESET_JSON_BYTES, label="Preset JSON"
            )
            mapping = load_preset_from_bytes(raw)
            log_event(
                "mapping_preset_loaded",
                source="upload",
                filename=getattr(preset_upload, "name", "preset.json"),
                profile=mapping.profile,
            )
        except UploadTooLargeError as e:
            error_id = new_error_id()
            log_event("mapping_preset_upload_rejected", error_id=error_id, reason=str(e))
            st.error(f"{e} Error ID: {error_id}")
            st.stop()
        except Exception as e:
            error_id = new_error_id()
            log_event("mapping_preset_load_failed", error_id=error_id, source="upload", error=str(e))
            st.error(f"Could not read mapping preset. Error ID: {error_id}")
            st.stop()

    elif mapping_mode == "Saved preset":
        saved_names = list_saved_preset_names()
        if not saved_names:
            st.info(
                "No saved presets yet. Use **Manual mapping** and **Save mapping preset** in the sidebar, "
                "or **Upload preset (JSON)**."
            )
            st.stop()
        chosen = st.sidebar.selectbox("Saved preset", saved_names)
        try:
            mapping = load_preset_by_name(chosen)
            log_event("mapping_preset_loaded", source="saved", preset=chosen, profile=mapping.profile)
        except Exception as e:
            error_id = new_error_id()
            log_event("mapping_preset_load_failed", error_id=error_id, source="saved", preset=chosen, error=str(e))
            st.error(f"Could not load saved preset. Error ID: {error_id}")
            st.stop()

    else:
        if auto_mapping_error:
            error_id = new_error_id()
            log_event("mapping_blocked", error_id=error_id, reason=auto_mapping_error)
            st.error(
                f"Auto mapping failed: {auto_mapping_error}. "
                f"Switch to **Manual mapping**, **Upload preset**, or **Saved preset** in the sidebar. Error ID: {error_id}"
            )
            st.stop()
        mapping = auto_mapping  # type: ignore[assignment]

    validation_report: dict = {}
    try:
        with st.spinner("Processing data..."):
            df, validation_report = validate_and_prepare_dataset(df_raw, mapping, min_date_parse_ratio=0.8)
            log_event(
                "validation_success",
                profile=mapping.profile,
                rows_input=int(len(df_raw)),
                rows_after_date_parse=int(validation_report.get("rows_after_date_parse", len(df))),
                date_parse_ratio=validation_report.get("date_parse_ratio"),
            )
    except ValidationError as e:
        error_id = new_error_id()
        log_event("validation_failed", error_id=error_id, message=e.message, report=e.report)
        st.error(f"Validation failed: {e.message} Error ID: {error_id}")
        st.stop()
    except Exception as e:
        error_id = new_error_id()
        log_event("validation_failed_unexpected", error_id=error_id, error=str(e))
        st.error(f"Could not validate the dataset. Error ID: {error_id}")
        st.stop()

    st.sidebar.title("Mapping preset")
    with st.sidebar.expander("Save current mapping", expanded=False):
        preset_name = st.text_input("Preset name (saved under artifacts/mapping_presets/)", key="mapping_preset_name_input")
        if st.button("Save mapping preset", key="mapping_preset_save_btn"):
            name_stripped = (preset_name or "").strip()
            if not name_stripped:
                st.warning("Enter a preset name before saving.")
            else:
                try:
                    out_path = save_preset(name_stripped, mapping)
                    log_event("mapping_preset_saved", preset=out_path.stem, profile=mapping.profile)
                    st.success(f"Saved: {out_path.name}")
                except ValueError as e:
                    st.warning(str(e))
                except Exception as e:
                    error_id = new_error_id()
                    log_event("mapping_preset_save_failed", error_id=error_id, error=str(e))
                    st.error(f"Could not save preset. Error ID: {error_id}")

    min_date = df[mapping.date_col].min()
    max_date = df[mapping.date_col].max()

    st.sidebar.title("Date range")
    start_date, end_date = _date_input_range("Filter", min_date, max_date)

    previous_start, previous_end = compute_previous_period(start_date, end_date)
    compare_enabled = st.sidebar.checkbox("Compare with previous period", value=True)

    min_rows_for_kpis = st.sidebar.number_input(
        "Minimum rows in period for KPIs",
        min_value=0,
        max_value=50_000,
        value=1,
        step=1,
        help="0 = no minimum. Fewer rows than this in a period hides KPI values and charts for that period only.",
    )

    st.sidebar.title("Display")
    compact_layout = st.sidebar.checkbox(
        "Compact layout (screenshare)",
        value=False,
        help="Smaller chart heights and tighter headings to fit more on one screen.",
    )

    st.sidebar.title("AI insight")
    _insight_tone_options: tuple[InsightTone, ...] = ("neutral", "executive", "brief")
    insight_tone: InsightTone = st.sidebar.selectbox(
        "Insight tone",
        _insight_tone_options,
        index=0,
        help="Wording only — the same KPI facts are used for every tone.",
    )
    use_openai = st.sidebar.checkbox(
        "Use OpenAI (enhanced 'what changed?' text)",
        value=False,
        disabled=not bool(os.getenv("OPENAI_API_KEY")),
    )
    if os.getenv("OPENAI_API_KEY"):
        st.sidebar.caption(
            "OpenAI sees **only pre-aggregated KPIs** from this session (totals, dates, top breakdown)—"
            "**not** raw CSV rows."
        )

    with st.spinner("Processing data..."):
        current_summary = compute_period_summary(
            df, mapping, start_date, end_date, min_rows_for_kpis=min_rows_for_kpis
        )
        previous_summary = compute_period_summary(
            df, mapping, previous_start, previous_end, min_rows_for_kpis=min_rows_for_kpis
        )
        ai_text = rule_based_what_changed(current_summary, previous_summary, tone=insight_tone)
        if use_openai:
            try:
                ai_text = openai_what_changed(current_summary, previous_summary, tone=insight_tone)
                log_event("ai_insight_mode", mode="openai", insight_tone=insight_tone)
            except Exception:
                ai_text = rule_based_what_changed(current_summary, previous_summary, tone=insight_tone)
                log_event("ai_insight_mode", mode="rule_fallback_after_openai_failure", insight_tone=insight_tone)
        else:
            log_event("ai_insight_mode", mode="rule_default", insight_tone=insight_tone)

    render_dashboard(
        current=current_summary,
        mapping=mapping,
        ai_text=ai_text,
        previous=previous_summary,
        compare_enabled=compare_enabled,
        compact=compact_layout,
        demo_quick_labels=list(sources.keys()),
    )

    st.sidebar.title("Export")
    if "last_snapshot_dir" not in st.session_state:
        st.session_state["last_snapshot_dir"] = None
    st.session_state.pop("last_snapshot_zip", None)
    st.session_state.pop("last_snapshot_zip_name", None)

    if st.sidebar.button("Export snapshot package"):
        try:
            snapshot_dir = export_snapshot_package(
                current=current_summary,
                previous=previous_summary,
                mapping=mapping,
                ai_text=ai_text,
                compare_enabled=compare_enabled,
                app_version=app_version,
                validation_report=validation_report,
            )
            st.session_state["last_snapshot_dir"] = str(snapshot_dir.resolve())
            log_event(
                "snapshot_export_success",
                profile=mapping.profile,
                output_dir=str(snapshot_dir),
            )
            st.sidebar.success(f"Snapshot saved: `{snapshot_dir.name}`. Use **Download snapshot ZIP** below.")
        except Exception as e:
            error_id = new_error_id()
            log_event("snapshot_export_failed", error_id=error_id, error=str(e))
            st.session_state["last_snapshot_dir"] = None
            st.sidebar.error(f"Snapshot export failed. Error ID: {error_id}")

    snap_dir_str = st.session_state.get("last_snapshot_dir")
    snap_path = Path(snap_dir_str) if snap_dir_str else None
    if snap_path and snap_path.is_dir():
        try:
            zip_bytes = snapshot_directory_to_zip_bytes(snap_path)
            st.sidebar.download_button(
                label="Download snapshot ZIP",
                data=zip_bytes,
                file_name=f"{snap_path.name}.zip",
                mime="application/zip",
                key="snapshot_zip_download",
            )
        except Exception as e:
            error_id = new_error_id()
            log_event("snapshot_zip_build_failed", error_id=error_id, error=str(e))
            st.sidebar.error(f"Could not build ZIP. Error ID: {error_id}")
