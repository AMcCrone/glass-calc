"""
calculator/design_calculator.py

This module renders the Glass Design Strength Calculator UI and computes
the design strength (f₍g;d₎) for different load durations based on user inputs.
"""

import streamlit as st
import pandas as pd
from config import (
    fbk_options,
    ksp_options,
    ksp_prime_options,
    kv_options,
    ke_options,
    f_gk_value,
    kmod_options
)
from utils.helpers import style_load_row

def render_calculator():
    """Render the Glass Design Strength Calculator interface and compute results."""
    st.markdown("<a name='glass-design-strength-calculator'></a>", unsafe_allow_html=True)
    st.title("Glass Design Strength Calculator")
    st.markdown("Precision engineering for glass structural design")

    # Standard Comparison Dropdown
    with st.expander("Which standard to use and their differences", expanded=False):
        st.markdown(
            r"""
**Standard Selection Guidance:**
Technical Recommendation (TT) suggests limiting the EN 16612 standard for calculating the lateral load resistance of linearly supported glazed elements used as infill panels in a class of consequences lower than those covered in EN 1990. 

**Recommended Usage:**
- For all structural glazing elements (floor plates, walls, beams, columns, or glass panels with point fixings), use the **IStructE Book** standard.
- EN 16612 is more suitable for simpler, non-critical glazing applications.

**Calculation Equations:**
For **annealed glass**:  
$$
f_{g;d} = \frac{k_e \; k_{mod} \; k_{sp} \; f_{g;k}}{\gamma_{M;A}}
$$
For **pre-stressed glass (EN 16612)**:  
$$
f_{g;d} = \frac{k_e \; k_{mod} \; k_{sp} \; f_{g;k}}{\gamma_{M;A}} + \frac{k_v \,(f_{b;k} - f_{g;k})}{\gamma_{M;v}}
$$
For **pre-stressed glass (IStructE)**:  
$$
f_{g;d} = \left(\frac{k_{mod} \; k_{sp} \; f_{g;k}}{\gamma_{M;A}} + \frac{k_v \,(f_{b;k} - f_{g;k})}{\gamma_{M;v}}\right) k_e
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
  - **IStructE**: $$ \gamma_{M;A} = 1.6 $$  
  - **EN 16612**: $$ \gamma_{M;A} = 1.8 $$
  
- For pre-stressed (non-annealed) glass:  
  - $$ \gamma_{M;A} $$ as above and $$ \gamma_{M;v} = 1.2 $$
            """
        )

    # --- Standard Selection ---
    standard = st.selectbox(
        "Select the Standard",
        ["EN 16612", "IStructE Structural Use of Glass in Buildings"],
        help="""
        Choose the design standard for your glass structure:
        - EN 16612: European standard for glass in construction
        - IStructE: Institution of Structural Engineers' guidance for glass design
        Refer to the 'Which standard to use and their differences' dropdown for detailed guidance.
        """
    )
    # Save to session state
    st.session_state["standard"] = standard

    # --- Input Parameters ---
    st.subheader("Input Parameters")

    # 1. Characteristic bending strength (f_{b;k})
    fbk_choice = st.selectbox(
        "Characteristic bending strength $$f_{b;k}$$",
        list(fbk_options.keys()),
        help="""
        Characteristic bending strength represents the inherent strength of the glass:
        - Depends on glass type (annealed, heat-strengthened, fully tempered)
        - Typically ranges from 35-120 MPa
        - Higher values indicate greater resistance to bending stress
        """
    )
    # Save to session state
    st.session_state["fbk_choice"] = fbk_choice
    
    fbk_value = fbk_options[fbk_choice]["value"]
    glass_category = fbk_options[fbk_choice]["category"]

    # 2. Glass surface profile factor (k_{sp})
    ksp_choice = st.selectbox(
        "Glass surface profile factor $$k_{sp}$$",
        list(ksp_options.keys()),
        help="""
        Surface profile factor accounts for glass surface characteristics:
        - Reflects the impact of surface processing on strength
        - Values typically range from 0.5 to 1.0
        - Heat treatment and surface conditions affect this factor
        """
    )
    # Save to session state
    st.session_state["ksp_choice"] = ksp_choice
    
    ksp_value = ksp_options[ksp_choice]

    # 3. Surface finish factor (k'_{sp})
    ksp_prime_choice = st.selectbox(
        "Surface finish factor $$k'_{sp}$$",
        list(ksp_prime_options.keys()),
        help="""
        Surface finish factor is a multiplier applied to k_sp:
        - Accounts for additional surface treatments
        - Modifies the base surface profile factor
        - Typically ranges from 0.8 to 1.0
        - Represents refinements in surface processing
        """
    )
    # Save to session state
    st.session_state["ksp_prime_choice"] = ksp_prime_choice
    
    ksp_prime_value = ksp_prime_options[ksp_prime_choice]

    # 4. Strengthening factor (k_{v})
    kv_choice = st.selectbox(
        "Strengthening factor $$k_{v}$$",
        list(kv_options.keys()),
        help="""
        Strengthening factor considers additional strengthening effects:
        - Relevant for prestressed or heat-treated glass
        - Accounts for residual stress and strengthening techniques
        - Typically used for non-annealed glass types
        """
    )
    # Save to session state
    st.session_state["kv_choice"] = kv_choice
    
    kv_value = kv_options[kv_choice]

    # 5. Edge strength factor (k_{e})
    ke_choice = st.selectbox(
        "Edge strength factor $$k_{e}$$",
        list(ke_options.keys()),
        help="""
        Edge strength factor considers glass edge conditions:
        - Accounts for support and edge processing
        - Reflects potential stress concentrations at glass edges
        - Impacts overall structural performance
        """
    )
    # Save to session state
    st.session_state["ke_choice"] = ke_choice
    
    ke_value = ke_options[ke_choice]

    # k_mod Clarification Expander
    with st.expander("k_mod Clarification", expanded=False):
        st.markdown(r"""
        **Load Duration Factor (k_mod) Detailed Explanation**
        
        **Note 4: Load Duration Factor Origins**
        - Values in Table "4. Factor for load duration" are from IStructE
        - Similar values found in BS 16612
        - General formula for load duration factor:
        
        $$k_{mod} = 0.663 \cdot t^{-1/16}$$
        
        Where:
        - $t$ is the load duration in hours
        
        **Note 5: Storm Condition Reference**
        - The value $k_{mod} = 0.74$ is based on a cumulative equivalent duration of 10 minutes
        - Considered representative of a storm effect lasting several hours
        - Higher $k_{mod}$ values for wind can be considered but must be justified
        - *Currently, no definitive guide exists for such modifications*
        
        **Note 6: Load Combination Considerations (EN 16612)**
        - For loads with different durations, use the **highest** $k_{mod}$ value
        - Selection process for $k_{mod}$:
          1. Identify $k_{mod}$ for each load type
          2. Choose the highest value for determining glass resistance
        
        **Example Load Combinations:**
        - Wind, snow, and self-weight:
          - $k_{mod} = 0.74$ (or 1.0) for combined scenario
        - Snow and self-weight:
          - $k_{mod} = 0.48$
        - Self-weight only:
          - $k_{mod} = 0.29$
        
        **Important Considerations:**
        - Always consider all potential load combinations
        - The highest $k_{mod}$ represents the most critical loading condition
        """)

    # Determine material partial safety factors based on glass type and standard.
    if glass_category == "annealed":
        gamma_MA = 1.6 if standard == "IStructE Structural Use of Glass in Buildings" else 1.8
        gamma_MV = None
    else:
        gamma_MA = 1.6 if standard == "IStructE Structural Use of Glass in Buildings" else 1.8
        gamma_MV = 1.2

    # --- Calculation of Design Strength ---
    st.subheader("Design Strength Calculation")
    results = []
    for load_type, kmod_value in kmod_options.items():
        if glass_category == "annealed":
            # For annealed glass:
            f_gd = (ke_value * kmod_value * ksp_value * ksp_prime_value * f_gk_value) / gamma_MA
        else:
            # For prestressed (non-annealed) glass:
            if standard == "EN 16612":
                f_gd = ((ke_value * kmod_value * ksp_value * ksp_prime_value * f_gk_value) / gamma_MA) + (
                    (kv_value * (fbk_value - f_gk_value)) / gamma_MV
                )
            else:  # IStructE standard
                f_gd = (((kmod_value * ksp_value * ksp_prime_value * f_gk_value) / gamma_MA) + (
                    (kv_value * (fbk_value - f_gk_value)) / gamma_MV
                )) * ke_value

        results.append({
            "Load Type": load_type,
            "k_mod": f"{kmod_value:.2f}",
            "fg;d (MPa)": f"{f_gd:.2f}"
        })

    df_results = pd.DataFrame(results)
    # Ensure the design strength column is numeric
    strength_col = "fg;d (MPa)"
    df_results[strength_col] = pd.to_numeric(df_results[strength_col], errors='coerce')
    
    # Save results and strength column to session state
    st.session_state["df_results"] = df_results
    st.session_state["strength_col"] = strength_col

    # --- Highlighting Selected Load Durations ---
    selected_loads = st.multiselect(
        "Select load durations to highlight",
        options=list(kmod_options.keys()),
        help="""
        Choose specific load durations to emphasize in the results:
        - Allows focused analysis of different loading scenarios
        - Helps compare design strengths under various conditions
        """
    )
    # Store selected loads in session state for styling
    st.session_state["selected_loads"] = selected_loads

    # Style the DataFrame to highlight selected rows using our helper function.
    df_styled = df_results.style.apply(style_load_row, axis=1)

    st.subheader("Design Strength Results")
    st.dataframe(df_styled.hide(axis="index"), use_container_width=True)
