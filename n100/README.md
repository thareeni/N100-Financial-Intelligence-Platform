# Nifty 100 Financial Intelligence Platform - Sprint 1 (Data Foundation & ETL Pipeline)

Production-grade ETL pipeline and SQLite data foundation for the Bluestock Fintech MJ28 project.

## Sprint 1 Overview
Sprint 1 establishes a fully loaded, validated, and normalized SQLite database (`nifty100.db` in project root) containing **10 tables** populated strictly from 12 raw Excel files. All 16 Data Quality (DQ-01 to DQ-16) validation rules are executed during load.

### Core Deliverables
- `nifty100.db`: SQLite database located in root directory (10 populated tables).
- `output/load_audit.csv`: Per-table load row counts, rejections, and execution metrics.
- `output/validation_failures.csv`: Structured log of Data Quality rule violations with severity levels.
- `src/etl/loader.py`: Comprehensive ingestion and SQLite database loading engine.
- `src/etl/normaliser.py`: Year standardization (`Mar-23`, `FY23`, etc. -> `YYYY-MM`) and ticker normalization.
- `src/etl/validator.py`: Implementation of 16 DQ validation rules.
- `db/schema.sql`: DDL schema for 10 tables with strict primary/foreign key constraints and indexes.
- `tests/etl/`: Unit test suite (35+ test cases).
- `notebooks/exploratory_queries.sql`: 10 SQL exploratory queries for data quality review.

---

## Quick Start Guide

### 1. Setup Virtual Environment & Install Dependencies
```bash
python -m venv .venv
# On Windows PowerShell:
.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Environment
Copy `.env.template` to `.env`:
```bash
cp .env.template .env
```
Default `DB_PATH=nifty100.db`.

### 3. Execute ETL Pipeline & Load Database
```bash
python -m src.etl.loader
# OR using Makefile:
make load
```

### 4. Run Unit Test Suite
```bash
pytest tests/
# OR using Makefile:
make test
```

---

## Sprint 1 Database Scope (10 Tables)
1. `companies` (Primary Key: `id` [NSE Ticker])
2. `profitandloss` (Composite Key: `company_id, year`)
3. `balancesheet` (Composite Key: `company_id, year`)
4. `cashflow` (Composite Key: `company_id, year`)
5. `analysis` (Key: `company_id`)
6. `documents` (Key: `id` [Auto PK])
7. `prosandcons` (Key: `id` [Auto PK])
8. `sectors` (Key: `company_id`)
9. `stock_prices` (Key: `id` [Auto PK])
10. `market_cap` (Key: `id` [Auto PK])
