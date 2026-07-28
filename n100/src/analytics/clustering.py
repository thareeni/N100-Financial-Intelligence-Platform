"""
Unsupervised Financial Clustering Module for Nifty 100 Financial Intelligence Platform.
Performs KMeans clustering on key financial metrics and exports output/cluster_labels.csv.
"""

import os
import sqlite3
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

DB_PATH = os.getenv("DB_PATH", "nifty100.db")
OUTPUT_PATH = "output/cluster_labels.csv"


def run_financial_clustering(db_path: str = DB_PATH, output_file: str = OUTPUT_PATH) -> pd.DataFrame:
    conn = sqlite3.connect(db_path)
    sql = """
        SELECT fr.company_id, c.company_name, s.broad_sector,
               fr.return_on_equity_pct, fr.debt_to_equity, fr.net_profit_margin_pct,
               fr.free_cash_flow_cr, fr.revenue_cagr_5yr, fr.pat_cagr_5yr
        FROM financial_ratios fr
        JOIN companies c ON fr.company_id = c.id
        LEFT JOIN sectors s ON fr.company_id = s.company_id
        WHERE fr.year = (SELECT MAX(year) FROM financial_ratios WHERE company_id = fr.company_id AND year != 'PARSE_ERROR')
    """
    df = pd.read_sql_query(sql, conn)
    conn.close()

    if df.empty:
        print("[WARNING] No ratio data found for clustering.")
        return pd.DataFrame()

    features = ["return_on_equity_pct", "debt_to_equity", "net_profit_margin_pct", "free_cash_flow_cr", "revenue_cagr_5yr", "pat_cagr_5yr"]
    X = df[features].fillna(0.0)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    df["cluster_id"] = kmeans.fit_predict(X_scaled)

    cluster_names = {
        0: "Cluster 0: Balanced Compounders",
        1: "Cluster 1: High Growth & Quality",
        2: "Cluster 2: Capital Intensive / Debt",
        3: "Cluster 3: Moderate Yield / Stable"
    }
    df["cluster_label"] = df["cluster_id"].map(cluster_names)

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df.to_csv(output_file, index=False)
    print(f"[INFO] Exported KMeans financial clustering labels to {output_file} ({len(df)} companies).")
    return df


if __name__ == "__main__":
    run_financial_clustering()
