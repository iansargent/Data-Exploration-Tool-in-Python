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
import leafmap.foliumap as leafmap
from app_utils import (get_user_files, 
                       convert_all_timestamps_to_str, process_uploaded_files,
                       land_suitability_metric_cards)


def render_mapping():
    st.markdown("<h2 style='color: #4a4a4a;'>VT Wastewater Infrastructure</h2>", unsafe_allow_html=True)
    user_files = get_user_files()
    processed_files = process_uploaded_files(user_files)

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

    m = leafmap.Map(center=[44.26, -72.57], zoom=8, zoom_snap=0.5)
    m.add_basemap(selected_basemap)

    column1, column2 = st.columns(2)
    rpcs = ["ACRPC", "BCRC", "CCRPC", "CVRPC", "LCPC", "MARC", "NVDA", "NWRPC", "RRPC", "TRORC", "WRC"]
    
    with column1:
        selected_rpc = st.selectbox(
            label="RPC",
            options=rpcs,
            index=0,
        )

    index = rpcs.index(selected_rpc)

    if selected_rpc:
        land_suit_path = f'/Users/iansargent/Desktop/ORCA/Steamlit App Testing/App Demo/WIM/{rpcs[index]}_Soil_Septic.fgb'
    
    suit_gdf = gpd.read_file(land_suit_path)

    
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

    m.add_gdf(
        df_filtered,
        layer_name="Land Suitability",
        style_function=style_function,
        info_mode="on_click",
        zoom_to_layer=True
    )
    
    # Add legend once for all layers
    m.add_legend(title="Land Suitability", legend_dict=category_colors)

    # Show the map
    m.to_streamlit(height=600)

    land_suitability_metric_cards(suit_gdf)


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
    render_mapping()


if __name__ == "__main__":
    show_mapping()