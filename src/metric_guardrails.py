from __future__ import annotations

import math
from typing import Optional


def safe_ratio(numerator: Optional[float], denominator: Optional[float]) -> Optional[float]:
    """
    Return numerator / denominator when the denominator is a finite number strictly greater than zero.
    Used for rates such as CTR to avoid divide-by-zero and non-finite results.
    """
    if numerator is None or denominator is None:
        return None
    try:
        n = float(numerator)
        d = float(denominator)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(n) or not math.isfinite(d) or d <= 0:
        return None
    out = n / d
    return out if math.isfinite(out) else None
