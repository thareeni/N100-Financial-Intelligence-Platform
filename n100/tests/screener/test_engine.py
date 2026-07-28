"""
Unit tests for Screener Engine (src/screener/engine.py).
Verifies preset screeners output counts (5-50 companies) and composite score calculations.
"""

import os
import pytest
import pandas as pd
from src.screener.engine import ScreenerEngine


def test_screener_config_load():
    engine = ScreenerEngine()
    assert "preset_screeners" in engine.config
    assert "Quality Compounder" in engine.config["preset_screeners"]


def test_preset_quality_compounder():
    engine = ScreenerEngine()
    df = engine.run_preset_screener("Quality Compounder")
    assert not df.empty
    assert 5 <= len(df) <= 50, f"Quality Compounder count {len(df)} outside 5-50 range"


def test_preset_value_pick():
    engine = ScreenerEngine()
    df = engine.run_preset_screener("Value Pick")
    assert not df.empty
    assert 5 <= len(df) <= 50, f"Value Pick count {len(df)} outside 5-50 range"


def test_preset_growth_accelerator():
    engine = ScreenerEngine()
    df = engine.run_preset_screener("Growth Accelerator")
    assert not df.empty
    assert 5 <= len(df) <= 50, f"Growth Accelerator count {len(df)} outside 5-50 range"


def test_preset_dividend_champion():
    engine = ScreenerEngine()
    df = engine.run_preset_screener("Dividend Champion")
    assert not df.empty
    assert 5 <= len(df) <= 50, f"Dividend Champion count {len(df)} outside 5-50 range"


def test_preset_debt_free_blue_chip():
    engine = ScreenerEngine()
    df = engine.run_preset_screener("Debt-Free Blue Chip")
    assert not df.empty
    assert 5 <= len(df) <= 50, f"Debt-Free Blue Chip count {len(df)} outside 5-50 range"


def test_preset_turnaround_watch():
    engine = ScreenerEngine()
    df = engine.run_preset_screener("Turnaround Watch")
    assert not df.empty
    assert 5 <= len(df) <= 50, f"Turnaround Watch count {len(df)} outside 5-50 range"


def test_composite_quality_score_range():
    engine = ScreenerEngine()
    df = engine.get_latest_universe_df()
    assert "composite_quality_score" in df.columns
    scores = df["composite_quality_score"].dropna()
    assert (scores >= 0.0).all() and (scores <= 100.0).all()


def test_export_screener_excel():
    engine = ScreenerEngine()
    out_path = engine.export_screener_excel("test_screener_output.xlsx")
    assert os.path.exists(out_path)
    os.remove(out_path)
