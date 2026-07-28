"""
Unit tests for ETL Loader Module.
"""

import os
import sqlite3
import pytest
from src.etl.loader import ETLLoader, DB_PATH


def test_loader_files_exist():
    loader = ETLLoader()
    # Should not raise exception when files exist
    loader.check_files_exist()


def test_loader_read_excel_files():
    loader = ETLLoader()
    raw_dfs, rows_in = loader.read_excel_files()
    
    assert "companies" in raw_dfs
    assert rows_in["companies"] == 92
    assert "profitandloss" in raw_dfs
    assert "balancesheet" in raw_dfs
    assert "cashflow" in raw_dfs


def test_loader_db_execution():
    loader = ETLLoader()
    loader.run_pipeline()
    
    db_file = DB_PATH
    assert os.path.exists(db_file), f"Database file {db_file} must exist in project root"

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Check companies count
    cursor.execute("SELECT COUNT(*) FROM companies;")
    comp_count = cursor.fetchone()[0]
    assert comp_count == 92, f"Expected 92 companies, got {comp_count}"

    # Check foreign key integrity
    cursor.execute("PRAGMA foreign_key_check;")
    fk_violations = cursor.fetchall()
    assert len(fk_violations) == 0, f"Foreign key violations found: {fk_violations}"

<<<<<<< HEAD
    # Re-run ratio & peer engines to preserve downstream tables for test suite isolation
    from src.analytics.runner import RatioEngineRunner
    from src.analytics.peer import PeerComparisonEngine
    RatioEngineRunner().run()
    PeerComparisonEngine().compute_peer_percentiles()

=======
>>>>>>> f81a2dbcaaaeea2037fd8e762649a9c1a489d5d3
    conn.close()
