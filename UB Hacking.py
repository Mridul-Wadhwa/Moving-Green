import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Load data
try:
    sec_data = pd.read_csv('data/State energy-related carbon dioxide emissions by sector.csv', header=3)
except FileNotFoundError:
    st.error("Sector data file not found.")
    st.stop()

# Fix col names and % values
sec_data.columns = sec_data.columns.str.replace(',', '').str.strip()
pct_cols = ['Commercial.1', 'Electric power.1', 'Residential.1', 'Industrial.1', 'Transportation.1']
for c in pct_cols:
    sec_data[c] = sec_data[c].replace({'%': ''}, regex=True).astype(float)

# Reshape data for sectors
sec_long = pd.melt(sec_data, id_vars=['State'], value_vars=['Commercial', 'Electric power', 'Residential', 'Industrial', 'Transportation'], var_name='Sector', value_name='Emissions')

# Select sector
sec = st.selectbox("Select a sector", options=['Commercial', 'Electric power', 'Residential', 'Industrial', 'Transportation'])

# Filtered map data
sec_filt = sec_long[sec_long['Sector'] == sec]
sec_map = px.choropleth(sec_filt, locations='State', locationmode="USA-states", color='Emissions', hover_name='State', hover_data={'Emissions': True, 'Sector': True}, color_continuous_scale="solar", title=f'{sec} Sector CO2 Emissions', labels={'Emissions': 'MMT of CO2'})
sec_map.update_geos(scope='usa')
st.plotly_chart(sec_map)

# Load fuel data
try:
    fuel_data = pd.read_csv('data/State energy-related carbon dioxide emissions by fuel.csv', header=3)
except FileNotFoundError:
    st.error("Fuel data file not found.")
    st.stop()

# Fix col names and % values
fuel_data.columns = fuel_data.columns.str.replace(',', '').str.strip()
fuel_cols = ['Coal', 'Petroleum', 'Natural Gas']
for f in fuel_cols:
    fuel_data[f] = fuel_data[f].replace({'%': ''}, regex=True).astype(float)

# Reshape data for fuels
fuel_long = pd.melt(fuel_data, id_vars=['State'], value_vars=fuel_cols, var_name='Fuel', value_name='Emissions')
fuel = st.selectbox("Select a fuel type", options=fuel_cols)

# Filtered fuel map
fuel_filt = fuel_long[fuel_long['Fuel'] == fuel]
fuel_map = px.choropleth(fuel_filt, locations='State', locationmode="USA-states", color='Emissions', hover_name='State', hover_data={'Emissions': True, 'Fuel': True}, color_continuous_scale="solar", title=f'{fuel} Emissions by State', labels={'Emissions': 'MMT of CO2'})
fuel_map.update_geos(scope='usa')
st.plotly_chart(fuel_map)

# Generate disaster data (fixed)
states = sec_data['State'].unique()
disasters = pd.DataFrame({
    'State': states,
    'Flood': np.random.choice([0, 1], size=len(states), p=[0.7, 0.3]),
    'Drought': np.random.choice([0, 1], size=len(states), p=[0.6, 0.4]),
    'Wildfire': np.random.choice([0, 1], size=len(states), p=[0.8, 0.2])
})
disasters.set_index('State', inplace=True)

# Overlay disaster states
st.write("### Climate Disaster Risks")
show_d = st.checkbox("Show disaster states")

if show_d:
    sec_d = sec_filt.merge(disasters, on='State', how='left').fillna(0)
    sec_d['Risk'] = sec_d[['Flood', 'Drought', 'Wildfire']].sum(axis=1)
    sec_d['Level'] = sec_d['Risk'].apply(lambda x: 'High' if x >= 2 else 'Mod' if x == 1 else 'Low')
    d_map = px.choropleth(sec_d, locations='State', locationmode="USA-states", color='Level', hover_name='State', color_discrete_map={'High': 'red', 'Mod': 'orange', 'Low': 'green'}, title=f'Disaster Risk - {sec} Emissions')
    d_map.update_geos(scope='usa')
    st.plotly_chart(d_map)

# State disaster details
st.write("### State Disaster Details")
s = st.selectbox("Select a state", options=states)
st.write("**Risk Levels for {}**".format(s))
st.write(disasters.loc[[s]].replace({1: 'High', 0: 'Low'}))

# Cost of living data
costs = {
    "AL": 45000, "AK": 67000, "AZ": 55000, "AR": 42000, "CA": 78000, "CO": 60000, "CT": 72000, "DE": 56000, "DC": 75000,
    "FL": 54000, "GA": 50000, "HI": 75000, "ID": 48000, "IL": 61000, "IN": 46000, "IA": 44000, "KS": 45000, "KY": 43000,
    "LA": 46000, "ME": 50000, "MD": 70000, "MA": 75000, "MI": 50000, "MN": 58000, "MS": 42000, "MO": 46000, "MT": 47000,
    "NE": 45000, "NV": 56000, "NH": 60000, "NJ": 72000, "NM": 48000, "NY": 78000, "NC": 52000, "ND": 46000, "OH": 50000,
    "OK": 45000, "OR": 62000, "PA": 55000, "RI": 68000, "SC": 50000, "SD": 44000, "TN": 48000, "TX": 51000, "UT": 56000,
    "VT": 65000, "VA": 65000, "WA": 70000, "WV": 40000, "WI": 48000, "WY": 44000
}

# Recommend state
st.write("### State Recommendation")
inc = st.number_input("Your annual income ($):", min_value=30000)

afford = [st for st, c in costs.items() if inc >= c]
emission_sums = sec_data[sec_data['State'].isin(afford)].copy()
emission_sums['Total'] = emission_sums[['Commercial', 'Electric power', 'Residential', 'Industrial', 'Transportation']].sum(axis=1)

if not emission_sums.empty:
    rec = emission_sums.loc[emission_sums['Total'].idxmin()]
    st.write(f"**Recommended State:** {rec['State']}")
    st.write(f"- **Total Emissions:** {rec['Total']} MMT of CO2")
    st.write(f"- **Cost of Living:** ${costs[rec['State']]:,}")
else:
    st.write("No states affordable based on income.")
