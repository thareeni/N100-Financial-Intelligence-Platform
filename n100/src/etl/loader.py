"""
ETL Loader Module.
Ingests 10 raw Excel datasets, normalises fields, validates data quality (DQ-01 to DQ-16),
loads cleaned tables into project root nifty100.db SQLite database, and generates load audit logs.
"""

import os
import time
import sqlite3
import datetime
import logging
from typing import Dict, List, Tuple
import pandas as pd
from dotenv import load_dotenv

from src.etl.normaliser import normalize_ticker, normalize_year
from src.etl.validator import DataQualityValidator

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("ETLLoader")

DB_PATH = os.getenv("DB_PATH", "nifty100.db")

# Define exact 10 source datasets for Sprint 1
CORE_FILES = {
    "companies": {"file": "companies.xlsx", "header": 1},
    "profitandloss": {"file": "profitandloss.xlsx", "header": 1},
    "balancesheet": {"file": "balancesheet.xlsx", "header": 1},
    "cashflow": {"file": "cashflow.xlsx", "header": 1},
    "analysis": {"file": "analysis.xlsx", "header": 1},
    "documents": {"file": "documents.xlsx", "header": 1},
    "prosandcons": {"file": "prosandcons.xlsx", "header": 1},
}

SUPPLEMENTARY_FILES = {
    "sectors": {"file": os.path.join("supporting datasets", "sectors.xlsx"), "header": 0},
    "stock_prices": {"file": os.path.join("supporting datasets", "stock_prices.xlsx"), "header": 0},
    "market_cap": {"file": os.path.join("supporting datasets", "market_cap.xlsx"), "header": 0},
}


class ETLLoader:
    def __init__(self, base_dir: str = "."):
        self.base_dir = base_dir
        self.db_path = os.path.join(self.base_dir, DB_PATH)
        self.output_dir = os.path.join(self.base_dir, "output")
        os.makedirs(self.output_dir, exist_ok=True)
        self.audit_log: List[Dict] = []

    def check_files_exist(self):
        all_specs = {**CORE_FILES, **SUPPLEMENTARY_FILES}
        missing = []
        for table, spec in all_specs.items():
            full_path = os.path.join(self.base_dir, spec["file"])
            if not os.path.exists(full_path):
                missing.append(full_path)
        
        if missing:
            err_msg = f"ETL Pipeline Halted: Required dataset files missing: {missing}"
            logger.error(err_msg)
            raise FileNotFoundError(err_msg)
        logger.info("All 10 required Excel source files verified.")

    def read_excel_files(self) -> Tuple[Dict[str, pd.DataFrame], Dict[str, int]]:
        raw_dfs = {}
        rows_in = {}
        all_specs = {**CORE_FILES, **SUPPLEMENTARY_FILES}

        for table, spec in all_specs.items():
            file_path = os.path.join(self.base_dir, spec["file"])
            logger.info(f"Reading {file_path} (header={spec['header']})...")
            df = pd.read_excel(file_path, header=spec["header"])
            rows_in[table] = len(df)
            raw_dfs[table] = df

        return raw_dfs, rows_in

    def normalise_datasets(self, raw_dfs: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        norm_dfs = {}
        for table_name, df in raw_dfs.items():
            df_norm = df.copy()

            # Clean column names (strip whitespace & lowercase)
            df_norm.columns = [str(c).strip().lower() for c in df_norm.columns]

            # Normalise ticker / company_id
            if table_name == "companies":
                if "id" in df_norm.columns:
                    df_norm["id"] = df_norm["id"].apply(normalize_ticker)
                # Strip company_name embedded newlines
                if "company_name" in df_norm.columns:
                    df_norm["company_name"] = df_norm["company_name"].astype(str).str.replace(r"\n", " ", regex=True).str.strip()
            else:
                if "company_id" in df_norm.columns:
                    df_norm["company_id"] = df_norm["company_id"].apply(normalize_ticker)

            # Normalise year for time-series tables
            if table_name in ["profitandloss", "balancesheet", "cashflow"]:
                if "year" in df_norm.columns:
                    df_norm["year"] = df_norm["year"].apply(normalize_year)

            norm_dfs[table_name] = df_norm

        return norm_dfs

    def initialize_schema(self, conn: sqlite3.Connection):
        schema_path = os.path.join(self.base_dir, "db", "schema.sql")
        if os.path.exists(schema_path):
            logger.info(f"Applying database schema from {schema_path}...")
            with open(schema_path, "r", encoding="utf-8") as f:
                schema_sql = f.read()
            conn.executescript(schema_sql)
            conn.commit()
        else:
            logger.warning(f"Schema file {schema_path} not found. Proceeding without schema script.")

    def run_pipeline(self):
        start_total = time.time()
        logger.info("Starting Sprint 1 ETL Pipeline execution...")

        # 1. Verify files exist
        self.check_files_exist()

        # 2. Read source Excel files
        raw_dfs, rows_in = self.read_excel_files()

        # 3. Normalise datasets
        norm_dfs = self.normalise_datasets(raw_dfs)

        # 4. Data Quality Validation
        validator = DataQualityValidator()
        failures, cleaned_dfs = validator.validate_all(norm_dfs)

        # Write validation failures log
        fail_df = pd.DataFrame(failures)
        if fail_df.empty:
            fail_df = pd.DataFrame(columns=["rule_id", "company_id", "year", "field", "issue", "severity"])
        
        fail_csv = os.path.join(self.output_dir, "validation_failures.csv")
        fail_df.to_csv(fail_csv, index=False)
        logger.info(f"Validation failures logged to {fail_csv} ({len(fail_df)} issues found).")

        # 5. Load into SQLite database
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        self.initialize_schema(conn)

        # Execution order: parent tables first
        load_order = [
            "companies",
            "profitandloss",
            "balancesheet",
            "cashflow",
            "analysis",
            "documents",
            "prosandcons",
            "sectors",
            "stock_prices",
            "market_cap"
        ]

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for table in load_order:
            t_start = time.time()
            df = cleaned_dfs.get(table, pd.DataFrame())
            
            in_cnt = rows_in.get(table, 0)
            out_cnt = len(df)
            rejected = in_cnt - out_cnt

            if not df.empty:
                table_cols = [r[1] for r in conn.execute(f"PRAGMA table_info('{table}');").fetchall()]
                valid_cols = [c for c in df.columns if c in table_cols]
                df[valid_cols].to_sql(table, conn, if_exists="append", index=False)

            t_elapsed = round(time.time() - t_start, 4)
            status = "SUCCESS" if rejected == 0 else "WARNING_REJECTIONS"

            all_specs = {**CORE_FILES, **SUPPLEMENTARY_FILES}
            src_file = all_specs[table]["file"]

            self.audit_log.append({
                "table_name": table,
                "source_file": src_file,
                "rows_in": in_cnt,
                "rows_out": out_cnt,
                "rejected": rejected,
                "status": status,
                "runtime_s": t_elapsed,
                "timestamp": timestamp
            })
            logger.info(f"Table '{table}' loaded into SQLite: {out_cnt} rows written, {rejected} rejected.")

        conn.commit()

        # Check FK integrity
        fk_check = conn.execute("PRAGMA foreign_key_check;").fetchall()
        if fk_check:
            logger.error(f"Foreign key constraint violations detected: {fk_check}")
        else:
            logger.info("PRAGMA foreign_key_check -> 0 violations.")

        conn.close()

        # Write audit log
        audit_df = pd.DataFrame(self.audit_log)
        audit_csv = os.path.join(self.output_dir, "load_audit.csv")
        audit_df.to_csv(audit_csv, index=False)
        logger.info(f"Load audit saved to {audit_csv}.")

        logger.info(f"Sprint 1 ETL Pipeline completed in {round(time.time() - start_total, 2)}s.")
        return audit_df, fail_df


if __name__ == "__main__":
    loader = ETLLoader()
    loader.run_pipeline()
