"""
Analyst User Guide PDF Generator for Nifty 100 Financial Intelligence Platform.
Generates docs/analyst_guide.pdf.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

OUTPUT_DIR = "docs"
REPORT_PATH = os.path.join(OUTPUT_DIR, "analyst_guide.pdf")


def generate_analyst_guide(output_file: str = REPORT_PATH):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=20, textColor=colors.HexColor('#1F4E78'), spaceAfter=8)
    sub_style = ParagraphStyle('DocSubTitle', parent=styles['Heading3'], fontSize=12, textColor=colors.HexColor('#555555'), spaceAfter=14)
    h2_style = ParagraphStyle('SectionHeading', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#1F4E78'), spaceBefore=12, spaceAfter=6)
    body_style = styles['Normal']

    doc = SimpleDocTemplate(output_file, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    story = []

    story.append(Paragraph("Nifty 100 Financial Intelligence Platform", title_style))
    story.append(Paragraph("Analyst & User Operations Guide", sub_style))

    story.append(Paragraph("1. Platform Architecture Overview", h2_style))
    story.append(Paragraph("The platform provides automated ETL ingestion, 50+ KPI computation, stock screening, peer benchmarking, financial health scoring (Altman Z & Beneish M), 3-stage DuPont ROE breakdown, valuation intelligence, and investment scoring for the 92 Nifty 100 companies.", body_style))

    story.append(Spacer(1, 10))
    story.append(Paragraph("2. Execution Guide", h2_style))

    guide_data = [
        ["Operation", "CLI Command / Entrypoint", "Description"],
        ["Run Full Pipeline", "python src/main.py (or make run)", "Runs ETL, Ratios, Screener, Peer, Health, DuPont & Scoring."],
        ["Launch Web Dashboard", "streamlit run dashboard/app.py", "Launches 8-Screen Interactive Production Web Dashboard."],
        ["Launch REST API", "uvicorn src.api.main:app --reload", "Launches 21-endpoint FastAPI REST web server."],
        ["Run Test Suite", "pytest tests/", "Executes 100+ pytest unit & integration tests."]
    ]

    t = Table(guide_data, colWidths=[120, 190, 230])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1F4E78')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CCCCCC')),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t)

    story.append(Spacer(1, 15))
    story.append(Paragraph("3. 8-Screen Dashboard Navigation", h2_style))
    story.append(Paragraph("1. Overview | 2. Screener | 3. Investment Intelligence | 4. Peer Comparison | 5. Company Deep Dive | 6. Valuation | 7. Financial Health | 8. Portfolio Summary", body_style))

    story.append(Spacer(1, 20))
    story.append(Paragraph("Bluestock Fintech MJ28 Nifty 100 Analytics Documentation.", ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.gray)))

    doc.build(story)
    print(f"[INFO] Generated Analyst Guide: {output_file}")


if __name__ == "__main__":
    generate_analyst_guide()
