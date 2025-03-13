"""
dashboard/interlayer_3d_plot.py

This module renders the "Interlayer Modulus, E(t), 3D Plot" section of the
Glass Design Tool. It loads interlayer data from an Excel file, processes
the data into a long format, and displays a 3D scatter plot with options to
highlight a specific data point based on user-selected temperature and load duration.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from config import time_map, tickvals, ticktext interlayer_options  # Assumes these are defined in config.py

def render_3d_plot():
    st.markdown("<a name='interlayer-3d-plot'></a>", unsafe_allow_html=True)
    st.title("Interlayer Modulus, E(t), 3D Plot")
    
    # Define the Excel file path. In this repo, it's stored in the 'data' folder.
    excel_file = "data/Interlayer_E(t)_Database.xlsx"
    
    # Create three columns for dropdowns: interlayer, temperature, load duration.
    col1, col2, col3 = st.columns(3)
    
    with col1:
        selected_interlayer = st.selectbox("Select Interlayer:", interlayer_options)
    
    # Attempt to load the selected interlayer sheet.
    try:
        df = pd.read_excel(excel_file, sheet_name=selected_interlayer)
    except Exception as e:
        st.error(f"Error loading Excel file for {selected_interlayer}: {e}")
        st.stop()
    
    # Extract unique temperature values from the data.
    if "Temperature (°C)" not in df.columns:
        st.error("Temperature data not found in the Excel file.")
        st.stop()
    temp_list = sorted(df["Temperature (°C)"].unique())
    
    # Convert the data from wide to long format.
    df_melted = df.melt(
        id_vars="Temperature (°C)",
        var_name="Time",
        value_name="E(MPa)"
    )
    
    # Replace non-numeric values with a fallback value (e.g., 0.05 MPa).
    df_melted["E(MPa)"] = pd.to_numeric(df_melted["E(MPa)"], errors="coerce").fillna(0.05)
    
    # Map load duration strings to seconds using the time_map from config.
    df_melted["Time_s"] = df_melted["Time"].map(time_map)
    
    with col2:
        selected_temp = st.selectbox("Select Temperature (°C):", temp_list)
    
    with col3:
        selected_time = st.selectbox("Select Load Duration:", list(time_map.keys()))
    
    # Find the data point matching the selected temperature and load duration.
    selected_point = df_melted[
        (df_melted["Temperature (°C)"] == selected_temp) &
        (df_melted["Time"] == selected_time)
    ]
    if not selected_point.empty:
        highlight_x = selected_point["Time_s"].values[0]
        highlight_y = selected_temp
        highlight_z = selected_point["E(MPa)"].values[0]
    else:
        highlight_x, highlight_y, highlight_z = None, None, None
    
    # Display the selected Young's modulus.
    if highlight_z is not None:
        st.markdown(f"**Selected Young's Modulus:** {highlight_z} MPa")
    else:
        st.markdown("**Selected data point not found.**")
    
    # Create the 3D scatter plot.
    trace_all = go.Scatter3d(
        x=df_melted["Time_s"],
        y=df_melted["Temperature (°C)"],
        z=df_melted["E(MPa)"],
        mode='markers',
        marker=dict(
            size=5,
            color=df_melted["E(MPa)"],
            colorscale='Viridis',
            opacity=0.8
        ),
        name="All Data",
        hovertemplate="Load Duration: %{x}<br>Temp.: %{y} °C<br>E(t): %{z} MPa"
    )
    
    # Create a trace for the highlighted point.
    trace_highlight = go.Scatter3d(
        x=[highlight_x] if highlight_x is not None else [],
        y=[highlight_y] if highlight_y is not None else [],
        z=[highlight_z] if highlight_z is not None else [],
        mode='markers',
        marker=dict(
            size=12,
            color='red',
            symbol='circle'
        ),
        name="Selected Point"
    )
    
    fig3d = go.Figure(data=[trace_all, trace_highlight])
    fig3d.update_layout(
        scene=dict(
            xaxis=dict(
                title='Load Duration',
                type='log',
                tickvals=tickvals,
                ticktext=ticktext
            ),
            yaxis=dict(title='Temperature (°C)'),
            zaxis=dict(title='E(t) [MPa]')
        ),
        margin=dict(l=0, r=0, b=0, t=0)
    )
    
    st.plotly_chart(fig3d, use_container_width=True)
