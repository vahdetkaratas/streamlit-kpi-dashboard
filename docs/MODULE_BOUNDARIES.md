# Module boundaries — KPI Dashboard App

This document states **which layer owns what**, so refactors stay predictable. The Streamlit entrypoint is `src/app.py` (minimal); orchestration lives in `src/app_flow.py`.

---

## Layer map

| Layer | Modules | Responsibility |
|-------|---------|----------------|
| **Data contract** | `data_model.py`, `validation.py` | Column mapping, date parsing helpers, CSV→validated `DataFrame` + `ColumnMapping`. No charts, no KPI business rules beyond typing columns. |
| **Metric safety** | `metric_guardrails.py` | Pure helpers (e.g. safe ratios). No I/O, no Streamlit. |
| **KPI logic** | `kpis.py` | Period filtering, aggregates, trend/breakdown frames → `PeriodKpiSummary`. No UI strings beyond labels implied by dict keys. |
| **Insight** | `ai_insight.py` | Text from two `PeriodKpiSummary` instances (rule + optional OpenAI). No raw CSV, no Plotly. |
| **Presentation** | `dashboard.py` | Streamlit layout, Plotly figures, formatting helpers (`_format_*`). No CSV load, no validation. |
| **I/O & packaging** | `load.py`, `export_snapshot.py`, `mapping_presets.py` | Read demo/upload paths; write snapshot folders/ZIP; preset JSON. |
| **Cross-cutting** | `observability.py`, `version.py` | Logging, error IDs, version string. |
| **Composition** | `app.py` (entry), `app_flow.py` | Wire sidebar → load → map → validate → KPIs → insight → dashboard → export; log events. Keep `app.py` minimal. |
| **Upload guardrails** | `upload_limits.py` | Max upload sizes for CSV / preset JSON (fail fast before heavy parse). |
| **App utilities** | `app_support.py` | Small pure helpers used by the flow (e.g. previous period dates). |

---

## Dependency direction (allowed)

```
app.py → app_flow
 ├── load, upload_limits, data_model, validation, mapping_presets, metric_guardrails (indirect via kpis)
 ├── kpis → data_model, metric_guardrails
 ├── dashboard → data_model, kpis
 ├── ai_insight → kpis
 ├── export_snapshot → data_model, kpis
 └── observability, version
```

Avoid **circular** imports (e.g. `kpis` must not import `dashboard` or `app`).

---

## Tests

- Prefer testing **pure logic** in `data_model`, `kpis`, `validation`, `export_snapshot`, `ai_insight`, and **formatters** in `dashboard` without launching Streamlit.
- Full UI flows are covered indirectly; end-to-end browser tests are out of scope for this repo (`docs/PRODUCT.md`).

---

Related: `docs/IMPLEMENTATION_REFERENCE.md`, `docs/SERVICE_DESIGN.md`.
