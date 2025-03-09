import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from fpdf import FPDF
# -----------------------
# Authentication Section
# -----------------------
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

# (No lengthy explanation text here; it is moved to Documentation)

st.header("Input Parameters")

# Overall standard selection
standard = st.selectbox(
    "Select the Standard",
    ["IStructE Structural Use of Glass in Buildings", "EN 16612"],
)

with st.expander("Help?"):
    st.markdown(
        "TT suggests limiting the standard EN 16612 for calculating the lateral load resistance of linearly supported glazed elements used as infill panels in a class of consequences lower than those covered in EN 1990. Thus, for all the structural glazing elements (such as floor plate, wall, beams, columns, or glass panel with point fixing), it is recommended the use of the IStructE Book."
        "Please, choose between EN-16612 & IStructE Book and not the DIN 18008, as not contemplated in the UK codes of practise."
    )

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

fbk_choice = st.selectbox("Characteristic bending strength $$f_{b;k}$$", list(fbk_options.keys()))

with st.expander("Help?"):
    st.markdown(
        "Note 1: **Prestressed glass** is the general term used for glass which has been subjected to a strengthening treatment, by heat or chemicals (e.g. heat strengthened, heat toughened, chemically toughened glass).\n\n"
        "Note 2: **Patterned glass** is glass that has passed through rollers to give it surface texture.\n\n"
        "Note 3: **Enamelled glass** is the same as fritted glass. It is glass which has a ceramic frit applied to the surface, by e.g. painting or screen printing, which is subsequently fired into the surface."
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
ke_choice = st.selectbox("Edge strength factor $$k_{e}$$", list(ke_options.keys()))
ke_value = ke_options[ke_choice]

with st.expander("Help?"):
    st.markdown(
        "Note 7: According to EN 16612 - Where glass edges are not stressed in bending (e.g. a pane with all edges supported) **ke = 1**. "
        "If glass edges are stressed in bending (e.g. a pane with two opposite edges supported or with three edges supported), **ke** can be lower than 1.0.\n\n"
        "Note 8: EN 16612 only applies edge strength factor to annealed glass and not to prestressed glass. "
        "IStructE applies edge strength factor to both annealed and prestressed glass.\n\n"
        "Note 9: Seamed edges are arrissed or ground edges by machine or by hand where the abrasive action is along the length of the edge."
    )

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
    options=list(kmod_options.keys())
)
with st.expander("Help?"):
    st.markdown(
        "Note 4: Values in Table \"4. Factor for load duration\" in this sheet are from IStructE. Similar values are found in BS 16612. "
        "Generally, for t being the load duration in hours, **kmod = 0.663t^-1/16**.\n\n"
        "Note 5: The value of **kmod = 0.74** is based on a cumulative equivalent duration of 10 min, considered representative of the effect of a storm which may last several hours. "
        "Higher values of **kmod** can be considered for wind, but need to be justified (currently there is no guide for this).\n\n"
        "Note 6: According to EN 16612 - Where loads with different durations need to be treated in combination, the proposed **kmod** for the load combination is the highest value, "
        "which is associated with any of the loads in the combination.\n\n"
        "How to select the right **kmod**? By choosing the highest **kmod** value for determining the glass resistance. "
        "However, all load combinations should be considered; for example, for wind, snow and self-weight: "
        "**kmod = 0.74 (or 1)** for wind, snow and self-weight; **kmod = 0.48** for snow and self-weight; **kmod = 0.29** for self-weight."
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

def generate_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_left_margin(15)
    pdf.set_right_margin(15)
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Add custom fonts.
    pdf.add_font("SourceSansProBlack", "", "fonts/SourceSansPro-Black.ttf", uni=True)
    pdf.add_font("SourceSansPro", "", "fonts/SourceSansPro-Regular.ttf", uni=True)
    pdf.add_font("SourceSansPro", "B", "fonts/SourceSansPro-Bold.ttf", uni=True)
    
    # Calculate available width (for A4, ~180 mm available).
    avail_width = pdf.w - pdf.l_margin - pdf.r_margin
    
    # ---------------------------
    # Title and Summary Section
    # ---------------------------
    pdf.set_font("SourceSansProBlack", "", 18)
    pdf.cell(0, 10, "Glass Stress Calculation Summary", ln=True, align="C")
    pdf.ln(5)
    
    # Helper function to write a key-value pair (with wrapping if necessary)
    def write_key_value(key, value):
        label_width = avail_width * 0.35  # 35% for the label
        pdf.set_font("SourceSansPro", "B", 4)
        pdf.cell(label_width, 10, key, ln=0)
        pdf.set_font("SourceSansPro", "", 4)
        pdf.multi_cell(0, 10, value)
    
    write_key_value("Standard Used:", standard)
    pdf.ln(2)
    
    pdf.set_font("SourceSansProBlack", "", 14)
    pdf.cell(0, 10, "Input Parameters:", ln=True)
    pdf.ln(2)
    
    write_key_value("Characteristic Bending Strength:", 
                    f"{fbk_choice} (Value: {fbk_value} N/mm2, Category: {glass_category})")
    write_key_value("Glass Surface Profile Factor:", f"{ksp_choice} (Value: {ksp_value})")
    write_key_value("Surface Finish Factor:", f"{ksp_prime_choice} (Value: {ksp_prime_value})")
    write_key_value("Strengthening Factor:", f"{kv_choice} (Value: {kv_value})")
    write_key_value("Edge Strength Factor:", f"{ke_choice} (Value: {ke_value})")
    write_key_value("Design Value for Glass:", f"{f_gk_value} N/mm2")
    
    if glass_category == "annealed":
        write_key_value("Material Partial Safety Factor:", f"gamma_M_A = {gamma_MA}")
    else:
        write_key_value("Material Partial Safety Factor:", f"gamma_M_A = {gamma_MA}, gamma_M_V = {gamma_MV}")
    pdf.ln(3)
    
    pdf.set_font("SourceSansProBlack", "", 14)
    pdf.cell(0, 10, "Calculation Equation:", ln=True)
    pdf.ln(2)
    
    pdf.set_font("SourceSansPro", "", 4)
    if glass_category == "annealed":
        equation_text = "f_g_d = (k_e * k_mod * k_sp * f_g_k) / gamma_M_A"
    else:
        if "EN" in standard:
            equation_text = "f_g_d = (k_e * k_mod * k_sp * f_g_k) / gamma_M_A + (k_v * (f_b_k - f_g_k)) / gamma_M_V"
        else:
            equation_text = "f_g_d = ((k_mod * k_sp * f_g_k) / gamma_M_A + (k_v * (f_b_k - f_g_k)) / gamma_M_V) * k_e"
    pdf.multi_cell(0, 10, equation_text)
    pdf.ln(5)
    
    # -------------------------------------------
    # Design Stress Results Table for Load Durations
    # -------------------------------------------
    pdf.set_font("SourceSansProBlack", "", 14)
    pdf.cell(0, 10, "Design Stress Results:", ln=True)
    pdf.ln(2)
    
    # Define column widths: 50% for Load Type, 20% for k_mod, 30% for f_g;d.
    w1 = avail_width * 0.5
    w2 = avail_width * 0.2
    w3 = avail_width * 0.3
    
    # Table Header.
    pdf.set_font("SourceSansPro", "B", 4)
    pdf.cell(w1, 10, "Load Type", border=1, align="C")
    pdf.cell(w2, 10, "k_mod", border=1, align="C")
    pdf.cell(w3, 10, "f_g;d (MPa)", border=1, align="C", ln=True)
    
    # Set a smaller font for table rows.
    pdf.set_font("SourceSansPro", "", 4)
    
    # Loop through each load duration option.
    for load_type, kmod_value in kmod_options.items():
        if glass_category == "annealed":
            f_gd = (ke_value * kmod_value * ksp_value * ksp_prime_value * f_gk_value) / gamma_MA
        else:
            if standard == "EN 16612":
                f_gd = ((ke_value * kmod_value * ksp_value * ksp_prime_value * f_gk_value) / gamma_MA) + ((kv_value * (fbk_value - f_gk_value)) / gamma_MV)
            else:
                f_gd = (((kmod_value * ksp_value * ksp_prime_value * f_gk_value) / gamma_MA) + ((kv_value * (fbk_value - f_gk_value)) / gamma_MV)) * ke_value
        
        # Highlight the row if this load type is among those selected by the user.
        fill = False
        if load_type in selected_loads:
            pdf.set_fill_color(235, 140, 113)
            fill = True
        
        # Use multi_cell for each cell to wrap text if needed.
        pdf.cell(w1, 10, load_type, border=1, align="C", fill=fill)
        pdf.cell(w2, 10, f"{kmod_value:.2f}", border=1, align="C", fill=fill)
        pdf.cell(w3, 10, f"{f_gd:.2f}", border=1, align="C", fill=fill, ln=True)
    
    pdf_content = pdf.output(dest="S")
    if isinstance(pdf_content, str):
        pdf_bytes = pdf_content.encode("latin1")
    else:
        pdf_bytes = bytes(pdf_content)
    return pdf_bytes

st.title("Glass Calculation Report Generator")

if st.button("Save Report as PDF"):
    pdf_bytes = generate_pdf()
    st.download_button(
        label="Download Glass_Calculation_Report.pdf",
        data=pdf_bytes,
        file_name="Glass_Calculation_Report.pdf",
        mime="application/pdf"
    )
