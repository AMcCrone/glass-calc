Glass Design Tool
The Glass Design Tool is a Streamlit-based application that calculates the design strength of glass based on various standards and input parameters. The project is structured in a modular way to facilitate maintainability, testing, and collaboration on GitHub.

Repository Structure
graphql
Copy
Edit
glass_design_tool/
├── main.py               # Entry point for the application
├── auth.py               # Handles authentication and password verification
├── config.py             # Central configuration file for constants and design options
├── calculator/           # Contains modules related to glass design calculations and PDF generation
│   ├── __init__.py       
│   ├── design_calculator.py  # Renders the calculator UI and performs design strength calculations
│   └── pdf_generator.py      # Generates PDF reports using ReportLab
├── dashboard/            # Contains modules for dashboard views and visualizations
│   ├── __init__.py       
│   ├── summary_dashboard.py  # Displays current design parameters and gauge charts
│   ├── interlayer_3d_plot.py # Visualizes interlayer modulus data as a 3D plot
│   └── interlayer_comparison.py # Provides interlayer comparison charts and data tables
├── docs/                # Contains documentation modules
│   ├── __init__.py       
│   └── documentation.py   # Renders calculation details, parameter definitions, and notes
├── utils/               # Utility functions and helper modules
│   ├── __init__.py       
│   └── helpers.py         # Provides common helper functions (e.g., dataframe styling, sidebar navigation)
└── data/                # Contains data assets used by the application
    └── Interlayer_E(t)_Database.xlsx  # Excel file with interlayer data
Getting Started
Prerequisites
Python 3.8+
Streamlit
Pandas
Plotly
ReportLab
Install the required dependencies with:

bash
Copy
Edit
pip install streamlit pandas plotly reportlab
Running the Application
From the root directory of the repository, run:

bash
Copy
Edit
streamlit run main.py
This will start the app and open it in your default browser.

Application Overview
Authentication:
The app uses a basic password protection mechanism defined in config.py and implemented in auth.py.

Glass Design Calculator:
The main calculation logic is found in calculator/design_calculator.py. It collects user inputs, computes design strengths for various load durations based on the selected parameters, and displays the results.

Dashboard:
Various dashboard components are provided under the dashboard/ directory:

Summary Dashboard: Displays current design parameters and visualizations.
Interlayer 3D Plot: Shows a 3D scatter plot of interlayer modulus data.
Interlayer Comparison: Compares different interlayer options based on selected conditions.
Documentation:
Detailed calculation formulas, parameter definitions, and usage notes are available in docs/documentation.py.

PDF Report Generation:
The module calculator/pdf_generator.py allows users to generate and download a PDF report of their calculations.

Utilities:
Shared helper functions, such as dataframe styling and sidebar navigation, are stored in utils/helpers.py.

Contributing
Contributions are welcome! Please fork the repository, create your feature branch, and submit a pull request with detailed explanations of your changes.

License
This project is licensed under the MIT License.

Acknowledgments
Thanks to Streamlit for the amazing app framework.
Special thanks to ReportLab for PDF generation.
This project is based on design principles from IStructE and EN 16612 standards.
