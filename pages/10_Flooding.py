"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Flooding Page (FEMA)
"""

# Necessary imports
import streamlit as st
import pydeck as pdk
import geopandas as gpd


#TODO: This API reference only retrieves the first 1000 features (rows). FIX THAT...WE NEED ALL 7300 something
@st.cache_data
def load_flood_data():
    import requests
    from io import BytesIO

    flood_url = "https://anrmaps.vermont.gov/arcgis/rest/services/Open_Data/OPENDATA_ANR_EMERGENCY_SP_NOCACHE_v2/MapServer/57/query?where=1%3D1&outFields=FLD_ZONE,FLD_AR_ID,STUDY_TYP&outSR=4326&f=json"
    flood_response = requests.get(flood_url)
    suit_gdf = gpd.read_file(BytesIO(flood_response.content))
    suit_gdf = suit_gdf.to_crs("EPSG:4326")

    return suit_gdf
    

def flooding():
    # Page header
    st.header("VT Flood Risk")

    # Load the FEMA flood hazard zones dataset
    flood_gdf = load_flood_data()

    # Filter the data to only include high-risk FEMA flood zones
    high_risk_zones = ["A", "AE", "A1-A30", "AH", "AO", "A99"]
    high_risk = flood_gdf[flood_gdf["FLD_ZONE"].isin(high_risk_zones)].copy()

    # Simplify the geometry for computing performance
    high_risk["geometry"] = high_risk["geometry"].simplify(0.0001, preserve_topology=True)

    # Extract polygon shapes for pydeck
    def get_coordinates(geom):
        if geom.geom_type == 'Polygon':
            return [list(geom.exterior.coords)]
        elif geom.geom_type == 'MultiPolygon':
            return [list(poly.exterior.coords) for poly in geom.geoms]
        return []
    # Define a new "coordinates" column derived from geometry
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
        tooltip={"text": "Zone: {FLD_ZONE}"}), height=550)


def show_flooding():
    flooding()


if __name__ == "__main__":
    show_flooding()
