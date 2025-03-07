import streamlit as st

st.title("Glass Design Strength Calculator")
st.markdown(
    """
This app calculates the design strength of glass based on two standards:
- **EN 16612**
- **IStructE Structural Use of Glass in Buildings**

The design strength is calculated using the following equation:

  **Design Strength = (f₍bk₎ × k₍sp₎ × k'₍sp₎ × k₍v₎ × k₍e₎ × k₍mod₎) / γ₍M₎**

Where:
- **f₍bk₎** is the characteristic bending strength (in N/mm²),
- **k₍sp₎** and **k'₍sp₎** are the glass surface profile factors,
- **k₍v₎** is the strengthening factor,
- **k₍mod₎** is the load duration factor,
- **k₍e₎** is the edge strength factor,
- **γ₍M₎** is the material partial safety factor.

For the material partial safety factor:
- For **basic annealed glass**:
  - IStructE: γ₍M₎ = 1.6  
  - EN 16612: γ₍M₎ = 1.8
- For **surface prestressed glass** (all other types):
  - Both IStructE and EN 16612: γ₍M₎ = 1.2

*Note: The factors below are taken from the provided data sets.*
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
fbk_choice = st.selectbox("Characteristic bending strength (f₍bk₎)", list(fbk_options.keys()))
fbk_value = fbk_options[fbk_choice]["value"]
glass_category = fbk_options[fbk_choice]["category"]

# 2. Glass surface profile factor (k₍sp₎)
ksp_options = {
    "Float glass": 1.0,
    "Drawn sheet glass": 1.0,
    "Enamelled float or drawn sheet glass": 1.0,
    "Patterned glass": 0.75,
    "Enamelled patterned glass": 0.75,
    "Polished wired glass": 0.75,
    "Patterned wired glass": 0.6,
    "None": 1.0,
    "Sandblasted": 0.6,
    "Acid etched": 1.0,
}
ksp_choice = st.selectbox("Glass surface profile factor (k₍sp₎)", list(ksp_options.keys()))
ksp_value = ksp_options[ksp_choice]

# 2 (again) for k'₍sp₎: using the same options
ksp2_choice = st.selectbox("Glass surface profile factor (k'₍sp₎)", list(ksp_options.keys()))
ksp2_value = ksp_options[ksp2_choice]

# 3. Strengthening factor (k₍v₎)
kv_options = {
    "Horizontal toughening": 1.0,
    "Vertical toughening": 0.6,
}
kv_choice = st.selectbox("Strengthening factor (k₍v₎)", list(kv_options.keys()))
kv_value = kv_options[kv_choice]

# 4. Load duration factor (k₍mod₎)
kmod_options = {
    "5 seconds – Single gust (Blast Load)": 1.00,
    "30 seconds – Domestic balustrade (Barrier load, domestic)": 0.89,
    "5 minutes – Workplace/public balustrade (Barrier load, public)": 0.77,
    "10 minutes – Multiple gust (storm) (Wind Load)": 0.74,
    "30 minutes – Maintenance access": 0.69,
    "5 hours – Pedestrian access": 0.60,
    "1 week – Snow short term": 0.48,
    "1 month – Snow medium term": 0.44,
    "3 months – Snow long term": 0.41,
    "50 years – Permanent": 0.29,
}
kmod_choice = st.selectbox("Load duration factor (k₍mod₎)", list(kmod_options.keys()))
kmod_value = kmod_options[kmod_choice]

# 5. Edge strength factor (k₍e₎)
ke_options = {
    "Edges not stressed in bending": 1.0,
    "Polished float edges": 1.0,
    "Seamed float edges": 0.9,
    "Other edge types": 0.8,
}
ke_choice = st.selectbox("Edge strength factor (k₍e₎)", list(ke_options.keys()))
ke_value = ke_options[ke_choice]

# 6 & 7. Material partial safety factor (γ₍M₎)
# Determine based on glass type (from f₍bk₎) and standard selection:
if glass_category == "basic":
    gamma_M = 1.6 if standard == "IStructE Structural Use of Glass in Buildings" else 1.8
else:
    gamma_M = 1.2

st.markdown(f"**Selected material partial safety factor (γ₍M₎): {gamma_M}**")

# Calculation (example equation)
if st.button("Calculate Design Strength"):
    # Equation:
    # Design Strength = (f_bk * k_sp * k'_sp * k_v * k_e * k_mod) / γ_M
    design_strength = (fbk_value * ksp_value * ksp2_value * kv_value * ke_value * kmod_value) / gamma_M
    st.markdown(f"### Design Strength: **{design_strength:.2f} N/mm²**")
