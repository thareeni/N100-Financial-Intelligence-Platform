"""
Company Tearsheet Generator for Nifty 100 Financial Intelligence Platform.
Generates a 1-page professional PDF Tearsheet for every company in reports/tearsheets/<TICKER>_tearsheet.pdf.
"""

import os
import sqlite3
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

DB_PATH = os.getenv("DB_PATH", "nifty100.db")
OUTPUT_DIR = os.path.join("reports", "tearsheets")


def generate_company_tearsheets(db_path: str = DB_PATH, output_dir: str = OUTPUT_DIR) -> int:
    os.makedirs(output_dir, exist_ok=True)
    conn = sqlite3.connect(db_path)

    cos_df = pd.read_sql_query("SELECT id, company_name FROM companies ORDER BY id", conn)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#1F4E78'),
        spaceAfter=6
    )

    sub_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Heading3'],
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#555555'),
        spaceAfter=12
    )

    h2_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#1F4E78'),
        spaceBefore=10,
        spaceAfter=6
    )

    body_style = styles['Normal']

    count = 0
    for _, co in cos_df.iterrows():
        cid = co["id"]
        cname = co["company_name"]

        # Fetch latest metrics
        sql = f"""
            SELECT fr.return_on_equity_pct, fr.debt_to_equity, fr.free_cash_flow_cr, fr.net_profit_margin_pct,
                   ins.investment_score, ins.investment_rating,
                   fh.altman_z_score, fh.financial_health_rating,
                   vm.valuation_score
            FROM financial_ratios fr
            LEFT JOIN investment_scores ins ON fr.company_id = ins.company_id AND fr.year = ins.year
            LEFT JOIN financial_health fh ON fr.company_id = fh.company_id AND fr.year = fh.year
            LEFT JOIN valuation_metrics vm ON fr.company_id = vm.company_id AND fr.year = vm.year
            WHERE fr.company_id = '{cid}' AND fr.year != 'PARSE_ERROR'
            ORDER BY fr.year DESC
            LIMIT 1
        """
        metrics_df = pd.read_sql_query(sql, conn)

        pdf_path = os.path.join(output_dir, f"{cid}_tearsheet.pdf")
        doc = SimpleDocTemplate(pdf_path, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
        story = []

        # Header
        story.append(Paragraph(f"{cname} ({cid})", title_style))
        story.append(Paragraph("Nifty 100 Financial Intelligence Company Tearsheet", sub_style))

        if not metrics_df.empty:
            m = metrics_df.iloc[0]
            score_str = f"{m['investment_score']:.1f}/100" if pd.notna(m['investment_score']) else "N/A"
            rating_str = str(m['investment_rating']) if pd.notna(m['investment_rating']) else "N/A"
            z_str = f"{m['altman_z_score']:.2f}" if pd.notna(m['altman_z_score']) else "N/A"
            health_str = str(m['financial_health_rating']) if pd.notna(m['financial_health_rating']) else "N/A"
            val_str = f"{m['valuation_score']:.1f}/100" if pd.notna(m['valuation_score']) else "N/A"
            roe_str = f"{m['return_on_equity_pct']:.1f}%" if pd.notna(m['return_on_equity_pct']) else "N/A"
            de_str = f"{m['debt_to_equity']:.2f}" if pd.notna(m['debt_to_equity']) else "N/A"
            fcf_str = f"₹{m['free_cash_flow_cr']:.1f} Cr" if pd.notna(m['free_cash_flow_cr']) else "N/A"

            # Table 1: Executive Key Indicators
            story.append(Paragraph("Executive Rating Summary", h2_style))
            data_rating = [
                ["Investment Rating", rating_str, "Composite Investment Score", score_str],
                ["Financial Health", health_str, "Altman Z-Score", z_str],
                ["Valuation Rating", val_str, "Return on Equity (ROE)", roe_str]
            ]
            t1 = Table(data_rating, colWidths=[140, 120, 160, 120])
            t1.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8F9FA')),
                ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#333333')),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CCCCCC')),
                ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
                ('PADDING', (0,0), (-1,-1), 6),
            ]))
            story.append(t1)

            story.append(Spacer(1, 10))
            story.append(Paragraph("Core Financial KPI Breakdown", h2_style))
            data_kpi = [
                ["KPI Metric", "Metric Value", "KPI Metric", "Metric Value"],
                ["Return on Equity (ROE)", roe_str, "Debt to Equity", de_str],
                ["Net Profit Margin", f"{m['net_profit_margin_pct']:.1f}%" if pd.notna(m['net_profit_margin_pct']) else "N/A", "Free Cash Flow", fcf_str]
            ]
            t2 = Table(data_kpi, colWidths=[140, 120, 160, 120])
            t2.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (1,0), colors.HexColor('#1F4E78')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CCCCCC')),
                ('PADDING', (0,0), (-1,-1), 5),
            ]))
            story.append(t2)
        else:
            story.append(Paragraph("Financial statement history available in platform database.", body_style))

        story.append(Spacer(1, 20))
        story.append(Paragraph("Report Generated by Bluestock Fintech N100 Financial Intelligence Engine.", ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.gray)))

        doc.build(story)
        count += 1

    conn.close()
    print(f"[INFO] Generated {count} company tearsheets in {output_dir}.")
    return count


if __name__ == "__main__":
    generate_company_tearsheets()
