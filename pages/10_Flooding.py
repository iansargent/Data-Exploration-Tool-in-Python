"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Flooding Page (FEMA)
"""

# Necessary imports
import streamlit as st
import pandas as pd
import geopandas as gpd
import leafmap.foliumap as leafmap

def render_mapping():
    st.markdown("<h2 style='color: #4a4a4a;'>VT Flooding Risk</h2>", unsafe_allow_html=True)

    m = leafmap.Map(center=[44.26, -72.57], zoom=8, zoom_snap=0.5)
    m.add_basemap("CartoDB.Positron")

    # Load your flood zone data
    flood_gdf = gpd.read_file('/Users/iansargent/Desktop/ORCA/Steamlit App Testing/VT_Flood_Hazard.geojson')

    # Define flood zone properties (color + risk label)
    floodzone_data = {
        "D": {"color": "#bdbdbd", "risk": "Undetermined"},
        "C": {"color": "#ccebc5", "risk": "Low"},
        "X": {"color": "#ccebc5", "risk": "Low"},
        "B": {"color": "#ffff99", "risk": "Moderate"},
        "A": {"color": "#fb6a4a", "risk": "High"},
        "AE": {"color": "#fb6a4a", "risk": "High"},
        "A1-A30": {"color": "#fb6a4a", "risk": "High"},
        "AH": {"color": "#fb6a4a", "risk": "High"},
        "AO": {"color": "#fb6a4a", "risk": "High"},
        "A99": {"color": "#fb6a4a", "risk": "High"},
        "V": {"color": "#de2d26", "risk": "Coastal High"},
        "VE": {"color": "#de2d26", "risk": "Coastal High"},
        "V1-V30": {"color": "#de2d26", "risk": "Coastal High"},
        "OPEN WATER": {"color": "#0571b0", "risk": "Open Water"},
        "AREA NOT INCLUDED": {"color": "#f0f0f0", "risk": "Not Included"},
    }

    # Group by risk level
    risk_groups = {}
    for zone, props in floodzone_data.items():
        risk = props["risk"]
        color = props["color"]
        if risk not in risk_groups:
            risk_groups[risk] = {
                "zones": [],
                "color": color
            }
        risk_groups[risk]["zones"].append(zone)

    # Add a separate layer per risk level
    for risk, group in risk_groups.items():
        subset = flood_gdf[flood_gdf["FLD_ZONE"].isin(group["zones"])]
        if not subset.empty:
            m.add_gdf(
                subset,
                layer_name=risk,
                style_function=lambda feat, color=group["color"]: {
                    "fillColor": color,
                    "color": "black",
                    "weight": 0.3,
                    "fillOpacity": 0.6
                }
            )

    # Add legend and layer control
    m.add_legend(title="Flood Risk Level", legend_dict={r: v["color"] for r, v in risk_groups.items()})
    m.add_layer_control()

    # Show the map
    m.to_streamlit(height=600)

    # Optional: show full GeoDataFrame
    st.subheader("Flood Data Table")
    st.dataframe(flood_gdf)

    return m

def show_mapping():
    render_mapping()

if __name__ == "__main__":
    show_mapping()
