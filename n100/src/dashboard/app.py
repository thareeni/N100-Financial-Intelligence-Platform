"""
Streamlit Production Dashboard for Nifty 100 Financial Intelligence Platform.
8-Screen Interactive Web Dashboard:
1. Overview
2. Screener
3. Investment Intelligence
4. Peer Comparison
5. Company Deep Dive
6. Valuation
7. Financial Health
8. Portfolio Summary
"""

import os
import sqlite3
import pandas as pd
import streamlit as st
import PIL.Image

st.set_page_config(
    page_title="Nifty 100 Financial Intelligence Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_PATH = os.getenv("DB_PATH", "nifty100.db")
OUTPUT_DIR = "output"
REPORTS_DIR = os.path.join("reports", "radar_charts")


@st.cache_data
def load_db_data(query: str, db_path: str = DB_PATH) -> pd.DataFrame:
    if not os.path.exists(db_path):
        return pd.DataFrame()
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


@st.cache_data
def load_excel_sheets(file_path: str) -> dict:
    if not os.path.exists(file_path):
        return {}
    xls = pd.ExcelFile(file_path)
    return {sheet: pd.read_excel(xls, sheet) for sheet in xls.sheet_names}


st.markdown("""
    <style>
    .main-header { font-size: 2.2rem; font-weight: 700; color: #1F4E78; margin-bottom: 0.5rem; }
    .sub-header { font-size: 1.1rem; color: #555555; margin-bottom: 1.5rem; }
    </style>
""", unsafe_allow_html=True)


# Screen 1: Overview
def render_screen_overview():
    st.markdown('<div class="main-header">1. Nifty 100 Overview</div>', unsafe_allow_html=True)
    cos_df = load_db_data("SELECT * FROM companies")
    sec_df = load_db_data("SELECT * FROM sectors")
    mc_df = load_db_data("SELECT * FROM market_cap WHERE year = (SELECT MAX(year) FROM market_cap)")

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Total Companies", len(cos_df))
    with c2: st.metric("Broad Sectors", sec_df["broad_sector"].nunique() if not sec_df.empty else 0)
    with c3: st.metric("Total Market Cap", f"₹{(mc_df['market_cap_crore'].sum()/100000.0):.2f} L Cr" if not mc_df.empty else "0")
    with c4: st.metric("Median P/E", f"{mc_df['pe_ratio'].median():.1f}x" if not mc_df.empty else "0")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Broad Sector Breakdown")
        if not sec_df.empty:
            st.bar_chart(sec_df["broad_sector"].value_counts())
    with col2:
        st.subheader("Top 10 Market Cap Leaders")
        if not mc_df.empty:
            st.dataframe(mc_df.sort_values(by="market_cap_crore", ascending=False).head(10)[["company_id", "market_cap_crore", "pe_ratio", "pb_ratio"]], use_container_width=True)


# Screen 2: Screener
def render_screen_screener():
    st.markdown('<div class="main-header">2. Stock Screener</div>', unsafe_allow_html=True)
    sheets = load_excel_sheets(os.path.join(OUTPUT_DIR, "screener_output.xlsx"))
    if not sheets:
        st.warning("screener_output.xlsx not found.")
        return
    preset = st.selectbox("Select Preset Screener", list(sheets.keys()))
    df = sheets[preset]
    st.subheader(f"{preset} ({len(df)} companies)")
    st.dataframe(df, use_container_width=True)


# Screen 3: Investment Intelligence
def render_screen_investment():
    st.markdown('<div class="main-header">3. Investment Intelligence</div>', unsafe_allow_html=True)
    df = load_db_data("""
        SELECT ins.company_id as Ticker, c.company_name as Company, s.broad_sector as Sector,
               ins.investment_score, ins.investment_rating, ins.quality_score, ins.growth_score, ins.value_score, ins.health_score
        FROM investment_scores ins
        JOIN companies c ON ins.company_id = c.id
        LEFT JOIN sectors s ON ins.company_id = s.company_id
        ORDER BY ins.investment_score DESC
    """)
    if df.empty:
        st.warning("No investment score data.")
        return
    ratings = df["investment_rating"].value_counts()
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Strong Buy (≥75)", ratings.get("Strong Buy", 0))
    with c2: st.metric("Buy (60-74)", ratings.get("Buy", 0))
    with c3: st.metric("Hold (45-59)", ratings.get("Hold", 0))
    with c4: st.metric("Avoid (<45)", ratings.get("Avoid", 0))
    st.dataframe(df, use_container_width=True)


# Screen 4: Peer Comparison
def render_screen_peer():
    st.markdown('<div class="main-header">4. Peer Comparison & Radar Analysis</div>', unsafe_allow_html=True)
    pg_df = load_db_data("SELECT DISTINCT peer_group_name FROM peer_groups")
    group = st.selectbox("Select Peer Group", pg_df["peer_group_name"].tolist() if not pg_df.empty else [])
    if group:
        df = load_db_data(f"SELECT * FROM peer_percentiles WHERE peer_group_name = '{group}'")
        st.dataframe(df, use_container_width=True)
        tickers = load_db_data(f"SELECT company_id FROM peer_groups WHERE peer_group_name = '{group}'")["company_id"].tolist()
        t = st.selectbox("Select Ticker for Radar Chart", tickers if tickers else [])
        if t:
            imgPath = os.path.join(REPORTS_DIR, f"{t}_radar.png")
            if os.path.exists(imgPath):
                st.image(PIL.Image.open(imgPath), width=500)


# Screen 5: Company Deep Dive
def render_screen_company_detail():
    st.markdown('<div class="main-header">5. Company Deep-Dive View</div>', unsafe_allow_html=True)
    cos = load_db_data("SELECT id, company_name FROM companies ORDER BY id")
    cid = st.selectbox("Select Ticker", cos["id"].tolist() if not cos.empty else [])
    if cid:
        df_r = load_db_data(f"SELECT * FROM financial_ratios WHERE company_id = '{cid}' ORDER BY year DESC")
        st.subheader(f"Financial Ratios: {cid}")
        st.dataframe(df_r, use_container_width=True)


# Screen 6: Valuation
def render_screen_valuation():
    st.markdown('<div class="main-header">6. Valuation Intelligence</div>', unsafe_allow_html=True)
    df = load_db_data("""
        SELECT vm.company_id as Ticker, c.company_name as Company,
               vm.valuation_score, vm.earnings_yield, vm.fcf_yield, vm.peg_ratio, vm.ev_sales, vm.ev_ebitda
        FROM valuation_metrics vm
        JOIN companies c ON vm.company_id = c.id
        ORDER BY vm.valuation_score DESC
    """)
    st.dataframe(df, use_container_width=True)


# Screen 7: Financial Health
def render_screen_health():
    st.markdown('<div class="main-header">7. Financial Health & Risk Flags</div>', unsafe_allow_html=True)
    df = load_db_data("""
        SELECT fh.company_id as Ticker, c.company_name as Company,
               fh.altman_z_score, fh.financial_health_rating, fh.beneish_m_score, fh.manipulation_risk_flag
        FROM financial_health fh
        JOIN companies c ON fh.company_id = c.id
        WHERE fh.year = (SELECT MAX(year) FROM financial_health WHERE company_id = fh.company_id)
        ORDER BY fh.altman_z_score ASC
    """)
    st.dataframe(df, use_container_width=True)


# Screen 8: Portfolio Summary
def render_screen_portfolio():
    st.markdown('<div class="main-header">8. Portfolio Summary & Asset Allocation</div>', unsafe_allow_html=True)
    df = load_db_data("""
        SELECT ins.company_id as Ticker, c.company_name as Company, s.broad_sector as Sector,
               ins.investment_score, ins.investment_rating, mc.market_cap_crore
        FROM investment_scores ins
        JOIN companies c ON ins.company_id = c.id
        LEFT JOIN sectors s ON ins.company_id = s.company_id
        LEFT JOIN market_cap mc ON ins.company_id = mc.company_id AND ins.year = mc.year
        WHERE ins.investment_rating IN ('Strong Buy', 'Buy')
        ORDER BY ins.investment_score DESC
    """)
    st.subheader(f"Recommended Portfolio Candidates ({len(df)} companies)")
    st.dataframe(df, use_container_width=True)


def main():
    st.sidebar.title("Nifty 100 Platform")
    page = st.sidebar.radio("Navigation", [
        "1 Overview",
        "2 Screener",
        "3 Investment Intelligence",
        "4 Peer Comparison",
        "5 Company Deep Dive",
        "6 Valuation",
        "7 Financial Health",
        "8 Portfolio Summary"
    ])

    if page == "1 Overview": render_screen_overview()
    elif page == "2 Screener": render_screen_screener()
    elif page == "3 Investment Intelligence": render_screen_investment()
    elif page == "4 Peer Comparison": render_screen_peer()
    elif page == "5 Company Deep Dive": render_screen_company_detail()
    elif page == "6 Valuation": render_screen_valuation()
    elif page == "7 Financial Health": render_screen_health()
    elif page == "8 Portfolio Summary": render_screen_portfolio()


if __name__ == "__main__":
    main()
