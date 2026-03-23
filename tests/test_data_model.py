from __future__ import annotations

import pandas as pd

from src.data_model import infer_mapping


def test_infer_mapping_sales():
    df = pd.DataFrame(
        {
            "order_date": ["2026-01-01", "2026-01-02"],
            "sales": [10.0, 20.0],
            "quantity": [1, 2],
            "category": ["A", "B"],
            "order_id": [1, 2],
        }
    )
    mapping = infer_mapping(df)
    assert mapping.profile == "sales"
    assert mapping.date_col == "order_date"
    assert mapping.revenue_col == "sales"
    assert mapping.volume_col == "quantity"
    assert mapping.dimension_col == "category"

