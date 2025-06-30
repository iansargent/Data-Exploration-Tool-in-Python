"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Economics Page (Census)
"""

# Necessary imports
import streamlit as st
import geopandas as gpd
import pydeck as pdk
import matplotlib.cm as cm
import matplotlib.colors as colors
from app_utils import split_name_col


def render_economics():
    # Page header
    st.header("Economics", divider="grey")

    # Read the Census selected economic variables dataset (DP03)
    econ_gdf = gpd.read_file('/Users/iansargent/Desktop/ORCA/Steamlit App Testing/Census/VT_ECONOMIC_ALL.fgb')
    # Split the "name" column into separate "County" and "Jurisdiction" columns
    econ_gdf = split_name_col(econ_gdf)

    st.subheader("Mapping")
    # Define the numerical columns in the GeoDataFrame for mapping
    numeric_cols = [col for col in econ_gdf.columns if econ_gdf[col].dtype in ['int64', 'float64']]
    # Add a user select box to choose which variable they want to map
    econ_variable = st.selectbox("Select an economic variable", numeric_cols)

    # Project geometry to latitude and longitude coordinates
    econ_gdf = econ_gdf.to_crs(epsg=4326)
    # Select only necessary columns for the dataframe being mapped. Drop any NA values
    econ_gdf_map = econ_gdf[["County", "Jurisdiction", econ_variable, "geometry"]].dropna().copy()

    # Normalize the economic variable for monochromatic coloring
    vmin = econ_gdf_map[econ_variable].min()
    vmax = econ_gdf_map[econ_variable].max()
    norm = colors.Normalize(vmin=vmin, vmax=vmax)
    cmap = cm.get_cmap("Greens")

    # Convert colors to [R, G, B, A] values
    econ_gdf_map["fill_color"] = econ_gdf_map[econ_variable].apply(
        lambda x: [int(c * 255) for c in cmap(norm(x))[:3]] + [180])

    # Convert the geometry column to GeoJSON coordinates
    econ_gdf_map["coordinates"] = econ_gdf_map.geometry.apply(
        lambda geom: geom.__geo_interface__["coordinates"])
        
    # Chloropleth map layer
    polygon_layer = pdk.Layer(
        "PolygonLayer",
        data=econ_gdf_map,
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
        tooltip={"text": "{Jurisdiction}: {" + econ_variable + "}"}
    ), height=550)

    return
            
def show_economics():
    # Display the page
    render_economics()


if __name__ == "__main__":
    show_economics()