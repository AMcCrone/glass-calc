# dashboard/interlayer_3d_plot.py
import streamlit as st
import plotly.graph_objs as go
import pandas as pd
from config import time_map

def render_3d_plot():
    st.markdown("<a name='interlayer-3d-plot'></a>", unsafe_allow_html=True)
    st.title("Interlayer Modulus, E(t), 3D Plot")
    col1, col2, col3 = st.columns(3)
    with col1:
        selected_interlayer = st.selectbox("Select Interlayer:", ["SentryGlas", "Trosifol Clear"])
    # Load Excel data and prepare the dataframe
    # (Assume df is loaded from the data folder)
    try:
        df = pd.read_excel("data/Interlayer_E(t)_Database.xlsx", sheet_name=selected_interlayer)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.stop()
    # Process data and create the 3D scatter plot
    df_melted = df.melt(id_vars="Temperature (°C)", var_name="Time", value_name="E(MPa)")
    df_melted["Time_s"] = df_melted["Time"].map(time_map)
    trace_all = go.Scatter3d(
        x=df_melted["Time_s"],
        y=df_melted["Temperature (°C)"],
        z=df_melted["E(MPa)"],
        mode='markers',
        marker=dict(size=5, colorscale='Viridis'),
        name="All Data"
    )
    fig3d = go.Figure(data=[trace_all])
    fig3d.update_layout(scene=dict(xaxis_title="Load Duration", yaxis_title="Temperature (°C)", zaxis_title="E(t) [MPa]"))
    st.plotly_chart(fig3d, use_container_width=True)
