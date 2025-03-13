import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from config import (
    fbk_options,
    ksp_options,
    ksp_prime_options,
    kv_options,
    ke_options,
    f_gk_value,
    kmod_options,
    time_list,
    time_map
)

def render_interlayer_comparison():
    """Render the Interlayer Comparison section of the dashboard."""
    st.markdown("<a name='interlayer-comparison'></a>", unsafe_allow_html=True)
    st.title("Interlayer Comparison Chart")

    # Create a simple comparison feature
    st.subheader("Compare Interlayers")

    # Get values from session state
    interlayer_options = st.session_state.get("interlayer_options", [])
    selected_interlayer = st.session_state.get("selected_interlayer", "")
    temp_list = st.session_state.get("temp_list", [])
    time_map = st.session_state.get("time_map", {})
    excel_file = st.session_state.get("excel_file", "")
    
    # Allow multiple interlayer selection for comparison
    compare_interlayers = st.multiselect(
        "Select interlayers to compare:",
        interlayer_options,
        default=[selected_interlayer] if selected_interlayer in interlayer_options else []
    )

    # Select comparison parameters
    col1, col2 = st.columns(2)
    with col1:
        compare_temp = st.selectbox("Select Temperature for Comparison (°C):", temp_list)
    with col2:
        compare_times = st.multiselect(
            "Select Load Durations for Comparison:",
            list(time_map.keys()) if time_map else ["3 sec", "3 min", "10 min", "1 day", "1 year"],
            default=["3 sec", "3 min", "10 min", "1 day", "1 year"]
        )

    if compare_interlayers and compare_times:
        # Create a dataframe to hold comparison data
        comparison_data = []
        
        # Load data for each selected interlayer
        for interlayer in compare_interlayers:
            try:
                df_interlayer = pd.read_excel(excel_file, sheet_name=interlayer)
                # Get values for the selected temperature
                if compare_temp in df_interlayer["Temperature (°C)"].values:
                    temp_data = df_interlayer[df_interlayer["Temperature (°C)"] == compare_temp].iloc[0]
                    
                    # Extract values for each selected time
                    for time_label in compare_times:
                        if time_label in temp_data.index:
                            value = temp_data[time_label]
                            # Convert to numeric, with fallback value
                            if pd.isna(value) or value == "No Data":
                                value = 0.05
                            else:
                                value = float(value)
                                
                            comparison_data.append({
                                "Interlayer": interlayer,
                                "Load Duration": time_label,
                                "E(MPa)": value
                            })
            except Exception as e:
                st.error(f"Error loading data for {interlayer}: {e}")
        
        # Create dataframe from collected data
        if comparison_data:
            df_comparison = pd.DataFrame(comparison_data)
            
            # Plot comparison bar chart
            fig = go.Figure()
            
            # Add bars for each interlayer and load duration
            for time_label in compare_times:
                df_subset = df_comparison[df_comparison["Load Duration"] == time_label]
                
                if not df_subset.empty:
                    fig.add_trace(go.Bar(
                        x=df_subset["Interlayer"],
                        y=df_subset["E(MPa)"],
                        name=time_label,
                        text=df_subset["E(MPa)"].round(2),
                        textposition='auto',
                    ))
            
            # Update layout
            fig.update_layout(
                title=f"Interlayer Comparison at {compare_temp}°C",
                xaxis_title="Interlayer Type",
                yaxis_title="Young's Modulus E(MPa)",
                barmode='group',
                legend_title="Load Duration"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Add a summary table
            st.subheader("Comparison Data Table")
            
            # Pivot the data for better display
            df_pivot = df_comparison.pivot(
                index="Interlayer", 
                columns="Load Duration", 
                values="E(MPa)"
            ).reset_index()
            
            # Format the data to 2 decimal places
            for col in df_pivot.columns:
                if col != "Interlayer":
                    df_pivot[col] = df_pivot[col].round(2)
                    
            st.dataframe(df_pivot)
        else:
            st.warning("No comparison data available for the selected parameters.")

    st.markdown("---")
