# utils/helpers.py
import streamlit as st

def style_load_row(row):
    selected_loads = st.session_state.get("selected_loads", [])
    return ['background-color: #EB8C71' if row["Load Type"] in selected_loads else '' for _ in row]

def add_sidebar_navigation():
    st.sidebar.markdown("""
    ## Navigation
    - [Dashboard](#dashboard)
    - [Glass Design Strength Calculator](#glass-design-strength-calculator)
    - [Interlayer 3D Plot](#interlayer-3d-plot)
    - [Interlayer Comparison](#interlayer-comparison)
    - [Documentation](#documentation)
    """, unsafe_allow_html=True)
