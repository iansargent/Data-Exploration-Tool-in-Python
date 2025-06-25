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
import leafmap as flm


def render_mapping_pydeck():
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

    # FILTER by Jurisdiction
    jurisdictions = ["All Jurisdictions"] + sorted(suit_gdf["Jurisdiction"].dropna().unique().tolist())
    with column2:
        selected_jurisdiction = st.multiselect("Jurisdiction", options=jurisdictions, default=["All Jurisdictions"])
    if selected_jurisdiction and "All Jurisdictions" not in selected_jurisdiction:
        suit_gdf = suit_gdf[suit_gdf["Jurisdiction"].isin(selected_jurisdiction)]

    suit_gdf = convert_all_timestamps_to_str(suit_gdf)

    # CATEGORY COLORS
    category_colors = {
        "Well Suited": [44, 160, 44, 180],       # green
        "Moderately Suited": [255, 204, 0, 180], # yellow
    }
    df_filtered = suit_gdf[suit_gdf["Suitability"].isin(category_colors.keys())].copy()
    df_filtered["coordinates"] = df_filtered["geometry"].apply(
        lambda geom: [list(geom.exterior.coords)] if geom.geom_type == "Polygon" 
        else [list(poly.exterior.coords) for poly in geom.geoms] if geom.geom_type == "MultiPolygon" 
        else []
    )
    df_filtered = df_filtered.explode("coordinates", ignore_index=True)

    df_filtered["fill_color"] = df_filtered["Suitability"].apply(lambda x: category_colors.get(x, [200, 200, 200, 0]))

    # LAND SUITABILITY LAYER
    polygon_layer = pdk.Layer(
        "PolygonLayer",
        data=df_filtered,
        get_polygon="coordinates",
        get_fill_color="fill_color",
        get_line_color=[20, 20, 20, 80],
        stroked=True,
        filled=True,
        pickable=True,
        auto_highlight=True,
    )

    # WASTEWATER TREATMENT FACILITIES
    WWTF_url = "https://raw.githubusercontent.com/VERSO-UVM/Wastewater-Infrastructure-Mapping/main/data/VermontWWTF.geojson"
    WWTF_response = requests.get(WWTF_url)
    WWTF_response.raise_for_status()
    WWTF_gdf = gpd.read_file(BytesIO(WWTF_response.content)).copy()
    WWTF_gdf = WWTF_gdf.to_crs("EPSG:4326")
    WWTF_gdf["lon"] = WWTF_gdf.geometry.centroid.x
    WWTF_gdf["lat"] = WWTF_gdf.geometry.centroid.y
    WWTF_gdf = WWTF_gdf.dropna(subset=["lat", "lon"])

    point_layer = pdk.Layer(
        "ScatterplotLayer",
        data=WWTF_gdf,
        get_position='[lon, lat]',
        get_radius=300,
        get_fill_color=[30, 144, 255, 180],  # Dodger blue
        pickable=True,
        tooltip=True
    )

    # LINEAR FEATURES
    # linear_url = "https://raw.githubusercontent.com/VERSO-UVM/Wastewater-Infrastructure-Mapping/main/MappingTemplate/LinearFeatures2025.02.geojson"
    # linear_response = requests.get(linear_url)
    # linear_response.raise_for_status()
    # linear_gdf = gpd.read_file(BytesIO(linear_response.content))

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

    # View setup
    view_state = pdk.ViewState(latitude=44.26, longitude=-72.57, zoom=8)

    # Render in Streamlit
    st.pydeck_chart(pdk.Deck(
        layers=[polygon_layer, point_layer],
        initial_view_state=view_state,
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
        tooltip={"text": "{Suitability}"}
    ))

    # Metric Cards
    land_suitability_metric_cards(df_filtered)
            
def show_mapping(): 
    render_mapping_pydeck()


if __name__ == "__main__":
    show_mapping()