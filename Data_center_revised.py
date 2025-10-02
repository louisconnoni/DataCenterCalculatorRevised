import streamlit as st
import pandas as pd

# -------------------------------
# Load and prepare dataset
# -------------------------------
@st.cache_data
def load_data():
    # Use header=2 so row 3 becomes the column headers
    df = pd.read_csv("DATACENTER.csv", header=2, encoding="latin1")

    # Rename useful columns (adjust names if they differ slightly in your CSV)
    df = df.rename(columns={
        "County FIPS": "FIPS",
        "EF": "EF",      # kg CO2e/kWh
        "ACF": "ACF",    # Available Water Remaining
        "SWI": "SWI",    # Scarce Water Index (L/kWh)
        "EWIF": "EWIF",  # External Water Impact Factor (from column C)
        df.columns[9]: "CountyState"
    })

    # Split CountyState ("County, State") into separate fields
    df[["County", "State"]] = df["CountyState"].str.split(",", n=1, expand=True)
    df["County"] = df["County"].str.strip()
    df["State"] = df["State"].str.strip()

    return df

df = load_data()

# -------------------------------
# Title and Intro
# -------------------------------
st.title("County Efficiency Calculator")
st.write("This app calculates **CUE**, **WSUE**, and **WUEsource** based on county FIPS, PUE, and WUE.")

# -------------------------------
# Dropdowns for State & County
# -------------------------------
states = sorted(df["State"].dropna().unique())
selected_state = st.selectbox("Select a State:", states)

counties = df[df["State"] == selected_state]["County"].dropna().sort_values().unique()
selected_county = st.selectbox("Select a County:", counties)

# Lookup row for selected county
filtered = df[(df["State"] == selected_state) & (df["County"] == selected_county)]

if filtered.empty:
    st.error("No data found for the selected state and county. Please check your CSV formatting.")
else:
    row = filtered.iloc[0]

    fips_code = row["FIPS"]
    ef_value = row["EF"]
    acf_value = row["ACF"]
    swi_value = row["SWI"]
    ewif_value = row["EWIF"]

    st.write(f"**FIPS Code:** {fips_code}")
    st.write(f"**EF (Emission Factor):** {ef_value} kg CO₂e/kWh")
    st.write(f"**ACF (Available Water Remaining):** {acf_value}")
    st.write(f"**SWI (Scarce Water Index):** {swi_value} L/kWh")
    st.write(f"**EWIF (External Water Impact Factor):** {ewif_value} L/kWh")

# -------------------------------
# Input Section
# -------------------------------
pue = st.number_input("Enter PUE (Power Usage Effectiveness):", min_value=0.0, step=0.01)
wue = st.number_input("Enter WUE (Water Usage Effectiveness) [L/kWh]:", min_value=0.0, step=0.01)

# -------------------------------
# Calculation
# -------------------------------
if st.button("Run Calculation"):
    cue = pue * ef_value                           # kg CO2e/kWh
    wsue = acf_value * wue + swi_value * pue       # L/kWh
    wuesource = wue + (ewif_value * pue)           # L/kWh

    st.success(f"CUE = {cue:.3f} kg CO₂e/kWh")
    st.success(f"WSUE = {wsue:.3f} L/kWh")
    st.success(f"WUEsource = {wuesource:.3f} L/kWh")
