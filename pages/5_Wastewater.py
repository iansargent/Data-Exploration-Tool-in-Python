"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Wastewater Page
"""

# Necessary imports
import streamlit as st
import pandas as pd
import geopandas as gpd
import leafmap.foliumap as flm
import leafmap as leafmap
from app_utils import (convert_all_timestamps_to_str, land_suitability_metric_cards)

import requests
from io import BytesIO


def render_mapping():
    
    st.markdown("<h2 style='color: #4a4a4a;'>VT Wastewater Infrastructure</h2>", unsafe_allow_html=True)

    m = flm.Map(center=[44.26, -72.57], zoom=8, zoom_snap=0.5)
    m.add_basemap("CartoDB.Positron")

    column1, column2 = st.columns(2)
    rpcs = ["ACRPC", "BCRC", "CCRPC", "CVRPC", "LCPC", "MARC", "NVDA", "NWRPC", "RRPC", "TRORC", "WRC"]
    
    with column1:
        selected_rpc = st.selectbox(
            label="RPC",
            options=rpcs,
            index=0,
        )
    i = rpcs.index(selected_rpc)

    # LAND SUITABILITY
    land_suit_url = f"https://github.com/VERSO-UVM/Vermont-Livability-Map/raw/main/data/{rpcs[i]}_Soil_Septic.fgb"
    # Stream download to avoid issues with large files
    suit_response = requests.get(land_suit_url)
    suit_response.raise_for_status()  # raises an error if download failed
    suit_gdf = gpd.read_file(BytesIO(suit_response.content))

    # LINEAR FEATURES
    linear_url = "https://raw.githubusercontent.com/VERSO-UVM/Wastewater-Infrastructure-Mapping/main/MappingTemplate/LinearFeatures2025.02.geojson"
    linear_response = requests.get(linear_url)
    linear_response.raise_for_status()
    linear_gdf = gpd.read_file(BytesIO(linear_response.content))

    # WASTEWATER TREATMENT FACILITIES
    # NOTE: File sizes are too large (915.6 MB) Needs to be more compressed
    # WWTF_url = "https://raw.githubusercontent.com/VERSO-UVM/Wastewater-Infrastructure-Mapping/main/data/VermontWWTF.geojson"
    # WWTF_response = requests.get(WWTF_url)
    # WWTF_response.raise_for_status()
    # WWTF_gdf = gpd.read_file(BytesIO(WWTF_response.content))
    
    # POINT FEATURES
    # NOTE: File sizes are too large (915.6 MB) Needs to be more compressed
    # NVDA_point_url = "https://raw.githubusercontent.com/VERSO-UVM/Vermont-Livability-Map/main/Viz%20geojsons/NVDA_Point.geojson"
    # NVDA_point_response = requests.get(NVDA_point_url)
    # NVDA_point_response.raise_for_status()
    # NVDA_point_gdf = gpd.read_file(BytesIO(NVDA_point_response.content))
    # WRC_point_url = "https://raw.githubusercontent.com/VERSO-UVM/Vermont-Livability-Map/main/Viz%20geojsons/WRC_Point.geojson"
    # WRC_point_response = requests.get(WRC_point_url)
    # WRC_point_response.raise_for_status()
    # WRC_point_gdf = gpd.read_file(BytesIO(WRC_point_response.content))

    jurisdictions = ["All Jurisdictions"] + suit_gdf["Jurisdiction"].unique().tolist()

    with column2:
        selected_jurisdiction = st.multiselect(
            label="Jurisdiction",
            options=jurisdictions,
            default=["All Jurisdictions"])
    

    if selected_jurisdiction and "All Jurisdictions" not in selected_jurisdiction:
        suit_gdf = suit_gdf[suit_gdf["Jurisdiction"].isin(selected_jurisdiction)]

    # Define your specific colors explicitly
    category_colors = {
        "Well Suited": "#2ca02c",       # green
        "Moderately Suited": "#ffcc00", # yellow
    }

    def style_function(feature):
        rating = feature["properties"]["Suitability"]
        if rating in category_colors:
            return {
                "fillColor": category_colors[rating],
                "color": "navy",
                "weight": 0.1,
                "fillOpacity": 0.8,
            }
        else:
            # Make features transparent (or don't show)
            return {
                "fillColor": "#00000000",  # fully transparent
                "color": "#02010100",
                "weight": 0,
                "fillOpacity": 0,
            }

    suit_gdf = convert_all_timestamps_to_str(suit_gdf)

    # Optional: filter the df to only include the two categories
    df_filtered = suit_gdf[suit_gdf["Suitability"].isin(category_colors.keys())]
    df_filtered = df_filtered.drop(columns=["OBJECTID_1", "Shape_Length", "Shape_Area"])

    m.add_gdf(df_filtered, layer_name="Land Suitability", style_function=style_function, info_mode="on_click", zoom_to_layer=True)
    m.add_gdf(linear_gdf, layer_name="Linear Features", info_mode="on_click", zoom_to_layer=True)
    # m.add_gdf(WWTF_gdf, layer_name="Linear Features", info_mode="on_click", zoom_to_layer=True)
    
    # Add legend once for all layers
    m.add_legend(title="Land Suitability", legend_dict=category_colors)

    # Show the map and metric cards
    m.to_streamlit(height=600)
    land_suitability_metric_cards(suit_gdf)

    return m
            
def show_mapping(): 
    # Display the page
    render_mapping()


if __name__ == "__main__":
    show_mapping()