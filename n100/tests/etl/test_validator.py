"""
Unit tests for Data Quality Validator Module.
"""

import pytest
import pandas as pd
from src.etl.validator import DataQualityValidator


def test_validator_dq01_duplicate_ticker():
    validator = DataQualityValidator()
    companies_df = pd.DataFrame({
        "id": ["TCS", "TCS", "INFY"],
        "company_name": ["Tata Consultancy Services", "Tata Consultancy Services", "Infosys"]
    })
    dfs = {"companies": companies_df}
    failures, cleaned = validator.validate_all(dfs)
    
    dq01_failures = [f for f in failures if f["rule_id"] == "DQ-01"]
    assert len(dq01_failures) > 0
    assert dq01_failures[0]["severity"] == "CRITICAL"


def test_validator_dq03_orphan_fk():
    validator = DataQualityValidator()
    companies_df = pd.DataFrame({"id": ["TCS"]})
    pl_df = pd.DataFrame({
        "company_id": ["TCS", "UNKNOWN_TICKER"],
        "year": ["2023-03", "2023-03"],
        "sales": [1000, 500]
    })
    dfs = {"companies": companies_df, "profitandloss": pl_df}
    failures, cleaned = validator.validate_all(dfs)
    
    dq03_failures = [f for f in failures if f["rule_id"] == "DQ-03"]
    assert len(dq03_failures) == 1
    assert dq03_failures[0]["company_id"] == "UNKNOWN_TICKER"
    assert len(cleaned["profitandloss"]) == 1


def test_validator_dq04_bs_imbalance():
    validator = DataQualityValidator()
    bs_df = pd.DataFrame({
        "company_id": ["TCS"],
        "year": ["2023-03"],
        "total_assets": [1000],
        "total_liabilities": [1200]
    })
    dfs = {"balancesheet": bs_df}
    failures, cleaned = validator.validate_all(dfs)
    
    dq04_failures = [f for f in failures if f["rule_id"] == "DQ-04"]
    assert len(dq04_failures) == 1
    assert dq04_failures[0]["severity"] == "WARNING"


def test_validator_dq05_opm_cross_check():
    validator = DataQualityValidator()
    pl_df = pd.DataFrame({
        "company_id": ["TCS"],
        "year": ["2023-03"],
        "sales": [1000],
        "operating_profit": [200],
        "opm_percentage": [10.0]  # Reported 10%, calculated 20%
    })
    dfs = {"profitandloss": pl_df}
    failures, cleaned = validator.validate_all(dfs)
    
    dq05_failures = [f for f in failures if f["rule_id"] == "DQ-05"]
    assert len(dq05_failures) == 1
    assert dq05_failures[0]["severity"] == "WARNING"
