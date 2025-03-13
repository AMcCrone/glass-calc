# calculator/pdf_generator.py
import io
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from datetime import datetime
import streamlit as st

def generate_pdf(standard, fbk_choice, fbk_value, ksp_choice, ksp_value, selected_loads, kmod_options):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    styles = getSampleStyleSheet()
    elements = []
    
    elements.append(Paragraph("Glass Design Strength Calculation Report", styles['Title']))
    elements.append(Spacer(1, 10))
    # Add content based on parameters and calculated results
    # For example, create a table of input parameters
    input_data = [
        ["Parameter", "Option", "Value"],
        ["Characteristic Bending Strength", fbk_choice, f"{fbk_value} N/mm²"],
        ["Glass Surface Profile", ksp_choice, f"{ksp_value}"],
        # ...
    ]
    table = Table(input_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(table)
    elements.append(Spacer(1, 10))
    
    # Add more sections, formulas, etc.
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    elements.append(Paragraph(f"Report generated: {current_time}", styles['Normal']))
    doc.build(elements)
    buffer.seek(0)
    return buffer

def pdf_download_button():
    # Example integration in the Streamlit UI:
    if st.button("Generate PDF Report"):
        pdf_buffer = generate_pdf("IStructE Structural Use of Glass in Buildings",
                                  "Annealed (EN-572-1, 45 N/mm²)",
                                  45, "Float glass", 1.0, ["5 seconds – Single gust (Blast Load)"], {})
        st.download_button(label="Download PDF", data=pdf_buffer, file_name="Glass_Design_Report.pdf", mime="application/pdf")
