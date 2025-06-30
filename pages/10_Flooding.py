"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Flooding Page (FEMA)
"""

# Necessary imports
import streamlit as st
import geopandas as gpd
import pydeck as pdk


def flooding():
    # Page header
    st.header("VT Flood Risk")

    # Load the FEMA flood hazard zones dataset
    flood_gdf = gpd.read_file('/Users/iansargent/Desktop/ORCA/Steamlit App Testing/VT_Flood_Hazard.geojson')

    # Filter the data to only include high-risk FEMA flood zones
    high_risk_zones = ["A", "AE", "A1-A30", "AH", "AO", "A99"]
    high_risk = flood_gdf[flood_gdf["FLD_ZONE"].isin(high_risk_zones)].copy()

    # Simplify the geometry for computing performance
    high_risk["geometry"] = high_risk["geometry"].simplify(0.001, preserve_topology=True)

    # Extract polygon shapes for pydeck
    def get_coordinates(geom):
        if geom.geom_type == 'Polygon':
            return [list(geom.exterior.coords)]
        elif geom.geom_type == 'MultiPolygon':
            return [list(poly.exterior.coords) for poly in geom.geoms]
        return []
    high_risk["coordinates"] = high_risk["geometry"].apply(get_coordinates)

    # "Explode" multipolygons into separate rows
    exploded = high_risk.explode(index_parts=False)
    exploded = exploded.explode("coordinates", ignore_index=True)

    # Flood zones map layer
    polygon_layer = pdk.Layer(
        "PolygonLayer",
        data=exploded,
        get_polygon="coordinates",
        get_fill_color=[255, 0, 0, 100],
        pickable=True,
        auto_highlight=True,
        stroked=True,
        filled=True,
    )

    # Set the map center and zoom level
    view_state = pdk.ViewState(latitude=44.26, longitude=-72.57, zoom=7.8)

    # Display map to the page
    st.pydeck_chart(pdk.Deck(
        layers=[polygon_layer],
        initial_view_state=view_state,
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
        tooltip={"text": "Zone: {FLD_ZONE}"}))


def show_flooding():
    flooding()


if __name__ == "__main__":
    show_flooding()
