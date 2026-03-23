# Deployment and verification

## Deployment options

1. **Streamlit Community Cloud** — connect the repo, set secrets if using OpenAI.  
2. **Container / VM** — Python image, install `requirements.txt`, expose Streamlit’s port.

**Run locally or in production:**

```bash
pip install -r requirements.txt
streamlit run src/app.py
```

**Headless example:**

```bash
streamlit run src/app.py --server.headless true --server.port 8501
```

---

## Environment variables

| Variable | Required | Purpose |
|----------|----------|---------|
| *(none)* | — | App runs with rule-based insight by default |
| `OPENAI_API_KEY` | Optional | Enhanced “what changed?” text |

Use `.env.example` as a template for local development (`python-dotenv` loads `.env` on startup).

---

## Pre-flight checklist

- [ ] Dependencies install cleanly (`pip install -r requirements.txt`)
- [ ] App starts: `streamlit run src/app.py`
- [ ] Sidebar shows app **version** (`VERSION` file)
- [ ] **Demo Sales** and **Demo Marketing** render end-to-end
- [ ] **Upload CSV** path works for a small sample file
- [ ] **Export snapshot** creates output under `artifacts/exports/` (folder is gitignored)
- [ ] With no API key, OpenAI option is disabled and rule-based insight works
- [ ] With API key, OpenAI path works or falls back safely on failure

---

## Verification checklist

- [ ] KPI cards, trend, and breakdown (when dimension exists) for both demos
- [ ] Period compare toggle affects KPI deltas
- [ ] Manual mapping can recover from ambiguous uploads
- [ ] Structured log output appears under `artifacts/logs/app.log` when the app runs
- [ ] Errors shown in the UI include an **error ID** when applicable

**Automated tests:**

```bash
python -m pytest -q
```

---

## Operations notes

- Keep **`VERSION`** aligned with releases you tag or ship.  
- Runtime logs: JSON-lines style events in `artifacts/logs/app.log`.  
- Use **error IDs** from the UI to correlate with log lines when debugging.
