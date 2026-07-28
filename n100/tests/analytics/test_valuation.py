"""
Unit tests for Valuation Intelligence Engine.
"""

import pytest
from src.analytics.valuation import calculate_valuation_score_components, ValuationEngine


def test_valuation_score_components():
    res = calculate_valuation_score_components(
        pe_ratio=15.0,
        pb_ratio=2.5,
        ev_ebitda=10.0,
        fcf_cr=500.0,
        mcap_cr=10000.0,
        sales_cr=8000.0,
        ev_cr=11000.0,
        pat_cagr_5yr=18.0
    )
    assert "earnings_yield" in res
    assert "fcf_yield" in res
    assert "valuation_score" in res
    assert 0.0 <= res["valuation_score"] <= 100.0


def test_valuation_engine_execution():
    engine = ValuationEngine()
    df = engine.run()
    assert not df.empty
    assert "valuation_score" in df.columns
    assert (df["valuation_score"] >= 0.0).all() and (df["valuation_score"] <= 100.0).all()
