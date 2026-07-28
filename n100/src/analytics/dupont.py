"""
3-Stage DuPont Analysis Engine.
Decomposes Return on Equity (ROE) into:
ROE = Net Profit Margin * Asset Turnover * Equity Multiplier
Populates dupont_analysis SQLite table.
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
logger = logging.getLogger("DuPontEngine")

DB_PATH = os.getenv("DB_PATH", "nifty100.db")


def calculate_dupont_stage3(
    net_profit: float,
    sales: float,
    total_assets: float,
    equity: float
) -> Tuple[Optional[float], Optional[float], Optional[float], Optional[float]]:
    """
    Calculates 3-stage DuPont components:
    - Net Profit Margin (NPM) = Net Profit / Sales
    - Asset Turnover (AT) = Sales / Total Assets
    - Equity Multiplier (EM) = Total Assets / Equity
    - DuPont ROE (%) = NPM * AT * EM * 100
    """
    if not sales or sales <= 0 or not total_assets or total_assets <= 0 or not equity or equity <= 0:
        return None, None, None, None

    npm = net_profit / sales if sales > 0 else 0.0
    at = sales / total_assets if total_assets > 0 else 0.0
    em = total_assets / equity if equity > 0 else 1.0
    dupont_roe = npm * at * em * 100.0

    return round(npm, 4), round(at, 4), round(em, 4), round(dupont_roe, 2)


class DuPontEngine:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path

    def run(self) -> pd.DataFrame:
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")

        # Ensure dupont_analysis table exists
        conn.execute("""
            CREATE TABLE IF NOT EXISTS dupont_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id VARCHAR NOT NULL,
                year VARCHAR NOT NULL,
                net_profit_margin NUMERIC,
                asset_turnover NUMERIC,
                equity_multiplier NUMERIC,
                dupont_roe NUMERIC,
                UNIQUE (company_id, year),
                FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
            );
        """)
        conn.commit()

        sql = """
            SELECT pl.company_id, pl.year, pl.sales, pl.net_profit,
                   bs.total_assets, bs.equity_capital, bs.reserves
            FROM profitandloss pl
            JOIN balancesheet bs ON pl.company_id = bs.company_id AND pl.year = bs.year
            WHERE pl.year != 'PARSE_ERROR'
        """
        df = pd.read_sql_query(sql, conn)
        if df.empty:
            logger.warning("No data found for DuPont Analysis.")
            conn.close()
            return pd.DataFrame()

        records = []
        for _, row in df.iterrows():
            cid = row["company_id"]
            yr = row["year"]
            net_prof = row["net_profit"] or 0.0
            sales = row["sales"] or 0.0
            tot_assets = row["total_assets"] or 0.0
            equity = (row["equity_capital"] or 0.0) + (row["reserves"] or 0.0)

            npm, at, em, dupont_roe = calculate_dupont_stage3(net_prof, sales, tot_assets, equity)

            records.append({
                "company_id": cid,
                "year": yr,
                "net_profit_margin": npm,
                "asset_turnover": at,
                "equity_multiplier": em,
                "dupont_roe": dupont_roe
            })

        res_df = pd.DataFrame(records)
        res_df = res_df.drop_duplicates(subset=["company_id", "year"]).reset_index(drop=True)
        conn.execute("DELETE FROM dupont_analysis;")
        res_df.to_sql("dupont_analysis", conn, if_exists="append", index=False)
        conn.commit()
        logger.info(f"Populated dupont_analysis table with {len(res_df)} rows.")
        conn.close()
        return res_df


if __name__ == "__main__":
    engine = DuPontEngine()
    engine.run()
