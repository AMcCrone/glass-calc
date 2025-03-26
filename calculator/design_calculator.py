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

    # --- Standard Selection ---
    standard = st.selectbox(
        "Select the Standard",
        ["EN 16612", "IStructE Structural Use of Glass in Buildings"],
        help="""
        Choose the design standard for your glass structure:
        - EN 16612: European standard for glass in construction
        - IStructE: Institution of Structural Engineers' guidance for glass design
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

    # Load Duration Factors (k_mod) Explanation
    st.info("""
    Load Duration Factors (k_mod) Notes:
    - Values represent modification factors for different load durations
    - Generally, k_mod = 0.663 * t^(-1/16), where t is load duration in hours
    - k_mod = 0.74 based on 10-minute cumulative equivalent duration (storm conditions)
    - For combined loads, use the highest k_mod value
    - Example: Wind (k_mod = 0.74), Snow and self-weight (k_mod = 0.48)
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

    # Additional explanation of design strength
    st.info("""
    Design Strength (fg;d) Explanation:
    - Calculated design strength considering multiple modification factors
    - Accounts for glass type, load duration, surface conditions, and support
    - Lower values indicate more conservative design
    - Helps ensure structural safety and performance
    """)
