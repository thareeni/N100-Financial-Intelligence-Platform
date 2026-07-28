"""
Unit & Integration tests for Pipeline Orchestrator and Production Dashboard.
"""

import os
import sqlite3
import pytest
from src.main import run_full_pipeline, DB_PATH


def test_pipeline_import():
    import src.main
    assert hasattr(src.main, "run_full_pipeline")


def test_database_connection():
    db_file = DB_PATH
    assert os.path.exists(db_file)
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM companies;")
    comp_cnt = c.fetchone()[0]
    assert comp_cnt == 92
    conn.close()


def test_output_reports_exist():
    required_outputs = [
        "output/screener_output.xlsx",
        "output/peer_comparison.xlsx",
        "output/investment_intelligence.xlsx",
        "output/load_audit.csv",
        "output/capital_allocation.csv"
    ]
    for out in required_outputs:
        assert os.path.exists(out), f"Output file {out} must exist"


def test_dashboard_imports():
    import dashboard.app
    assert hasattr(dashboard.app, "render_page_overview")
    assert hasattr(dashboard.app, "render_page_screener")
    assert hasattr(dashboard.app, "render_page_investment_intelligence")
    assert hasattr(dashboard.app, "render_page_peer_comparison")
    assert hasattr(dashboard.app, "render_page_company_detail")
