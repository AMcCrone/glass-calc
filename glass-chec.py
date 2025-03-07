import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as go
# import matplotlib.pyplot as plt

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

# Overall standard selection
standard = st.selectbox(
    "Select the Standard",
    ["IStructE Structural Use of Glass in Buildings", "EN 16612"],
)

st.header("Input Parameters")

# 1. Characteristic bending strength (f_{b;k})
# Each entry has an associated glass category: "basic" means annealed, others are non-annealed.
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

# 2. Glass surface profile factor (k_{sp}) – excluding finish options
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

# 3. Surface finish factor (k'_{sp}) – new parameter with only three options.
# (Note: This parameter is not used in the new design strength equations.)
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

# Calculation for each load duration case:
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

    # # Plot a graph of loading duration vs. k_mod using the theoretical relation:
    # # k_mod = 0.663 * t^(-1/16)
    # # Here, t (loading duration) is plotted on the x-axis (in seconds).
    # t_values = np.logspace(0, np.log10(1.6e9), 200)  # from 1 second to ~50 years in seconds
    # k_mod_theoretical = 0.663 * t_values**(-1/16)

    # fig, ax = plt.subplots()
    # ax.plot(t_values, k_mod_theoretical, label=r"$k_{mod} = 0.663 \, t^{-1/16}$")
    # ax.set_xscale('log')
    # ax.set_xlabel("Loading Duration (s)")
    # ax.set_ylabel("$k_{mod}$")
    # ax.legend()
    # ax.grid(True, which="both", ls="--", lw=0.5)
    # st.pyplot(fig)


st.title("SentryGlas® Relaxation Modulus 3D Plot")

# -----------------------------------------------------
# 1) Define the time points in seconds (for log scale)
# -----------------------------------------------------
time_map = {
    "1 sec":      1,
    "3 sec":      3,
    "5 sec":      5,
    "10 sec":     10,
    "30 sec":     30,
    "1 min":      60,
    "5 min":      300,
    "10 min":     600,
    "30 min":     1800,
    "1 hour":     3600,
    "6 hours":    21600,
    "12 hours":   43200,
    "1 day":      86400,
    "2 days":     172800,
    "5 days":     432000,
    "1 week":     604800,
    "3 weeks":    1814400,
    "1 month":    2592000,   # ~30 days
    "1 year":     31536000,
    "10 years":   315360000,
    "50 years":   1576800000
}

# -----------------------------------------------------
# 2) Input data from your table
# -----------------------------------------------------
data = {
    "Temperature (°C)": [-20,   0,   10,  20,  25,  30,  35,   40,   50,   60,    70,    80],
    "1 sec":            [838, 749, 693, 629, 511, 443, 338,  229, 108.6, 35.4, 11.31,  4.65],
    "3 sec":            [835, 743, 681, 612, 485, 413, 302,  187,   78,  24.5,  8.8,   4.0],
    "5 sec":            [835, 740, 678, 606, 474, 405, 287,  167,  66.3, 20.67, 8.13,  3.66],
    "10 sec":           [832, 737, 664, 594, 456, 381, 266,  143, 166.5, 51.84, 22.05, 9.99],
    "30 sec":           [832, 732, 661, 602, 433, 349, 230,  109,   40,  12.8,  6.3,   2.9],
    "1 min":            [829, 726, 651, 567, 413, 324, 209, 91.6,  33.8, 10.9,  5.64,  2.5],
    "5 min":            [821, 717, 638, 549, 340, 243, 158,   57,  21.7,   7.6,  4.2,   1.7],
    "10 min":           [818, 714, 618, 525, 334, 220, 141, 46.9, 18.57,  6.75, 3.45,  1.35],
    "30 min":           [815, 708, 629, 511, 308, 194, 122,   34,  14.6,   5.5,  2.9,   1.1],
    "1 hour":           [809, 703, 597, 493, 294, 178, 103, 27.8,  12.6,   5.1,  2.5,   1.0],
    "6 hours":          [806, 680, 574, 458, 263, 162, 78.2,   17.1,  9.72,  4.26, 1.95, 0.9],
    "12 hours":         [804, 668, 560, 438, 250, 153, 68.4,   15,    8.94,  4.05, 1.89, 0.9],
    "1 day":            [801, 665, 553, 428, 234, 146, 60.1,   13.5,  8.4,   3.8,  1.8,  0.8],
    "2 days":           [798, 654, 543, 406, 206, 105, 48.9,   12.3,  8.01,  3.78, 1.74, 0.87],
    "5 days":           [795, 648, 516, 380, 177, 72,  36.7,   11,    7.2,   3.6,  1.6,  0.7],
    "1 week":           [795, 645, 519, 368, 160, 66,  33.8,   10.9,  7.26,  3.54, 1.62, 0.75],
    "3 weeks":          [792, 639, 498, 336, 131, 38,  24.6,   10,    6.5,   3.3,  1.5,  0.6],
    "1 month":          [786, 636, 499, 330, 123, 35,  22.1,   9.9,   6.5,   3.3,  1.5,  0.8],
    "1 year":           [772, 605, 467, 282, 93.3,20.3,14.7,   9.3,   6.3,   3,    1.4,  0.6],
    "10 years":         [749, 579, 448, 256, 70.6,15,  12.2,   8.84,  6,     2.9,  1.3,  0.5],
    "50 years":         [720, 559, 421, 223, 52.6,11.9, 9.03,  6.86,  5.46,  2.22, 1.05, 0.48]
}

df = pd.DataFrame(data)

# -----------------------------------------------------
# 3) Convert wide table into a "long" format
# -----------------------------------------------------
df_melted = df.melt(
    id_vars="Temperature (°C)",
    var_name="Time",
    value_name="E(MPa)"
)

# -----------------------------------------------------
# 4) Map time labels to numeric seconds for log scale
# -----------------------------------------------------
df_melted["Time_s"] = df_melted["Time"].map(time_map)

# -----------------------------------------------------
# 5) Create the 3D Plotly scatter
# -----------------------------------------------------
fig = go.Figure(data=[go.Scatter3d(
    x=df_melted["Time_s"],                 # X-axis: numeric time in seconds
    y=df_melted["Temperature (°C)"],       # Y-axis: temperature
    z=df_melted["E(MPa)"],                 # Z-axis: relaxation modulus
    mode='markers',
    marker=dict(
        size=5,
        color=df_melted["E(MPa)"],
        colorscale='Viridis',
        opacity=0.8
    )
)])

fig.update_layout(
    scene=dict(
        xaxis=dict(title='Time [s]', type='log'),       # log scale on x-axis
        yaxis=dict(title='Temperature [°C]'),
        zaxis=dict(title='E(t) [MPa]')
    ),
    margin=dict(l=0, r=0, b=0, t=0)
)

# -----------------------------------------------------
# 6) Display the plot in Streamlit
# -----------------------------------------------------
st.plotly_chart(fig, use_container_width=True)

