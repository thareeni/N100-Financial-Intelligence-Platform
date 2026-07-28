"""
Unit tests for Investment Score Engine & Intelligence Exporter.
"""

import os
import pytest
from src.analytics.investment_score import calculate_investment_rating, InvestmentScoreEngine


def test_investment_rating_classification():
    assert calculate_investment_rating(85.0) == "Strong Buy"
    assert calculate_investment_rating(68.0) == "Buy"
    assert calculate_investment_rating(52.0) == "Hold"
    assert calculate_investment_rating(35.0) == "Avoid"


def test_investment_score_engine_execution():
    engine = InvestmentScoreEngine()
    df = engine.run()
    assert not df.empty
    assert "investment_score" in df.columns
    assert "investment_rating" in df.columns
    assert (df["investment_score"] >= 0.0).all() and (df["investment_score"] <= 100.0).all()
    
    excel_path = os.path.join("output", "investment_intelligence.xlsx")
    assert os.path.exists(excel_path), f"{excel_path} must exist"
