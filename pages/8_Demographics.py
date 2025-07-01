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
from app_utils import split_name_col


def render_demographics():
    # Page header
    st.header("Demographics", divider="grey")    
    
    # Read the Census selected demographic variables dataset (DP05)
    demographic_gdf = pyogrio.read_dataframe('https://raw.githubusercontent.com/iansargent/Data-Exploration-Tool-in-Python/main/Data/Census/VT_DEMOGRAPHIC_ALL.fgb')
    # Split the "name" column into separate "County" and "Jurisdiction" columns
    demographic_gdf = split_name_col(demographic_gdf)
    
    st.subheader("Mapping")
    # Define the numerical columns in the GeoDataFrame for mapping
    numeric_cols = [col for col in demographic_gdf.columns if demographic_gdf[col].dtype in ['int64', 'float64']]
    # Add a user select box to choose which variable they want to map
    demographic_variable = st.selectbox("Select a Demographic variable", numeric_cols)

    # Project geometry to latitude and longitude coordinates
    demographic_gdf = demographic_gdf.to_crs(epsg=4326)
    # Select only necessary columns for the dataframe being mapped. Drop any NA values
    demographic_gdf_map = demographic_gdf[["County", "Jurisdiction", demographic_variable, "geometry"]].dropna().copy()

    # Normalize the demographic variable for monochromatic coloring
    vmin = demographic_gdf_map[demographic_variable].min()
    vmax = demographic_gdf_map[demographic_variable].max()
    norm = colors.Normalize(vmin=vmin, vmax=vmax)
    cmap = cm.get_cmap("Blues")

    # Convert colors to [R, G, B, A] values
    demographic_gdf_map["fill_color"] = demographic_gdf_map[demographic_variable].apply(
        lambda x: [int(c * 255) for c in cmap(norm(x))[:3]] + [180])

    # Convert the geometry column to GeoJSON coordinates
    demographic_gdf_map["coordinates"] = demographic_gdf_map.geometry.apply(
        lambda geom: geom.__geo_interface__["coordinates"])
    
    # Chloropleth map layer
    polygon_layer = pdk.Layer(
        "PolygonLayer",
        data=demographic_gdf_map,
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
        tooltip={"text": "{Jurisdiction}: {" + demographic_variable + "}"}
    ), height=550)
    
    return
            
def show_demographics():
    # Display the page
    render_demographics()


if __name__ == "__main__":
    show_demographics()