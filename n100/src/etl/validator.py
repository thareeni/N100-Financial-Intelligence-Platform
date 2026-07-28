"""
ETL Data Quality Validator Module.
Executes 16 Data Quality (DQ-01 to DQ-16) validation rules on loaded DataFrames.
"""

import re
from typing import Dict, List, Tuple
import pandas as pd


class DataQualityValidator:
    def __init__(self):
        self.failures: List[Dict[str, str]] = []

    def log_failure(self, rule_id: str, company_id: str, year: str, field: str, issue: str, severity: str):
        self.failures.append({
            "rule_id": rule_id,
            "company_id": str(company_id),
            "year": str(year) if year is not None else "N/A",
            "field": field,
            "issue": issue,
            "severity": severity
        })

    def validate_all(self, dfs: Dict[str, pd.DataFrame]) -> Tuple[List[Dict[str, str]], Dict[str, pd.DataFrame]]:
        cleaned_dfs = {}
        for table, df in dfs.items():
            cleaned_dfs[table] = df.copy()

        companies_df = cleaned_dfs.get("companies")
        valid_company_ids = set()

        # DQ-01: Company PK Uniqueness & DQ-08: Ticker Format
        if companies_df is not None:
            dup_tickers = companies_df[companies_df["id"].duplicated()]["id"].tolist()
            if dup_tickers:
                for t in dup_tickers:
                    self.log_failure("DQ-01", t, "N/A", "id", "Duplicate company ticker in companies table", "CRITICAL")
            
            valid_company_ids = set(companies_df["id"].dropna().tolist())
            for idx, row in companies_df.iterrows():
                cid = str(row["id"])
                if not (2 <= len(cid) <= 12 and re.match(r"^[A-Z0-9&\-]+$", cid)):
                    self.log_failure("DQ-08", cid, "N/A", "id", f"Ticker format out of spec: {cid}", "CRITICAL")

        # Process child tables
        for table_name, df in cleaned_dfs.items():
            if df.empty:
                continue

            # DQ-03: FK Integrity
            if "company_id" in df.columns and valid_company_ids:
                orphan_mask = ~df["company_id"].isin(valid_company_ids)
                orphans = df[orphan_mask]
                if not orphans.empty:
                    for _, row in orphans.iterrows():
                        cid = row["company_id"]
                        yr = row.get("year", "N/A")
                        self.log_failure("DQ-03", cid, yr, "company_id", f"Orphan row in {table_name} - company_id not in companies", "CRITICAL")
                    # Reject orphan rows
                    cleaned_dfs[table_name] = df[~orphan_mask].copy()

            # DQ-07: Year Format check for time-series tables
            if "year" in df.columns:
                for _, row in df.iterrows():
                    cid = row.get("company_id", row.get("id", "N/A"))
                    yr = str(row["year"])
                    # If table has string year (like P&L, BS, CF)
                    if table_name in ["profitandloss", "balancesheet", "cashflow"]:
                        if not re.match(r"^\d{4}-\d{2}$", yr):
                            self.log_failure("DQ-07", cid, yr, "year", f"Invalid year format: {yr}", "CRITICAL")

            # DQ-02: Annual PK Uniqueness in P&L, BS, CF
            if table_name in ["profitandloss", "balancesheet", "cashflow"] and {"company_id", "year"}.issubset(df.columns):
                dups = df[df.duplicated(subset=["company_id", "year"], keep=False)]
                if not dups.empty:
                    for _, row in dups.iterrows():
                        self.log_failure("DQ-02", row["company_id"], row["year"], "company_id,year", f"Duplicate key in {table_name}", "CRITICAL")
                    # Deduplicate: keep last occurrence
                    cleaned_dfs[table_name] = cleaned_dfs[table_name].drop_duplicates(subset=["company_id", "year"], keep="last")

        # Specific table validations
        pl_df = cleaned_dfs.get("profitandloss")
        bs_df = cleaned_dfs.get("balancesheet")
        cf_df = cleaned_dfs.get("cashflow")
        doc_df = cleaned_dfs.get("documents")
        sec_df = cleaned_dfs.get("sectors")

        # Financial sector tickers to exclude from positive sales requirement (DQ-06)
        financial_tickers = set()
        if sec_df is not None and not sec_df.empty:
            financial_tickers = set(sec_df[sec_df["broad_sector"] == "Financials"]["company_id"].tolist())

        # P&L validations
        if pl_df is not None and not pl_df.empty:
            for _, row in pl_df.iterrows():
                cid = row["company_id"]
                yr = row["year"]
                sales = pd.to_numeric(row.get("sales"), errors="coerce")
                op = pd.to_numeric(row.get("operating_profit"), errors="coerce")
                opm = pd.to_numeric(row.get("opm_percentage"), errors="coerce")
                net_profit = pd.to_numeric(row.get("net_profit"), errors="coerce")
                tax_pct = pd.to_numeric(row.get("tax_percentage"), errors="coerce")
                eps = pd.to_numeric(row.get("eps"), errors="coerce")
                div_payout = pd.to_numeric(row.get("dividend_payout"), errors="coerce")

                # DQ-05: OPM Cross-Check
                if sales and sales != 0 and op is not None and opm is not None:
                    calc_opm = (op / sales) * 100
                    if abs(opm - calc_opm) >= 1.0:
                        self.log_failure("DQ-05", cid, yr, "opm_percentage", f"OPM mismatch: reported {opm}%, calculated {calc_opm:.2f}%", "WARNING")

                # DQ-06: Positive Sales (for non-financials)
                if cid not in financial_tickers and (sales is None or sales <= 0):
                    self.log_failure("DQ-06", cid, yr, "sales", f"Non-positive sales for non-financial: {sales}", "WARNING")

                # DQ-11: Tax Rate Range
                if tax_pct is not None and not pd.isna(tax_pct):
                    if tax_pct < 0 or tax_pct > 60:
                        self.log_failure("DQ-11", cid, yr, "tax_percentage", f"Tax percentage out of normal range: {tax_pct}%", "WARNING")

                # DQ-12: Dividend Payout Cap
                if div_payout is not None and not pd.isna(div_payout):
                    if div_payout > 200:
                        self.log_failure("DQ-12", cid, yr, "dividend_payout", f"High dividend payout ratio: {div_payout}%", "WARNING")

                # DQ-14: EPS Sign Consistency
                if net_profit is not None and eps is not None and not pd.isna(net_profit) and not pd.isna(eps):
                    if net_profit > 0 and eps <= 0:
                        self.log_failure("DQ-14", cid, yr, "eps", f"EPS negative or zero while net_profit > 0: EPS={eps}, PAT={net_profit}", "WARNING")

        # Balance Sheet validations
        if bs_df is not None and not bs_df.empty:
            for _, row in bs_df.iterrows():
                cid = row["company_id"]
                yr = row["year"]
                tot_assets = pd.to_numeric(row.get("total_assets"), errors="coerce")
                tot_liab = pd.to_numeric(row.get("total_liabilities"), errors="coerce")
                fa = pd.to_numeric(row.get("fixed_assets"), errors="coerce")

                # DQ-04: Balance Sheet Balance (<1% diff)
                if tot_assets and tot_assets > 0 and tot_liab is not None:
                    diff_pct = abs(tot_assets - tot_liab) / tot_assets
                    if diff_pct >= 0.01:
                        self.log_failure("DQ-04", cid, yr, "total_assets", f"Balance sheet imbalance: assets={tot_assets}, liab={tot_liab} (diff={diff_pct:.2%})", "WARNING")

                # DQ-15: Strict Balance Check (INFO)
                if tot_assets is not None and tot_liab is not None and tot_assets != tot_liab:
                    self.log_failure("DQ-15", cid, yr, "total_assets", f"Strict balance discrepancy: assets={tot_assets}, liab={tot_liab}", "INFO")

                # DQ-10: Non-Negative Fixed Assets
                if fa is not None and not pd.isna(fa) and fa < 0:
                    self.log_failure("DQ-10", cid, yr, "fixed_assets", f"Negative fixed assets: {fa}", "WARNING")

        # Cash Flow validations
        if cf_df is not None and not cf_df.empty:
            for _, row in cf_df.iterrows():
                cid = row["company_id"]
                yr = row["year"]
                cfo = pd.to_numeric(row.get("operating_activity"), errors="coerce") or 0
                cfi = pd.to_numeric(row.get("investing_activity"), errors="coerce") or 0
                cff = pd.to_numeric(row.get("financing_activity"), errors="coerce") or 0
                net_cf = pd.to_numeric(row.get("net_cash_flow"), errors="coerce")

                # DQ-09: Net Cash Check (tolerance 10 Cr)
                if net_cf is not None and not pd.isna(net_cf):
                    calc_net = cfo + cfi + cff
                    if abs(net_cf - calc_net) > 10:
                        self.log_failure("DQ-09", cid, yr, "net_cash_flow", f"Net cash flow mismatch: reported={net_cf}, sum={calc_net}", "WARNING")

        # Documents URL validation (DQ-13)
        if doc_df is not None and not doc_df.empty:
            for _, row in doc_df.iterrows():
                cid = row.get("company_id", "N/A")
                yr = row.get("year", "N/A")
                url = str(row.get("annual_report", ""))
                if not url or not (url.startswith("http://") or url.startswith("https://")):
                    self.log_failure("DQ-13", cid, yr, "annual_report", f"Invalid annual report URL format: {url}", "WARNING")

        # DQ-16: Historical Coverage Check (>= 5 years per company)
        if pl_df is not None and not pl_df.empty:
            counts = pl_df.groupby("company_id")["year"].nunique()
            for cid, count in counts.items():
                if count < 5:
                    self.log_failure("DQ-16", cid, "N/A", "year", f"Historical coverage < 5 years ({count} years found)", "WARNING")

        return self.failures, cleaned_dfs
