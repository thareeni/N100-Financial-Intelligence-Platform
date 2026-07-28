-- 10 Exploratory SQL Queries for Nifty 100 Data Foundation (Sprint 1)

-- Query 1: Verification of Master Company Count
SELECT COUNT(*) AS total_companies FROM companies;

-- Query 2: Distribution of Data Coverage (Years per Company in Profit & Loss)
SELECT company_id, COUNT(year) AS years_count
FROM profitandloss
GROUP BY company_id
ORDER BY years_count DESC;

-- Query 3: Companies with less than 5 years of financial history
SELECT company_id, COUNT(year) AS years_count
FROM profitandloss
GROUP BY company_id
HAVING years_count < 5;

-- Query 4: Total Row Counts Across All 10 Tables
SELECT 'companies' AS table_name, COUNT(*) AS row_count FROM companies
UNION ALL
SELECT 'profitandloss', COUNT(*) FROM profitandloss
UNION ALL
SELECT 'balancesheet', COUNT(*) FROM balancesheet
UNION ALL
SELECT 'cashflow', COUNT(*) FROM cashflow
UNION ALL
SELECT 'analysis', COUNT(*) FROM analysis
UNION ALL
SELECT 'documents', COUNT(*) FROM documents
UNION ALL
SELECT 'prosandcons', COUNT(*) FROM prosandcons
UNION ALL
SELECT 'sectors', COUNT(*) FROM sectors
UNION ALL
SELECT 'stock_prices', COUNT(*) FROM stock_prices
UNION ALL
SELECT 'market_cap', COUNT(*) FROM market_cap;

-- Query 5: Sector-Wise Company Count
SELECT broad_sector, COUNT(company_id) AS company_count
FROM sectors
GROUP BY broad_sector
ORDER BY company_count DESC;

-- Query 6: Top 10 Revenue Companies in Latest Available Year
SELECT p.company_id, c.company_name, p.year, p.sales
FROM profitandloss p
JOIN companies c ON p.company_id = c.id
WHERE p.year = (SELECT MAX(year) FROM profitandloss)
ORDER BY p.sales DESC
LIMIT 10;

-- Query 7: Identification of Zero-Debt Companies (Latest Year)
SELECT b.company_id, c.company_name, b.year, b.borrowings
FROM balancesheet b
JOIN companies c ON b.company_id = c.id
WHERE b.borrowings = 0 AND b.year = (SELECT MAX(year) FROM balancesheet)
ORDER BY c.company_name;

-- Query 8: Consistent Positive Cash Flow Companies (Past 5 Years)
SELECT company_id, COUNT(*) AS positive_cf_years
FROM cashflow
WHERE operating_activity > 0
GROUP BY company_id
HAVING positive_cf_years >= 5;

-- Query 9: Annual Report URL Availability Count per Company
SELECT c.id AS company_id, c.company_name, COUNT(d.year) AS report_count
FROM companies c
LEFT JOIN documents d ON c.id = d.company_id
GROUP BY c.id, c.company_name
ORDER BY report_count ASC;

-- Query 10: Market Capitalization Overview (Latest Year)
SELECT m.company_id, s.broad_sector, m.year, m.market_cap_crore
FROM market_cap m
JOIN sectors s ON m.company_id = s.company_id
WHERE m.year = (SELECT MAX(year) FROM market_cap)
ORDER BY m.market_cap_crore DESC
LIMIT 15;
