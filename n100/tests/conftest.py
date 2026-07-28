"""
Pytest global configuration, path setup, and database initialization fixture.
Ensures src package is discoverable and nifty100.db is fully populated with
Sprint 1, Sprint 2, and Sprint 3 tables before running tests.
"""

import sys
import os
import sqlite3
import pytest

sys.path.insert(0, os.path.abspath("."))

from src.etl.loader import ETLLoader, DB_PATH
from src.analytics.runner import RatioEngineRunner
from src.analytics.peer import PeerComparisonEngine


@pytest.fixture(scope="session", autouse=True)
def ensure_database_populated():
    """Session fixture ensuring DB has companies, financial_ratios, and peer tables populated."""
    db_file = DB_PATH
    
    need_load = False
    if not os.path.exists(db_file):
        need_load = True
    else:
        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()]
        if "companies" not in tables or "financial_ratios" not in tables:
            need_load = True
        else:
            c.execute("SELECT COUNT(*) FROM companies;")
            if c.fetchone()[0] == 0:
                need_load = True
        conn.close()

    if need_load:
        ETLLoader().run_pipeline()
        RatioEngineRunner().run()
        PeerComparisonEngine().compute_peer_percentiles()
