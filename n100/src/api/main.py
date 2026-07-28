"""
FastAPI REST Server for Nifty 100 Financial Intelligence Platform.
Exposes 17 REST endpoints for financial analytics, screeners, peer comparison, and investment intelligence.
"""

import os
import sqlite3
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

DB_PATH = os.getenv("DB_PATH", "nifty100.db")

app = FastAPI(
    title="Nifty 100 Financial Intelligence REST API",
    description="Production REST API providing financial ratios, stock screeners, peer benchmarking, DuPont breakdown, Altman Z/Beneish M health scores, and investment ratings for 92 Nifty 100 companies.",
    version="1.0.0"
)


def get_db_connection():
    if not os.path.exists(DB_PATH):
        raise HTTPException(status_code=500, detail="Database file not found.")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.get("/")
def root():
    return {
        "platform": "Nifty 100 Financial Intelligence Platform",
        "status": "online",
        "docs_url": "/docs"
    }


@app.get("/health")
def health_check():
    conn = get_db_connection()
    c = conn.cursor()
    comp_cnt = c.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
    conn.close()
    return {"status": "HEALTHY", "companies_loaded": comp_cnt, "database": DB_PATH}


@app.get("/companies")
def list_companies():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM companies ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/companies/{ticker}")
def get_company(ticker: str):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM companies WHERE id = ?", (ticker.upper(),)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail=f"Company {ticker} not found.")
    return dict(row)


@app.get("/ratios/{ticker}")
def get_company_ratios(ticker: str):
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM financial_ratios WHERE company_id = ? ORDER BY year DESC", (ticker.upper(),)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/valuation/{ticker}")
def get_valuation(ticker: str):
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM valuation_metrics WHERE company_id = ? ORDER BY year DESC", (ticker.upper(),)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/investment-scores")
def list_investment_scores():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM investment_scores ORDER BY investment_score DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/investment-scores/{ticker}")
def get_investment_score(ticker: str):
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM investment_scores WHERE company_id = ?", (ticker.upper(),)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail=f"Score for {ticker} not found.")
    return dict(row)


@app.get("/financial-health/{ticker}")
def get_financial_health(ticker: str):
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM financial_health WHERE company_id = ? ORDER BY year DESC", (ticker.upper(),)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/dupont/{ticker}")
def get_dupont_analysis(ticker: str):
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM dupont_analysis WHERE company_id = ? ORDER BY year DESC", (ticker.upper(),)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/screeners")
def list_screeners():
    from src.screener.engine import ScreenerEngine
    screener = ScreenerEngine(DB_PATH)
    presets = list(screener.preset_screeners.keys())
    return {"available_presets": presets}


@app.get("/screeners/{preset_name}")
def run_screener_preset(preset_name: str):
    from src.screener.engine import ScreenerEngine
    screener = ScreenerEngine(DB_PATH)
    df = screener.run_preset_screener(preset_name)
    return df.to_dict(orient="records")


@app.get("/peer-comparison/{group_name}")
def get_peer_comparison(group_name: str):
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM peer_percentiles WHERE peer_group_name = ?", (group_name,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/sectors")
def list_sectors():
    conn = get_db_connection()
    rows = conn.execute("SELECT broad_sector, COUNT(*) as count FROM sectors GROUP BY broad_sector").fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/market-cap")
def get_market_cap_rankings():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM market_cap WHERE year = (SELECT MAX(year) FROM market_cap) ORDER BY market_cap_crore DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/portfolio")
def get_portfolio_candidates():
    conn = get_db_connection()
    sql = """
        SELECT ins.company_id, c.company_name, s.broad_sector, ins.investment_score, ins.investment_rating
        FROM investment_scores ins
        JOIN companies c ON ins.company_id = c.id
        LEFT JOIN sectors s ON ins.company_id = s.company_id
        WHERE ins.investment_rating IN ('Strong Buy', 'Buy')
        ORDER BY ins.investment_score DESC
    """
    rows = conn.execute(sql).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/search")
def search_companies(q: str = Query(..., min_length=1)):
    conn = get_db_connection()
    sql = "SELECT * FROM companies WHERE id LIKE ? OR company_name LIKE ?"
    pattern = f"%{q}%"
    rows = conn.execute(sql, (pattern, pattern)).fetchall()
    conn.close()
    return [dict(r) for r in rows]
