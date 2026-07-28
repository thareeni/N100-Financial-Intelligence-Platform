"""
Unit tests for CAGR Calculation Engine (cagr.py).
"""

import pytest
from src.analytics.cagr import calculate_cagr


def test_cagr_positive_normal():
    val, flag = calculate_cagr(100, 161.051, 5)
    assert flag == "NORMAL"
    assert val == 10.0  # 10% CAGR


def test_cagr_decline_to_loss():
    val, flag = calculate_cagr(100, -50, 5)
    assert val is None
    assert flag == "DECLINE_TO_LOSS"


def test_cagr_turnaround():
    val, flag = calculate_cagr(-50, 100, 5)
    assert val is None
    assert flag == "TURNAROUND"


def test_cagr_both_negative():
    val, flag = calculate_cagr(-50, -20, 5)
    assert val is None
    assert flag == "BOTH_NEGATIVE"


def test_cagr_zero_base():
    val, flag = calculate_cagr(0, 100, 5)
    assert val is None
    assert flag == "ZERO_BASE"


def test_cagr_insufficient_years():
    val, flag = calculate_cagr(100, 150, 2)
    assert val is None
    assert flag == "INSUFFICIENT"
