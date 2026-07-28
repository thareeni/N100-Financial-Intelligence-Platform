"""
Unit tests for Financial Ratios Engine (ratios.py).
"""

import pytest
from src.analytics.ratios import (
    calculate_net_profit_margin,
    calculate_operating_profit_margin,
    calculate_roe,
    calculate_roce,
    calculate_roa,
    calculate_debt_to_equity,
    calculate_interest_coverage,
    calculate_net_debt,
    calculate_asset_turnover,
    calculate_book_value_per_share
)


def test_npm_positive():
    assert calculate_net_profit_margin(100, 500) == 20.0


def test_npm_zero_sales():
    assert calculate_net_profit_margin(100, 0) is None


def test_opm_positive():
    assert calculate_operating_profit_margin(150, 1000) == 15.0


def test_opm_zero_sales():
    assert calculate_operating_profit_margin(150, 0) is None


def test_roe_positive():
    assert calculate_roe(100, 200, 300) == 20.0  # 100 / 500 * 100


def test_roe_negative_equity():
    assert calculate_roe(100, 100, -200) is None  # Total equity <= 0


def test_roe_zero_equity():
    assert calculate_roe(100, 0, 0) is None


def test_roce_normal():
    assert calculate_roce(200, 50, 100, 400, 500) == 15.0  # (200-50) / 1000 * 100


def test_roce_zero_capital():
    assert calculate_roce(0, 0, 0, 0, 0) is None


def test_roa_normal():
    assert calculate_roa(50, 1000) == 5.0


def test_de_normal():
    assert calculate_debt_to_equity(200, 100, 300) == 0.5  # 200 / 400


def test_de_debtfree():
    assert calculate_debt_to_equity(0, 100, 300) == 0.0


def test_de_negative_equity():
    assert calculate_debt_to_equity(200, 50, -100) is None


def test_icr_normal():
    assert calculate_interest_coverage(100, 20, 30) == 4.0  # (100+20) / 30


def test_icr_zero_interest():
    assert calculate_interest_coverage(100, 20, 0) is None


def test_net_debt():
    assert calculate_net_debt(500, 100, 50) == 350.0  # 500 - 150


def test_asset_turnover():
    assert calculate_asset_turnover(2000, 1000) == 2.0


def test_book_value_per_share():
    assert calculate_book_value_per_share(100, 900, 2) == 20.0  # Shares = 100/2 = 50. BVPS = 1000/50 = 20
