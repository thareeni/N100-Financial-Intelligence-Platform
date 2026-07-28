"""
Sprint 2 Financial Ratio Engine Runner.
Queries nifty100.db, calculates 50+ KPIs for all company-year combinations,
populates financial_ratios table in SQLite, and generates edge-case logs & capital allocation output.
"""

import os
import sqlite3
import logging
import pandas as pd
from typing import Dict, List, Optional
from dotenv import load_dotenv

from src.analytics.ratios import (
    calculate_net_profit_margin,
    calculate_operating_profit_margin,
    calculate_roe,
    calculate_roce,
    calculate_roa,
    calculate_debt_to_equity,
    calculate_interest_coverage,
    calculate_net_debt,
    calculate_asset_turnover,
    calculate_book_value_per_share
)
from src.analytics.cagr import calculate_cagr
from src.analytics.cashflow_kpis import (
    calculate_free_cash_flow,
    calculate_cfo_quality_score,
    calculate_capex_intensity,
    calculate_fcf_conversion_rate,
    classify_capital_allocation,
    safe_float
)

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("RatioRunner")

DB_PATH = os.getenv("DB_PATH", "nifty100.db")


class RatioEngineRunner:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.output_dir = "output"
        os.makedirs(self.output_dir, exist_ok=True)
        self.edge_case_logs: List[str] = []

    def log_edge_case(self, msg: str):
        self.edge_case_logs.append(msg)
        logger.debug(msg)

    def run(self):
        logger.info(f"Connecting to database {self.db_path}...")
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")

        # Create financial_ratios table if not exists
        conn.execute("""
            CREATE TABLE IF NOT EXISTS financial_ratios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id VARCHAR NOT NULL,
                year VARCHAR NOT NULL,
                net_profit_margin_pct NUMERIC,
                operating_profit_margin_pct NUMERIC,
                return_on_equity_pct NUMERIC,
                return_on_capital_employed_pct NUMERIC,
                return_on_assets_pct NUMERIC,
                debt_to_equity NUMERIC,
                interest_coverage NUMERIC,
                net_debt_cr NUMERIC,
                asset_turnover NUMERIC,
                total_debt_cr NUMERIC,
                cash_from_operations_cr NUMERIC,
                free_cash_flow_cr NUMERIC,
                capex_cr NUMERIC,
                cfo_pat_ratio NUMERIC,
                capex_intensity_pct NUMERIC,
                fcf_conversion_rate_pct NUMERIC,
                capital_allocation_pattern TEXT,
                earnings_per_share NUMERIC,
                book_value_per_share NUMERIC,
                dividend_payout_ratio_pct NUMERIC,
                revenue_cagr_3yr NUMERIC,
                revenue_cagr_5yr NUMERIC,
                revenue_cagr_10yr NUMERIC,
                pat_cagr_3yr NUMERIC,
                pat_cagr_5yr NUMERIC,
                pat_cagr_10yr NUMERIC,
                eps_cagr_5yr NUMERIC,
                revenue_cagr_5yr_flag TEXT,
                pat_cagr_5yr_flag TEXT,
                UNIQUE (company_id, year),
                FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
            );
        """)
        conn.commit()

        # Load input tables
        pl_df = pd.read_sql_query("SELECT * FROM profitandloss", conn)
        bs_df = pd.read_sql_query("SELECT * FROM balancesheet", conn)
        cf_df = pd.read_sql_query("SELECT * FROM cashflow", conn)
        co_df = pd.read_sql_query("SELECT * FROM companies", conn)
        sec_df = pd.read_sql_query("SELECT * FROM sectors", conn)

        financial_tickers = set()
        if not sec_df.empty:
            financial_tickers = set(sec_df[sec_df["broad_sector"] == "Financials"]["company_id"].tolist())

        company_face_value = {}
        if not co_df.empty:
            company_face_value = dict(zip(co_df["id"], co_df["face_value"]))

        # Merge P&L, BS, CF on (company_id, year)
        merged = pd.merge(pl_df, bs_df, on=["company_id", "year"], how="outer", suffixes=("_pl", "_bs"))
        merged = pd.merge(merged, cf_df, on=["company_id", "year"], how="outer", suffixes=("", "_cf"))

        # Clean duplicates / NaNs in key fields
        merged = merged.dropna(subset=["company_id", "year"]).copy()
        merged = merged.sort_values(by=["company_id", "year"]).reset_index(drop=True)

        logger.info(f"Merged financial history: {len(merged)} company-year records.")

        # Dictionary to build company time-series for CAGR calculations
        # Structure: company_id -> list of dicts ordered by year
        company_records: Dict[str, List[dict]] = {}

        ratios_rows = []
        cap_alloc_rows = []

        for idx, row in merged.iterrows():
            cid = str(row["company_id"])
            yr = str(row["year"])
            is_financial = cid in financial_tickers

            sales = safe_float(row.get("sales"))
            net_profit = safe_float(row.get("net_profit"))
            op_profit = safe_float(row.get("operating_profit"))
            opm_pct = safe_float(row.get("opm_percentage"))
            other_inc = safe_float(row.get("other_income"))
            interest = safe_float(row.get("interest"))
            depreciation = safe_float(row.get("depreciation"))
            eps = safe_float(row.get("eps"))
            div_payout = safe_float(row.get("dividend_payout"))

            eq_cap = safe_float(row.get("equity_capital"))
            reserves = safe_float(row.get("reserves"))
            borrowings = safe_float(row.get("borrowings"))
            tot_assets = safe_float(row.get("total_assets"))
            investments = safe_float(row.get("investments"))
            fixed_assets = safe_float(row.get("fixed_assets"))

            cfo = safe_float(row.get("operating_activity"))
            cfi = safe_float(row.get("investing_activity"))
            cff = safe_float(row.get("financing_activity"))
            net_cf = safe_float(row.get("net_cash_flow"))

            fv = company_face_value.get(cid)

            # --- Compute KPIs ---
            npm = calculate_net_profit_margin(net_profit, sales)
            opm = calculate_operating_profit_margin(op_profit, sales)
            roe = calculate_roe(net_profit, eq_cap, reserves)
            roce = calculate_roce(op_profit, depreciation, eq_cap, reserves, borrowings, is_financial)
            roa = calculate_roa(net_profit, tot_assets)

            de = calculate_debt_to_equity(borrowings, eq_cap, reserves, is_financial)
            icr = calculate_interest_coverage(op_profit, other_inc, interest)
            net_debt = calculate_net_debt(borrowings, investments, 0.0)
            asset_turn = calculate_asset_turnover(sales, tot_assets)
            bvps = calculate_book_value_per_share(eq_cap, reserves, fv)

            fcf = calculate_free_cash_flow(cfo, cfi)
            cfo_pat = calculate_cfo_quality_score(cfo, net_profit)
            capex_intensity = calculate_capex_intensity(cfi, sales)
            fcf_conv = calculate_fcf_conversion_rate(fcf, op_profit)
            cap_alloc_label = classify_capital_allocation(cfo, cfi, cff)

            # Edge Case Logging
            if de == 0.0 and (borrowings is None or borrowings == 0):
                self.log_edge_case(f"[{cid} {yr}] Debt-free company: borrowings=0, D/E set to 0.0")
            if interest == 0 or interest is None:
                self.log_edge_case(f"[{cid} {yr}] Interest is 0/None: ICR set to None (Debt Free)")
            if roe is None and net_profit is not None:
                self.log_edge_case(f"[{cid} {yr}] Negative/Zero total equity: ROE set to None")

            cap_alloc_rows.append({
                "company_id": cid,
                "year": yr,
                "CFO_sign": "+" if (cfo or 0) >= 0 else "-",
                "CFI_sign": "+" if (cfi or 0) >= 0 else "-",
                "CFF_sign": "+" if (cff or 0) >= 0 else "-",
                "pattern_label": cap_alloc_label
            })

            rec = {
                "company_id": cid,
                "year": yr,
                "sales": sales,
                "net_profit": net_profit,
                "eps": eps,
                "net_profit_margin_pct": npm,
                "operating_profit_margin_pct": opm,
                "return_on_equity_pct": roe,
                "return_on_capital_employed_pct": roce,
                "return_on_assets_pct": roa,
                "debt_to_equity": de,
                "interest_coverage": icr,
                "net_debt_cr": net_debt,
                "asset_turnover": asset_turn,
                "total_debt_cr": borrowings,
                "cash_from_operations_cr": cfo,
                "free_cash_flow_cr": fcf,
                "capex_cr": abs(cfi) if cfi is not None else None,
                "cfo_pat_ratio": cfo_pat,
                "capex_intensity_pct": capex_intensity,
                "fcf_conversion_rate_pct": fcf_conv,
                "capital_allocation_pattern": cap_alloc_label,
                "earnings_per_share": eps,
                "book_value_per_share": bvps,
                "dividend_payout_ratio_pct": div_payout,
            }

            ratios_rows.append(rec)

            if cid not in company_records:
                company_records[cid] = []
            company_records[cid].append(rec)

        # --- Compute CAGRs over time-series ---
        ratios_df = pd.DataFrame(ratios_rows)
        ratios_df["revenue_cagr_3yr"] = None
        ratios_df["revenue_cagr_5yr"] = None
        ratios_df["revenue_cagr_10yr"] = None
        ratios_df["pat_cagr_3yr"] = None
        ratios_df["pat_cagr_5yr"] = None
        ratios_df["pat_cagr_10yr"] = None
        ratios_df["eps_cagr_5yr"] = None
        ratios_df["revenue_cagr_5yr_flag"] = "INSUFFICIENT"
        ratios_df["pat_cagr_5yr_flag"] = "INSUFFICIENT"

        # Map index for fast updates
        row_map = {(r["company_id"], r["year"]): i for i, r in ratios_df.iterrows()}

        for cid, history in company_records.items():
            n = len(history)
            for idx, current in enumerate(history):
                cyr = current["year"]
                c_idx = row_map[(cid, cyr)]

                # 3Y CAGR (look back 3 steps)
                if idx >= 3:
                    base = history[idx - 3]
                    v, f = calculate_cagr(base["sales"], current["sales"], 3)
                    ratios_df.at[c_idx, "revenue_cagr_3yr"] = v
                    v, f = calculate_cagr(base["net_profit"], current["net_profit"], 3)
                    ratios_df.at[c_idx, "pat_cagr_3yr"] = v

                # 5Y CAGR (look back 5 steps)
                if idx >= 5:
                    base = history[idx - 5]
                    v, f = calculate_cagr(base["sales"], current["sales"], 5)
                    ratios_df.at[c_idx, "revenue_cagr_5yr"] = v
                    ratios_df.at[c_idx, "revenue_cagr_5yr_flag"] = f

                    v, f = calculate_cagr(base["net_profit"], current["net_profit"], 5)
                    ratios_df.at[c_idx, "pat_cagr_5yr"] = v
                    ratios_df.at[c_idx, "pat_cagr_5yr_flag"] = f

                    v, f = calculate_cagr(base["eps"], current["eps"], 5)
                    ratios_df.at[c_idx, "eps_cagr_5yr"] = v

                # 10Y CAGR (look back 10 steps)
                if idx >= 10:
                    base = history[idx - 10]
                    v, f = calculate_cagr(base["sales"], current["sales"], 10)
                    ratios_df.at[c_idx, "revenue_cagr_10yr"] = v

                    v, f = calculate_cagr(base["net_profit"], current["net_profit"], 10)
                    ratios_df.at[c_idx, "pat_cagr_10yr"] = v

        # Drop temporary helper columns
        db_df = ratios_df.drop(columns=["sales", "net_profit", "eps"])

        # Populate financial_ratios table in SQLite
        conn.execute("DELETE FROM financial_ratios;")
        db_df.to_sql("financial_ratios", conn, if_exists="append", index=False)
        conn.commit()

        # Check count
        cnt = conn.execute("SELECT COUNT(*) FROM financial_ratios;").fetchone()[0]
        logger.info(f"Populated financial_ratios table with {cnt} rows.")

        conn.close()

        # Output log files
        log_file = os.path.join(self.output_dir, "ratio_edge_cases.log")
        with open(log_file, "w", encoding="utf-8") as f:
            f.write("\n".join(self.edge_case_logs))
        logger.info(f"Edge case logs written to {log_file} ({len(self.edge_case_logs)} entries).")

        cap_alloc_df = pd.DataFrame(cap_alloc_rows)
        cap_file = os.path.join(self.output_dir, "capital_allocation.csv")
        cap_alloc_df.to_csv(cap_file, index=False)
        logger.info(f"Capital allocation matrix written to {cap_file}.")

        return cnt, ratios_df


if __name__ == "__main__":
    runner = RatioEngineRunner()
    runner.run()
