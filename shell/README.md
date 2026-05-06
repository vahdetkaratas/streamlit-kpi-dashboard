# Multi-profile static shell (KPI dashboard)

Source for recruiter vs commercial landing pages. Project facts and body copy live in `shell/projects/` and `shell/body/`; identity sidebar comes from `shell/profiles/`.

## Render

From the repository root (requires Node.js):

```bash
node shell/render-shell.mjs --project shell/projects/kpi-dashboard.json --body shell/body/kpi-dashboard.html --out layout-shell --profile recruiter

node shell/render-shell.mjs --project shell/projects/kpi-dashboard.json --body shell/body/kpi-dashboard.html --out layout-shell-commercial --profile commercial
```

Outputs per target directory:

- `index.html`, `shell.css`, `demo-content.css`, `shell.js`, `favicon.svg`, `profile.json`

Do not edit `layout-shell*` by hand; change `shell/` and re-run the commands.

## Files

- `index.html` — template with `{{PLACEHOLDER}}` tokens
- `render-shell.mjs` — merges profile + project JSON and body partial
- `profiles/recruiter.json`, `profiles/commercial.json` — sidebar identity
- `projects/kpi-dashboard.json` — KPI project metadata and per-profile overrides
- `body/kpi-dashboard.html` — long-form HTML partial (no Streamlit / API coupling)
