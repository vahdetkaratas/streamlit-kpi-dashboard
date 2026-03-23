from __future__ import annotations

from typing import Literal, Optional

from .kpis import PeriodKpiSummary

InsightTone = Literal["neutral", "executive", "brief"]


def _fmt_number(x: Optional[float]) -> str:
    if x is None:
        return "N/A"
    if abs(x) >= 1_000_000:
        return f"{x/1_000_000:.2f}M"
    if abs(x) >= 1_000:
        return f"{x/1_000:.2f}K"
    return f"{x:.2f}"


def _pct_change(current: Optional[float], previous: Optional[float]) -> Optional[float]:
    if current is None or previous is None:
        return None
    if previous == 0:
        return None
    return (current - previous) / previous * 100.0


def _rule_parts(current: PeriodKpiSummary, previous: PeriodKpiSummary) -> dict:
    metric_name = "Revenue" if current.profile == "sales" else "Spend"
    anchor_current = current.totals.get(metric_name)
    anchor_previous = previous.totals.get(metric_name)

    anchor_pct = _pct_change(anchor_current, anchor_previous)
    if anchor_pct is None:
        change_text = "a change compared to the previous period"
    else:
        direction = "up" if anchor_pct >= 0 else "down"
        change_text = f"{direction} by {abs(anchor_pct):.1f}%"

    secondary_line = ""
    if current.profile == "sales":
        sec_current = current.totals.get("Volume")
        sec_prev = previous.totals.get("Volume")
        pct = _pct_change(sec_current, sec_prev)
        if sec_current is not None and pct is not None:
            direction = "up" if pct >= 0 else "down"
            secondary_line = f"- Volume is {direction} ({abs(pct):.1f}%).\n"
    else:
        ctr_current = current.totals.get("CTR")
        ctr_prev = previous.totals.get("CTR")
        pct = _pct_change(ctr_current, ctr_prev)
        if ctr_current is not None and pct is not None:
            direction = "up" if pct >= 0 else "down"
            secondary_line = f"- CTR is {direction} ({abs(pct):.1f}%).\n"

    breakdown_line = ""
    if current.breakdown is not None and len(current.breakdown) > 0:
        top_dim = str(current.breakdown.iloc[0]["dimension"])
        top_val = float(current.breakdown.iloc[0]["value"])

        prev_val = None
        if previous.breakdown is not None and len(previous.breakdown) > 0:
            match = previous.breakdown[previous.breakdown["dimension"] == top_dim]
            if not match.empty:
                prev_val = float(match.iloc[0]["value"])

        if prev_val is None:
            breakdown_line = f"- Top {top_dim} leads the period with {_fmt_number(top_val)}.\n"
        else:
            pct = _pct_change(top_val, prev_val)
            if pct is None:
                breakdown_line = f"- Top {top_dim} leads with {_fmt_number(top_val)}.\n"
            else:
                direction = "higher" if pct >= 0 else "lower"
                breakdown_line = (
                    f"- Top {top_dim} is {direction} by {abs(pct):.1f}% "
                    f"({_fmt_number(top_val)} vs {_fmt_number(prev_val)}).\n"
                )

    date_range_text = f"{current.start_date:%Y-%m-%d} to {current.end_date:%Y-%m-%d}"
    prev_range_text = f"{previous.start_date:%Y-%m-%d} to {previous.end_date:%Y-%m-%d}"

    return {
        "metric_name": metric_name,
        "anchor_current": anchor_current,
        "anchor_previous": anchor_previous,
        "change_text": change_text,
        "secondary_line": secondary_line,
        "breakdown_line": breakdown_line,
        "date_range_text": date_range_text,
        "prev_range_text": prev_range_text,
    }


def _assemble_rule_neutral(parts: dict) -> str:
    metric_name = parts["metric_name"]
    anchor_line = (
        f"In {parts['date_range_text']}, {metric_name} is "
        f"{_fmt_number(parts['anchor_current'])} ({parts['change_text']}).\n"
    )
    return (
        anchor_line
        + f"Compared with {parts['prev_range_text']}.\n"
        + parts["secondary_line"]
        + parts["breakdown_line"]
    ).strip()


def _assemble_rule_executive(parts: dict) -> str:
    metric_name = parts["metric_name"]
    summary = (
        f"Summary: In {parts['date_range_text']}, {metric_name} is "
        f"{_fmt_number(parts['anchor_current'])} ({parts['change_text']}). "
        f"Prior window: {parts['prev_range_text']} "
        f"(previous {metric_name}: {_fmt_number(parts['anchor_previous'])}).\n"
    )
    detail = ""
    if parts["secondary_line"]:
        detail += parts["secondary_line"]
    if parts["breakdown_line"]:
        detail += parts["breakdown_line"]
    return (summary + detail).strip()


def _assemble_rule_brief(parts: dict) -> str:
    metric_name = parts["metric_name"]
    lines = [
        f"{metric_name} {_fmt_number(parts['anchor_current'])} ({parts['change_text']}). "
        f"{parts['date_range_text']}.",
        f"Prior: {parts['prev_range_text']}.",
    ]
    if parts["breakdown_line"].strip():
        lines.append(parts["breakdown_line"].strip())
    elif parts["secondary_line"].strip():
        lines.append(parts["secondary_line"].strip())
    return "\n".join(lines)


def rule_based_what_changed(
    current: PeriodKpiSummary,
    previous: PeriodKpiSummary,
    *,
    tone: InsightTone = "neutral",
) -> str:
    parts = _rule_parts(current, previous)
    if tone == "executive":
        return _assemble_rule_executive(parts)
    if tone == "brief":
        return _assemble_rule_brief(parts)
    return _assemble_rule_neutral(parts)


def openai_system_prompt_for_tone(tone: InsightTone) -> str:
    base = (
        "You are a KPI assistant. Write a 'what changed?' summary for a business dashboard. "
        "Use ONLY numbers and labels from the user message. Do not invent metrics, segments, "
        "causes, or values. If a figure is missing or N/A, do not substitute a guess. "
        "Write in English."
    )
    if tone == "neutral":
        return (
            base
            + " Output 3–6 lines starting with '- ' (bullet style). No title line. "
            "Stay factual; avoid opinions and hedging."
        )
    if tone == "executive":
        return (
            base
            + " Output 3–4 bullets starting with '- '. Lead with the main metric vs prior period, "
            "then supporting points. Professional, concise tone suitable for leadership."
        )
    return (
        base
        + " Output at most 3 short bullets starting with '- '. "
        "Total under 90 words. No filler phrases."
    )


def _openai_user_prompt_constraints() -> str:
    return (
        "\nConstraints (must follow):\n"
        "- Use only numbers that appear in this message; do not extrapolate.\n"
        "- Do not introduce new KPIs, dimensions, or time ranges.\n"
        "- If percent change is blank, say change is not stated from the inputs.\n"
    )


def openai_what_changed(
    current: PeriodKpiSummary,
    previous: PeriodKpiSummary,
    *,
    tone: InsightTone = "neutral",
) -> str:
    """
    Optional OpenAI enhancement.

    This function must not rely on raw CSV rows; it uses only precomputed KPI
    totals and top breakdown values.
    """
    import os

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured.")

    from openai import OpenAI

    metric_name = "Revenue" if current.profile == "sales" else "Spend"
    anchor_current = current.totals.get(metric_name)
    anchor_previous = previous.totals.get(metric_name)
    anchor_pct = _pct_change(anchor_current, anchor_previous)

    top_dim = None
    top_current = None
    top_previous = None
    if current.breakdown is not None and not current.breakdown.empty:
        top_dim = str(current.breakdown.iloc[0]["dimension"])
        top_current = float(current.breakdown.iloc[0]["value"])
        if previous.breakdown is not None and not previous.breakdown.empty:
            match = previous.breakdown[previous.breakdown["dimension"] == top_dim]
            if not match.empty:
                top_previous = float(match.iloc[0]["value"])

    date_range_text = f"{current.start_date:%Y-%m-%d} to {current.end_date:%Y-%m-%d}"
    prev_range_text = f"{previous.start_date:%Y-%m-%d} to {previous.end_date:%Y-%m-%d}"

    system_prompt = openai_system_prompt_for_tone(tone)

    pct_text = "" if anchor_pct is None else f"{anchor_pct:.1f}%"
    user_prompt = (
        f"Current period: {date_range_text}\n"
        f"Previous period: {prev_range_text}\n\n"
        f"Main metric: {metric_name}\n"
        f"- Current: {_fmt_number(anchor_current)}\n"
        f"- Previous: {_fmt_number(anchor_previous)}\n"
        f"- Percent change (only if computable from inputs): {pct_text}\n\n"
    )

    if current.profile == "sales":
        vol_c = current.totals.get("Volume")
        vol_p = previous.totals.get("Volume")
        orders_c = current.totals.get("Orders")
        orders_p = previous.totals.get("Orders")
        user_prompt += (
            "Other KPI totals:\n"
            f"- Volume current: {_fmt_number(vol_c)}; previous: {_fmt_number(vol_p)}\n"
            f"- Orders current: {_fmt_number(orders_c)}; previous: {_fmt_number(orders_p)}\n\n"
        )
    else:
        conv_c = current.totals.get("Conversions")
        conv_p = previous.totals.get("Conversions")
        ctr_c = current.totals.get("CTR")
        ctr_p = previous.totals.get("CTR")
        ctr_current_text = "" if ctr_c is None else f"{ctr_c*100:.1f}%"
        ctr_previous_text = "" if ctr_p is None else f"{ctr_p*100:.1f}%"
        user_prompt += (
            "Other KPI totals:\n"
            f"- Conversions current: {_fmt_number(conv_c)}; previous: {_fmt_number(conv_p)}\n"
            f"- CTR current: {ctr_current_text}; previous: {ctr_previous_text}\n\n"
        )

    if top_dim is not None:
        user_prompt += (
            "Top breakdown mover (dimension):\n"
            f"- Dimension: {top_dim}\n"
            f"- Current value: {_fmt_number(top_current)}\n"
            f"- Previous value: {_fmt_number(top_previous)}\n\n"
        )

    user_prompt += _openai_user_prompt_constraints()

    client = OpenAI(api_key=api_key)
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.2,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    content = resp.choices[0].message.content or ""
    return content.strip() if content.strip() else rule_based_what_changed(current, previous, tone=tone)
