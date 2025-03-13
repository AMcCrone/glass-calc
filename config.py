# config.py
"""
Configuration file for the Glass Design Tool.

This module contains constants and option dictionaries used in the app,
including authentication settings, time duration mappings, and design
parameters for the glass strength calculations.
"""

# -----------------------------
# Time Duration Mappings
# -----------------------------
# Each tuple contains a label and its equivalent in seconds.
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

# Mapping labels to seconds and other plotting definitions
time_map = {label: seconds for label, seconds in time_list}
tickvals = [seconds for label, seconds in time_list]
ticktext = [label for label, seconds in time_list]

# -----------------------------
# Glass Design Options
# -----------------------------

# Characteristic bending strength options (f_b;k)
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

# Glass surface profile factor options (k_sp)
ksp_options = {
    "Float glass": 1.0,
    "Drawn sheet glass": 1.0,
    "Enamelled float or drawn sheet glass": 1.0,
    "Patterned glass": 0.75,
    "Enamelled patterned glass": 0.75,
    "Polished wired glass": 0.75,
    "Patterned wired glass": 0.6,
}

# Surface finish factor options (k'_sp)
ksp_prime_options = {
    "None": 1.0,
    "Sand blasted": 0.6,
    "Acid etched": 1.0,
}

# Strengthening factor options (k_v)
kv_options = {
    "Horizontal toughening": 1.0,
    "Vertical toughening": 0.6,
}

# Edge strength factor options (k_e)
ke_options = {
    "Edges not stressed in bending": 1.0,
    "Polished float edges": 1.0,
    "Seamed float edges": 0.9,
    "Other edge types": 0.8,
}

# Fixed design value for glass (f_g;k)
f_gk_value = 45  # N/mm²

# Load duration factor options (k_mod)
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
