"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Flooding Page (FEMA)
"""
import streamlit as st
import geopandas as gpd
import pydeck as pdk
import pandas as pd
import shapely


def render_mapping_pydeck():
    st.header("VT Flood Risk")

    # Load flood hazard zones
    flood_gdf = gpd.read_file('/Users/iansargent/Desktop/ORCA/Steamlit App Testing/VT_Flood_Hazard.geojson')

    # Filter to high-risk FEMA flood zones
    high_risk_zones = ["A", "AE", "A1-A30", "AH", "AO", "A99"]
    high_risk = flood_gdf[flood_gdf["FLD_ZONE"].isin(high_risk_zones)].copy()

    # Simplify geometry for performance
    high_risk["geometry"] = high_risk["geometry"].simplify(0.001, preserve_topology=True)

    # Extract polygons for pydeck
    def get_coordinates(geom):
        if geom.geom_type == 'Polygon':
            return [list(geom.exterior.coords)]
        elif geom.geom_type == 'MultiPolygon':
            return [list(poly.exterior.coords) for poly in geom.geoms]
        return []

    high_risk["coordinates"] = high_risk["geometry"].apply(get_coordinates)

    # Explode multipolygons into separate rows
    exploded = high_risk.explode(index_parts=False)
    exploded = exploded.explode("coordinates", ignore_index=True)

    # Build pydeck layer
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

    # Set map view
    view_state = pdk.ViewState(
        latitude=44.26,
        longitude=-72.57,
        zoom=7.8,
        pitch=0
    )

    # Display map
    st.pydeck_chart(pdk.Deck(
        layers=[polygon_layer],
        initial_view_state=view_state,
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
        tooltip={"text": "Zone: {FLD_ZONE}"}
    ))

def show_mapping():
    render_mapping_pydeck()

if __name__ == "__main__":
    show_mapping()
