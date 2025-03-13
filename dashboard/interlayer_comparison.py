# dashboard/interlayer_comparison.py
import streamlit as st
import pandas as pd
import plotly.graph_objs as go

def render_interlayer_comparison():
    st.markdown("<a name='interlayer-comparison'></a>", unsafe_allow_html=True)
    st.title("Interlayer Comparison Chart")
    compare_interlayers = st.multiselect("Select interlayers to compare:", ["SentryGlas", "Trosifol Clear"], default=["SentryGlas"])
    compare_temp = st.selectbox("Select Temperature (°C):", [0, 10, 20, 30])
    compare_times = st.multiselect("Select Load Durations for Comparison:", ["3 sec", "10 min", "1 day"], default=["3 sec", "1 day"])
    # Load and process data for each selected interlayer
    comparison_data = []
    for interlayer in compare_interlayers:
        try:
            df = pd.read_excel("data/Interlayer_E(t)_Database.xlsx", sheet_name=interlayer)
            if compare_temp in df["Temperature (°C)"].values:
                temp_data = df[df["Temperature (°C)"] == compare_temp].iloc[0]
                for time_label in compare_times:
                    value = temp_data.get(time_label, 0.05)
                    comparison_data.append({
                        "Interlayer": interlayer,
                        "Load Duration": time_label,
                        "E(MPa)": float(value) if pd.notna(value) else 0.05
                    })
        except Exception as e:
            st.error(f"Error loading data for {interlayer}: {e}")
    if comparison_data:
        df_comparison = pd.DataFrame(comparison_data)
        fig = go.Figure()
        for time_label in compare_times:
            df_subset = df_comparison[df_comparison["Load Duration"] == time_label]
            fig.add_trace(go.Bar(
                x=df_subset["Interlayer"],
                y=df_subset["E(MPa)"],
                name=time_label
            ))
        fig.update_layout(barmode='group', title=f"Comparison at {compare_temp}°C")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No comparison data available.")
