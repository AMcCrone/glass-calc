import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import io
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm

# -----------------------
# Authentication Section
# -----------------------
# Retrieve the password from secrets
if "password" in st.secrets:
    PASSWORD = st.secrets["password"]
else:
    PASSWORD = "demo"  # Fallback for development

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

# -----------------------
# Common Definitions
# -----------------------
# Define the time duration mapping (used in both sections)
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

# -----------------------
# Sidebar Navigation Menu (Bookmarks)
# -----------------------
st.sidebar.markdown("""
## Navigation
- [Glass Design Strength Calculator](#glass-design-strength-calculator)
- [Interlayer Relaxation Modulus 3D Plot](#interlayer-relaxation-modulus-3d-plot)
- [Documentation](#documentation)
""", unsafe_allow_html=True)

# =============================================================================
# Glass Design Strength Calculator Section
# =============================================================================
st.markdown("<a name='glass-design-strength-calculator'></a>", unsafe_allow_html=True)
st.title("Glass Design Strength Calculator")

# Overall standard selection
standard = st.selectbox(
    "Select the Standard",
    ["IStructE Structural Use of Glass in Buildings", "EN 16612"],
    help="TT suggests limiting the standard EN 16612 for calculating the lateral load resistance of linearly supported glazed elements used as infill panels in a class of consequences lower than those covered in EN 1990. For all structural glazing elements (floor plate, wall, beams, columns, or glass panel with point fixing), it is recommended to use the IStructE Book. Please choose between EN-16612 & IStructE Book and not the DIN 18008, as it's not contemplated in the UK codes of practice."
)

st.header("Input Parameters")

# 1. Characteristic bending strength (f_{b;k})
fbk_options = {
    "Annealed (EN-572-1, 45 N/mm²)": {"value": 45, "category": "annealed"},
    "Heat strengthened (EN 1863-1, 70 N/mm²)": {"value": 70, "category": "prestressed"},
    "Heat strengthened patterned (EN 1863-1, 55 N/mm²)": {"value": 55, "category": "prestressed"},
    "Heat strengthened enamelled (EN 1863-1, 45 N/mm²)": {"value": 45, "category": "prestressed"},
    "Toughened (EN 12150-1, 120 N/mm²)": {"value": 120, "category": "prestressed"},
    "Toughened patterned (EN 12150-1, 90 N/mm²)": {"value": 90, "category": "prestressed"},
    "Toughened enamelled (EN 12150-1, 75 N/mm²)": {"value": 75, "category": "prestressed"},
    "Chemically toughened (EN 12337-1, 150 N/mm²)": {"value": 150, "category": "prestressed"},
    "Chemically toughened patterned (EN 12337-1, 100 N/mm²)": {"value": 100, "category": "prestressed"},
}

fbk_choice = st.selectbox(
    "Characteristic bending strength $$f_{b;k}$$", 
    list(fbk_options.keys()),
    help="Note 1: Prestressed glass is the general term used for glass which has been subjected to a strengthening treatment, by heat or chemicals (e.g. heat strengthened, heat toughened, chemically toughened glass).\n\nNote 2: Patterned glass is glass that has passed through rollers to give it surface texture.\n\nNote 3: Enamelled glass is the same as fritted glass. It is glass which has a ceramic frit applied to the surface, by e.g. painting or screen printing, which is subsequently fired into the surface."
)

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
ke_choice = st.selectbox(
    "Edge strength factor $$k_{e}$$", 
    list(ke_options.keys()),
    help="Note 7: According to EN 16612 - Where glass edges are not stressed in bending (e.g. a pane with all edges supported) ke = 1. If glass edges are stressed in bending (e.g. a pane with two opposite edges supported or with three edges supported), ke can be lower than 1.0.\n\nNote 8: EN 16612 only applies edge strength factor to annealed glass and not to prestressed glass. IStructE applies edge strength factor to both annealed and prestressed glass.\n\nNote 9: Seamed edges are arrissed or ground edges by machine or by hand where the abrasive action is along the length of the edge."
)
ke_value = ke_options[ke_choice]

# Fixed design value for glass (f_{g;k}) is always 45 N/mm².
f_gk_value = 45

# Define material partial safety factors:
if glass_category == "annealed":
    gamma_MA = 1.6 if standard == "IStructE Structural Use of Glass in Buildings" else 1.8
    gamma_MV = None
else:
    gamma_MA = 1.6 if standard == "IStructE Structural Use of Glass in Buildings" else 1.8
    gamma_MV = 1.2

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

# --- Auto-update Calculation for Design Strength Table ---
results = []
for load_type, kmod_value in kmod_options.items():
    if glass_category == "annealed":  # Annealed glass
        f_gd = (ke_value * kmod_value * ksp_value * ksp_prime_value * f_gk_value) / gamma_MA
    else:  # Non-annealed glass
        if standard == "EN 16612":
            f_gd = ((ke_value * kmod_value * ksp_value * ksp_prime_value * f_gk_value) / gamma_MA) + ((kv_value * (fbk_value - f_gk_value)) / gamma_MV)
        else:  # IStructE
            f_gd = (((kmod_value * ksp_value * ksp_prime_value * f_gk_value) / gamma_MA) + ((kv_value * (fbk_value - f_gk_value)) / gamma_MV)) * ke_value

    results.append({
        "Load Type": load_type,
        "k_mod": f"{kmod_value:.2f}",
        "fg;d (MPa)": f"{f_gd:.2f}"
    })
df_results = pd.DataFrame(results)
# Ensure the design strength column is numeric
strength_col = "fg;d (MPa)"
df_results[strength_col] = pd.to_numeric(df_results[strength_col], errors='coerce')

# Create a multiselect widget to choose load durations to highlight
selected_loads = st.multiselect(
    "Select load durations to highlight",
    options=list(kmod_options.keys()),
    help="Note 4: Values in Table \"4. Factor for load duration\" in this sheet are from IStructE. Similar values are found in BS 16612. Generally, for t being the load duration in hours, kmod = 0.663t^-1/16.\n\nNote 5: The value of kmod = 0.74 is based on a cumulative equivalent duration of 10 min, considered representative of the effect of a storm which may last several hours. Higher values of kmod can be considered for wind, but need to be justified (currently there is no guide for this).\n\nNote 6: According to EN 16612 - Where loads with different durations need to be treated in combination, the proposed kmod for the load combination is the highest value, which is associated with any of the loads in the combination.\n\nHow to select the right kmod? By choosing the highest kmod value for determining the glass resistance. However, all load combinations should be considered; for example, for wind, snow and self-weight: kmod = 0.74 (or 1) for wind, snow and self-weight; kmod = 0.48 for snow and self-weight; kmod = 0.29 for self-weight."
)

# Define a styling function that applies the highlight color if the row's "Load Type" is selected.
def style_load_row(row):
    if row["Load Type"] in selected_loads:
        return ['background-color: #EB8C71'] * len(row)
    else:
        return [''] * len(row)

# Apply the style function and display the styled DataFrame.
df_styled = df_results.style.apply(style_load_row, axis=1)
st.subheader("Design Strength Results")
# Display the DataFrame without the index column
st.dataframe(df_styled.hide(axis="index"))

# =============================================================================
# Dashboard Section - Summary View
# =============================================================================
st.markdown("<a name='dashboard'></a>", unsafe_allow_html=True)
st.title("Glass Design Dashboard")

# Create dashboard layout
dashboard_col1, dashboard_col2 = st.columns(2)

with dashboard_col1:
    st.subheader("Current Design Parameters")
    
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
    if selected_loads:
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
                    {"range": [0, 30], "color": "#FF9999"},
                    {"range": [30, 70], "color": "#FFDD99"},
                    {"range": [70, 150], "color": "#99CC99"}
                ],
                "threshold": {
                    "line": {"color": "red", "width": 4},
                    "thickness": 0.75,
                    "value": float(min_strength)
                }
            }
        ))
        gauge.update_layout(height=250, margin=dict(l=10, r=10, t=50, b=10))
        st.plotly_chart(gauge, use_container_width=True)

with dashboard_col2:
    st.subheader("Quick Interlayer Selector")

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
    
    # Create a discrete slider with 20-degree intervals
    temp_list = sorted(df["Temperature (°C)"].unique())
    quick_temp = st.slider("Temperature (°C):", min(temp_list), max(temp_list), 20, step=20)
    
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
                '#1A659E' if i == 0 else  # Best option
                '#3CAEA3' if i == 1 else  # Second best
                '#2C8C99' if i == 2 else  # Third
                '#7D938A' if i == 3 else  # Middle
                '#9C8D84'                 # Others
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


# =============================================================================
# Interlayer Relaxation Modulus 3D Plot Section
# =============================================================================
st.markdown("<a name='interlayer-relaxation-modulus-3d-plot'></a>", unsafe_allow_html=True)
st.title("Interlayer Relaxation Modulus 3D Plot")

# 1. Create dropdown for interlayer selection
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
# Replace non-numeric values (e.g. "No Data") with 0.05 N/mm²
df_melted["E(MPa)"] = pd.to_numeric(df_melted["E(MPa)"], errors="coerce").fillna(0.05)
# Map the load duration strings to numeric seconds for the log-scale x-axis
df_melted["Time_s"] = df_melted["Time"].map(time_map)

# 4. Create selection boxes for Temperature and Load Duration
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
    name="All Data",
    hovertemplate="Load Duration: %{x}<br>Temp.: %{y} °C<br>E(t): %{z} MPa"
)
# Change the selected point to a red circle (symbol "circle") of the same size (12)
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

# =============================================================================
# Documentation Section
# =============================================================================
st.markdown("<a name='documentation'></a>", unsafe_allow_html=True)
st.title("Documentation")
st.markdown(
    r"""
**Calculation Details:**

The design strength is calculated using one of four equations depending on whether the glass is annealed (annealed) or non-annealed (prestressed), and based on the selected standard.

For **annealed glass**:  
$$
f_{g;d} = \frac{k_e \, k_{mod} \, k_{sp} \, f_{g;k}}{\gamma_{M;A}}
$$

For **pre-stressed glass**:  
- **EN 16612:**  
$$
f_{g;d} = \frac{k_e \, k_{mod} \, k_{sp} \, f_{g;k}}{\gamma_{M;A}} + \frac{k_v \,(f_{b;k} - f_{g;k})}{\gamma_{M;v}}
$$
- **IStructE:**  
$$
f_{g;d} = \left(\frac{k_{mod} \, k_{sp} \, f_{g;k}}{\gamma_{M;A}} + \frac{k_v \,(f_{b;k} - f_{g;k})}{\gamma_{M;v}}\right) k_e
$$

**Parameters:**
- $$ f_{b;k} $$: Characteristic bending strength (N/mm²)  
- $$ k_{sp} $$: Glass surface profile factor  
- $$ k'_{sp} $$: Surface finish factor (None = 1, Sand blasted = 0.6, Acid etched = 1)  
- $$ k_{v} $$: Strengthening factor  
- $$ k_{e} $$: Edge strength factor  
- $$ k_{mod} $$: Load duration factor  
- $$ f_{g;k} $$: Design value for glass (fixed at 45 N/mm²)

**Material Partial Safety Factors:**
- For annealed glass:  
  - IStructE: $$ \gamma_{M;A} = 1.6 $$  
  - EN 16612: $$ \gamma_{M;A} = 1.8 $$
- For non-annealed glass:  
  - $$ \gamma_{M;A} $$ as above and $$ \gamma_{M;v} = 1.2 $$
    """,
    unsafe_allow_html=True,
)

# =============================================================================
# Appendix - Full Parameter Tables for Glass Strength Design
# =============================================================================
st.markdown("<a name='appendix'></a>", unsafe_allow_html=True)
st.title("Appendix")

# Define a generic style function to highlight the selected option.
def style_selected(row, selected_value, key='Option'):
    if row[key] == selected_value:
        return ['background-color: #EB8C71'] * len(row)
    else:
        return [''] * len(row)

# -----------------------
# Characteristic Bending Strength Options (f₍b;k₎)
# -----------------------
st.markdown("#### $$ f_{b;k} $$ - Characteristic Bending Strength")
df_fbk = pd.DataFrame({
    "Option": list(fbk_options.keys()),
    "Value (N/mm²)": [fbk_options[k]["value"] for k in fbk_options]
}).round(2)
df_fbk_styled = df_fbk.style.apply(lambda row: style_selected(row, fbk_choice, key="Option"), axis=1)
st.dataframe(df_fbk_styled.hide(axis="index"))

# -----------------------
# Glass Surface Profile Factor Options (kₛₚ)
# -----------------------
st.markdown("#### $$ k_{sp} $$ - Glass Surface Profile Factor")
df_ksp = pd.DataFrame({
    "Option": list(ksp_options.keys()),
    "Value": list(ksp_options.values())
}).round(2)
df_ksp_styled = df_ksp.style.apply(lambda row: style_selected(row, ksp_choice, key="Option"), axis=1)
st.dataframe(df_ksp_styled.hide(axis="index"))

# -----------------------
# Surface Finish Factor Options (k'ₛₚ)
# -----------------------
st.markdown("#### $$ k'_{sp} $$ - Surface Finish Factor")
df_ksp_prime = pd.DataFrame({
    "Option": list(ksp_prime_options.keys()),
    "Value": list(ksp_prime_options.values())
}).round(2)
df_ksp_prime_styled = df_ksp_prime.style.apply(lambda row: style_selected(row, ksp_prime_choice, key="Option"), axis=1)
st.dataframe(df_ksp_prime_styled.hide(axis="index"))

# -----------------------
# Strengthening Factor Options (kᵥ)
# -----------------------
st.markdown("#### $$ k_{v} $$ - Strengthening Factor")
df_kv = pd.DataFrame({
    "Option": list(kv_options.keys()),
    "Value": list(kv_options.values())
}).round(2)
df_kv_styled = df_kv.style.apply(lambda row: style_selected(row, kv_choice, key="Option"), axis=1)
st.dataframe(df_kv_styled.hide(axis="index"))

# -----------------------
# Edge Strength Factor Options (kₑ)
# -----------------------
st.markdown("#### $$ k_{e} $$ - Edge Strength Factor")
df_ke = pd.DataFrame({
    "Option": list(ke_options.keys()),
    "Value": list(ke_options.values())
}).round(2)
df_ke_styled = df_ke.style.apply(lambda row: style_selected(row, ke_choice, key="Option"), axis=1)
st.dataframe(df_ke_styled.hide(axis="index"))

# -----------------------
# Load Duration Factor Options (k_mod)
# -----------------------
st.markdown("#### $$ k_{mod} $$ - Load Duration Factor Options (k_mod)")
df_kmod = pd.DataFrame({
    "Load Type": list(kmod_options.keys()),
    "k_mod": list(kmod_options.values())
}).round(2)
# Use the style function already defined in the app to highlight selected rows.
df_kmod_styled = df_kmod.style.apply(style_load_row, axis=1)
st.dataframe(df_kmod_styled.hide(axis="index"))

import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from datetime import datetime

# =============================================================================
# Improved PDF Generation - using ReportLab
# =============================================================================
def generate_pdf():
    """Generate a PDF report with the current calculation settings and results"""
    
    # Create a buffer for the PDF content
    buffer = io.BytesIO()
    
    # Create the PDF document with A4 size
    doc = SimpleDocTemplate(buffer, pagesize=A4, 
                           rightMargin=15*mm, leftMargin=15*mm,
                           topMargin=15*mm, bottomMargin=15*mm)
    
    # Get default styles
    styles = getSampleStyleSheet()
    
    # Modify existing styles instead of adding new ones with the same name
    styles['Title'].fontSize = 16
    styles['Title'].spaceAfter = 12
    
    styles['Heading2'].fontSize = 14
    styles['Heading2'].spaceAfter = 8
    
    # Add a new style with a unique name
    styles.add(ParagraphStyle(name='Normal-Bold',
                             parent=styles['Normal'],
                             fontName='Helvetica-Bold'))
    
    # Create content elements
    elements = []
    
    # Title
    elements.append(Paragraph("Glass Design Strength Calculation Report", styles['Title']))
    elements.append(Spacer(1, 10))
    
    # Standard Used
    elements.append(Paragraph("Standard Used", styles['Heading2']))
    elements.append(Paragraph(standard, styles['Normal']))
    elements.append(Spacer(1, 10))
    
    # Input Parameters Section
    elements.append(Paragraph("Input Parameters", styles['Heading2']))
    
    # Create a table for the input parameters
    input_data = [
        ["Parameter", "Selected Option", "Value"],
        ["Characteristic Bending Strength", fbk_choice, f"{fbk_value} N/mm²"],
        ["Glass Surface Profile Factor", ksp_choice, f"{ksp_value}"],
        ["Surface Finish Factor", ksp_prime_choice, f"{ksp_prime_value}"],
        ["Strengthening Factor", kv_choice, f"{kv_value}"],
        ["Edge Strength Factor", ke_choice, f"{ke_value}"],
        ["Design Value for Glass", "", f"{f_gk_value} N/mm²"]
    ]
    
    # Add safety factors
    if glass_category == "annealed":
        input_data.append(["Material Partial Safety Factor", f"γM,A = {gamma_MA}", ""])
    else:
        input_data.append(["Material Partial Safety Factors", f"γM,A = {gamma_MA}, γM,V = {gamma_MV}", ""])
    
    # Create the table
    input_table = Table(input_data, colWidths=[110, 250, 70])
    input_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (2, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (2, 0), colors.black),
        ('ALIGN', (0, 0), (2, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (2, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (2, 0), 6),
        ('BACKGROUND', (0, 1), (2, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (2, 1), (2, -1), 'CENTER'),
    ]))
    elements.append(input_table)
    elements.append(Spacer(1, 15))
    
    # Results Section
    elements.append(Paragraph("Design Strength Results", styles['Heading2']))
    
    # Create table data from calculation results
    results_data = [["Load Type", "k_mod", "fg;d (MPa)"]]
    
    # Add each result row
    for load_type, kmod_value in kmod_options.items():
        if glass_category == "annealed":
            f_gd = (ke_value * kmod_value * ksp_value * ksp_prime_value * f_gk_value) / gamma_MA
        else:
            if standard == "EN 16612":
                f_gd = ((ke_value * kmod_value * ksp_value * ksp_prime_value * f_gk_value) / gamma_MA) + \
                      ((kv_value * (fbk_value - f_gk_value)) / gamma_MV)
            else:  # IStructE
                f_gd = (((kmod_value * ksp_value * ksp_prime_value * f_gk_value) / gamma_MA) + \
                       ((kv_value * (fbk_value - f_gk_value)) / gamma_MV)) * ke_value
        
        row = [load_type, f"{kmod_value:.2f}", f"{f_gd:.2f}"]
        results_data.append(row)
    
    # Create the table with appropriate column widths
    results_table = Table(results_data, colWidths=[250, 70, 110])
    
    # Base table style
    table_style = [
        ('BACKGROUND', (0, 0), (2, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (2, 0), colors.black),
        ('ALIGN', (0, 0), (2, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (2, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (2, 0), 6),
        ('BACKGROUND', (0, 1), (2, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 1), (2, -1), 'CENTER'),
    ]
    
    # Highlight selected load durations
    for i, row in enumerate(results_data[1:], 1):  # Skip header row
        if row[0] in selected_loads:
            table_style.append(('BACKGROUND', (0, i), (2, i), colors.Color(0.925, 0.549, 0.443)))  # #EB8C71
    
    # Apply the style to the table
    results_table.setStyle(TableStyle(table_style))
    elements.append(results_table)
    elements.append(Spacer(1, 15))
    
    # Add formula explanation
    elements.append(Paragraph("Calculation Formula Used:", styles['Heading2']))
    if glass_category == "annealed":
        formula_text = """
        For annealed glass:
        fₙₓₚ = (kₑ × k_mod × kₛₚ × k'ₛₚ × f_g,k) / γ_M,A
        """
    else:
        if standard == "EN 16612":
            formula_text = """
            For pre-stressed glass (EN 16612):
            fₙₓₚ = (kₑ × k_mod × kₛₚ × k'ₛₚ × f_g,k) / γ_M,A + (kᵥ × (f_b,k - f_g,k)) / γ_M,v
            """
        else:  # IStructE
            formula_text = """
            For pre-stressed glass (IStructE):
            fₙₓₚ = ((k_mod × kₛₚ × k'ₛₚ × f_g,k) / γ_M,A + (kᵥ × (f_b,k - f_g,k)) / γ_M,v) × kₑ
            """
    
    elements.append(Paragraph(formula_text, styles['Normal']))
    elements.append(Spacer(1, 10))
    
    # Add parameter definitions
    elements.append(Paragraph("Parameter Definitions:", styles['Normal-Bold']))
    param_definitions = """
    • f_b,k: Characteristic bending strength (N/mm²)
    • kₛₚ: Glass surface profile factor
    • k'ₛₚ: Surface finish factor
    • kᵥ: Strengthening factor
    • kₑ: Edge strength factor
    • k_mod: Load duration factor
    • f_g,k: Design value for glass (fixed at 45 N/mm²)
    • γ_M,A: Material partial safety factor for annealed glass
    • γ_M,v: Material partial safety factor for non-annealed glass
    """
    elements.append(Paragraph(param_definitions, styles['Normal']))
    
    # Add interlayer information if relevant
    if include_interlayer_info:
        elements.append(Spacer(1, 15))
        elements.append(Paragraph("Interlayer Information", styles['Heading2']))
        
        interlayer_text = f"""
        Selected Interlayer: {interlayer_type}
        Temperature: {temperature} °C
        Load Duration: {load_duration}
        Calculated Young's Modulus: {calculated_modulus} MPa
        """
        elements.append(Paragraph(interlayer_text, styles['Normal']))
    
    # Add project information if available
    if project_info:
        elements.append(Spacer(1, 15))
        elements.append(Paragraph("Project Information", styles['Heading2']))
        elements.append(Paragraph(f"Project Name: {project_name}", styles['Normal']))
        elements.append(Paragraph(f"Project Number: {project_number}", styles['Normal']))
        elements.append(Paragraph(f"Engineer: {engineer_name}", styles['Normal']))
        if project_notes:
            elements.append(Paragraph("Notes:", styles['Normal-Bold']))
            elements.append(Paragraph(project_notes, styles['Normal']))
    
    # Add footer with date and version info
    elements.append(Spacer(1, 20))
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    elements.append(Paragraph(f"Report generated: {current_time}", styles['Normal']))
    elements.append(Paragraph("Glass Design Calculator v1.0.0 | © 2025", styles['Normal']))
    
    # Build the PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer


# In your Streamlit UI section:
# ============================

# Project Information Input
st.header("Project Information")
col1, col2 = st.columns(2)
with col1:
    project_info = st.checkbox("Include project information", value=False)
    project_name = st.text_input("Project Name", "", disabled=not project_info)
    project_number = st.text_input("Project Number", "", disabled=not project_info)
with col2:
    engineer_name = st.text_input("Engineer", "", disabled=not project_info)
    project_notes = st.text_area("Project Notes", "", disabled=not project_info)

# Interlayer Information Option
include_interlayer_info = st.checkbox("Include interlayer information in report", value=False)
if include_interlayer_info:
    # These variables should be defined elsewhere in your code
    st.info(f"The report will include interlayer data for {interlayer_type} at {temperature}°C with {load_duration} load duration.")

# Generate PDF button
if st.button("Generate PDF Report"):
    with st.spinner("Generating PDF report..."):
        pdf_buffer = generate_pdf()
        
        st.download_button(
            label="Download PDF Report",
            data=pdf_buffer,
            file_name="Glass_Design_Strength_Report.pdf",
            mime="application/pdf",
            help="Click to download the PDF report with all calculation details"
        )
        
        st.success("PDF report generated successfully!")

# Add notes for the interlayer section
st.markdown("<a name='interlayer-notes'></a>", unsafe_allow_html=True)
st.title("Interlayer Notes")
st.markdown("""
### About the Interlayer Relaxation Modulus Data

The Young's modulus of the interlayer is a key parameter for analyzing laminated glass. Unlike glass, the interlayer is viscoelastic, which means its stiffness (Young's modulus) depends on:

1. **Duration of loading** - Longer loads result in lower stiffness
2. **Temperature** - Higher temperatures result in lower stiffness

This 3D plot visualizes how the Young's modulus E(t) varies with both temperature and load duration for different interlayer materials commonly used in structural glass applications.

#### Common Interlayer Materials:

- **SentryGlas (SG)** - Ionoplast interlayer with higher stiffness and post-breakage strength
- **SentryGlas Xtra** - Enhanced version of SentryGlas
- **Trosifol Clear / Ultra Clear** - PVB interlayer with high clarity
- **Trosifol Extra Stiff** - Stiff PVB variant for structural applications
- **Trosifol SC Monolayer** - Structural PVB variant

#### Data Sources:
- Manufacturer technical datasheets
- Published research papers
- Industry standards

#### Engineering Applications:
This data is useful for:
- Design of structural glass elements
- Predicting deflection under different loading scenarios
- Analyzing post-breakage performance
- Temperature-dependent behavior assessment

#### Usage Notes:
- For structural calculations, engineers should use values appropriate for the expected temperature and load duration
- For critical applications, testing may be required to validate performance
- Use conservative values when multiple load conditions apply
""")

# Footer section with version information
st.markdown("---")
st.markdown("*Glass Design Calculator v1.0.0 | © 2025*")

# =============================================================================
# Interlayer Comparison Section
# =============================================================================
st.markdown("<a name='interlayer-comparison'></a>", unsafe_allow_html=True)
st.title("Interlayer Comparison Chart")

# Create a simple comparison feature
st.subheader("Compare Interlayers")

# Allow multiple interlayer selection for comparison
compare_interlayers = st.multiselect(
    "Select interlayers to compare:",
    interlayer_options,
    default=[selected_interlayer]
)

# Select comparison parameters
col1, col2 = st.columns(2)
with col1:
    compare_temp = st.selectbox("Select Temperature for Comparison (°C):", temp_list)
with col2:
    compare_times = st.multiselect(
        "Select Load Durations for Comparison:",
        list(time_map.keys()),
        default=["3 sec", "10 min", "1 day", "1 year"]
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
