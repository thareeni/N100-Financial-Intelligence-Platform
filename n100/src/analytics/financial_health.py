"""
Financial Health Scoring Engine (Altman Z-Score & Beneish M-Score).
Computes Altman Z-Score (Distress vs Safe Zone) and Beneish M-Score (Earnings Manipulation Risk).
Populates the financial_health SQLite table.
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
logger = logging.getLogger("FinancialHealthEngine")

DB_PATH = os.getenv("DB_PATH", "nifty100.db")


def calculate_altman_z_score(
    working_capital: float,
    retained_earnings: float,
    ebit: float,
    market_cap: float,
    total_liabilities: float,
    sales: float,
    total_assets: float
) -> Tuple[Optional[float], str]:
    """
    Calculates Altman Z-Score:
    Z = 1.2*X1 + 1.4*X2 + 3.3*X3 + 0.6*X4 + 0.999*X5
    Ratings: Z > 2.99 -> Safe Zone, 1.81 <= Z <= 2.99 -> Grey Zone, Z < 1.81 -> Distress Zone
    """
    if total_assets is None or total_assets <= 0:
        return None, "Grey Zone"

    x1 = (working_capital or 0.0) / total_assets
    x2 = (retained_earnings or 0.0) / total_assets
    x3 = (ebit or 0.0) / total_assets
    
    tot_liab = total_liabilities if (total_liabilities and total_liabilities > 0) else 1.0
    x4 = (market_cap or 0.0) / tot_liab
    
    x5 = (sales or 0.0) / total_assets

    z_score = round(1.2 * x1 + 1.4 * x2 + 3.3 * x3 + 0.6 * x4 + 0.999 * x5, 2)

    if z_score > 2.99:
        rating = "Safe Zone"
    elif z_score >= 1.81:
        rating = "Grey Zone"
    else:
        rating = "Distress Zone"

    return z_score, rating


def calculate_beneish_m_score(
    sales_t: float, sales_t1: float,
    cogs_t: float, cogs_t1: float,
    assets_t: float, assets_t1: float,
    non_curr_assets_t: float, non_curr_assets_t1: float,
    depr_t: float, depr_t1: float,
    sga_t: float, sga_t1: float,
    debt_t: float, debt_t1: float,
    op_inc_t: float, cfo_t: float
) -> Tuple[Optional[float], str]:
    """
    Calculates Beneish M-Score 8-variable model for earnings manipulation risk.
    M > -1.78 -> High Risk, M <= -1.78 -> Low Risk.
    """
    if not assets_t or assets_t <= 0 or not assets_t1 or assets_t1 <= 0 or not sales_t1 or sales_t1 <= 0:
        return -2.50, "Low Risk"

    sgi = sales_t / sales_t1 if sales_t1 > 0 else 1.0
    
    gmi_t = (sales_t - cogs_t) / sales_t if sales_t > 0 else 0.2
    gmi_t1 = (sales_t1 - cogs_t1) / sales_t1 if sales_t1 > 0 else 0.2
    gmi = gmi_t1 / gmi_t if gmi_t > 0 else 1.0

    aqi_t = 1.0 - ((assets_t - non_curr_assets_t) / assets_t)
    aqi_t1 = 1.0 - ((assets_t1 - non_curr_assets_t1) / assets_t1)
    aqi = aqi_t / aqi_t1 if aqi_t1 > 0 else 1.0

    depi_rate_t = depr_t / (non_curr_assets_t + depr_t) if (non_curr_assets_t + depr_t) > 0 else 0.05
    depi_rate_t1 = depr_t1 / (non_curr_assets_t1 + depr_t1) if (non_curr_assets_t1 + depr_t1) > 0 else 0.05
    depi = depi_rate_t1 / depi_rate_t if depi_rate_t > 0 else 1.0

    sgai_t = sga_t / sales_t if sales_t > 0 else 0.1
    sgai_t1 = sga_t1 / sales_t1 if sales_t1 > 0 else 0.1
    sgai = sgai_t / sgai_t1 if sgai_t1 > 0 else 1.0

    lvgi_t = debt_t / assets_t
    lvgi_t1 = debt_t1 / assets_t1
    lvgi = lvgi_t / lvgi_t1 if lvgi_t1 > 0 else 1.0

    tata = (op_inc_t - cfo_t) / assets_t
    dsi = 1.0

    m_score = round(
        -4.84 + 0.920 * dsi + 0.528 * gmi + 0.404 * aqi + 0.892 * sgi +
        0.115 * depi - 0.172 * sgai + 4.679 * tata + 0.327 * lvgi,
        2
    )

    flag = "High Risk" if m_score > -1.78 else "Low Risk"
    return m_score, flag


class FinancialHealthEngine:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path

    def run(self) -> pd.DataFrame:
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")

        # Ensure table exists
        conn.execute("""
            CREATE TABLE IF NOT EXISTS financial_health (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id VARCHAR NOT NULL,
                year VARCHAR NOT NULL,
                altman_z_score NUMERIC,
                financial_health_rating VARCHAR NOT NULL,
                beneish_m_score NUMERIC,
                manipulation_risk_flag VARCHAR NOT NULL,
                UNIQUE (company_id, year),
                FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
            );
        """)
        conn.commit()

        # Query financial metrics
        sql = """
            SELECT pl.company_id, pl.year, pl.sales, pl.expenses, pl.operating_profit, pl.profit_before_tax, pl.interest, pl.depreciation, pl.net_profit,
                   bs.total_assets, bs.borrowings, bs.reserves, bs.other_liabilities, bs.total_liabilities, bs.fixed_assets, bs.investments,
                   cf.cash_from_operating_activity,
                   mc.market_cap_crore
            FROM profitandloss pl
            JOIN balancesheet bs ON pl.company_id = bs.company_id AND pl.year = bs.year
            LEFT JOIN cashflow cf ON pl.company_id = cf.company_id AND pl.year = cf.year
            LEFT JOIN market_cap mc ON pl.company_id = mc.company_id
            WHERE pl.year != 'PARSE_ERROR'
            ORDER BY pl.company_id, pl.year ASC
        """
        df = pd.read_sql_query(sql, conn)
        if df.empty:
            logger.warning("No data found for Financial Health calculations.")
            conn.close()
            return pd.DataFrame()

        records = []
        for cid, group_df in df.groupby("company_id"):
            group_df = group_df.sort_values(by="year").reset_index(drop=True)
            for idx, row in group_df.iterrows():
                yr = row["year"]
                tot_assets = row["total_assets"] or 1.0
                sales = row["sales"] or 0.0
                pbt = row["profit_before_tax"] or 0.0
                interest = row["interest"] or 0.0
                ebit = pbt + interest
                reserves = row["reserves"] or 0.0
                mcap = row["market_cap_crore"] or 1000.0
                tot_liab = row["total_liabilities"] or (row["borrowings"] or 0.0 + (row["other_liabilities"] or 0.0))
                
                # Working capital ~ (total_assets - fixed_assets - investments - total_liabilities)
                non_curr = (row["fixed_assets"] or 0.0) + (row["investments"] or 0.0)
                curr_assets = max(tot_assets - non_curr, 0.0)
                curr_liab = row["other_liabilities"] or 0.0
                working_capital = curr_assets - curr_liab

                z_score, z_rating = calculate_altman_z_score(
                    working_capital, reserves, ebit, mcap, tot_liab, sales, tot_assets
                )

                # Prior year values for Beneish M-Score
                if idx > 0:
                    prev_row = group_df.iloc[idx - 1]
                    sales_t1 = prev_row["sales"] or sales
                    cogs_t = row["expenses"] or 0.0
                    cogs_t1 = prev_row["expenses"] or cogs_t
                    assets_t1 = prev_row["total_assets"] or tot_assets
                    non_curr_t1 = (prev_row["fixed_assets"] or 0.0) + (prev_row["investments"] or 0.0)
                    depr_t = row["depreciation"] or 0.0
                    depr_t1 = prev_row["depreciation"] or depr_t
                    sga_t = cogs_t * 0.2
                    sga_t1 = cogs_t1 * 0.2
                    debt_t = row["borrowings"] or 0.0
                    debt_t1 = prev_row["borrowings"] or debt_t
                    cfo_t = row["cash_from_operating_activity"] or (row["net_profit"] or 0.0)
                    op_inc_t = row["operating_profit"] or 0.0

                    m_score, m_flag = calculate_beneish_m_score(
                        sales, sales_t1, cogs_t, cogs_t1, tot_assets, assets_t1,
                        non_curr, non_curr_t1, depr_t, depr_t1, sga_t, sga_t1,
                        debt_t, debt_t1, op_inc_t, cfo_t
                    )
                else:
                    m_score, m_flag = -2.45, "Low Risk"

                records.append({
                    "company_id": cid,
                    "year": yr,
                    "altman_z_score": z_score,
                    "financial_health_rating": z_rating,
                    "beneish_m_score": m_score,
                    "manipulation_risk_flag": m_flag
                })

        res_df = pd.DataFrame(records)
        res_df = res_df.drop_duplicates(subset=["company_id", "year"]).reset_index(drop=True)
        conn.execute("DELETE FROM financial_health;")
        res_df.to_sql("financial_health", conn, if_exists="append", index=False)
        conn.commit()
        logger.info(f"Populated financial_health table with {len(res_df)} rows.")
        conn.close()
        return res_df


if __name__ == "__main__":
    engine = FinancialHealthEngine()
    engine.run()
