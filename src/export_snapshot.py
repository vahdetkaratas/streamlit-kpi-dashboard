from __future__ import annotations

import io
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import plotly.express as px

from src.data_model import ColumnMapping
from src.kpis import PeriodKpiSummary

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPORT_ROOT = PROJECT_ROOT / "artifacts" / "exports"


def _build_trend_figure(current: PeriodKpiSummary):
    fig = px.line(current.trend, x="date", y="value", markers=False)
    fig.update_layout(height=320, margin=dict(l=0, r=0, t=30, b=0))
    return fig


def _build_breakdown_figure(current: PeriodKpiSummary, mapping: ColumnMapping):
    if current.breakdown is None or current.breakdown.empty or not mapping.dimension_col:
        return None
    fig = px.bar(
        current.breakdown,
        x="dimension",
        y="value",
        title=f"Top {mapping.dimension_col} by {mapping.trend_metric_label}",
    )
    fig.update_layout(height=320, margin=dict(l=20, r=20, t=40, b=20))
    return fig


def build_snapshot_summary_markdown(*, snapshot_payload: dict[str, Any], ai_text: str) -> str:
    """Human-readable handoff summary; mirrors snapshot.json without dumping raw JSON."""
    dr = snapshot_payload["date_range"]
    pr = snapshot_payload["previous_period"]
    kg = snapshot_payload.get("kpi_guardrails") or {}
    lines = [
        "# KPI Dashboard — snapshot summary",
        "",
        f"- **App version:** `{snapshot_payload['app_version']}`",
        f"- **Profile:** {snapshot_payload['profile']}",
        f"- **Trend metric:** {snapshot_payload['trend_metric_label']}",
        f"- **Compare with previous period:** {'yes' if snapshot_payload['compare_enabled'] else 'no'}",
        "",
        "## Date ranges",
        "",
        f"- **Current:** {dr['start']} → {dr['end']}",
        f"- **Previous:** {pr['start']} → {pr['end']}",
        "",
        "## KPI totals",
        "",
        "### Current period",
        "",
        _totals_markdown_table(snapshot_payload["totals_current"]),
        "",
        "### Previous period",
        "",
        _totals_markdown_table(snapshot_payload["totals_previous"]),
        "",
        "## Row counts & guardrails",
        "",
        f"- **Minimum rows for KPIs:** {kg.get('min_rows_for_kpis', '—')}",
    ]
    cur = kg.get("current") or {}
    prev = kg.get("previous") or {}
    lines += [
        f"- **Current period rows:** {cur.get('period_row_count', '—')} "
        f"({'suppressed' if cur.get('kpis_suppressed') else 'ok'})",
        f"- **Previous period rows:** {prev.get('period_row_count', '—')} "
        f"({'suppressed' if prev.get('kpis_suppressed') else 'ok'})",
        "",
        "## Dimension",
        "",
        f"- **Breakdown column:** {snapshot_payload.get('dimension_column') or '_(none)_'}",
        "",
        "## What changed? (insight)",
        "",
        "```text",
        (ai_text or "").strip(),
        "```",
        "",
        "## Package files",
        "",
        "- `snapshot.json` — machine-readable metadata and totals",
        "- `SNAPSHOT_SUMMARY.md` — this file",
        "- `trend.csv` — daily trend series",
        "- `breakdown.csv` — top dimensions (if exported)",
        "- `insight.txt` — same text as the insight section above",
        "- `validation_report.json` — dataset validation (if present)",
        "- `trend.png` / `breakdown.png` — chart images when Kaleido is available",
        "",
    ]
    return "\n".join(lines)


def _totals_markdown_table(totals: dict[str, Any]) -> str:
    if not totals:
        return "_No totals._"
    rows = [f"| Metric | Value |", f"| --- | --- |"]
    for k in sorted(totals.keys()):
        v = totals[k]
        cell = "—" if v is None else f"{v}"
        rows.append(f"| {k} | {cell} |")
    return "\n".join(rows)


def snapshot_directory_to_zip_bytes(directory: Path) -> bytes:
    """Zip all files in a snapshot folder (flat names in archive root)."""
    buf = io.BytesIO()
    files = sorted(p for p in directory.iterdir() if p.is_file())
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in files:
            zf.write(path, arcname=path.name)
    return buf.getvalue()


def export_snapshot_package(
    *,
    current: PeriodKpiSummary,
    previous: PeriodKpiSummary,
    mapping: ColumnMapping,
    ai_text: str,
    compare_enabled: bool,
    app_version: str,
    validation_report: Optional[dict] = None,
) -> Path:
    """
    Export a deterministic snapshot package for handoff.

    Output includes:
    - snapshot.json (metadata + KPI totals)
    - trend.csv
    - breakdown.csv (if available)
    - insight.txt
    - SNAPSHOT_SUMMARY.md (handoff summary)
    - trend.png, breakdown.png (if image engine is available)
    """
    EXPORT_ROOT.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    out_dir = EXPORT_ROOT / f"snapshot-{mapping.profile}-{ts}"
    out_dir.mkdir(parents=True, exist_ok=True)

    snapshot_payload = {
        "app_version": app_version,
        "profile": mapping.profile,
        "date_range": {
            "start": f"{current.start_date:%Y-%m-%d}",
            "end": f"{current.end_date:%Y-%m-%d}",
        },
        "previous_period": {
            "start": f"{previous.start_date:%Y-%m-%d}",
            "end": f"{previous.end_date:%Y-%m-%d}",
        },
        "compare_enabled": compare_enabled,
        "trend_metric_label": mapping.trend_metric_label,
        "totals_current": current.totals,
        "totals_previous": previous.totals,
        "dimension_column": mapping.dimension_col,
        "kpi_guardrails": {
            "min_rows_for_kpis": current.min_rows_for_kpis,
            "current": {
                "period_row_count": current.period_row_count,
                "kpis_suppressed": current.kpis_suppressed,
            },
            "previous": {
                "period_row_count": previous.period_row_count,
                "kpis_suppressed": previous.kpis_suppressed,
            },
        },
    }
    (out_dir / "snapshot.json").write_text(json.dumps(snapshot_payload, indent=2), encoding="utf-8")

    summary_md = build_snapshot_summary_markdown(snapshot_payload=snapshot_payload, ai_text=ai_text)
    (out_dir / "SNAPSHOT_SUMMARY.md").write_text(summary_md, encoding="utf-8")

    if validation_report is not None:
        (out_dir / "validation_report.json").write_text(
            json.dumps(validation_report, indent=2),
            encoding="utf-8",
        )

    current.trend.to_csv(out_dir / "trend.csv", index=False)
    if current.breakdown is not None and not current.breakdown.empty:
        current.breakdown.to_csv(out_dir / "breakdown.csv", index=False)

    (out_dir / "insight.txt").write_text(ai_text.strip() + "\n", encoding="utf-8")

    # Optional PNG export. If kaleido/engine is unavailable, skip silently and keep package deterministic.
    try:
        trend_fig = _build_trend_figure(current)
        trend_fig.write_image(str(out_dir / "trend.png"))
    except Exception:
        pass

    try:
        breakdown_fig = _build_breakdown_figure(current, mapping)
        if breakdown_fig is not None:
            breakdown_fig.write_image(str(out_dir / "breakdown.png"))
    except Exception:
        pass

    return out_dir

