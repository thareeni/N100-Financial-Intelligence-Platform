"""
Final End-to-End Validation Suite for Sprint 6 Quality Assurance.
"""

import os
import sqlite3
import pytest
from src.main import DB_PATH, run_full_pipeline


def test_database_connection_and_tables():
    assert os.path.exists(DB_PATH), f"Database {DB_PATH} must exist in project root."
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    required_tables = [
        "companies", "profitandloss", "balancesheet", "cashflow",
        "analysis", "documents", "prosandcons", "sectors",
        "stock_prices", "market_cap", "financial_ratios",
        "peer_groups", "peer_percentiles", "financial_health",
        "dupont_analysis", "valuation_metrics", "investment_scores"
    ]

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    existing_tables = [r[0] for r in cursor.fetchall()]

    for tbl in required_tables:
        assert tbl in existing_tables, f"Table {tbl} missing from database."

    conn.close()


def test_foreign_key_integrity():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_key_check;")
    fk_violations = cursor.fetchall()
    assert len(fk_violations) == 0, f"Foreign key violations found: {fk_violations}"
    conn.close()


def test_data_counts():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM companies;")
    comp_cnt = cursor.fetchone()[0]
    assert comp_cnt == 92, f"Expected 92 companies, found {comp_cnt}"

    cursor.execute("SELECT COUNT(*) FROM financial_ratios;")
    ratio_cnt = cursor.fetchone()[0]
    assert ratio_cnt > 1000, f"Expected >1000 financial ratio rows, found {ratio_cnt}"

    cursor.execute("SELECT COUNT(*) FROM investment_scores;")
    inv_cnt = cursor.fetchone()[0]
    assert inv_cnt >= 90, f"Expected >=90 investment scores, found {inv_cnt}"

    conn.close()


def test_required_output_files():
    required_files = [
        "output/screener_output.xlsx",
        "output/peer_comparison.xlsx",
        "output/investment_intelligence.xlsx",
        "output/load_audit.csv",
        "output/capital_allocation.csv"
    ]

    for filepath in required_files:
        assert os.path.exists(filepath), f"Required output file {filepath} is missing."
        assert os.path.getsize(filepath) > 0, f"File {filepath} is empty."
