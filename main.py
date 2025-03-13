# main.py
import streamlit as st
from auth import check_password, ensure_authenticated
from config import PASSWORD  # other common variables can be imported here
from calculator.design_calculator import render_calculator
from dashboard.summary_dashboard import render_dashboard
from dashboard.interlayer_3d_plot import render_3d_plot
from dashboard.interlayer_comparison import render_interlayer_comparison
from docs.documentation import render_documentation
from calculator.pdf_generator import pdf_download_button
from utils.helpers import add_sidebar_navigation

# --- Authentication ---
ensure_authenticated()  # This function calls check_password and stops if not logged in

# --- Main App Layout ---
st.title("Glass Design Tool")
add_sidebar_navigation()  # Render sidebar links

# Render sections (you can organize layout with tabs or sections)
render_calculator()
render_dashboard()
render_3d_plot()
render_interlayer_comparison()
render_documentation()
pdf_download_button()  # Button for PDF generation

# ... add footer, about section, etc.
