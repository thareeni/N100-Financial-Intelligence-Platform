# Nifty 100 Financial Intelligence Platform

A production-grade Python and SQLite financial analytics, stock screening, peer benchmarking, and investment intelligence platform for the Nifty 100 universe.

---

## 🌟 Key Features & Capabilities

1. **Data Foundation & Ingestion Engine (Sprint 1)**:
   - Automated ingestion of 12 Excel financial datasets into SQLite (`nifty100.db`).
   - 16 Data Quality (DQ-01 to DQ-16) validation checks with strict foreign key integrity.

2. **Financial Ratio Engine (Sprint 2)**:
   - Computes 50+ KPIs across Profitability, Leverage, Efficiency, Valuation, and Cash Quality.
   - 3Y/5Y/10Y CAGR Engine with turnaround and decline edge-case flags.
   - 8-pattern Capital Allocation Classifier.

3. **Stock Screener & Peer Comparison Engine (Sprint 3)**:
   - Multi-criteria filtering supporting 15 financial metrics with Financial sector D/E carve-outs.
   - 0–100 Winsorised Composite Quality Score.
   - 6 Pre-built Preset Screeners (Quality Compounder, Value Pick, Growth Accelerator, Dividend Champion, Debt-Free Blue Chip, Turnaround Watch).
   - Intra-group percentile rankings & 56 8-axis Matplotlib polar radar PNG charts (`reports/radar_charts/`).

4. **Advanced Investment Analytics Layer (Sprint 4)**:
   - **Altman Z-Score** (Distress vs Safe Zone classification).
   - **Beneish M-Score** (8-variable earnings manipulation risk detection).
   - **3-Stage DuPont ROE Breakdown** ($\text{ROE} = \text{NPM} \times \text{Asset Turnover} \times \text{Equity Multiplier}$).
   - **Valuation Intelligence Engine** (Earnings Yield, FCF Yield, PEG Ratio, EV/Sales, EV/EBITDA).
   - **0–100 Investment Score & Rating Classifier** (**Strong Buy**, **Buy**, **Hold**, **Avoid**).

5. **Production Readiness & Interactive Dashboard (Sprint 5)**:
   - Single-command pipeline orchestrator (`python src/main.py`).
   - Interactive 5-page Streamlit production dashboard (`streamlit run dashboard/app.py`).
   - Containerized deployment (`Dockerfile`, `.env.template`, `.github/workflows/test.yml`).

6. **QA, Final Validation & Reporting (Sprint 6)**:
   - Automated end-to-end QA validation suite (`tests/test_final_validation.py`).
   - Project Health Report Generator (`src/final_report.py` -> `output/final_project_report.xlsx`).

---

## 🏗️ Architecture & Data Flow

```
[Raw Excel Source Datasets (12 Files)]
                 │
                 ▼
     [src/etl/loader.py (Sprint 1)]
                 │  (Ingests & Validates DQ-01 to DQ-16)
                 ▼
        [SQLite: nifty100.db]
                 │
                 ▼
  [src/analytics/runner.py (Sprint 2)]
                 │  (Computes 50+ Ratios & CAGRs)
                 ▼
   [src/screener/engine.py (Sprint 3)] ──► [output/screener_output.xlsx]
                 │  (Winsorised Quality Score & Presets)
                 ▼
   [src/analytics/peer.py (Sprint 3)] ──► [reports/radar_charts/*.png] & [output/peer_comparison.xlsx]
                 │  (Percentiles & 8-Axis Radar)
                 ▼
 [src/analytics/investment_score.py (Sprint 4)] ──► [output/investment_intelligence.xlsx]
                 │  (Health, DuPont, Valuation, Investment Score)
                 ▼
 [src/main.py (Pipeline Orchestration)]
                 │
                 ▼
 [dashboard/app.py (Sprint 5 Streamlit Production Dashboard)]
```

---

## 🛠️ Installation & Quickstart

### Prerequisites
- Python 3.10+
- SQLite3

### Setup Instructions

1. **Clone Repository & Set Up Virtual Environment**:
   ```bash
   git clone <repository-url>
   cd n100
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   ```bash
   cp .env.template .env
   ```

---

## 🚀 Running the Platform

### 1. Run Complete Pipeline (Single Command Orchestration)
Runs ETL, Ratios, Screener, Peer Engine, Health Scoring, DuPont Breakdown, Valuation, and Investment Scoring:
```bash
python src/main.py
# or using Makefile:
make run
```

### 2. Launch Interactive Production Dashboard
Launch the 5-page Streamlit web dashboard:
```bash
streamlit run dashboard/app.py
# or using Makefile:
make dashboard
```
Access dashboard in your web browser at: `http://localhost:8501`.

### 3. Generate Final Project Health Report
```bash
python src/final_report.py
# or using Makefile:
make final
```

### 4. Run Unit Test Suite
Execute all pytest unit & integration tests with HTML report generation:
```bash
pytest tests/ --html=output/pytest_report.html --self-contained-html
# or using Makefile:
make test
```

---

## 📊 Dashboard Overview & Page Structure

1. **Page 1: Nifty 100 Overview**: Total companies, sector counts, total market cap, median P/E, sector distribution bar chart.
2. **Page 2: Stock Screener**: Interactive filtering across all 6 preset screeners with sector, quality score, and ROE sliders.
3. **Page 3: Investment Intelligence**: Ranked list of top investment opportunities, metric cards for Strong Buy / Buy / Hold / Avoid counts.
4. **Page 4: Peer Comparison**: Intra-group metric tables, percentile ranks, and 8-axis radar chart PNG viewer.
5. **Page 5: Company Deep-Dive View**: Selected ticker 360-degree view showing ratios, DuPont breakdown, Altman Z-Score, Beneish M-Score, valuation multiples, and investment ratings.

---

## 📂 Deliverables & Output Files Reference

| File Path | Description |
|-----------|-------------|
| `nifty100.db` | Main SQLite Database (17 populated tables) |
| `output/screener_output.xlsx` | 6 Preset Screener Sheets with 20 KPI columns & threshold color fills |
| `output/peer_comparison.xlsx` | 11 Peer Group sheets with percentile ranks & median summary rows |
| `output/investment_intelligence.xlsx` | 5-sheet Investment Intelligence report (Top 20 opportunities, Health, DuPont, Valuation, Risk Flags) |
| `output/final_project_report.xlsx` | Sprint 6 Final Project Health & QA Report |
| `output/capital_allocation.csv` | 8-pattern Capital Allocation classifications for 92 companies |
| `output/load_audit.csv` | ETL Ingestion Row Count Audit Log |
| `output/validation_failures.csv` | Data Quality Rules DQ-01 to DQ-16 log |
| `output/ratio_edge_cases.log` | Log of ratio formula edge cases |
| `reports/radar_charts/*.png` | 56 8-axis Matplotlib polar radar charts |
| `output/pytest_report.html` | Self-contained HTML unit test execution report |

---

## 🏆 Sprint Completion Summary (Sprints 1 to 6)

- **Sprint 1**: Data Foundation & ETL Pipeline (10 core tables, 16 DQ rules, 42 tests).
- **Sprint 2**: Financial Ratio Engine & CAGR Engine (Populated `financial_ratios`, 30 tests).
- **Sprint 3**: Stock Screener & Peer Comparison Engine (Composite Quality Score, 6 Presets, Radar Charts, 12 tests).
- **Sprint 4**: Advanced Analytics & Investment Intelligence (Altman Z, Beneish M, DuPont, Valuation, Investment Score, 11 tests).
- **Sprint 5**: Production Readiness, Single-Command Pipeline, Interactive Streamlit Dashboard, Docker, CI/CD Workflow.
- **Sprint 6**: Final Production Validation (`test_final_validation.py`), Project Health Report Generator (`final_project_report.xlsx`), Documentation & Quality Assurance.
