# config.py
# Common time definitions
time_list = [
    ("1 sec", 1),
    ("3 sec", 3),
    ("5 sec", 5),
    ("10 sec", 10),
    ("30 sec", 30),
    ("1 min", 60),
    # ... add other options
]
time_map = {label: seconds for label, seconds in time_list}
tickvals = [seconds for label, seconds in time_list]
ticktext = [label for label, seconds in time_list]

# Options dictionaries for glass design
fbk_options = {
    "Annealed (EN-572-1, 45 N/mm²)": {"value": 45, "category": "annealed"},
    "Heat strengthened (EN 1863-1, 70 N/mm²)": {"value": 70, "category": "prestressed"},
    # ... other options
}
ksp_options = {
    "Float glass": 1.0,
    "Patterned glass": 0.75,
    # ...
}
# Define other options: ksp_prime_options, kv_options, ke_options, kmod_options, etc.
