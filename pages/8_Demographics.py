"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Demographics Page (Census)
"""

# Necessary imports
import streamlit as st
import geopandas as gpd
import pydeck as pdk
import matplotlib.cm as cm
import matplotlib.colors as colors
import pyogrio
from streamlit_rendering import filter_dataframe
from app_utils import split_name_col, rename_and_merge_census_cols, jenks_color_map


@st.cache_data
def load_2023_demographics():
    url_2023 = 'https://raw.githubusercontent.com/iansargent/Data-Exploration-Tool-in-Python/main/Data/Census/VT_DEMOGRAPHIC_ALL.fgb'
    demographics_gdf_2023 = pyogrio.read_dataframe(url_2023)
    demographics_gdf_2023 = split_name_col(demographics_gdf_2023)
    
    return demographics_gdf_2023

def render_demographics():
    # Page header
    st.header("Demographics", divider="grey")   
    mapping, snapshot = st.tabs(tabs=["Mapping", "Snapshot"])

    demographics_gdf_2023 = load_2023_demographics()
    tidy_2023 = rename_and_merge_census_cols(demographics_gdf_2023)

    with mapping:
        st.subheader("Mapping")
        
        # Select the combination of vars we're interested in
        filtered_2023 = filter_dataframe(tidy_2023, filter_columns=["Category", "Subcategory", "Variable", "Measure"])
        # Project geometry to latitude and longitude coordinates
        filtered_2023 = filtered_2023.to_crs(epsg=4326)

        col1, _, _ = st.columns(3)
        n_classes = col1.slider(label="Adjust the level of detail", value=10, min_value=5, max_value=15)
        # Define the Jenk's colormap and apply it to the dataframe
        jenks_cmap_dict = jenks_color_map(filtered_2023, n_classes, "Blues")
        filtered_2023['fill_color'] = filtered_2023['color_groups'].astype(str).map(jenks_cmap_dict)
        # Fill null values with a transparent color
        filtered_2023['fill_color'] = filtered_2023['fill_color'].fillna("(0, 0, 0, 0)")

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
        view_state = pdk.ViewState(latitude=44.26, longitude=-72.57, min_zoom=6.5, zoom=7)

        # Display the map to the page
        st.pydeck_chart(pdk.Deck(
            layers=[polygon_layer],
            initial_view_state=view_state,
            map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
            tooltip={"text": "{Jurisdiction}: {Value}"}), height=550)
        
        tidy_2023
        filtered_2023

    ## Census Snapshot section (Housing) ##
    with snapshot:
        st.subheader("Demographic Snapshot")
            
def show_demographics():
    # Display the page
    render_demographics()


if __name__ == "__main__":
    show_demographics()