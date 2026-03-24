# Implementation Reference — KPI Dashboard App

**Authoritative stack and layout for this repository.** Planning source files outside `docs/` are not required to use or ship the app.

---

## 1. Repository layout (target)

```
kpi-dashboard-app/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
│
├── data/
│   ├── demo_sales/
│   ├── demo_marketing/
│   └── mapping_presets/    # example JSON mapping presets (committed)
│
├── src/
│   ├── __init__.py
│   ├── load.py
│   ├── data_model.py       # aggregation, date parsing, column mapping
│   ├── mapping_presets.py  # save/load ColumnMapping as JSON
│   ├── metric_guardrails.py # safe ratios (e.g. CTR), finite checks
│   ├── kpis.py             # KPI computation
│   ├── dashboard.py        # Streamlit UI sections / Plotly figures
│   ├── demo_ux.py          # portfolio hero, guide cards, quick demo buttons
│   ├── ui_theme.py         # Plotly light template; optional theme hook (Streamlit default UI)
│   ├── ai_insight.py       # "what changed?" (LLM + rule fallback)
│   ├── app_flow.py         # Streamlit wiring (sidebar → KPIs → export)
│   ├── app_support.py      # small pure helpers for app_flow
│   ├── upload_limits.py    # max upload sizes for CSV / preset JSON
│   └── app.py              # Streamlit entry: `st.set_page_config` (first), then `app_flow`
│
└── tests/
```

At runtime the app creates **`artifacts/`** (gitignored): `exports/`, `logs/`, `mapping_presets/`, and optionally `screenshots/` for documentation or demos.

```
# not in git — example after running the app:
artifacts/
├── exports/          # snapshot-* folders from sidebar export
├── logs/             # app.log (structured events)
├── mapping_presets/  # saved JSON presets
└── screenshots/      # optional; e.g. README screenshots
```

---

## 1b. Module boundaries

For layer ownership and import direction (refactor guardrails), see **`MODULE_BOUNDARIES.md`**.

---

## 2. ADR — UI framework

| Decision | **Streamlit** for the web UI |
|----------|------------------------------|
| Context | Alternatives such as Dash exist; this repo standardizes on one stack. |
| Decision | Use **Streamlit + Plotly** only here. |
| Consequences | Fast iteration for a single-page analytics UI; less custom front-end code. |
| Status | Accepted |

---

## 3. requirements.txt

```
pandas
plotly
streamlit
openai
python-dotenv
pytest
```

---

## 4. KPI column aliases (defaults)

| Role | Example column names |
|------|----------------------|
| Revenue | `amount`, `revenue`, `sales` |
| Volume | `quantity`, `qty` |
| Date | `date`, `order_date`, `created_at`, `campaign_date` |
| Category / dimension | `category`, `product_type`, `region`, `channel` |

Full metric definitions: `DATA_AND_METRICS_SPEC.md`.

---

## 5. Paths (code constants)

```python
from pathlib import Path

DEMO_SALES = Path("data/demo_sales/sales.csv")
DEMO_MARKETING = Path("data/demo_marketing/campaign.csv")
OUTPUT_DIR = Path("artifacts/screenshots")
```

---

## 6. Demo datasets (concrete)

### Demo 1 — Sales / retail

| Field | Value |
|-------|--------|
| Source | Kaggle: [superstore-sales](https://www.kaggle.com/datasets/vivek468/superstore-dataset-final) or [retail-sales](https://www.kaggle.com/datasets/manjeetsingh/retaildataset) |
| File | `data/demo_sales/sales.csv` |
| Columns (typical) | `order_date`, `sales`, `quantity`, `region`, `category`, `product` |
| KPI focus | Revenue, volume, category split, region breakdown, trend |

### Demo 2 — Marketing campaign

| Field | Value |
|-------|--------|
| Source | Kaggle: [Marketing Campaign](https://www.kaggle.com/datasets/rodsaldanha/arketing-campaign) or synthetic |
| File | `data/demo_marketing/campaign.csv` |
| Columns (typical) | `campaign_date`, `channel`, `spend`, `impressions`, `clicks`, `conversions` |
| KPI focus | Spend, conversions, CTR, channel comparison |

If `revenue` is missing, do not fabricate ROI; show “insufficient data” for ROI-style KPIs.

---

## 7. Commands

| Action | Command |
|--------|---------|
| Run app | `streamlit run src/app.py` |
| Tests | `python -m pytest` |

---

## 8. API keys (OpenAI)

Use `.env` with `OPENAI_API_KEY` (see `.env.example`). The app loads variables via `python-dotenv` on startup.

---

## 9. .gitignore

```
__pycache__/
.pytest_cache/
.venv/
venv/
*.pyc
.env
artifacts/
```

---

## 10. README checklist

- [ ] Repo name: `kpi-dashboard-app` (or your chosen name)
- [ ] Description: KPI dashboard, trend charts, optional AI summary
- [ ] Metric definitions — which KPIs appear on the dashboard
- [ ] Data schema — required and optional columns
- [ ] Two demos: sales + marketing

