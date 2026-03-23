# KPI Dashboard App

Single-page KPI dashboard for CSV-based marketing or sales metrics:
- KPI cards
- trend chart
- breakdown chart
- short “what changed?” summary (rule-based, optional OpenAI enhancement)
- optional period compare deltas on KPI cards (absolute + %)
- snapshot export folder + **Download snapshot ZIP** from the sidebar
- manual column mapping for ambiguous CSV schemas
- JSON mapping presets (upload, save to disk, reload for repeat datasets)
- explicit schema validation with date coverage and numeric coercion checks
- metric guardrails: safe CTR ratio; optional minimum rows per period before showing KPIs
- **Insight tone** (neutral / executive / brief) for rule-based and OpenAI “what changed?” text
- **Compact layout** sidebar mode for denser screenshare views

The implementation follows the scope in `docs/` and keeps MVP intentionally narrow.

## Quick start

### 1) Install dependencies

```bash
pip install -r requirements.txt
```

### 2) Run the app

```bash
streamlit run src/app.py
```

The app version is read from `VERSION` and shown in the sidebar.

### 3) Optional OpenAI setup

Create `.env` from `.env.example`:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

If no API key is present, the app automatically uses the rule-based insight text.

When OpenAI is enabled, the model receives **only pre-aggregated KPIs** (totals, date ranges, top breakdown)—**not** the raw CSV. The sidebar states this when an API key is configured.

Use **Insight tone** in the sidebar to change wording only (same KPI facts). **Compact layout** reduces chart height and heading size for calls and demos.

**Upload limits:** CSV uploads are capped at **25 MB**; mapping preset JSON at **512 KB** (see `src/upload_limits.py`). Oversized files are rejected with an error ID before parsing.

**CI:** With the repo on GitHub, `.github/workflows/ci.yml` runs tests and a small import check on push/PR to `main` or `master`.

### 4) CSV onboarding options

- **Auto-detect** (default): tries aliases for date/metric/dimension columns.
- **Manual mapping**: user selects profile and required columns when auto mapping is ambiguous.
- **Upload preset (JSON)**: load a saved mapping file (see `data/mapping_presets/example_sales.json` for shape).
- **Saved preset**: lists `.json` files under `artifacts/mapping_presets/` (use **Save current mapping** in the sidebar after a successful run).

Preset files use `schema_version: 1` and mirror the fields on `ColumnMapping` (`profile`, `date_col`, `revenue_col` / `spend_col`, optional columns, `trend_metric_col`, `trend_metric_label`).

### 5) KPI guardrails (sidebar)

- **Minimum rows in period for KPIs**: if the filtered date range has fewer rows than this value, that period’s KPI numbers, trend, and breakdown are omitted (shown as N/A / empty). Set to **0** to disable.
- Marketing **CTR** is computed only when impressions are a finite number `> 0` (no divide-by-zero).

## Features (overview)

- Streamlit single-page dashboard (`src/app.py` → `src/app_flow.py`, `src/dashboard.py`)
- CSV upload or built-in demos (`src/load.py`); column mapping and validation (`src/data_model.py`, `src/validation.py`)
- KPI totals, trend, breakdown (`src/kpis.py`); optional period compare
- “What changed?” — rule-based and optional OpenAI (`src/ai_insight.py`)
- Snapshot export + ZIP; mapping presets; structured logging and error IDs
- Demo data: `data/demo_sales/sales.csv`, `data/demo_marketing/campaign.csv`
- Tests under `tests/` (`python -m pytest`)

App version is read from `VERSION`.

## Target users

- Operations managers
- Sales managers
- Marketing leads
- Small business owners who need KPI visibility without full BI setup

## Information architecture (MVP)

- **Single-page** layout (no tabs in MVP)
- Section order:
  1. KPI cards
  2. trend chart
  3. breakdown chart
  4. “what changed?” summary
- Chart cap for MVP: **2 charts** (trend + breakdown)

## Data schema (minimum contract)

Required:
- one date column (`date`, `order_date`, `created_at`, `campaign_date`, ...)
- at least one metric column (`sales`, `revenue`, `amount`, `spend`, `conversions`, ...)

Optional but recommended:
- one dimension column (`category`, `region`, `product`, `channel`)

If required fields are missing, the app shows a preparation error and stops safely.

## Default KPI sets

### Sales / retail demo
- Revenue (sum)
- Volume (sum)
- Orders / rows (nunique order_id or row count)
- Revenue trend
- Category/region breakdown (if available)

### Marketing campaign demo
- Spend (sum)
- Conversions (sum)
- CTR (`clicks / impressions`)
- Spend trend
- Channel breakdown

## Repository structure

```text
9_kpi_dashboard_app/
├── data/           # demo CSVs + example mapping preset (committed)
├── src/            # app entry: app.py → app_flow.py; see docs/IMPLEMENTATION_REFERENCE.md
├── tests/
├── docs/
├── requirements.txt
└── .env.example
```

Runtime folder **`artifacts/`** (exports, logs, saved presets, optional screenshots) is created automatically and is **gitignored**.

## Demo screenshots

The **`artifacts/`** folder is **not** committed (see `.gitignore`); the app creates it when you export, save presets, or log events. For README or doc screenshots, create `artifacts/screenshots/` locally and drop files there, for example:

- Sales dashboard (desktop): `artifacts/screenshots/sales-dashboard-desktop.png`
- Marketing dashboard (desktop): `artifacts/screenshots/marketing-dashboard-desktop.png`
- Mobile-friendly preview: `artifacts/screenshots/dashboard-mobile-preview.png`

## Snapshot export

1. Click **Export snapshot package** to write a timestamped folder under `artifacts/exports/snapshot-<profile>-<timestamp>/`.
2. Click **Download snapshot ZIP** (appears after a successful export) to fetch a ZIP of that folder in the browser.

Each snapshot bundle contains:
- `snapshot.json` (metadata + KPI totals for current/previous period)
- `SNAPSHOT_SUMMARY.md` (human-readable handoff: ranges, totals tables, guardrails, insight)
- `validation_report.json` (schema/date/numeric validation summary)
- `trend.csv`
- `breakdown.csv` (if a dimension chart exists)
- `insight.txt`
- `trend.png` and `breakdown.png` (when image export engine is available)

## Documentation map

| Start here | Purpose |
|------------|---------|
| [docs/README.md](docs/README.md) | Reading order and quick reference |
| [docs/PRODUCT.md](docs/PRODUCT.md) | Product scope, capabilities, limitations |
| [docs/DATA_AND_METRICS_SPEC.md](docs/DATA_AND_METRICS_SPEC.md) | KPI definitions and CSV contract |
| [docs/SERVICE_DESIGN.md](docs/SERVICE_DESIGN.md) | Technical pipeline |
| [docs/IMPLEMENTATION_REFERENCE.md](docs/IMPLEMENTATION_REFERENCE.md) | Stack ADR, paths, commands |
| [docs/MODULE_BOUNDARIES.md](docs/MODULE_BOUNDARIES.md) | Module layers and allowed dependencies |
| [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | Deploy, environment, verification |

Canonical specifications for this project live under **`docs/`** (English).
