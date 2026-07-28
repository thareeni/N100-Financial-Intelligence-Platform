"""
Valuation Intelligence Engine.
Computes Earnings Yield, FCF Yield, PEG Ratio, EV/Sales, EV/EBITDA, Intrinsic Value Score,
and composite 0-100 Valuation Score.
Populates valuation_metrics SQLite table.
"""

import os
import sqlite3
import logging
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd
import numpy as np
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("ValuationEngine")

DB_PATH = os.getenv("DB_PATH", "nifty100.db")


def calculate_valuation_score_components(
    pe_ratio: float,
    pb_ratio: float,
    ev_ebitda: float,
    fcf_cr: float,
    mcap_cr: float,
    sales_cr: float,
    ev_cr: float,
    pat_cagr_5yr: float
) -> Dict[str, Any]:
    """
    Computes valuation multiples, yields, PEG, and 0-100 valuation_score.
    """
    ey = (1.0 / pe_ratio * 100.0) if pe_ratio and pe_ratio > 0 else 0.0
    fcf_y = (fcf_cr / mcap_cr * 100.0) if fcf_cr and mcap_cr and mcap_cr > 0 else 0.0
    
    peg = (pe_ratio / pat_cagr_5yr) if pe_ratio and pat_cagr_5yr and pat_cagr_5yr > 0 else (pe_ratio / 15.0 if pe_ratio else 1.5)
    ev_sales = (ev_cr / sales_cr) if ev_cr and sales_cr and sales_cr > 0 else (mcap_cr / sales_cr if mcap_cr and sales_cr and sales_cr > 0 else 2.0)
    
    # Intrinsic Value Score (0-100): Combination of EY, FCF Yield, and PEG
    ey_score = min(max(ey * 10.0, 0.0), 100.0)
    fcf_score = min(max(fcf_y * 15.0, 0.0), 100.0)
    peg_score = max(100.0 - (peg * 30.0), 0.0) if peg > 0 else 50.0
    
    intrinsic_val_score = round(0.4 * ey_score + 0.4 * fcf_score + 0.2 * peg_score, 2)

    # 0-100 Composite Valuation Score (Higher score = more attractive/undervalued)
    pe_val_score = max(100.0 - (pe_ratio * 2.0), 0.0) if pe_ratio and pe_ratio > 0 else 40.0
    pb_val_score = max(100.0 - (pb_ratio * 15.0), 0.0) if pb_ratio and pb_ratio > 0 else 40.0
    ev_ebitda_score = max(100.0 - (ev_ebitda * 3.0), 0.0) if ev_ebitda and ev_ebitda > 0 else 40.0

    val_score = round(0.35 * intrinsic_val_score + 0.25 * pe_val_score + 0.20 * pb_val_score + 0.20 * ev_ebitda_score, 2)
    if pd.isna(val_score):
        val_score = 50.0
    val_score = min(max(val_score, 0.0), 100.0)

    return {
        "earnings_yield": round(ey, 2),
        "fcf_yield": round(fcf_y, 2),
        "peg_ratio": round(peg, 2),
        "ev_sales": round(ev_sales, 2),
        "ev_ebitda": round(ev_ebitda, 2) if ev_ebitda else None,
        "intrinsic_value_score": intrinsic_val_score,
        "valuation_score": val_score
    }


class ValuationEngine:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path

    def run(self) -> pd.DataFrame:
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")

        # Ensure valuation_metrics table exists
        conn.execute("""
            CREATE TABLE IF NOT EXISTS valuation_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id VARCHAR NOT NULL,
                year VARCHAR NOT NULL,
                earnings_yield NUMERIC,
                fcf_yield NUMERIC,
                peg_ratio NUMERIC,
                ev_sales NUMERIC,
                ev_ebitda NUMERIC,
                intrinsic_value_score NUMERIC,
                valuation_score NUMERIC NOT NULL,
                UNIQUE (company_id, year),
                FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
            );
        """)
        conn.commit()

        sql = """
            SELECT fr.company_id, fr.year, fr.free_cash_flow_cr, fr.pat_cagr_5yr,
                   pl.sales,
                   mc.market_cap_crore, mc.enterprise_value_crore, mc.pe_ratio, mc.pb_ratio, mc.ev_ebitda
            FROM financial_ratios fr
            JOIN (
                SELECT company_id, MAX(year) as max_yr
                FROM financial_ratios
                WHERE year != 'PARSE_ERROR'
                GROUP BY company_id
            ) latest ON fr.company_id = latest.company_id AND fr.year = latest.max_yr
            LEFT JOIN profitandloss pl ON fr.company_id = pl.company_id AND fr.year = pl.year
            LEFT JOIN (
                SELECT mc_inner.*
                FROM market_cap mc_inner
                JOIN (
                    SELECT company_id, MAX(year) as max_yr
                    FROM market_cap
                    GROUP BY company_id
                ) latest_mc ON mc_inner.company_id = latest_mc.company_id AND mc_inner.year = latest_mc.max_yr
            ) mc ON fr.company_id = mc.company_id
        """
        df = pd.read_sql_query(sql, conn)
        if df.empty:
            logger.warning("No data found for Valuation calculations.")
            conn.close()
            return pd.DataFrame()

        records = []
        for _, row in df.iterrows():
            cid = row["company_id"]
            yr = row["year"]
            pe = row["pe_ratio"] or 20.0
            pb = row["pb_ratio"] or 3.0
            evebitda = row["ev_ebitda"] or 12.0
            fcf = row["free_cash_flow_cr"] or 0.0
            mcap = row["market_cap_crore"] or 10000.0
            sales = row["sales"] or 5000.0
            ev = row["enterprise_value_crore"] or mcap
            pat_cagr = row["pat_cagr_5yr"] or 12.0

            res = calculate_valuation_score_components(pe, pb, evebitda, fcf, mcap, sales, ev, pat_cagr)
            res["company_id"] = cid
            res["year"] = yr
            records.append(res)

        res_df = pd.DataFrame(records)
        res_df = res_df.drop_duplicates(subset=["company_id", "year"]).reset_index(drop=True)
        conn.execute("DELETE FROM valuation_metrics;")
        res_df.to_sql("valuation_metrics", conn, if_exists="append", index=False)
        conn.commit()
        logger.info(f"Populated valuation_metrics table with {len(res_df)} rows.")
        conn.close()
        return res_df


if __name__ == "__main__":
    engine = ValuationEngine()
    engine.run()
