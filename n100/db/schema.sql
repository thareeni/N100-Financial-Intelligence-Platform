-- Nifty 100 Financial Intelligence Platform - SQLite Database Schema (Sprint 1, 2 & 3)

PRAGMA foreign_keys = ON;

-- 1. Master Company Reference
DROP TABLE IF EXISTS companies;
CREATE TABLE companies (
    id VARCHAR PRIMARY KEY,
    company_logo TEXT,
    company_name VARCHAR NOT NULL,
    chart_link TEXT,
    about_company TEXT,
    website TEXT,
    nse_profile TEXT,
    bse_profile TEXT,
    face_value NUMERIC,
    book_value NUMERIC,
    roce_percentage NUMERIC,
    roe_percentage NUMERIC
);

-- 2. Annual Profit & Loss Statements
DROP TABLE IF EXISTS profitandloss;
CREATE TABLE profitandloss (
    id INTEGER,
    company_id VARCHAR NOT NULL,
    year VARCHAR NOT NULL,
    sales NUMERIC,
    expenses NUMERIC,
    operating_profit NUMERIC,
    opm_percentage NUMERIC,
    other_income NUMERIC,
    interest NUMERIC,
    depreciation NUMERIC,
    profit_before_tax NUMERIC,
    tax_percentage NUMERIC,
    net_profit NUMERIC,
    eps NUMERIC,
    dividend_payout NUMERIC,
    PRIMARY KEY (company_id, year),
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- 3. Annual Balance Sheet
DROP TABLE IF EXISTS balancesheet;
CREATE TABLE balancesheet (
    id INTEGER,
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
    other_asset NUMERIC,
    total_assets NUMERIC,
    PRIMARY KEY (company_id, year),
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- 4. Annual Cash Flow Statements
DROP TABLE IF EXISTS cashflow;
CREATE TABLE cashflow (
    id INTEGER,
    company_id VARCHAR NOT NULL,
    year VARCHAR NOT NULL,
    operating_activity NUMERIC,
    investing_activity NUMERIC,
    financing_activity NUMERIC,
    net_cash_flow NUMERIC,
    PRIMARY KEY (company_id, year),
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- 5. Pre-Computed Growth Metrics (Partial Coverage)
DROP TABLE IF EXISTS analysis;
CREATE TABLE analysis (
    id INTEGER PRIMARY KEY,
    company_id VARCHAR NOT NULL,
    compounded_sales_growth TEXT,
    compounded_profit_growth TEXT,
    stock_price_cagr TEXT,
    roe TEXT,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- 6. Annual Report Repository
DROP TABLE IF EXISTS documents;
CREATE TABLE documents (
    id INTEGER PRIMARY KEY,
    company_id VARCHAR NOT NULL,
    year INTEGER NOT NULL,
    annual_report TEXT,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- 7. Qualitative Investment Insights
DROP TABLE IF EXISTS prosandcons;
CREATE TABLE prosandcons (
    id INTEGER PRIMARY KEY,
    company_id VARCHAR NOT NULL,
    pros TEXT,
    cons TEXT,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- 8. Company Sector Mapping
DROP TABLE IF EXISTS sectors;
CREATE TABLE sectors (
    id INTEGER,
    company_id VARCHAR PRIMARY KEY,
    broad_sector TEXT NOT NULL,
    sub_sector TEXT NOT NULL,
    index_weight_pct NUMERIC,
    market_cap_category TEXT,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- 9. Monthly Stock Price History (Simulated)
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

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_pl_company ON profitandloss(company_id);
CREATE INDEX IF NOT EXISTS idx_bs_company ON balancesheet(company_id);
CREATE INDEX IF NOT EXISTS idx_cf_company ON cashflow(company_id);
CREATE INDEX IF NOT EXISTS idx_docs_company ON documents(company_id);
CREATE INDEX IF NOT EXISTS idx_sp_company_date ON stock_prices(company_id, date);
CREATE INDEX IF NOT EXISTS idx_mc_company_year ON market_cap(company_id, year);
CREATE INDEX IF NOT EXISTS idx_fr_company_year ON financial_ratios(company_id, year);
CREATE INDEX IF NOT EXISTS idx_pg_company ON peer_groups(company_id);
CREATE INDEX IF NOT EXISTS idx_pp_company_metric ON peer_percentiles(company_id, peer_group_name, metric);
