# Product overview — KPI Dashboard App

Single-page **business KPI dashboard** for CSV data: KPI cards, trend and breakdown charts, optional period comparison, and a short “what changed?” summary (rule-based with optional OpenAI). Built with **Streamlit**, **Plotly**, and **pandas**.

---

## Who it’s for

Teams and small businesses that want a **practical** view of sales or marketing-style metrics without standing up full BI infrastructure.

---

## Capabilities

- Load **demo** datasets (sales + marketing) or **upload** a CSV
- Automatic or **manual column mapping**; optional **JSON mapping presets**
- **Validation** of required columns, date parse coverage, and numeric fields
- **KPI cards**, **trend** chart, **breakdown** chart (when a dimension is mapped)
- Optional **compare with previous period** on cards
- **Snapshot export** (JSON, CSV, markdown summary, optional chart PNGs) and **ZIP download**
- **Structured logging** and user-facing **error IDs** for support

---

## Out of scope

- Multi-user authentication and role-based access  
- Live database connectors or ETL (CSV-first)  
- Native mobile apps  
- Unlimited ad-hoc chart types or a full KPI formula editor  
- Enterprise BI parity (e.g. Power BI / Tableau replacement)

---

## Limitations

- **Best fit:** Sales and marketing-style tabular CSVs.  
- **Not real-time:** Upload / batch-style data only.  
- **Rough scale:** On the order of **10k–100k rows** without extra performance work.  
- **OpenAI:** When enabled, the API receives **aggregated KPI context only**, not raw CSV rows (see app sidebar note).

---

## Technical reference

| Topic | Document |
|--------|-----------|
| Data contract, KPIs, layout | `DATA_AND_METRICS_SPEC.md` |
| Pipeline and modules (conceptual) | `SERVICE_DESIGN.md` |
| Repo layout, commands, stack ADR | `IMPLEMENTATION_REFERENCE.md` |
| Layer ownership and imports | `MODULE_BOUNDARIES.md` |
| Deploy and verify | `DEPLOYMENT.md` |
