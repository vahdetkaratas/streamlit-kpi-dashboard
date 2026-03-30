# KPI Dashboard App

Single-page **Streamlit** dashboard for **sales or marketing** CSVs: built-in demos or your own upload, column mapping (auto, manual, or JSON presets), then KPI cards, **trend** and **breakdown** charts, optional **compare to the previous period**, a short **“what changed?”** blurb (rules by default), and **snapshot export** (folder + ZIP in the sidebar).

**Stack:** pandas, Plotly, Streamlit. Optional **OpenAI** only sees aggregated KPI context when enabled—not raw rows.

**Live demo:** [kpi-dashboard.vahdetkaratas.com](https://kpi-dashboard.vahdetkaratas.com/)

## Run

Requires **Python 3.11+** (matches `Dockerfile`).

```bash
pip install -r requirements.txt
streamlit run src/app.py
```

Version comes from `VERSION` (shown in the sidebar).

## OpenAI (optional)

Copy `.env.example` to `.env` and set `OPENAI_API_KEY`. Without it, the app uses rule-based insight text only. When enabled, only aggregated KPIs are sent to the API—not raw CSV rows.

## Limits

- CSV upload: max **25 MB**; mapping preset JSON: max **512 KB** (`src/upload_limits.py`).

## Tests

```bash
python -m pytest
```

CI runs on push/PR via `.github/workflows/ci.yml`.

## Export

Sidebar **Export snapshot package** writes under `artifacts/exports/`; **Download snapshot ZIP** appears after a successful export. `artifacts/` is gitignored.

## Sample data

Demo CSVs and an example mapping preset live under `data/` (e.g. `data/demo_sales/`, `data/demo_marketing/`).

## Container (optional)

```bash
docker build -t kpi-dashboard .
docker run --rm -p 8501:8501 kpi-dashboard
```

Then open `http://localhost:8501`.
