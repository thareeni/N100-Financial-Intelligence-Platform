-- Nifty 100 Financial Intelligence Platform - Exploratory SQL Queries

-- 1. Top 10 Companies by Return on Equity (ROE)
SELECT fr.company_id, c.company_name, s.broad_sector, fr.return_on_equity_pct
FROM financial_ratios fr
JOIN companies c ON fr.company_id = c.id
LEFT JOIN sectors s ON fr.company_id = s.company_id
WHERE fr.year != 'PARSE_ERROR'
ORDER BY fr.return_on_equity_pct DESC
LIMIT 10;

-- 2. Highest 5-Year Revenue CAGR Companies
SELECT fr.company_id, c.company_name, fr.revenue_cagr_5yr, fr.cagr_flag
FROM financial_ratios fr
JOIN companies c ON fr.company_id = c.id
WHERE fr.revenue_cagr_5yr IS NOT NULL AND fr.revenue_cagr_5yr != 0
ORDER BY fr.revenue_cagr_5yr DESC
LIMIT 10;

-- 3. Lowest Debt-to-Equity (Zero Debt Blue Chips)
SELECT fr.company_id, c.company_name, fr.debt_to_equity, fr.return_on_equity_pct
FROM financial_ratios fr
JOIN companies c ON fr.company_id = c.id
WHERE fr.debt_to_equity = 0.0 AND fr.return_on_equity_pct > 15.0
ORDER BY fr.return_on_equity_pct DESC
LIMIT 10;

-- 4. Highest Free Cash Flow (FCF in Crore)
SELECT fr.company_id, c.company_name, fr.free_cash_flow_cr, fr.cfo_pat_ratio
FROM financial_ratios fr
JOIN companies c ON fr.company_id = c.id
ORDER BY fr.free_cash_flow_cr DESC
LIMIT 10;

-- 5. Peer Group Percentile Ranking Comparison
SELECT pp.peer_group_name, pp.company_id, pp.metric, pp.value, pp.percentile_rank
FROM peer_percentiles pp
WHERE pp.metric = 'return_on_equity_pct'
ORDER BY pp.peer_group_name, pp.percentile_rank DESC;

-- 6. Broad Sector Summary (Average ROE & Total Market Cap)
SELECT s.broad_sector, COUNT(c.id) as company_count,
       AVG(fr.return_on_equity_pct) as avg_roe,
       SUM(mc.market_cap_crore) as total_mcap_cr
FROM sectors s
JOIN companies c ON s.company_id = c.id
LEFT JOIN financial_ratios fr ON c.id = fr.company_id
LEFT JOIN market_cap mc ON c.id = mc.company_id
GROUP BY s.broad_sector
ORDER BY total_mcap_cr DESC;

-- 7. Valuation Multiple & Intrinsic Valuation Ranking
SELECT vm.company_id, c.company_name, vm.valuation_score, vm.earnings_yield, vm.fcf_yield, vm.peg_ratio
FROM valuation_metrics vm
JOIN companies c ON vm.company_id = c.id
ORDER BY vm.valuation_score DESC
LIMIT 15;

-- 8. Composite Investment Score & Rating Breakdown
SELECT ins.company_id, c.company_name, ins.investment_score, ins.investment_rating,
       ins.quality_score, ins.growth_score, ins.value_score, ins.health_score, ins.momentum_score
FROM investment_scores ins
JOIN companies c ON ins.company_id = c.id
ORDER BY ins.investment_score DESC;
