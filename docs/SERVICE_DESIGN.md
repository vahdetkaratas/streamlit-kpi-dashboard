# Service design — KPI Dashboard App

Technical flow for this repository.

---

## 1. Pipeline overview

```
CSV (demo or upload)
        │
        ▼
┌───────────────────┐
│ Load + mapping    │  `load.py`, `data_model.py`, `validation.py`
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ KPI computation   │  `kpis.py` — totals, trend, breakdown
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ Dashboard UI      │  `dashboard.py` — Streamlit + Plotly
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ AI insight        │  `ai_insight.py` — rule-based + optional OpenAI
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ Export            │  `export_snapshot.py` — snapshot folder + ZIP
└───────────────────┘
```

**Performance:** After load, aggregate **once** per period; charts use aggregated series, not per-row plotting at scale.

---

## 2. Input / output

| Stage | Format | Description |
|-------|--------|-------------|
| Input | CSV | Sales- or marketing-style rows |
| In memory | `DataFrame` + `ColumnMapping` | Validated, typed dates |
| Output | Web UI | Cards, charts, insight text |

---

## 3. Dashboard sections

| Section | Content |
|---------|---------|
| KPI cards | Revenue / volume / orders or spend / conversions / CTR |
| Trend | Time series on primary trend metric |
| Breakdown | Top dimensions when a dimension column is mapped |
| Filters | Date range; optional compare with previous period |
| Insight | Short “what changed?” text |

Section order: `DATA_AND_METRICS_SPEC.md` §1.

---

## 4. Source modules (actual paths)

| Module | Responsibility |
|--------|----------------|
| `src/load.py` | CSV from disk or upload |
| `src/data_model.py` | Column inference / manual mapping, date handling |
| `src/validation.py` | Schema checks before KPIs |
| `src/kpis.py` | Aggregates and `PeriodKpiSummary` |
| `src/dashboard.py` | Streamlit layout and Plotly figures |
| `src/ai_insight.py` | Insight generation |
| `src/export_snapshot.py` | Snapshot package on disk |
| `src/app_flow.py` | Sidebar orchestration |

---

## 5. KPI types (summary)

Sales-style: revenue, volume, order count, category/region splits.  
Marketing-style: spend, conversions, clicks, impressions, CTR, channel split — see `DATA_AND_METRICS_SPEC.md` §3–4.

---

## 6. Stack

- **UI:** Streamlit  
- **Charts:** Plotly  
- **Data:** pandas  
- **Optional AI:** OpenAI API with rule-based fallback  

---

## 7. UX risk to control

Too many charts reduce clarity; this app targets **two** main charts (trend + breakdown) plus cards (`DATA_AND_METRICS_SPEC.md`).

---

*See also: `DATA_AND_METRICS_SPEC.md`, `IMPLEMENTATION_REFERENCE.md`, `MODULE_BOUNDARIES.md`.*
