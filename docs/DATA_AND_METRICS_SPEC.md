# Data Contract and Default Metrics

**Minimum columns**, **KPI definitions**, and **layout** for MVP and demo datasets. Implementation and customer-facing README should align with this spec.

---

## 1. Layout decision (MVP)

| Decision | Choice |
|----------|--------|
| Structure | **Single page**, vertical scroll |
| Sections | Top: KPI cards → trend → breakdown charts → AI summary (bottom or optional narrow side column) |
| Tabs | Not in MVP (V2) |

---

## 2. Global minimum contract (any CSV)

The app cannot build a meaningful dashboard without:

| Role | Required? | Example column names (aliases) |
|------|-----------|---------------------------------|
| Date | **Required** | `date`, `order_date`, `created_at`, `campaign_date` |
| Metric (≥1) | **Required** | `amount`, `revenue`, `sales`, `quantity`, `spend`, `conversions`, … |
| Breakdown dimension | Optional (recommended) | `category`, `region`, `product`, `channel` |

**Rule:** Map columns from a known alias list; if ambiguous, offer simple UI controls (dropdowns) for date / primary metric / dimension in MVP.

---

## 3. Demo 1 — Sales / retail (default KPIs)

**File:** `data/demo_sales/sales.csv` (see `IMPLEMENTATION_REFERENCE.md`)

| KPI / view | Logic | Typical columns |
|------------|--------|-----------------|
| Total revenue | `sum(sales or amount)` | `sales`, `amount` |
| Total volume | `sum(quantity)` | `quantity` |
| Order / row count | `count(*)` or `nunique(order_id)` | rows or `order_id` |
| Trend | Revenue or volume by day/week | date + metric |
| Category split | Revenue or count by `category` | `category` |
| Region split (if present) | Same by `region` | `region` |

**MVP chart target:** 2–3 charts (e.g. revenue trend, category bar/pie, optional region).

---

## 4. Demo 2 — Marketing campaign (default KPIs)

**File:** `data/demo_marketing/campaign.csv`

| KPI / view | Logic | Typical columns |
|------------|--------|-----------------|
| Total spend | `sum(spend)` | `spend`, `cost` |
| Conversions | `sum(conversions)` | `conversions` |
| Clicks / impressions | `sum(clicks)`, `sum(impressions)` | `clicks`, `impressions` |
| CTR | `clicks / impressions` where `impressions > 0` | derived |
| Channel split | Spend or conversions by `channel` | `channel` |
| Trend | Daily/weekly spend or conversions | `campaign_date` + metric |

**Note:** If there is no `revenue`, omit ROI or show “insufficient data”; do not force ROI.

---

## 5. AI “What changed?” — input / output

| Field | Spec |
|-------|------|
| Recommended input | For selected range vs **previous period of equal length**: totals (revenue or spend, volume), top category/channel, simple % deltas |
| Output cap | ~120–200 words **or** 4–6 bullets; UI language configurable per client or locale |
| No API | Rule-based summary: “X up/down ~Y%”, “top category Z” |

Do **not** send raw CSV rows to the model — cost and privacy.

---

## 6. Default stack (implementation)

This repository: **Streamlit + Plotly + pandas** (`IMPLEMENTATION_REFERENCE.md` §2–3).

---

## 7. Out of scope (product)

- Multi-user authentication and role-based access  
- Live database / ETL pipelines; CSV is the primary input  
- Native mobile clients  
- Arbitrary chart-type requests or a full KPI formula editor  

Details: `PRODUCT.md`.

---

*See also: `IMPLEMENTATION_REFERENCE.md` §3–6, `SERVICE_DESIGN.md`, `PRODUCT.md`*
