"""
ETL Data Normaliser Module.
Provides ticker and financial year normalization functions.
"""

import re
from typing import Any, Optional

MONTH_MAP = {
    "jan": "01", "january": "01",
    "feb": "02", "february": "02",
    "mar": "03", "march": "03",
    "apr": "04", "april": "04",
    "may": "05",
    "jun": "06", "june": "06",
    "jul": "07", "july": "07",
    "aug": "08", "august": "08",
    "sep": "09", "september": "09",
    "oct": "10", "october": "10",
    "nov": "11", "november": "11",
    "dec": "12", "december": "12"
}


def normalize_ticker(val: Any) -> str:
    """
    Normalise company ticker to uppercase stripped string.
    Returns 'MISSING' if empty or NaN.
    """
    if val is None or (isinstance(val, float) and str(val) == "nan"):
        return "MISSING"
    
    s = str(val).strip().upper()
    if not s or s == "NAN":
        return "MISSING"
    
    return s


def normalize_year(val: Any) -> str:
    """
    Standardise financial year labels to 'YYYY-MM' format.
    Handles variants like Mar-23, FY23, March-2023, 2023, Dec-22, Jun-23, 2023-03.
    Returns 'PARSE_ERROR' for invalid formats.
    """
    if val is None or (isinstance(val, float) and str(val) == "nan"):
        return "PARSE_ERROR"

    s = str(val).strip()
    if not s or s.upper() == "NAN":
        return "PARSE_ERROR"

    # Already YYYY-MM format
    if re.match(r"^\d{4}-\d{2}$", s):
        return s

    # FY prefix, e.g., FY23, FY2023, FY 23
    fy_match = re.match(r"^FY\s*(\d{2}|\d{4})$", s, re.IGNORECASE)
    if fy_match:
        yr_str = fy_match.group(1)
        if len(yr_str) == 2:
            yr = int(yr_str)
            full_yr = 2000 + yr if yr < 80 else 1900 + yr
        else:
            full_yr = int(yr_str)
        return f"{full_yr:04d}-03"

    # Plain 4-digit year, e.g., 2023, 2024
    if re.match(r"^\d{4}$", s):
        return f"{int(s):04d}-03"

    # Plain 2-digit year (e.g. 23)
    if re.match(r"^\d{2}$", s):
        yr = int(s)
        full_yr = 2000 + yr if yr < 80 else 1900 + yr
        return f"{full_yr:04d}-03"

    # Month-Year formats, e.g. Mar-23, Mar 23, March-2023, Dec-22, Jun-23, Mar 2016 9m
    my_match = re.match(r"^([a-zA-Z]+)[-\s]+(\d{2}|\d{4})(?:\s+.*)?$", s)
    if my_match:
        month_str = my_match.group(1).lower()
        yr_str = my_match.group(2)
        
        if month_str not in MONTH_MAP:
            return "PARSE_ERROR"
        
        mm = MONTH_MAP[month_str]
        if len(yr_str) == 2:
            yr = int(yr_str)
            full_yr = 2000 + yr if yr < 80 else 1900 + yr
        else:
            full_yr = int(yr_str)
            
        return f"{full_yr:04d}-{mm}"

    return "PARSE_ERROR"
