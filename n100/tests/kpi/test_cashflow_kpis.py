"""
Unit tests for Cash Flow Intelligence Module (cashflow_kpis.py).
"""

import pytest
from src.analytics.cashflow_kpis import (
    calculate_free_cash_flow,
    calculate_cfo_quality_score,
    calculate_capex_intensity,
    calculate_fcf_conversion_rate,
    classify_capital_allocation
)


def test_free_cash_flow():
    assert calculate_free_cash_flow(500, -200) == 300.0


def test_cfo_quality_score():
    assert calculate_cfo_quality_score(600, 500) == 1.2


def test_capex_intensity():
    assert calculate_capex_intensity(-150, 3000) == 5.0  # abs(-150)/3000 * 100


def test_fcf_conversion_rate():
    assert calculate_fcf_conversion_rate(300, 500) == 60.0  # 300/500 * 100


def test_classify_reinvestor():
    # (+, -, -)
    assert classify_capital_allocation(500, -200, -100) == "Reinvestor / Shareholder Returns"


def test_classify_distress():
    # (-, +, +)
    assert classify_capital_allocation(-100, 50, 50) == "Distress / Liquidation"
