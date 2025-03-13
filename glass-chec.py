# glass-chec.py
import streamlit as st

# Import auth first so it handles authentication on load.
import auth

from config import *
from calculator.design_calculator import render_calculator
from dashboard.summary_dashboard import render_dashboard
from dashboard.interlayer_3d_plot import render_3d_plot
from dashboard.interlayer_comparison import render_interlayer_comparison
from docs.documentation import render_documentation
from calculator.pdf_generator import pdf_download_button
from utils.helpers import add_sidebar_navigation

# --- Main App Layout ---
st.title("Glass Design Tool")

# Render sections (you can organize layout with tabs or sections)
render_calculator()
render_dashboard()
render_3d_plot()
render_interlayer_comparison()
render_documentation()
pdf_download_button()  # Button for PDF generation

# Update the sidebar navigation to include the dashboard
st.sidebar.markdown("""
## Navigation
- [Dashboard](#dashboard)
- [Glass Design Strength Calculator](#glass-design-strength-calculator)
- [Interlayer Relaxation Modulus 3D Plot](#interlayer-relaxation-modulus-3d-plot)
- [Interlayer Comparison](#interlayer-comparison)
- [Design Recommendations](#design-recommendations)
- [Documentation](#documentation)
- [Appendix](#appendix)
""", unsafe_allow_html=True)

# Add an "About" section to the sidebar
with st.sidebar.expander("About this Tool"):
    st.markdown("""
    **Glass Design Tool v1.0.0**
    
    This application provides TT engineers with tools to:
    - Calculate glass design strength based on EN 16612 and IStructE Structural Use of Glass in Buildings 
    - Analyse interlayer behavior at different temperatures and load durations
    - Compare performance of different interlayers
    """)

# Add a footer to the app
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: gray; font-size: 0.8em;">
        Glass Design Tool v1.0.0 | © 2025 | Based on IStructE and EN 16612 standards<br>
        <small>For educational and professional use. Always consult applicable building codes and regulations.</small>
    </div>
    """,
    unsafe_allow_html=True
)
