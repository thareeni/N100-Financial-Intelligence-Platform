"""
Cash Flow Intelligence Module.
Computes Free Cash Flow (FCF), CFO Quality Score, CapEx Intensity, FCF Conversion Rate,
and classifies company capital allocation patterns across 8 sign combinations.
"""

from typing import Optional, Any, Tuple


def safe_float(val: Any) -> Optional[float]:
    if val is None:
        return None
    try:
        f = float(val)
        return None if f != f else f
    except (ValueError, TypeError):
        return None


def calculate_free_cash_flow(operating_activity: Any, investing_activity: Any) -> Optional[float]:
    """Free Cash Flow (Cr) = CFO + CFI"""
    cfo = safe_float(operating_activity)
    cfi = safe_float(investing_activity)
    if cfo is None or cfi is None:
        return None
    return round(cfo + cfi, 4)


def calculate_cfo_quality_score(operating_activity: Any, net_profit: Any) -> Optional[float]:
    """CFO Quality Score (CFO / PAT) = operating_activity / net_profit"""
    cfo = safe_float(operating_activity)
    pat = safe_float(net_profit)
    if pat is None or pat == 0 or cfo is None:
        return None
    return round(cfo / pat, 4)


def calculate_capex_intensity(investing_activity: Any, sales: Any) -> Optional[float]:
    """CapEx Intensity % = abs(investing_activity) / sales * 100"""
    cfi = safe_float(investing_activity)
    s = safe_float(sales)
    if s is None or s == 0 or cfi is None:
        return None
    capex = abs(cfi)
    return round((capex / s) * 100.0, 4)


def calculate_fcf_conversion_rate(free_cash_flow: Any, operating_profit: Any) -> Optional[float]:
    """FCF Conversion Rate % = (FCF / operating_profit) * 100"""
    fcf = safe_float(free_cash_flow)
    op = safe_float(operating_profit)
    if op is None or op == 0 or fcf is None:
        return None
    return round((fcf / op) * 100.0, 4)


def classify_capital_allocation(operating_activity: Any, investing_activity: Any, financing_activity: Any) -> str:
    """
    Classifies 8 capital allocation sign patterns based on (CFO, CFI, CFF):
    1. (+, -, -) -> Reinvestor / Shareholder Returns
    2. (+, -, +) -> Growth Capital / Expansion
    3. (+, +, -) -> Divestment / Debt Repayment
    4. (+, +, +) -> Asset Liquidation / Cash Accumulation
    5. (-, -, +) -> External Funding for Operations
    6. (-, +, +) -> Distress / Liquidation
    7. (-, -, -) -> Cash Burn / High Stress
    8. (-, +, -) -> Asset Sale / Debt Repayment
    """
    cfo = safe_float(operating_activity) or 0.0
    cfi = safe_float(investing_activity) or 0.0
    cff = safe_float(financing_activity) or 0.0

    s1 = "+" if cfo >= 0 else "-"
    s2 = "+" if cfi >= 0 else "-"
    s3 = "+" if cff >= 0 else "-"

    pattern = f"({s1}, {s2}, {s3})"

    labels = {
        "(+, -, -)": "Reinvestor / Shareholder Returns",
        "(+, -, +)": "Growth Capital / Expansion",
        "(+, +, -)": "Divestment / Debt Repayment",
        "(+, +, +)": "Asset Liquidation / Cash Accumulation",
        "(-, -, +)": "External Funding for Operations",
        "(-, +, +)": "Distress / Liquidation",
        "(-, -, -)": "Cash Burn / High Stress",
        "(-, +, -)": "Asset Sale / Debt Repayment",
    }

    return labels.get(pattern, "Unclassified Pattern")
