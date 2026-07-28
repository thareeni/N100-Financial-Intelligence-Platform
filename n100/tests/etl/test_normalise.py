"""
Unit tests for ETL Normaliser Module.
Covers 20 year normalization test cases and 15 ticker normalization test cases (35+ total).
"""

import pytest
from src.etl.normaliser import normalize_ticker, normalize_year


# --- 20 Test Cases for normalize_year ---

def test_year_mar23():
    assert normalize_year("Mar-23") == "2023-03"

def test_year_mar23_space():
    assert normalize_year("Mar 23") == "2023-03"

def test_year_march2023():
    assert normalize_year("March-2023") == "2023-03"

def test_year_2023_int():
    assert normalize_year(2023) == "2023-03"

def test_year_2023_str():
    assert normalize_year("2023") == "2023-03"

def test_year_2024_str():
    assert normalize_year("2024") == "2024-03"

def test_year_fy23():
    assert normalize_year("FY23") == "2023-03"

def test_year_fy23_space():
    assert normalize_year("FY 23") == "2023-03"

def test_year_fy2023():
    assert normalize_year("FY2023") == "2023-03"

def test_year_dec22():
    assert normalize_year("Dec-22") == "2022-12"

def test_year_dec2022_space():
    assert normalize_year("Dec 2022") == "2022-12"

def test_year_december2022():
    assert normalize_year("December-2022") == "2022-12"

def test_year_jun23():
    assert normalize_year("Jun-23") == "2023-06"

def test_year_june2023():
    assert normalize_year("June-2023") == "2023-06"

def test_year_jan24():
    assert normalize_year("Jan-24") == "2024-01"

def test_year_sep21():
    assert normalize_year("Sep-21") == "2021-09"

def test_year_already_formatted():
    assert normalize_year("2023-03") == "2023-03"

def test_year_already_formatted_dec():
    assert normalize_year("2022-12") == "2022-12"

def test_year_garbage():
    assert normalize_year("garbage") == "PARSE_ERROR"

def test_year_none():
    assert normalize_year(None) == "PARSE_ERROR"


# --- 15 Test Cases for normalize_ticker ---

def test_ticker_tcs_upper():
    assert normalize_ticker("TCS") == "TCS"

def test_ticker_tcs_lower():
    assert normalize_ticker("tcs") == "TCS"

def test_ticker_tcs_spaces():
    assert normalize_ticker("  tcs  ") == "TCS"

def test_ticker_hdfcbank_upper():
    assert normalize_ticker("HDFCBANK") == "HDFCBANK"

def test_ticker_hdfcbank_spaces():
    assert normalize_ticker(" hdfcbank ") == "HDFCBANK"

def test_ticker_bajaj_auto_hyphen():
    assert normalize_ticker("BAJAJ-AUTO") == "BAJAJ-AUTO"

def test_ticker_bajaj_auto_spaces():
    assert normalize_ticker(" bajaj-auto ") == "BAJAJ-AUTO"

def test_ticker_mm_ampersand():
    assert normalize_ticker("M&M") == "M&M"

def test_ticker_mm_spaces():
    assert normalize_ticker(" m&m ") == "M&M"

def test_ticker_infy_upper():
    assert normalize_ticker("INFY") == "INFY"

def test_ticker_infy_spaces():
    assert normalize_ticker(" infy ") == "INFY"

def test_ticker_tatamotors_upper():
    assert normalize_ticker("TATAMOTORS") == "TATAMOTORS"

def test_ticker_tatamotors_spaces():
    assert normalize_ticker(" tatamotor ") == "TATAMOTOR"

def test_ticker_none():
    assert normalize_ticker(None) == "MISSING"

def test_ticker_empty():
    assert normalize_ticker("") == "MISSING"
