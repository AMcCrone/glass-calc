import streamlit as st
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from config import (
    fbk_options,
    ksp_options,
    ksp_prime_options,
    kv_options,
    ke_options,
    f_gk_value,
    kmod_options,
    time_list,
    time_map,
    interlayer_options
)

def render_dashboard():
    """Render the Glass Design Dashboard summary view."""
    st.markdown("<a name='dashboard'></a>", unsafe_allow_html=True)
    st.title("Glass Design Dashboard")

    # Create a two-column layout
    dashboard_col1, dashboard_col2 = st.columns(2)

    # -----------------------------
    # Column 1: Current Design Parameters
    # -----------------------------
    with dashboard_col1:
        st.subheader("Current Design Parameters")

        # Get values from session state
        fbk_choice = st.session_state.get("fbk_choice", "")
        standard = st.session_state.get("standard", "")
        ke_choice = st.session_state.get("ke_choice", "")
        ksp_choice = st.session_state.get("ksp_choice", "")
        selected_loads = st.session_state.get("selected_loads", [])
        df_results = st.session_state.get("df_results", pd.DataFrame())
        strength_col = st.session_state.get("strength_col", "")

        # Create a summary card with current parameters
        st.markdown(
            f"""
            <div style="padding: 15px; border-radius: 5px; border: 1px solid #ddd; background-color: #f9f9f9;">
                <h4 style="margin-top: 0;">Glass Design</h4>
                <p><strong>Glass Type:</strong> {fbk_choice}</p>
                <p><strong>Standard:</strong> {standard}</p>
                <p><strong>Edge Type:</strong> {ke_choice}</p>
                <p><strong>Surface Profile:</strong> {ksp_choice}</p>
                <p><strong>Selected Loads:</strong> {', '.join(selected_loads) if selected_loads else 'None'}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Create a mini strength gauge visualization
        if selected_loads and not df_results.empty and strength_col:
            min_strength = df_results[df_results["Load Type"].isin(selected_loads)][strength_col].min()

            # Create a gauge chart to show design strength
            gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=float(min_strength),
                title={"text": "Min. Design Strength (MPa)"},
                gauge={
                    "axis": {"range": [0, 150]},
                    "bar": {"color": "#EB8C71"},
                    "steps": [
                        {"range": [0, 30], "color": "#E7F8F9"},
                        {"range": [30, 70], "color": "#B8E9EC"},
                        {"range": [70, 150], "color": "#88DBDF"}
                    ],
                    "threshold": {
                        "line": {"color": "#D3451D", "width": 4},
                        "thickness": 0.75,
                        "value": float(min_strength)
                    }
                }
            ))
            gauge.update_layout(height=250, margin=dict(l=10, r=10, t=50, b=10))
            st.plotly_chart(gauge, use_container_width=True)

    # -----------------------------
    # Column 2: Quick Interlayer Selector
    # -----------------------------
    with dashboard_col2:
        st.subheader("Quick Interlayer Selector")

        # Get values from session state
        selected_interlayer = st.session_state.get("selected_interlayer", "")
        excel_file = st.session_state.get("excel_file", "")

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

        interlayer_options = st.session_state.get("interlayer_options", [])

        # Create a discrete slider with 20-degree intervals
        min_temp, max_temp = min(temp_list), max(temp_list)
        temp_values = sorted(set([min_temp, max_temp] + list(range(min_temp, max_temp + 1, 20))))
        quick_temp = st.select_slider("Temperature (°C):", options=temp_values, value=20 if 20 in temp_values else temp_values[0])

        # Load duration selector - simplified
        quick_duration_options = ["3 sec (Impact)", "10 min (Wind)", "1 day (Snow)", "1 year (Permanent)"]
        quick_duration = st.selectbox("Load Duration:", quick_duration_options)

        # Map the simplified options to actual durations
        duration_map = {
            "3 sec (Impact)": "3 sec",
            "10 min (Wind)": "10 min",
            "1 day (Snow)": "1 day",
            "1 year (Permanent)": "1 year"
        }
        mapped_duration = duration_map[quick_duration]

        # Create a comparison for all interlayers at this temperature and duration
        quick_comparison_data = []

        if excel_file and interlayer_options:
            for interlayer in interlayer_options:
                try:
                    df_interlayer = pd.read_excel(excel_file, sheet_name=interlayer)
                    # Find closest temperature if exact match not available
                    available_temps = df_interlayer["Temperature (°C)"].values
                    closest_temp = available_temps[np.abs(available_temps - quick_temp).argmin()]

                    temp_data = df_interlayer[df_interlayer["Temperature (°C)"] == closest_temp].iloc[0]

                    if mapped_duration in temp_data.index:
                        value = temp_data[mapped_duration]
                        # Convert to numeric, with fallback value
                        if pd.isna(value) or value == "No Data":
                            value = 0.05
                        else:
                            value = float(value)

                        quick_comparison_data.append({
                            "Interlayer": interlayer,
                            "E(MPa)": value
                        })
                except Exception as e:
                    st.error(f"Error loading data for {interlayer}: {e}")

        if quick_comparison_data:
            df_quick = pd.DataFrame(quick_comparison_data)
            df_quick = df_quick.sort_values(by="E(MPa)", ascending=False)

            # Plot horizontal bar chart
            bar_fig = go.Figure()

            bar_fig.add_trace(go.Bar(
                y=df_quick["Interlayer"],
                x=df_quick["E(MPa)"],
                orientation='h',
                marker_color=[
                    '#00303C' if i == 0 else  # Best option
                    '#00A3AD' if i == 1 else  # Second best
                    '#88DBDF' if i == 2 else  # Third
                    '#636669'                 # Others
                    for i in range(len(df_quick))
                ],
                text=df_quick["E(MPa)"].round(2),
                textposition='auto',
            ))

            bar_fig.update_layout(
                title=f"Interlayer Stiffness at {quick_temp}°C, {quick_duration}",
                xaxis_title="Young's Modulus E(MPa)",
                yaxis=dict(
                    title="",
                    categoryorder='total ascending',
                ),
                height=300,
                margin=dict(l=10, r=10, t=50, b=10)
            )

            st.plotly_chart(bar_fig, use_container_width=True)

            # Add recommendation based on stiffness requirements
            top_interlayer = df_quick.iloc[0]["Interlayer"]
            st.markdown(
                f"""
                <div style="padding: 10px; border-radius: 5px; border: 1px solid #1A659E; background-color: #f0f8ff;">
                    <strong>Recommended Interlayer:</strong> {top_interlayer}
                    <br>
                    <small>Based on highest stiffness for the selected conditions</small>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.warning("No comparison data available.")

    # Add visual UI improvements
    st.markdown("""
    <style>
    div.stButton > button {
        background-color: #3CAEA3;
        color: white;
        font-weight: bold;
    }
    div.stButton > button:hover {
        background-color: #1A659E;
        color: white;
    }
    .reportview-container .main .block-container {
        padding-top: 2rem;
    }
    h1, h2, h3 {
        color: #1A659E;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("---")
