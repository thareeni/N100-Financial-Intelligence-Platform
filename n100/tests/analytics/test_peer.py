"""
Unit tests for Peer Comparison Engine (src/analytics/peer.py).
"""

import os
import sqlite3
import pytest
from src.analytics.peer import PeerComparisonEngine


def test_peer_percentiles_calculation():
    engine = PeerComparisonEngine()
    df = engine.compute_peer_percentiles()
    assert not df.empty
    assert "percentile_rank" in df.columns
    
    # Check percentile values between 0 and 1
    ranks = df["percentile_rank"].dropna()
    assert (ranks >= 0.0).all() and (ranks <= 1.0).all()


def test_radar_charts_generation():
    engine = PeerComparisonEngine()
    count = engine.generate_radar_charts()
    assert count > 0, "At least 1 radar chart should be generated"
    assert os.path.exists(os.path.join("reports", "radar_charts"))


def test_export_peer_comparison_excel():
    engine = PeerComparisonEngine()
    out_path = engine.export_peer_comparison_excel("test_peer_comparison.xlsx")
    assert os.path.exists(out_path)
    os.remove(out_path)
