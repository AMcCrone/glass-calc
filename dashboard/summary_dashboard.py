# dashboard/summary_dashboard.py
import streamlit as st
import plotly.graph_objs as go
import pandas as pd

def render_dashboard():
    st.markdown("<a name='dashboard'></a>", unsafe_allow_html=True)
    st.title("Glass Design Dashboard")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Current Design Parameters")
        st.markdown("""
            <div style="padding: 15px; border: 1px solid #ddd;">
                <p><strong>Glass Type:</strong> Annealed (EN-572-1, 45 N/mm²)</p>
                <p><strong>Standard:</strong> IStructE Structural Use of Glass in Buildings</p>
                <p><strong>Edge Type:</strong> Polished float edges</p>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.subheader("Quick Interlayer Selector")
        # Quick selector UI elements
        quick_temp = st.select_slider("Temperature (°C):", options=range(-20, 81, 5), value=20)
        quick_duration = st.selectbox("Load Duration:", ["3 sec (Impact)", "10 min (Wind)", "1 day (Snow)"])
        st.write(f"Selected: {quick_temp}°C and {quick_duration}")
        # Render gauge chart etc.
        dummy_value = 75
        gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=dummy_value,
            title={"text": "Min. Design Strength (MPa)"}
        ))
        st.plotly_chart(gauge, use_container_width=True)
