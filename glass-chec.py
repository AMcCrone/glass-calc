import streamlit as st
import pandas as pd

st.title("Glass Design Strength Calculator")
st.markdown(
    r"""
This app calculates the design strength of glass based on two standards:
- **EN 16612**
- **IStructE Structural Use of Glass in Buildings**

The design strength is calculated using one of four equations depending on whether the glass is annealed (basic) or not, and on the selected standard.

For **annealed glass** (basic):
$$
f_{gd} = \frac{k_e \, k_{mod} \, k_{sp} \, f_{gk}}{\gamma_{ma}}
$$

For **all but annealed glass**:
- **EN 16612:**
$$
f_{gd} = \frac{k_e \, k_{mod} \, k_{sp} \, f_{gk}}{\gamma_{ma}} + \frac{k_v \,(f_{bk} - f_{gk})}{\gamma_{mv}}
$$
- **IStructE:**
$$
f_{gd} = \left(\frac{k_{mod} \, k_{sp} \, f_{gk}}{\gamma_{ma}} + \frac{k_v \,(f_{bk} - f_{gk})}{\gamma_{mv}}\right) k_e
$$

where:
- $$ f_{bk} $$ is the characteristic bending strength (N/mm²),
- $$ k_{sp} $$ is the glass surface profile factor,
- $$ k'_{sp} $$ is the surface finish factor (**None** = 1, **Sand blasted** = 0.6, **Acid etched** = 1) – (this parameter is now separate from \( k_{sp} \)),
- $$ k_v $$ is the strengthening factor,
- $$ k_e $$ is the edge strength factor,
- $$ k_{mod} $$ is the load duration factor,
- $$ f_{gk} $$ is the design value for glass,
- For annealed glass:
  - IStructE: $$ \gamma_{ma} = 1.6 $$  
  - EN 16612: $$ \gamma_{ma} = 1.8 $$
- For surface prestressed (non-annealed) glass:
  - $$ \gamma_{mv} = 1.2 $$.

*Note: Adjust any factors or assumptions (such as the default value for $$ f_{gk} $$ for non-annealed glass) as necessary to match your detailed model.*
    """,
    unsafe_allow_html=True,
)

# Overall standard selection
standard = st.selectbox(
    "Select the Standard",
    ["IStructE Structural Use of Glass in Buildings", "EN 16612"],
)

st.header("Input Parameters")

# 1. Characteristic bending strength (f₍bk₎)
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
fbk_choice = st.selectbox("Characteristic bending strength $$f_{bk}$$", list(fbk_options.keys()))
fbk_value = fbk_options[fbk_choice]["value"]
glass_category = fbk_options[fbk_choice]["category"]

# 2. Glass surface profile factor (k₍sp₎) – excluding finish options
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

# 3. Surface finish factor (k'₍sp₎) – new parameter with only three options.
# (Note: This parameter is not used in the new design strength equations.)
ksp_prime_options = {
    "None": 1.0,
    "Sand blasted": 0.6,
    "Acid etched": 1.0,
}
ksp_prime_choice = st.selectbox("Surface finish factor $$k'_{sp}$$", list(ksp_prime_options.keys()))
ksp_prime_value = ksp_prime_options[ksp_prime_choice]

# 4. Strengthening factor (k₍v₎)
kv_options = {
    "Horizontal toughening": 1.0,
    "Vertical toughening": 0.6,
}
kv_choice = st.selectbox("Strengthening factor $$k_{v}$$", list(kv_options.keys()))
kv_value = kv_options[kv_choice]

# 5. Edge strength factor (k₍e₎)
ke_options = {
    "Edges not stressed in bending": 1.0,
    "Polished float edges": 1.0,
    "Seamed float edges": 0.9,
    "Other edge types": 0.8,
}
ke_choice = st.selectbox("Edge strength factor $$k_{e}$$", list(ke_options.keys()))
ke_value = ke_options[ke_choice]

# New input: Design value for glass, f_gk.
# For annealed glass, default is equal to f_bk.
# For non-annealed glass, an assumed default (e.g., 75% of f_bk) is provided.
if glass_category == "basic":
    default_fgk = fbk_value
else:
    default_fgk = fbk_value * 0.75  # You may adjust this default value as needed.
fgk_value = st.number_input("Enter design value for glass, $$f_{gk}$$ (N/mm²)", value=default_fgk, step=1.0)

# Define material partial safety factors:
# For annealed glass (basic):
if glass_category == "basic":
    gamma_ma = 1.6 if standard == "IStructE Structural Use of Glass in Buildings" else 1.8
    # gamma_mv is not used for annealed glass.
    gamma_mv = None
else:
    gamma_ma = 1.6 if standard == "IStructE Structural Use of Glass in Buildings" else 1.8
    gamma_mv = 1.2

st.markdown(f"**Selected material partial safety factor $$\\gamma_{ma if glass_category=='basic' else 'ma'}$$: {gamma_ma}**")
if gamma_mv:
    st.markdown(f"**Selected material partial safety factor $$\\gamma_{mv}$$: {gamma_mv}**")

# 6. Load duration factors (k₍mod₎) – full table of options
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
            fgd = (ke_value * kmod_value * ksp_value * fgk_value) / gamma_ma
        else:  # Non-annealed glass
            if standard == "EN 16612":
                fgd = ((ke_value * kmod_value * ksp_value * fgk_value) / gamma_ma) + ((kv_value * (fbk_value - fgk_value)) / gamma_mv)
            else:  # IStructE
                fgd = (((kmod_value * ksp_value * fgk_value) / gamma_ma) + ((kv_value * (fbk_value - fgk_value)) / gamma_mv)) * ke_value

        results.append({
            "Load Type": load_type,
            "k_mod": kmod_value,
            "Glass Design Strength (N/mm²)": f"{fgd:.2f}"
        })
        
    df_results = pd.DataFrame(results)
    st.table(df_results)
