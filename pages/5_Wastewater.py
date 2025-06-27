"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Wastewater Page
"""

# Necessary imports
import streamlit as st
import geopandas as gpd
import pandas as pd
import pydeck as pdk
import requests
from io import BytesIO
from app_utils import (convert_all_timestamps_to_str, land_suitability_metric_cards)


def render_wastewater():
    st.header("VT Wastewater Infrastructure")

    column1, column2 = st.columns(2)
    rpcs = ["ACRPC", "BCRC", "CCRPC", "CVRPC", "LCPC", "MARC", "NVDA", "NWRPC", "RRPC", "TRORC", "WRC"]
    
    with column1:
        selected_rpc = st.selectbox("RPC", options=rpcs, index=0)

    i = rpcs.index(selected_rpc)

    # LAND SUITABILITY DATA
    land_suit_url = f"https://github.com/VERSO-UVM/Vermont-Livability-Map/raw/main/data/{rpcs[i]}_Soil_Septic.fgb"
    suit_response = requests.get(land_suit_url)
    suit_response.raise_for_status()
    suit_gdf = gpd.read_file(BytesIO(suit_response.content))
    suit_gdf = suit_gdf.to_crs("EPSG:4326")

    # FILTER by Jurisdiction
    jurisdictions = ["All Jurisdictions"] + sorted(suit_gdf["Jurisdiction"].dropna().unique().tolist())
    with column2:
        selected_jurisdiction = st.multiselect("Jurisdiction", options=jurisdictions, default=["All Jurisdictions"])
    if selected_jurisdiction and "All Jurisdictions" not in selected_jurisdiction:
        suit_gdf = suit_gdf[suit_gdf["Jurisdiction"].isin(selected_jurisdiction)]
    suit_gdf = convert_all_timestamps_to_str(suit_gdf)

    # CATEGORY COLORS
    category_colors = {"Well Suited": [44, 160, 44, 180],
                       "Moderately Suited": [255, 204, 0, 180]}
    suit_filtered = suit_gdf[suit_gdf["Suitability"].isin(category_colors.keys())].copy()        
    suit_filtered["fill_color"] = suit_filtered["Suitability"].apply(lambda x: category_colors.get(x))

    def extract_2d_coords(g):
        return [[ [x, y] for x, y in g.exterior.coords ]]
    suit_filtered["polygon_coords"] = suit_filtered.geometry.apply(extract_2d_coords)

    # LAND SUITABILITY LAYER
    soil_layer = pdk.Layer(
        "PolygonLayer",
        data=suit_filtered,
        get_polygon="polygon_coords",
        get_fill_color="fill_color",
        get_line_color=[20, 20, 20, 180],
        pickable=True,
        auto_highlight=True,
        stroked=True,
        filled=True,
    )

    bounds = suit_filtered.total_bounds
    center_lon = (bounds[0] + bounds[2]) / 2
    center_lat = (bounds[1] + bounds[3]) / 2
    view_state = pdk.ViewState(latitude=center_lat, longitude=center_lon, zoom=9)

    # Render in Streamlit
    st.pydeck_chart(pdk.Deck(
        layers=[soil_layer],
        initial_view_state=view_state,
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
    ), use_container_width=True)

    # Metric Cards
    land_suitability_metric_cards(suit_filtered)
    
            
def show_mapping(): 
    render_wastewater()


if __name__ == "__main__":
    show_mapping()