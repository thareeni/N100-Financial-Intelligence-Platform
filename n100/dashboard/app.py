"""
Streamlit Production Dashboard for Nifty 100 Financial Intelligence Platform.
Interactive multi-page dashboard displaying:
- Page 1: Nifty 100 Overview
- Page 2: Stock Screener Dashboard
- Page 3: Investment Intelligence
- Page 4: Peer Comparison & Radar Analysis
- Page 5: Company Deep-Dive View
"""

import os
import sqlite3
import pandas as pd
import streamlit as st
import PIL.Image
import yaml

# Page configuration
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


# Custom CSS styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1F4E78;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #555555;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8F9FA;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 5px solid #1F4E78;
    }
    </style>
""", unsafe_allow_html=True)


def render_page_overview():
    st.markdown('<div class="main-header">Nifty 100 Overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Executive Summary & Sector Breakdown across 92 Companies</div>', unsafe_allow_html=True)

    cos_df = load_db_data("SELECT * FROM companies")
    sec_df = load_db_data("SELECT * FROM sectors")
    mc_df = load_db_data("""
        SELECT mc.*
        FROM market_cap mc
        JOIN (SELECT company_id, MAX(year) as max_yr FROM market_cap GROUP BY company_id) latest
        ON mc.company_id = latest.company_id AND mc.year = latest.max_yr
    """)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Companies", len(cos_df))
    with col2:
        num_sectors = sec_df["broad_sector"].nunique() if not sec_df.empty else 0
        st.metric("Broad Sectors", num_sectors)
    with col3:
        tot_mcap = mc_df["market_cap_crore"].sum() / 100000.0 if not mc_df.empty else 0.0
        st.metric("Total Market Cap", f"₹{tot_mcap:.2f} Lakh Cr")
    with col4:
        avg_pe = mc_df["pe_ratio"].median() if not mc_df.empty else 0.0
        st.metric("Median P/E Ratio", f"{avg_pe:.1f}x")

    st.markdown("---")
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader("Broad Sector Distribution")
        if not sec_df.empty:
            sec_counts = sec_df["broad_sector"].value_counts().reset_index()
            sec_counts.columns = ["Sector", "Count"]
            st.bar_chart(sec_counts.set_index("Sector"))

    with col_right:
        st.subheader("Market Cap Breakdown (Top 10)")
        if not mc_df.empty:
            top_mc = mc_df.sort_values(by="market_cap_crore", ascending=False).head(10)
            st.dataframe(
                top_mc[["company_id", "market_cap_crore", "pe_ratio", "pb_ratio", "dividend_yield_pct"]],
                use_container_width=True
            )


def render_page_screener():
    st.markdown('<div class="main-header">Stock Screener Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Multi-Criteria Filtering & 6 Preset Screeners</div>', unsafe_allow_html=True)

    screener_file = os.path.join(OUTPUT_DIR, "screener_output.xlsx")
    sheets = load_excel_sheets(screener_file)

    if not sheets:
        st.warning("screener_output.xlsx not found. Please run pipeline first.")
        return

    preset_name = st.selectbox("Select Preset Screener", list(sheets.keys()))
    df = sheets[preset_name]

    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        sectors = ["All"] + list(df["broad_sector"].dropna().unique()) if "broad_sector" in df.columns else ["All"]
        sel_sector = st.selectbox("Filter by Sector", sectors)
    with col_f2:
        min_score = st.slider("Minimum Composite Quality Score", 0.0, 100.0, 0.0)
    with col_f3:
        min_roe = st.slider("Minimum ROE %", -10.0, 50.0, -10.0)

    filtered_df = df.copy()
    if sel_sector != "All":
        filtered_df = filtered_df[filtered_df["broad_sector"] == sel_sector]
    if "composite_quality_score" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["composite_quality_score"] >= min_score]
    if "return_on_equity_pct" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["return_on_equity_pct"] >= min_roe]

    st.subheader(f"{preset_name} ({len(filtered_df)} companies)")
    st.dataframe(filtered_df, use_container_width=True)


def render_page_investment_intelligence():
    st.markdown('<div class="main-header">Investment Intelligence Layer</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Synthesis of Quality, Growth, Value, Financial Health & Momentum</div>', unsafe_allow_html=True)

    inv_df = load_db_data("""
        SELECT ins.company_id as Ticker, c.company_name as Company, s.broad_sector as Sector,
               ins.investment_score, ins.investment_rating,
               ins.quality_score, ins.growth_score, ins.value_score, ins.health_score, ins.momentum_score
        FROM investment_scores ins
        JOIN companies c ON ins.company_id = c.id
        LEFT JOIN sectors s ON ins.company_id = s.company_id
        ORDER BY ins.investment_score DESC
    """)

    if inv_df.empty:
        st.warning("Investment scores not found. Run pipeline first.")
        return

    ratings = inv_df["investment_rating"].value_counts()
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Strong Buy (Score ≥ 75)", ratings.get("Strong Buy", 0))
    with c2:
        st.metric("Buy (Score 60-74)", ratings.get("Buy", 0))
    with c3:
        st.metric("Hold (Score 45-59)", ratings.get("Hold", 0))
    with c4:
        st.metric("Avoid (Score < 45)", ratings.get("Avoid", 0))

    st.markdown("---")
    st.subheader("Top Investment Opportunities (Ranked by Score)")
    st.dataframe(inv_df, use_container_width=True)


def render_page_peer_comparison():
    st.markdown('<div class="main-header">Peer Comparison & Radar Charts</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Intra-Group Percentile Rankings & 8-Axis Radar Overlay</div>', unsafe_allow_html=True)

    pg_df = load_db_data("SELECT DISTINCT peer_group_name FROM peer_groups")
    if pg_df.empty:
        st.warning("Peer groups not found.")
        return

    group_list = pg_df["peer_group_name"].tolist()
    sel_group = st.selectbox("Select Peer Group", group_list)

    sql = f"""
        SELECT pg.company_id as Ticker, c.company_name as Company, pg.is_benchmark as Benchmark,
               fr.return_on_equity_pct as ROE_pct, fr.debt_to_equity as DE_ratio, fr.free_cash_flow_cr as FCF_cr,
               fr.pat_cagr_5yr as PAT_CAGR_5Y, fr.revenue_cagr_5yr as Rev_CAGR_5Y
        FROM peer_groups pg
        JOIN companies c ON pg.company_id = c.id
        LEFT JOIN (
            SELECT fr_inner.*
            FROM financial_ratios fr_inner
            JOIN (
                SELECT company_id, MAX(year) as max_yr FROM financial_ratios WHERE year != 'PARSE_ERROR' GROUP BY company_id
            ) latest ON fr_inner.company_id = latest.company_id AND fr_inner.year = latest.max_yr
        ) fr ON pg.company_id = fr.company_id
        WHERE pg.peer_group_name = '{sel_group}'
    """
    group_cos = load_db_data(sql)

    st.subheader(f"Peer Group Metrics: {sel_group}")
    st.dataframe(group_cos, use_container_width=True)

    st.markdown("---")
    st.subheader("Radar Chart Inspection")
    sel_ticker = st.selectbox("Select Company Ticker for Radar Overlay", group_cos["Ticker"].tolist() if not group_cos.empty else [])

    if sel_ticker:
        chart_file = os.path.join(REPORTS_DIR, f"{sel_ticker}_radar.png")
        if os.path.exists(chart_file):
            image = PIL.Image.open(chart_file)
            st.image(image, caption=f"{sel_ticker} 8-Axis Peer Radar Chart", width=550)
        else:
            st.warning(f"Radar chart PNG for {sel_ticker} not found.")


def render_page_company_detail():
    st.markdown('<div class="main-header">Company Deep-Dive View</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Complete 360-Degree Financial & Investment Profile</div>', unsafe_allow_html=True)

    cos_df = load_db_data("SELECT id, company_name FROM companies ORDER BY id")
    if cos_df.empty:
        st.warning("No companies found.")
        return

    co_map = dict(zip(cos_df["id"], cos_df["company_name"]))
    sel_cid = st.selectbox("Select Company Ticker", list(co_map.keys()), format_func=lambda x: f"{x} - {co_map[x]}")

    if sel_cid:
        sql_summary = f"""
            SELECT ins.investment_score, ins.investment_rating,
                   fh.altman_z_score, fh.financial_health_rating, fh.beneish_m_score, fh.manipulation_risk_flag,
                   vm.valuation_score, vm.earnings_yield, vm.fcf_yield, vm.peg_ratio
            FROM investment_scores ins
            LEFT JOIN financial_health fh ON ins.company_id = fh.company_id AND ins.year = fh.year
            LEFT JOIN valuation_metrics vm ON ins.company_id = vm.company_id AND ins.year = vm.year
            WHERE ins.company_id = '{sel_cid}'
        """
        sum_df = load_db_data(sql_summary)

        if not sum_df.empty:
            row = sum_df.iloc[0]
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.metric("Investment Score", f"{row['investment_score']:.1f}/100", row["investment_rating"])
            with m2:
                st.metric("Altman Z-Score", f"{row['altman_z_score']:.2f}", row["financial_health_rating"])
            with m3:
                st.metric("Beneish M-Score", f"{row['beneish_m_score']:.2f}", row["manipulation_risk_flag"])
            with m4:
                st.metric("Valuation Score", f"{row['valuation_score']:.1f}/100")

        st.markdown("---")
        t1, t2, t3, t4 = st.tabs(["Financial Ratios", "DuPont ROE Breakdown", "Financial Health", "Valuation Multiples"])

        with t1:
            fr_df = load_db_data(f"SELECT year, return_on_equity_pct, net_profit_margin_pct, debt_to_equity, free_cash_flow_cr, revenue_cagr_5yr FROM financial_ratios WHERE company_id = '{sel_cid}' ORDER BY year DESC")
            st.dataframe(fr_df, use_container_width=True)

        with t2:
            dp_df = load_db_data(f"SELECT year, net_profit_margin, asset_turnover, equity_multiplier, dupont_roe FROM dupont_analysis WHERE company_id = '{sel_cid}' ORDER BY year DESC")
            st.dataframe(dp_df, use_container_width=True)

        with t3:
            fh_df = load_db_data(f"SELECT year, altman_z_score, financial_health_rating, beneish_m_score, manipulation_risk_flag FROM financial_health WHERE company_id = '{sel_cid}' ORDER BY year DESC")
            st.dataframe(fh_df, use_container_width=True)

        with t4:
            vm_df = load_db_data(f"SELECT year, valuation_score, earnings_yield, fcf_yield, peg_ratio, ev_sales, ev_ebitda FROM valuation_metrics WHERE company_id = '{sel_cid}' ORDER BY year DESC")
            st.dataframe(vm_df, use_container_width=True)


def main():
    st.sidebar.title("Nifty 100 Platform")
    st.sidebar.markdown("### Navigation")
    page = st.sidebar.radio("Go to Page", [
        "1. Nifty 100 Overview",
        "2. Stock Screener",
        "3. Investment Intelligence",
        "4. Peer Comparison",
        "5. Company Detail View"
    ])

    if page == "1. Nifty 100 Overview":
        render_page_overview()
    elif page == "2. Stock Screener":
        render_page_screener()
    elif page == "3. Investment Intelligence":
        render_page_investment_intelligence()
    elif page == "4. Peer Comparison":
        render_page_peer_comparison()
    elif page == "5. Company Detail View":
        render_page_company_detail()

    st.sidebar.markdown("---")
    st.sidebar.info("Antigravity AI - Bluestock Fintech MJ28")


if __name__ == "__main__":
    main()
