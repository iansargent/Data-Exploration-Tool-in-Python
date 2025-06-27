"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Demographics Page (Census)
"""

# Necessary imports
import streamlit as st
import pandas as pd
import geopandas as gpd
import leafmap.foliumap as leafmap
import pydeck as pdk
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors
from app_utils import split_name_col


def render_demographics():
    st.header("Demographics", divider="grey")    
    
    demographic_gdf = gpd.read_file('/Users/iansargent/Desktop/ORCA/Steamlit App Testing/Census/VT_DEMOGRAPHIC_ALL.fgb')
    demographic_gdf = split_name_col(demographic_gdf)
    
    st.subheader("Mapping")
    # Define the numerical columns in the GeoDataFrame for mapping
    numeric_cols = [col for col in demographic_gdf.columns if demographic_gdf[col].dtype in ['int64', 'float64']]
    # Add a user select box to choose which variable they want to map
    demographic_variable = st.selectbox("Select a Demographic variable", numeric_cols)

    # Project to lat/lon for Pydeck
    demographic_gdf = demographic_gdf.to_crs(epsg=4326)
    demographic_gdf_map = demographic_gdf[["County", "Jurisdiction", demographic_variable, "geometry"]].dropna().copy()

    # Normalize the demographic variable
    vmin = demographic_gdf_map[demographic_variable].min()
    vmax = demographic_gdf_map[demographic_variable].max()
    norm = colors.Normalize(vmin=vmin, vmax=vmax)
    cmap = cm.get_cmap("Blues")

    # Convert to [R, G, B, A] values
    demographic_gdf_map["fill_color"] = demographic_gdf_map[demographic_variable].apply(
        lambda x: [int(c * 255) for c in cmap(norm(x))[:3]] + [180])

    # Convert geometry to GeoJSON-style coordinates
    demographic_gdf_map["coordinates"] = demographic_gdf_map.geometry.apply(
        lambda geom: geom.__geo_interface__["coordinates"])
    
    # Set view state
    view_state = pdk.ViewState(latitude=44.26, longitude=-72.57, zoom=7)
    
    # Pydeck PolygonLayer
    polygon_layer = pdk.Layer(
        "PolygonLayer",
        data=demographic_gdf_map,
        get_polygon="coordinates[0]",
        get_fill_color="fill_color",
        pickable=True,
        auto_highlight=True,
    )
    
    # Display map
    st.pydeck_chart(pdk.Deck(
        layers=[polygon_layer],
        initial_view_state=view_state,
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
        tooltip={"text": "{Jurisdiction}: {" + demographic_variable + "}"}
    ), height=550)
    
    return
            
def show_mapping():
    # Display the page
    render_demographics()


if __name__ == "__main__":
    show_mapping()