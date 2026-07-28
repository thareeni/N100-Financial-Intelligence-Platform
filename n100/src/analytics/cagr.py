"""
Compound Annual Growth Rate (CAGR) Calculation Engine.
Handles all sign combination edge cases and returns (cagr_value, flag).
"""

from typing import Tuple, Optional, Any


def calculate_cagr(start_val: Any, end_val: Any, num_years: int) -> Tuple[Optional[float], str]:
    """
    Calculate CAGR % over num_years.
    Formula: ((end_val / start_val) ** (1 / num_years) - 1) * 100

    Returns Tuple of (cagr_value_pct, flag_status):
    - (val, "NORMAL"): Both positive
    - (None, "TURNAROUND"): Start negative, end positive
    - (None, "DECLINE_TO_LOSS"): Start positive, end negative
    - (None, "BOTH_NEGATIVE"): Both start and end negative
    - (None, "ZERO_BASE"): Base value is zero
    - (None, "INSUFFICIENT"): num_years < 3 or missing values
    """
    if start_val is None or end_val is None:
        return (None, "INSUFFICIENT")

    try:
        start = float(start_val)
        end = float(end_val)
    except (ValueError, TypeError):
        return (None, "INSUFFICIENT")

    if num_years < 3:
        return (None, "INSUFFICIENT")

    if start == 0.0:
        return (None, "ZERO_BASE")

    if start > 0 and end > 0:
        cagr = ((end / start) ** (1.0 / float(num_years)) - 1.0) * 100.0
        return (round(cagr, 4), "NORMAL")

    if start > 0 and end < 0:
        return (None, "DECLINE_TO_LOSS")

    if start < 0 and end > 0:
        return (None, "TURNAROUND")

    if start < 0 and end < 0:
        return (None, "BOTH_NEGATIVE")

    return (None, "UNKNOWN")
