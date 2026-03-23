from __future__ import annotations

import io
from pathlib import Path
from typing import Any, Dict, Union

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DEMO_SALES_PATH = PROJECT_ROOT / "data/demo_sales/sales.csv"
DEMO_MARKETING_PATH = PROJECT_ROOT / "data/demo_marketing/campaign.csv"


def load_csv_from_path(path: Union[str, Path]) -> pd.DataFrame:
    """Load a CSV file into a pandas DataFrame."""
    return pd.read_csv(path)


def load_csv_uploaded(uploaded_file: Any) -> pd.DataFrame:
    """Load a CSV from Streamlit's UploadedFile (file-like object)."""
    return pd.read_csv(uploaded_file)


def load_csv_from_bytes(data: bytes) -> pd.DataFrame:
    """Load CSV from raw bytes (after size checks)."""
    return pd.read_csv(io.BytesIO(data))


def get_demo_sources() -> Dict[str, Path]:
    return {
        "Demo Sales": DEMO_SALES_PATH,
        "Demo Marketing": DEMO_MARKETING_PATH,
    }
