"""
Financial Ratio Calculator Engine.
Computes Profitability, Leverage, Efficiency, and Equity Valuation KPIs with robust edge-case handling.
"""

import logging
from typing import Optional, Any

logger = logging.getLogger("RatioEngine")


def safe_float(val: Any) -> Optional[float]:
    if val is None:
        return None
    try:
        f = float(val)
        return None if f != f else f  # Check NaN
    except (ValueError, TypeError):
        return None


# --- Profitability Ratios ---

def calculate_net_profit_margin(net_profit: Any, sales: Any) -> Optional[float]:
    """Net Profit Margin % = (net_profit / sales) * 100"""
    np = safe_float(net_profit)
    s = safe_float(sales)
    if s is None or s == 0 or np is None:
        return None
    return round((np / s) * 100.0, 4)


def calculate_operating_profit_margin(operating_profit: Any, sales: Any) -> Optional[float]:
    """Operating Profit Margin % = (operating_profit / sales) * 100"""
    op = safe_float(operating_profit)
    s = safe_float(sales)
    if s is None or s == 0 or op is None:
        return None
    return round((op / s) * 100.0, 4)


def calculate_roe(net_profit: Any, equity_capital: Any, reserves: Any) -> Optional[float]:
    """
    Return on Equity % = (net_profit / (equity_capital + reserves)) * 100
    Edge Case: Negative or Zero total equity returns None.
    """
    np = safe_float(net_profit)
    eq = safe_float(equity_capital) or 0.0
    res = safe_float(reserves) or 0.0
    total_equity = eq + res

    if np is None or total_equity <= 0:
        return None
    return round((np / total_equity) * 100.0, 4)


def calculate_roce(
    operating_profit: Any,
    depreciation: Any,
    equity_capital: Any,
    reserves: Any,
    borrowings: Any,
    is_financial: bool = False
) -> Optional[float]:
    """
    Return on Capital Employed % = (EBIT / Capital Employed) * 100
    EBIT = operating_profit - depreciation
    Capital Employed = equity_capital + reserves + borrowings
    """
    op = safe_float(operating_profit) or 0.0
    dep = safe_float(depreciation) or 0.0
    ebit = op - dep

    eq = safe_float(equity_capital) or 0.0
    res = safe_float(reserves) or 0.0
    borr = safe_float(borrowings) or 0.0
    cap_employed = eq + res + borr

    if cap_employed <= 0 or (op == 0 and dep == 0):
        return None
    
    return round((ebit / cap_employed) * 100.0, 4)


def calculate_roa(net_profit: Any, total_assets: Any) -> Optional[float]:
    """Return on Assets % = (net_profit / total_assets) * 100"""
    np = safe_float(net_profit)
    ta = safe_float(total_assets)
    if ta is None or ta == 0 or np is None:
        return None
    return round((np / ta) * 100.0, 4)


# --- Leverage & Efficiency Ratios ---

def calculate_debt_to_equity(
    borrowings: Any,
    equity_capital: Any,
    reserves: Any,
    is_financial: bool = False
) -> Optional[float]:
    """
    Debt to Equity Ratio = borrowings / (equity_capital + reserves)
    Edge Cases:
    - Borrowings == 0 returns 0.0 (Debt-free)
    - Total Equity <= 0 returns None
    """
    borr = safe_float(borrowings) or 0.0
    eq = safe_float(equity_capital) or 0.0
    res = safe_float(reserves) or 0.0
    total_equity = eq + res

    if borr == 0.0:
        return 0.0

    if total_equity <= 0:
        return None

    de_ratio = round(borr / total_equity, 4)
    
    if is_financial and de_ratio > 5.0:
        logger.debug(f"High D/E of {de_ratio} is structurally normal for Financials sector.")
        
    return de_ratio


def calculate_interest_coverage(
    operating_profit: Any,
    other_income: Any,
    interest: Any
) -> Optional[float]:
    """
    Interest Coverage Ratio = (operating_profit + other_income) / interest
    Edge Case: Interest == 0 returns None (Debt-free).
    """
    op = safe_float(operating_profit) or 0.0
    oth = safe_float(other_income) or 0.0
    intr = safe_float(interest)

    if intr is None or intr == 0:
        return None

    total_earnings = op + oth
    return round(total_earnings / intr, 4)


def calculate_net_debt(
    borrowings: Any,
    investments: Any,
    cash_proxy: Any = 0.0
) -> Optional[float]:
    """Net Debt = borrowings - (investments + cash_proxy)"""
    borr = safe_float(borrowings) or 0.0
    inv = safe_float(investments) or 0.0
    cash = safe_float(cash_proxy) or 0.0
    return round(borr - (inv + cash), 4)


def calculate_asset_turnover(sales: Any, total_assets: Any) -> Optional[float]:
    """Asset Turnover Ratio = sales / total_assets"""
    s = safe_float(sales)
    ta = safe_float(total_assets)
    if ta is None or ta == 0 or s is None:
        return None
    return round(s / ta, 4)


def calculate_book_value_per_share(
    equity_capital: Any,
    reserves: Any,
    face_value: Any
) -> Optional[float]:
    """
    Book Value Per Share = Total Equity / Number of Shares
    Number of Shares = Equity Capital / Face Value
    """
    eq = safe_float(equity_capital) or 0.0
    res = safe_float(reserves) or 0.0
    fv = safe_float(face_value)

    if fv is None or fv == 0 or eq <= 0:
        return None

    num_shares_cr = eq / fv
    if num_shares_cr == 0:
        return None

    total_equity = eq + res
    return round(total_equity / num_shares_cr, 4)
