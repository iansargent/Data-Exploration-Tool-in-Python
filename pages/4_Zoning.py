"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Zoning Page
"""

# Necessary imports
import streamlit as st
import pandas as pd
import leafmap.foliumap as leafmap
from app_utils import (render_zoning_layer, render_table, render_comparison_table, load_zoning_data)
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np


def render_mapping():
    st.markdown("<h2 style='color: #4a4a4a;'>VT Zoning</h2>", unsafe_allow_html=True)
    
    basemaps = {
        "Light": "CartoDB.Positron",
        "Standard": "OpenStreetMap",
        "Satellite": "Esri.WorldImagery",
        "Elevation": "OpenTopoMap",
        "Shaded Relief Map": "Esri.WorldShadedRelief",
        "Hillshade Map": "Esri.WorldHillshade",
        "National Geographic": "Esri.NatGeoWorldMap",
        "World Street Map": "Esri.WorldStreetMap"
    }
    
    basemap_select_box = st.selectbox("**Basemap**", list(basemaps.keys()), index=0)
    selected_basemap = basemaps[basemap_select_box]

    m = leafmap.Map(center=[44.26, -72.57], zoom_snap=0.5)
    m.add_basemap(selected_basemap)

    
    zoning_gdf = load_zoning_data()
    _, filtered_gdf = render_zoning_layer(m)

    housing_gdf = gpd.read_file("/Users/iansargent/Desktop/ORCA/house_geo_update.fgb")
    
    numeric_cols = [col for col in housing_gdf.columns if housing_gdf[col].dtype in ['int64', 'float64']]
    housing_variable = st.selectbox("Select a Housing variable", numeric_cols)

    housing_gdf_map = housing_gdf[["NAME.y", housing_variable, "geometry"]].dropna()


    def style_function(feature):
        return {
            "fillOpacity": 0.2,
            "weight": 0.5,
            "color": "black",
            "fillColor": "#2171b5"  # Default fill color (can be dynamic)
        }
    m.add_data(
        housing_gdf_map,
        column=housing_variable,
        scheme="NaturalBreaks",
        cmap="Blues",
        legend_title="Housing",
        layer_name="Housing")
        
    # --- Always Show the Map ---
    m.to_streamlit(height=600)

    # --- Zoning Table and Comparison Below ---
    st.markdown("### Zoning Districts Table")
    selected = render_table(filtered_gdf)
    try:
        if not selected.empty:
            render_comparison_table(selected)
    except Exception as e:
        st.warning(f"No Selected Districts to Compare: {e}")
    
    st.subheader("Housing Data")
    st.dataframe(housing_gdf[["NAME.y", housing_variable]])

    return m
            
def show_mapping():
    
    # Apply a background color to the page
    st.markdown(
    """
    <style>
    html, body, [class*="css"]  {
        font-family: 'Avenir', 'Arial', sans-serif; font-weight: 300;
    }
    [data-testid="stAppViewContainer"] {
        background-image: url("https://t3.ftcdn.net/jpg/01/99/28/98/360_F_199289808_twlKOyrViuqfzyV5JFmYdly2GHihxqEh.jpg");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center;
    }
    [data-testid="stHeader"] {
        background: rgba(255, 255, 255, 0.0);
    }
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.5);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Set the global fonts 
    st.markdown(
    """
    <style>
    /* Set Helvetica (fallback to Arial, sans-serif) globally */
    html, body, [class*="css"]  {
        font-family: 'Avenir', 'Arial', sans-serif; font-weight: 300;
    }
    </style>
    """, unsafe_allow_html=True)
        
    # Display the page
    map = render_mapping()


if __name__ == "__main__":
    show_mapping()