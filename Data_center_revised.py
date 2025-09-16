import streamlit as st
import pandas as pd

# -------------------------------
# Load and prepare dataset
# -------------------------------
@st.cache_data
def load_data():
    # Skip the first 3 metadata rows
    df = pd.read_csv("DATACENTER.csv", skiprows=3, encoding="latin1")

    # Rename useful columns
    df = df.rename(columns={
        df.columns[0]: "FIPS",
        df.columns[3]: "EF",   # kg CO2e/kWh
        df.columns[4]: "ACF",  # unitless fraction
        df.columns[5]: "SWI",  # L/kWh
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
st.write("This app calculates **CUE** and **WSUE** based on county FIPS, PUE, and WUE.")

# -------------------------------
# Dropdowns for State & County
# -------------------------------
states = sorted(df["State"].unique())
selected_state = st.selectbox("Select a State:", states)

counties = df[df["State"] == selected_state]["County"].sort_values().unique()
selected_county = st.selectbox("Select a County:", counties)

# Lookup row for selected county
row = df[(df["State"] == selected_state) & (df["County"] == selected_county)].iloc[0]

fips_code = row["FIPS"]
ef_value = row["EF"]
acf_value = row["ACF"]
swi_value = row["SWI"]

st.write(f"**FIPS Code:** {fips_code}")
st.write(f"**EF (Emission Factor):** {ef_value} kg CO₂e/kWh")
st.write(f"**ACF (Adjustment Coefficient):** {acf_value} (unitless)")
st.write(f"**SWI (Source Water Intensity):** {swi_value} L/kWh")

# -------------------------------
# Input Section
# -------------------------------
pue = st.number_input("Enter PUE (Power Usage Effectiveness):", min_value=0.0, step=0.01)
wue = st.number_input("Enter WUE (Water Usage Effectiveness) [L/kWh]:", min_value=0.0, step=0.01)

# -------------------------------
# Calculation
# -------------------------------
if st.button("Run Calculation"):
    cue = pue * ef_value                      # kg CO2e/kWh
    wsue = acf_value * wue + swi_value * pue  # L/kWh

    st.success(f"CUE = {cue:.3f} kg CO₂e/kWh")
    st.success(f"WSUE = {wsue:.3f} L/kWh")

# -------------------------------
# Info Button
# -------------------------------
if st.button("More Information"):
    st.info("""
    **About this App**  
    - Select a **State** and **County** (FIPS code is automatically retrieved).  
    - Enter **PUE (Power Usage Effectiveness)** and **WUE (Water Usage Effectiveness, L/kWh)**.  
    - The app calculates:  
        - **CUE (kg CO₂e/kWh) = PUE × EF**  
        - **WSUE (L/kWh) = ACF × WUE + SWI × PUE**  
    - Units:  
        - EF, CUE → kg CO₂e/kWh  
        - WUE, SWI, WSUE → L/kWh  
        - ACF → unitless  
    """)
