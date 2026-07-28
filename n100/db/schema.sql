-- SQLite Schema for Nifty 100 Financial Intelligence Platform
-- Target Database: nifty100.db (SQLite)
-- Database Standard: Explicit Primary Keys, Foreign Keys, Datatypes, Indexing

PRAGMA foreign_keys = ON;

-- 1. Core Companies Table
DROP TABLE IF EXISTS companies;
CREATE TABLE companies (
    id VARCHAR PRIMARY KEY, -- Primary Key: NSE Ticker Symbol (e.g., RELIANCE, TCS)
    company_name VARCHAR NOT NULL,
    bse_code VARCHAR,
    isin VARCHAR UNIQUE,
    company_logo VARCHAR,
    chart_link VARCHAR,
    face_value NUMERIC
);

-- 2. Annual Profit & Loss Data
DROP TABLE IF EXISTS profitandloss;
CREATE TABLE profitandloss (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id VARCHAR NOT NULL,
    year VARCHAR NOT NULL, -- e.g., '2023-03' or '2024-03'
    sales NUMERIC,
    expenses NUMERIC,
    operating_profit NUMERIC,
    opm_percent NUMERIC,
    other_income NUMERIC,
    interest NUMERIC,
    depreciation NUMERIC,
    profit_before_tax NUMERIC,
    tax_percent NUMERIC,
    net_profit NUMERIC,
    eps_in_rs NUMERIC,
    dividend_payout_percent NUMERIC,
    UNIQUE (company_id, year),
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- 3. Annual Balance Sheet Data
DROP TABLE IF EXISTS balancesheet;
CREATE TABLE balancesheet (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id VARCHAR NOT NULL,
    year VARCHAR NOT NULL,
    equity_capital NUMERIC,
    reserves NUMERIC,
    borrowings NUMERIC,
    other_liabilities NUMERIC,
    total_liabilities NUMERIC,
    fixed_assets NUMERIC,
    cwip NUMERIC,
    investments NUMERIC,
    other_asset_items NUMERIC,
    total_assets NUMERIC,
    UNIQUE (company_id, year),
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- 4. Annual Cash Flow Data
DROP TABLE IF EXISTS cashflow;
CREATE TABLE cashflow (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id VARCHAR NOT NULL,
    year VARCHAR NOT NULL,
    cash_from_operating_activity NUMERIC,
    cash_from_investing_activity NUMERIC,
    cash_from_financing_activity NUMERIC,
    net_cash_flow NUMERIC,
    UNIQUE (company_id, year),
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- 5. Qualitative Financial Analysis Table
DROP TABLE IF EXISTS analysis;
CREATE TABLE analysis (
    id INTEGER PRIMARY KEY,
    company_id VARCHAR NOT NULL,
    company_name VARCHAR,
    sales_growth_3yr_pct NUMERIC,
    sales_growth_5yr_pct NUMERIC,
    profit_growth_3yr_pct NUMERIC,
    profit_growth_5yr_pct NUMERIC,
    roe_3yr_avg_pct NUMERIC,
    roe_5yr_avg_pct NUMERIC,
    roce_3yr_avg_pct NUMERIC,
    roce_5yr_avg_pct NUMERIC,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- 6. Document Filings & Reports Metadata
DROP TABLE IF EXISTS documents;
CREATE TABLE documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id VARCHAR NOT NULL,
    title TEXT,
    document_type TEXT,
    date TEXT,
    url TEXT,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- 7. Corporate Pros and Cons Statements
DROP TABLE IF EXISTS prosandcons;
CREATE TABLE prosandcons (
    id INTEGER PRIMARY KEY,
    company_id VARCHAR NOT NULL,
    company_name VARCHAR,
    pros_text TEXT,
    cons_text TEXT,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- 8. Sector Mapping & Classifications
DROP TABLE IF EXISTS sectors;
CREATE TABLE sectors (
    company_id VARCHAR PRIMARY KEY,
    company_name VARCHAR,
    broad_sector VARCHAR,
    sub_sector VARCHAR,
    index_weight_pct NUMERIC,
    market_cap_category VARCHAR,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- 9. Monthly Stock Price History
DROP TABLE IF EXISTS stock_prices;
CREATE TABLE stock_prices (
    id INTEGER PRIMARY KEY,
    company_id VARCHAR NOT NULL,
    date VARCHAR NOT NULL,
    open_price NUMERIC,
    high_price NUMERIC,
    low_price NUMERIC,
    close_price NUMERIC,
    volume INTEGER,
    adjusted_close NUMERIC,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- 10. Annual Valuation Multiples
DROP TABLE IF EXISTS market_cap;
CREATE TABLE market_cap (
    id INTEGER PRIMARY KEY,
    company_id VARCHAR NOT NULL,
    year INTEGER NOT NULL,
    market_cap_crore NUMERIC,
    enterprise_value_crore NUMERIC,
    pe_ratio NUMERIC,
    pb_ratio NUMERIC,
    ev_ebitda NUMERIC,
    dividend_yield_pct NUMERIC,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- 11. Sprint 2: Financial Ratios & Computed KPIs Table
DROP TABLE IF EXISTS financial_ratios;
CREATE TABLE financial_ratios (
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

-- 12. Sprint 3: Peer Comparison Groups Table
DROP TABLE IF EXISTS peer_groups;
CREATE TABLE peer_groups (
    id INTEGER PRIMARY KEY,
    peer_group_name VARCHAR NOT NULL,
    company_id VARCHAR NOT NULL,
    is_benchmark BOOLEAN DEFAULT 0,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- 13. Sprint 3: Peer Percentiles Ranking Table
DROP TABLE IF EXISTS peer_percentiles;
CREATE TABLE peer_percentiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id VARCHAR NOT NULL,
    peer_group_name VARCHAR NOT NULL,
    year VARCHAR NOT NULL,
    metric VARCHAR NOT NULL,
    metric_value NUMERIC,
    percentile_rank NUMERIC NOT NULL,
    is_benchmark BOOLEAN DEFAULT 0,
    UNIQUE (company_id, peer_group_name, year, metric),
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- 14. Sprint 4: Financial Health Scoring Table (Altman Z-Score & Beneish M-Score)
DROP TABLE IF EXISTS financial_health;
CREATE TABLE financial_health (
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

-- 15. Sprint 4: 3-Stage DuPont Analysis Table
DROP TABLE IF EXISTS dupont_analysis;
CREATE TABLE dupont_analysis (
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

-- 16. Sprint 4: Valuation Multiples & Intrinsic Value Table
DROP TABLE IF EXISTS valuation_metrics;
CREATE TABLE valuation_metrics (
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

-- 17. Sprint 4: Overall Investment Scores & Ratings Table
DROP TABLE IF EXISTS investment_scores;
CREATE TABLE investment_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id VARCHAR NOT NULL,
    year VARCHAR NOT NULL,
    quality_score NUMERIC NOT NULL,
    growth_score NUMERIC NOT NULL,
    value_score NUMERIC NOT NULL,
    health_score NUMERIC NOT NULL,
    momentum_score NUMERIC NOT NULL,
    investment_score NUMERIC NOT NULL,
    investment_rating VARCHAR NOT NULL,
    UNIQUE (company_id, year),
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_pl_company ON profitandloss(company_id);
CREATE INDEX IF NOT EXISTS idx_bs_company ON balancesheet(company_id);
CREATE INDEX IF NOT EXISTS idx_cf_company ON cashflow(company_id);
CREATE INDEX IF NOT EXISTS idx_docs_company ON documents(company_id);
CREATE INDEX IF NOT EXISTS idx_sp_company_date ON stock_prices(company_id, date);
CREATE INDEX IF NOT EXISTS idx_mc_company_year ON market_cap(company_id, year);
CREATE INDEX IF NOT EXISTS idx_fr_company_year ON financial_ratios(company_id, year);
CREATE INDEX IF NOT EXISTS idx_pg_company ON peer_groups(company_id);
CREATE INDEX IF NOT EXISTS idx_pp_company_metric ON peer_percentiles(company_id, peer_group_name, metric);
CREATE INDEX IF NOT EXISTS idx_fh_company_year ON financial_health(company_id, year);
CREATE INDEX IF NOT EXISTS idx_da_company_year ON dupont_analysis(company_id, year);
CREATE INDEX IF NOT EXISTS idx_vm_company_year ON valuation_metrics(company_id, year);
CREATE INDEX IF NOT EXISTS idx_is_company_year ON investment_scores(company_id, year);
