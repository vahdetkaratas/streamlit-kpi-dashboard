from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from src.data_model import ColumnMapping

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PRESETS_DIR = PROJECT_ROOT / "artifacts" / "mapping_presets"

SCHEMA_VERSION = 1


def serialize_mapping(mapping: ColumnMapping) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "profile": mapping.profile,
        "date_col": mapping.date_col,
        "revenue_col": mapping.revenue_col,
        "volume_col": mapping.volume_col,
        "order_id_col": mapping.order_id_col,
        "spend_col": mapping.spend_col,
        "conversions_col": mapping.conversions_col,
        "clicks_col": mapping.clicks_col,
        "impressions_col": mapping.impressions_col,
        "dimension_col": mapping.dimension_col,
        "trend_metric_col": mapping.trend_metric_col,
        "trend_metric_label": mapping.trend_metric_label,
    }


def deserialize_mapping(data: dict[str, Any]) -> ColumnMapping:
    if int(data.get("schema_version", 0)) != SCHEMA_VERSION:
        raise ValueError(f"Unsupported preset schema_version (expected {SCHEMA_VERSION}).")

    profile = data.get("profile")
    if profile not in ("sales", "marketing"):
        raise ValueError("Preset must include profile: 'sales' or 'marketing'.")

    date_col = data.get("date_col")
    trend_metric_col = data.get("trend_metric_col")
    trend_metric_label = data.get("trend_metric_label") or ""

    if not date_col or not isinstance(date_col, str):
        raise ValueError("Preset must include a non-empty date_col string.")
    if not trend_metric_col or not isinstance(trend_metric_col, str):
        raise ValueError("Preset must include a non-empty trend_metric_col string.")

    return ColumnMapping(
        profile=profile,  # type: ignore[arg-type]
        date_col=date_col,
        revenue_col=data.get("revenue_col"),
        volume_col=data.get("volume_col"),
        order_id_col=data.get("order_id_col"),
        spend_col=data.get("spend_col"),
        conversions_col=data.get("conversions_col"),
        clicks_col=data.get("clicks_col"),
        impressions_col=data.get("impressions_col"),
        dimension_col=data.get("dimension_col"),
        trend_metric_col=trend_metric_col,
        trend_metric_label=str(trend_metric_label),
    )


def list_saved_preset_names() -> list[str]:
    PRESETS_DIR.mkdir(parents=True, exist_ok=True)
    return sorted(p.stem for p in PRESETS_DIR.glob("*.json"))


def load_preset_by_name(name: str) -> ColumnMapping:
    safe = _sanitize_preset_name(name)
    path = PRESETS_DIR / f"{safe}.json"
    if not path.is_file():
        raise FileNotFoundError(f"Preset not found: {safe}")
    return load_preset_from_path(path)


def load_preset_from_path(path: Path) -> ColumnMapping:
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("Preset file must contain a JSON object.")
    return deserialize_mapping(data)


def load_preset_from_bytes(raw: bytes) -> ColumnMapping:
    data = json.loads(raw.decode("utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Preset file must contain a JSON object.")
    return deserialize_mapping(data)


def save_preset(name: str, mapping: ColumnMapping) -> Path:
    safe = _sanitize_preset_name(name)
    if not safe:
        raise ValueError("Preset name is empty after sanitization.")

    PRESETS_DIR.mkdir(parents=True, exist_ok=True)
    path = PRESETS_DIR / f"{safe}.json"
    path.write_text(json.dumps(serialize_mapping(mapping), indent=2), encoding="utf-8")
    return path


def _sanitize_preset_name(name: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9._-]+", "_", (name or "").strip())
    return cleaned.strip("._-")[:80]
