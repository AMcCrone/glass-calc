import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as go

# Retrieve the password from secrets
PASSWORD = st.secrets["password"]

# Initialize authentication state
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

def check_password():
    """Check the password input against the secret password."""
    if st.session_state.get("password_input") == PASSWORD:
        st.session_state["authenticated"] = True
    else:
        st.error("Incorrect password.")

# If the user is not authenticated, show the password input and halt the app.
if not st.session_state["authenticated"]:
    st.text_input("Enter Password:", type="password", key="password_input", on_change=check_password)
    st.stop()

st.title("Glass Design Strength Calculator")
st.markdown(
    r"""
This app calculates the design strength of glass based on two standards:
- **EN 16612**
- **IStructE Structural Use of Glass in Buildings**

The design strength is calculated using one of four equations depending on whether the glass is annealed (basic) or not, and on the selected standard.

For **annealed glass** (basic):
$$
f_{g;d} = \frac{k_e \, k_{mod} \, k_{sp} \, f_{g;k}}{\gamma_{M;A}}
$$

For **all but annealed glass**:
- **EN 16612:**
$$
f_{g;d} = \frac{k_e \, k_{mod} \, k_{sp} \, f_{g;k}}{\gamma_{M;A}} + \frac{k_v \,(f_{b;k} - f_{g;k})}{\gamma_{M;v}}
$$
- **IStructE:**
$$
f_{g;d} = \left(\frac{k_{mod} \, k_{sp} \, f_{g;k}}{\gamma_{M;A}} + \frac{k_v \,(f_{b;k} - f_{g;k})}{\gamma_{M;v}}\right) k_e
$$

where:
- $$ f_{b;k} $$ is the characteristic bending strength (N/mm²),
- $$ k_{sp} $$ is the glass surface profile factor,
- $$ k'_{sp} $$ is the surface finish factor (**None** = 1, **Sand blasted** = 0.6, **Acid etched** = 1) – (this parameter is now separate from $$ k_{sp} $$),
- $$ k_{v} $$ is the strengthening factor,
- $$ k_{e} $$ is the edge strength factor,
- $$ k_{mod} $$ is the load duration factor,
- $$ f_{g;k} $$ is the design value for glass (fixed at 45 N/mm²),
- For annealed glass:
  - IStructE: $$ \gamma_{M;A} = 1.6 $$  
  - EN 16612: $$ \gamma_{M;A} = 1.8 $$
- For surface prestressed (non-annealed) glass:
  - $$ \gamma_{M;v} = 1.2 $$.

*Note: Adjust any factors or assumptions as necessary to match your detailed model.*
    """,
    unsafe_allow_html=True,
)

# =============================================================================
# Define the time duration mapping once for both plots
# =============================================================================
time_list = [
    ("1 sec", 1),
    ("3 sec", 3),
    ("5 sec", 5),
    ("10 sec", 10),
    ("30 sec", 30),
    ("1 min", 60),
    ("5 min", 300),
    ("10 min", 600),
    ("30 min", 1800),
    ("1 hour", 3600),
    ("6 hours", 21600),
    ("12 hours", 43200),
    ("1 day", 86400),
    ("2 days", 172800),
    ("5 days", 432000),
    ("1 week", 604800),
    ("3 weeks", 1814400),
    ("1 month", 2592000),
    ("1 year", 31536000),
    ("10 years", 315360000),
    ("50 years", 1576800000)
]
time_map = {label: seconds for label, seconds in time_list}
tickvals = [seconds for label, seconds in time_list]
ticktext = [label for label, seconds in time_list]

# =============================================================================
# Input Parameters for Glass Design Strength
# =============================================================================

# Overall standard selection
standard = st.selectbox(
    "Select the Standard",
    ["IStructE Structural Use of Glass in Buildings", "EN 16612"],
)

st.header("Input Parameters")

# 1. Characteristic bending strength (f_{b;k})
fbk_options = {
    "Annealed (EN-572-1, 45 N/mm²)": {"value": 45, "category": "basic"},
    "Heat strengthened (EN 1863-1, 70 N/mm²)": {"value": 70, "category": "prestressed"},
    "Heat strengthened patterned (EN 1863-1, 55 N/mm²)": {"value": 55, "category": "prestressed"},
    "Heat strengthened enamelled (EN 1863-1, 45 N/mm²)": {"value": 45, "category": "prestressed"},
    "Toughened (EN 12150-1, 120 N/mm²)": {"value": 120, "category": "prestressed"},
    "Toughened patterned (EN 12150-1, 90 N/mm²)": {"value": 90, "category": "prestressed"},
    "Toughened enamelled (EN 12150-1, 75 N/mm²)": {"value": 75, "category": "prestressed"},
    "Chemically toughened (EN 12337-1, 150 N/mm²)": {"value": 150, "category": "prestressed"},
    "Chemically toughened patterned (EN 12337-1, 100 N/mm²)": {"value": 100, "category": "prestressed"},
}
fbk_choice = st.selectbox("Characteristic bending strength $$f_{b;k}$$", list(fbk_options.keys()))
fbk_value = fbk_options[fbk_choice]["value"]
glass_category = fbk_options[fbk_choice]["category"]

# 2. Glass surface profile factor (k_{sp})
ksp_options = {
    "Float glass": 1.0,
    "Drawn sheet glass": 1.0,
    "Enamelled float or drawn sheet glass": 1.0,
    "Patterned glass": 0.75,
    "Enamelled patterned glass": 0.75,
    "Polished wired glass": 0.75,
    "Patterned wired glass": 0.6,
}
ksp_choice = st.selectbox("Glass surface profile factor $$k_{sp}$$", list(ksp_options.keys()))
ksp_value = ksp_options[ksp_choice]

# 3. Surface finish factor (k'_{sp})
ksp_prime_options = {
    "None": 1.0,
    "Sand blasted": 0.6,
    "Acid etched": 1.0,
}
ksp_prime_choice = st.selectbox("Surface finish factor $$k'_{sp}$$", list(ksp_prime_options.keys()))
ksp_prime_value = ksp_prime_options[ksp_prime_choice]

# 4. Strengthening factor (k_{v})
kv_options = {
    "Horizontal toughening": 1.0,
    "Vertical toughening": 0.6,
}
kv_choice = st.selectbox("Strengthening factor $$k_{v}$$", list(kv_options.keys()))
kv_value = kv_options[kv_choice]

# 5. Edge strength factor (k_{e})
ke_options = {
    "Edges not stressed in bending": 1.0,
    "Polished float edges": 1.0,
    "Seamed float edges": 0.9,
    "Other edge types": 0.8,
}
ke_choice = st.selectbox("Edge strength factor $$k_{e}$$", list(ke_options.keys()))
ke_value = ke_options[ke_choice]

# Fixed design value for glass (f_{g;k}) is always 45 N/mm².
f_gk_value = 45
st.markdown(f"**Fixed design value for glass $$f_{{g;k}}$$: {f_gk_value} N/mm²**")

# Define material partial safety factors:
if glass_category == "basic":
    gamma_MA = 1.6 if standard == "IStructE Structural Use of Glass in Buildings" else 1.8
    gamma_MV = None
else:
    gamma_MA = 1.6 if standard == "IStructE Structural Use of Glass in Buildings" else 1.8
    gamma_MV = 1.2

if glass_category == "basic":
    st.markdown(f"**Selected material partial safety factor $$\\gamma_{{M;A}}$$: {gamma_MA}**")
else:
    st.markdown(f"**Selected material partial safety factor $$\\gamma_{{M;A}}$$: {gamma_MA}**")
    st.markdown(f"**Selected material partial safety factor $$\\gamma_{{M;v}}$$: {gamma_MV}**")

# 6. Load duration factors (k_{mod}) – full table of options
kmod_options = {
    "5 seconds – Single gust (Blast Load)": 1.00,
    "30 seconds – Domestic balustrade (Barrier load, domestic)": 0.89,
    "5 minutes – Workplace/public balustrade (Barrier load, public)": 0.77,
    "10 minutes – Multiple gust (Wind Load)": 0.74,
    "30 minutes – Maintenance access": 0.69,
    "5 hours – Pedestrian access": 0.60,
    "1 week – Snow short term": 0.48,
    "1 month – Snow medium term": 0.44,
    "3 months – Snow long term": 0.41,
    "50 years – Permanent": 0.29,
}

# Calculation for each load duration case
if st.button("Calculate Design Strength for All Load Cases"):
    results = []
    for load_type, kmod_value in kmod_options.items():
        # Four cases based on standard and whether the glass is annealed (basic) or not.
        if glass_category == "basic":  # Annealed glass (both standards use the same formula)
            f_gd = (ke_value * kmod_value * ksp_value * f_gk_value) / gamma_MA
        else:  # Non-annealed glass
            if standard == "EN 16612":
                f_gd = ((ke_value * kmod_value * ksp_value * f_gk_value) / gamma_MA) + ((kv_value * (fbk_value - f_gk_value)) / gamma_MV)
            else:  # IStructE
                f_gd = (((kmod_value * ksp_value * f_gk_value) / gamma_MA) + ((kv_value * (fbk_value - f_gk_value)) / gamma_MV)) * ke_value

        results.append({
            "Load Type": load_type,
            "k_mod": kmod_value,
            "Glass Design Strength $$f_{g;d}$$ (N/mm²)": f"{f_gd:.2f}"
        })
        
    df_results = pd.DataFrame(results)
    st.table(df_results)

# =============================================================================
# 2D Plot: Theoretical Load Duration Factor (k_mod)
# =============================================================================
st.subheader("Theoretical Load Duration Factor (k_mod)")
# Generate theoretical data from 1 sec to ~50 years (1.6e9 seconds) on a log scale
t_values = np.logspace(0, np.log10(1.6e9), 200)
k_mod_theoretical = 0.663 * t_values**(-1/16)

trace = go.Scatter(
    x=t_values,
    y=k_mod_theoretical,
    mode="lines",
    name=r"$k_{mod} = 0.663\,t^{-1/16}$"
)
layout = go.Layout(
    xaxis=dict(
        title="Loading Duration",
        type="log",
        tickvals=tickvals,
        ticktext=ticktext
    ),
    yaxis=dict(title="k_mod"),
    legend=dict(x=0.05, y=0.95),
    template="plotly_white"
)
fig2d = go.Figure(data=[trace], layout=layout)
st.plotly_chart(fig2d, use_container_width=True)

# =============================================================================
# Interlayer Relaxation Modulus 3D Plot Section
# =============================================================================
st.title("Interlayer Relaxation Modulus 3D Plot")

# 1. Create dropdowns for interlayer, temperature, and load duration
interlayer_options = [
    "SentryGlas", 
    "SentryGlas Xtra", 
    "Trosifol Clear - Ultra Clear", 
    "Trosifol Extra Stiff", 
    "Trosifol SC Monolayer"
]
selected_interlayer = st.selectbox("Select Interlayer:", interlayer_options)

# 2. Load the Excel file (each sheet is one interlayer)
excel_file = "Interlayer_E(t)_Database.xlsx"  # Ensure this file is in your repository
try:
    df = pd.read_excel(excel_file, sheet_name=selected_interlayer)
except Exception as e:
    st.error(f"Error loading Excel file: {e}")
    st.stop()

# 3. Convert the wide table into long format
df_melted = df.melt(
    id_vars="Temperature (°C)",
    var_name="Time",
    value_name="E(MPa)"
)
# Ensure modulus values are numeric
df_melted["E(MPa)"] = pd.to_numeric(df_melted["E(MPa)"], errors="coerce")
df_melted.dropna(subset=["E(MPa)"], inplace=True)
# Map the load duration strings to numeric seconds for log-scale
df_melted["Time_s"] = df_melted["Time"].map(time_map)

# 4. Create selection boxes for Temperature and Load Duration
temp_list = sorted(df["Temperature (°C)"].unique())
selected_temp = st.selectbox("Select Temperature (°C):", temp_list)
selected_time = st.selectbox("Select Load Duration:", list(time_map.keys()))

# Find the corresponding data point
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

# Display the selected Young's modulus above the graph
if highlight_z is not None:
    st.markdown(f"**Selected Young's Modulus:** {highlight_z} MPa")
else:
    st.markdown("**Selected data point not found.**")

# 5. Create the 3D Plotly Scatter Plot
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
    name="All Data"
)
trace_highlight = go.Scatter3d(
    x=[highlight_x] if highlight_x is not None else [],
    y=[highlight_y] if highlight_y is not None else [],
    z=[highlight_z] if highlight_z is not None else [],
    mode='markers',
    marker=dict(
        size=12,
        color='red',
        symbol='diamond'
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
