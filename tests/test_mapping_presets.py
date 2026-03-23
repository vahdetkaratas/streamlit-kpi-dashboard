import json

import pytest

from src.data_model import ColumnMapping
from src.mapping_presets import (
    deserialize_mapping,
    load_preset_from_bytes,
    save_preset,
    serialize_mapping,
)


def test_serialize_deserialize_roundtrip():
    m = ColumnMapping(
        profile="sales",
        date_col="order_date",
        revenue_col="sales",
        volume_col="qty",
        order_id_col="order_id",
        dimension_col="region",
        trend_metric_col="sales",
        trend_metric_label="Revenue",
    )
    d = serialize_mapping(m)
    m2 = deserialize_mapping(d)
    assert m2 == m


def test_deserialize_rejects_bad_schema():
    with pytest.raises(ValueError, match="schema_version"):
        deserialize_mapping({"schema_version": 99, "profile": "sales"})


def test_load_preset_from_bytes_invalid_json():
    with pytest.raises(json.JSONDecodeError):
        load_preset_from_bytes(b"not json")


def test_save_preset_roundtrip(tmp_path, monkeypatch):
    import src.mapping_presets as mp

    monkeypatch.setattr(mp, "PRESETS_DIR", tmp_path)

    m = ColumnMapping(
        profile="marketing",
        date_col="campaign_date",
        spend_col="cost",
        conversions_col="conv",
        trend_metric_col="cost",
        trend_metric_label="Spend",
    )
    path = save_preset("my_client", m)
    assert path.is_file()
    raw = path.read_bytes()
    m2 = load_preset_from_bytes(raw)
    assert m2.profile == "marketing"
    assert m2.date_col == "campaign_date"
