"""
Main Pipeline Orchestrator for Nifty 100 Financial Intelligence Platform.
Executes the full end-to-end data & analytics pipeline:
1. ETL Data Ingestion & Validation (Sprint 1)
2. Financial Ratio Engine (Sprint 2)
3. Stock Screener & Composite Quality Scoring Engine (Sprint 3)
4. Peer Comparison & Radar Chart Generator (Sprint 3)
5. Financial Health Engine - Altman Z & Beneish M (Sprint 4)
6. 3-Stage DuPont Analysis Engine (Sprint 4)
7. Valuation Intelligence Engine (Sprint 4)
8. Investment Scoring & Intelligence Exporter (Sprint 4)
"""

import os
import sys
import time
import logging
import sqlite3
import pandas as pd
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath("."))

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("PipelineOrchestrator")

DB_PATH = os.getenv("DB_PATH", "nifty100.db")


def run_full_pipeline(db_path: str = DB_PATH) -> bool:
    """Executes all 5 pipeline stages sequentially."""
    start_time = time.time()
    logger.info("==================================================")
    logger.info("STARTING NIFTY 100 FINANCIAL INTELLIGENCE PIPELINE")
    logger.info("==================================================")

    try:
        # Stage 1: ETL Pipeline
        logger.info("\n--- Stage 1: ETL Ingestion & DQ Validation ---")
        from src.etl.loader import ETLLoader
        loader = ETLLoader()
        loader.run_pipeline()

        # Stage 2: Ratio Engine
        logger.info("\n--- Stage 2: Financial Ratio Calculation ---")
        from src.analytics.runner import RatioEngineRunner
        ratio_runner = RatioEngineRunner(db_path=db_path)
        ratio_runner.run()

        # Stage 3: Screener Engine
        logger.info("\n--- Stage 3: Stock Screener & Composite Quality Scoring ---")
        from src.screener.engine import ScreenerEngine
        screener = ScreenerEngine(db_path=db_path)
        screener.export_screener_excel()

        # Stage 4: Peer Comparison & Radar Charts
        logger.info("\n--- Stage 4: Peer Percentile Ranking & Radar Charts ---")
        from src.analytics.peer import PeerComparisonEngine
        peer_engine = PeerComparisonEngine(db_path=db_path)
        peer_engine.compute_peer_percentiles()
        peer_engine.generate_radar_charts()
        peer_engine.export_peer_comparison_excel()

        # Stage 5: Advanced Analytics & Investment Score Engine
        logger.info("\n--- Stage 5: Financial Health, DuPont, Valuation & Investment Scoring ---")
        from src.analytics.investment_score import InvestmentScoreEngine
        inv_engine = InvestmentScoreEngine(db_path=db_path)
        inv_engine.run()

        elapsed = round(time.time() - start_time, 2)
        logger.info("==================================================")
        logger.info(f"PIPELINE COMPLETED SUCCESSFULLY IN {elapsed} SECONDS")
        logger.info("==================================================")

        # Print Execution Summary
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        print("\n=== PIPELINE EXECUTION SUMMARY ===")
        print(f"Database File: {db_path}")
        print(f"Companies Processed: {c.execute('SELECT COUNT(*) FROM companies').fetchone()[0]}")
        print(f"Financial Ratios Computed: {c.execute('SELECT COUNT(*) FROM financial_ratios').fetchone()[0]}")
        print(f"Peer Group Rankings: {c.execute('SELECT COUNT(*) FROM peer_percentiles').fetchone()[0]}")
        print(f"Financial Health Ratings: {c.execute('SELECT COUNT(*) FROM financial_health').fetchone()[0]}")
        print(f"Investment Ratings: {c.execute('SELECT COUNT(*) FROM investment_scores').fetchone()[0]}")
        print("Generated Output Reports:")
        print(" - output/load_audit.csv")
        print(" - output/validation_failures.csv")
        print(" - output/ratio_edge_cases.log")
        print(" - output/capital_allocation.csv")
        print(" - output/screener_output.xlsx")
        print(" - output/peer_comparison.xlsx")
        print(" - output/investment_intelligence.xlsx")
        print(" - reports/radar_charts/ (56 PNG charts)")
        print("===================================\n")
        conn.close()

        return True

    except Exception as e:
        logger.error(f"Pipeline execution failed: {str(e)}", exc_info=True)
        return False


if __name__ == "__main__":
    success = run_full_pipeline()
    if not success:
        sys.exit(1)
