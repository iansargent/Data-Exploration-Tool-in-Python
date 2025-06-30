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
from app_utils import split_name_col


def render_social():
    # Page header
    st.header("Social", divider="grey")

    # Read the Census selected social variables dataset (DP05)
    social_gdf = gpd.read_file('/Users/iansargent/Desktop/ORCA/Steamlit App Testing/Census/VT_SOCIAL_ALL.fgb')
    # Split the "name" column into separate "County" and "Jurisdiction" columns
    social_gdf = split_name_col(social_gdf)

    st.subheader("Mapping")
    # Define the numerical columns in the GeoDataFrame for mapping
    numeric_cols = [col for col in social_gdf.columns if social_gdf[col].dtype in ['int64', 'float64']]
    # Add a user select box to choose which variable they want to map
    social_variable = st.selectbox("Select a Social variable", numeric_cols)

    # Project geometry to latitude and longitude coordinates
    social_gdf = social_gdf.to_crs(epsg=4326)
    # Select only necessary columns for the dataframe being mapped. Drop any NA values
    social_gdf_map = social_gdf[["County", "Jurisdiction", social_variable, "geometry"]].dropna().copy()
    
    # Normalize the social variable for monochromatic coloring
    vmin = social_gdf_map[social_variable].min()
    vmax = social_gdf_map[social_variable].max()
    norm = colors.Normalize(vmin=vmin, vmax=vmax)
    cmap = cm.get_cmap("Purples")

    # Convert colors to [R, G, B, A] values
    social_gdf_map["fill_color"] = social_gdf_map[social_variable].apply(
        lambda x: [int(c * 255) for c in cmap(norm(x))[:3]] + [180])

    # Convert the geometry column to GeoJSON coordinates
    social_gdf_map["coordinates"] = social_gdf_map.geometry.apply(
        lambda geom: geom.__geo_interface__["coordinates"])
    
    # Chloropleth map layer
    polygon_layer = pdk.Layer(
        "PolygonLayer",
        data=social_gdf_map,
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
        tooltip={"text": "{Jurisdiction}: {" + social_variable + "}"}
    ), height=550)
    
    return
            
def show_social():
    # Display the page
    render_social()


if __name__ == "__main__":
    show_social()