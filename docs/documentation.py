"""
docs/documentation.py

This module renders the documentation section of the Glass Design Tool,
including calculation details, parameter definitions, and additional notes.
"""

import streamlit as st

def render_documentation():
    """Render the Documentation section for the Glass Design Tool."""
    st.markdown("<a name='documentation'></a>", unsafe_allow_html=True)
    st.title("Documentation")
    
    st.markdown(
        r"""
**Calculation Details:**

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

**Notes:**

- Ensure that the appropriate standard is selected for your design scenario.
- Validate input parameters to ensure realistic behavior under various load conditions.
- The formulas and parameters are based on the guidelines provided by IStructE and EN 16612.
- For detailed information on glass properties and structural design, consult the official documentation and standards.

For further assistance or to report issues, please refer to the project repository.
        """,
        unsafe_allow_html=True
    )
