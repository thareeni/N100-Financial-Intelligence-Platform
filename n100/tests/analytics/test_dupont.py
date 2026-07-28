"""
Unit tests for 3-Stage DuPont Analysis Engine.
"""

import pytest
from src.analytics.dupont import calculate_dupont_stage3, DuPontEngine


def test_dupont_stage3_calculation():
    npm, at, em, dupont_roe = calculate_dupont_stage3(
        net_profit=150.0,
        sales=1000.0,
        total_assets=2000.0,
        equity=800.0
    )
    assert npm == 0.15
    assert at == 0.5
    assert em == 2.5
    assert dupont_roe == round(0.15 * 0.5 * 2.5 * 100, 2)  # 18.75%


def test_dupont_stage3_missing_data():
    npm, at, em, dupont_roe = calculate_dupont_stage3(
        net_profit=100.0,
        sales=0.0,
        total_assets=1000.0,
        equity=500.0
    )
    assert npm is None
    assert dupont_roe is None


def test_dupont_engine_execution():
    engine = DuPontEngine()
    df = engine.run()
    assert not df.empty
    assert "dupont_roe" in df.columns
    assert "equity_multiplier" in df.columns
