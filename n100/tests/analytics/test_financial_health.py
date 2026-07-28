"""
Unit tests for Financial Health Scoring Engine (Altman Z-Score & Beneish M-Score).
"""

import pytest
from src.analytics.financial_health import calculate_altman_z_score, calculate_beneish_m_score, FinancialHealthEngine


def test_altman_z_score_safe_zone():
    z_score, rating = calculate_altman_z_score(
        working_capital=5000.0,
        retained_earnings=10000.0,
        ebit=4000.0,
        market_cap=50000.0,
        total_liabilities=5000.0,
        sales=20000.0,
        total_assets=25000.0
    )
    assert z_score is not None
    assert z_score > 2.99
    assert rating == "Safe Zone"


def test_altman_z_score_distress_zone():
    z_score, rating = calculate_altman_z_score(
        working_capital=-2000.0,
        retained_earnings=-5000.0,
        ebit=-1000.0,
        market_cap=1000.0,
        total_liabilities=10000.0,
        sales=2000.0,
        total_assets=12000.0
    )
    assert z_score is not None
    assert z_score < 1.81
    assert rating == "Distress Zone"


def test_beneish_m_score_calculation():
    m_score, flag = calculate_beneish_m_score(
        sales_t=1000.0, sales_t1=900.0,
        cogs_t=600.0, cogs_t1=550.0,
        assets_t=2000.0, assets_t1=1800.0,
        non_curr_assets_t=1200.0, non_curr_assets_t1=1100.0,
        depr_t=100.0, depr_t1=90.0,
        sga_t=120.0, sga_t1=110.0,
        debt_t=400.0, debt_t1=450.0,
        op_inc_t=280.0, cfo_t=250.0
    )
    assert m_score is not None
    assert flag in ["High Risk", "Low Risk"]


def test_financial_health_engine_execution():
    engine = FinancialHealthEngine()
    df = engine.run()
    assert not df.empty
    assert "altman_z_score" in df.columns
    assert "financial_health_rating" in df.columns
    assert "beneish_m_score" in df.columns
    assert "manipulation_risk_flag" in df.columns
