"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Social Page (Census)
"""

# Necessary imports
import streamlit as st
import geopandas as gpd
import pydeck as pdk
import matplotlib.cm as cm
import matplotlib.colors as colors
import pyogrio
from streamlit_rendering import filter_dataframe
from app_utils import split_name_col, rename_and_merge_census_cols


@st.cache_data
def load_2023_social():
    url_2023 = 'https://raw.githubusercontent.com/iansargent/Data-Exploration-Tool-in-Python/main/Data/Census/VT_SOCIAL_ALL.fgb'
    social_gdf_2023 = pyogrio.read_dataframe(url_2023)
    social_gdf_2023 = split_name_col(social_gdf_2023)
    
    return social_gdf_2023


def render_social():
    # Page header
    st.header("Social", divider="grey")
    mapping, snapshot = st.tabs(tabs=["Mapping", "Snapshot"])

    social_gdf_2023 = load_2023_social()
    tidy_2023 = rename_and_merge_census_cols(social_gdf_2023)

    with mapping:
        st.subheader("Mapping")
        
        # Select the combination of vars we're interested in
        filtered_2023 = filter_dataframe(tidy_2023, filter_columns=["Category", "Subcategory", "Variable", "Measure"])
        # Project geometry to latitude and longitude coordinates
        filtered_2023 = filtered_2023.to_crs(epsg=4326)
        
        # Normalize the social variable for monochromatic coloring
        vmin = filtered_2023['Value'].min()
        vmax = filtered_2023['Value'].max()
        norm = colors.Normalize(vmin=vmin, vmax=vmax)
        cmap = cm.get_cmap("Purples")

        # Convert colors to [R, G, B, A] values
        filtered_2023["fill_color"] = filtered_2023['Value'].apply(
            lambda x: [int(c * 255) for c in cmap(norm(x))[:3]] + [180])

        # Convert the geometry column to GeoJSON coordinates
        filtered_2023["coordinates"] = filtered_2023.geometry.apply(
            lambda geom: geom.__geo_interface__["coordinates"])
            
        # Chloropleth map layer
        polygon_layer = pdk.Layer(
            "PolygonLayer",
            data=filtered_2023,
            get_polygon="coordinates[0]",
            get_fill_color="fill_color",
            pickable=True,
            auto_highlight=True,
        )

        # Set the map center and zoom level
        view_state = pdk.ViewState(latitude=44.26, longitude=-72.57, zoom=7)

        # Display the map to the page
        st.pydeck_chart(pdk.Deck(
            layers=[polygon_layer],
            initial_view_state=view_state,
            map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
            tooltip={"text": "{Jurisdiction}: {Value}"}), height=550)

    # Social Snapshot
    with snapshot:
        st.subheader("Social Snapshot")
            
def show_social():
    # Display the page
    render_social()


if __name__ == "__main__":
    show_social()