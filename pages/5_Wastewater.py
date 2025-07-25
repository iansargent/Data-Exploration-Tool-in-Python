"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Wastewater Page
"""

# Necessary imports
import streamlit as st
import geopandas as gpd
import pydeck as pdk
import requests
from io import BytesIO
from app_utils.data_cleaning import convert_all_timestamps_to_str
from app_utils.wastewater import land_suitability_metric_cards


@st.cache_data
def load_soil_septic(rpc):
    land_suit_url = f"https://github.com/VERSO-UVM/Vermont-Livability-Map/raw/main/data/{rpc}_Soil_Septic.fgb"
    suit_response = requests.get(land_suit_url)
    suit_response.raise_for_status()
    suit_gdf = gpd.read_file(BytesIO(suit_response.content))
    suit_gdf = suit_gdf.to_crs("EPSG:4326")
    return suit_gdf
    

def render_wastewater():
    # Page header
    st.header("Wastewater Infrastructure")

    # Set columns to display the filter boxes
    column1, column2 = st.columns(2)
    # Define a list of RPCs for the RPC filter selection box
    rpcs = ["ACRPC", "BCRC", "CCRPC", "CVRPC", "LCPC", "MARC", "NVDA", "NWRPC", "RRPC", "TRORC", "WRC"]
    
    # On the left, display the RPC selection
    with column1:
        selected_rpc = st.selectbox("RPC", options=rpcs, index=0)

    # Take the index of that selection for data loading
    i = rpcs.index(selected_rpc)

    # LAND SUITABILITY DATA
    suit_gdf = load_soil_septic(rpcs[i])
    suit_gdf["geometry"] = suit_gdf["geometry"].simplify(0.0001, preserve_topology=True)

    # Filter by Jurisdiction (or All Jurisdictions)
    jurisdictions = ["All Jurisdictions"] + sorted(suit_gdf["Jurisdiction"].dropna().unique().tolist())
    with column2:
        selected_jurisdiction = st.multiselect("Jurisdiction", options=jurisdictions, default=["All Jurisdictions"])
    if selected_jurisdiction and "All Jurisdictions" not in selected_jurisdiction:
        suit_gdf = suit_gdf[suit_gdf["Jurisdiction"].isin(selected_jurisdiction)]
    # Convert all timestamps to string for easier mapping
    suit_gdf = convert_all_timestamps_to_str(suit_gdf)

    # Define soil suitability colors to be shown on the map
    category_colors = {"Well Suited": [44, 160, 44, 180],
                       "Moderately Suited": [255, 204, 0, 180]}
    suit_filtered = suit_gdf[suit_gdf["Suitability"].isin(category_colors.keys())].copy()        
    suit_filtered["fill_color"] = suit_filtered["Suitability"].apply(lambda x: category_colors.get(x))

    # Extract the coordinates from the geometry column to map the polygon layer
    def extract_2d_coords(g):
        return [[ [x, y] for x, y in g.exterior.coords ]]
    suit_filtered["polygon_coords"] = suit_filtered.geometry.apply(extract_2d_coords)

    # Land suitability map layer
    soil_layer = pdk.Layer(
        "PolygonLayer",
        data=suit_filtered,
        get_polygon="polygon_coords",
        get_fill_color="fill_color",
        get_line_color=[20, 20, 20, 180],
        pickable=True,
        auto_highlight=True,
        stroked=True,
        filled=True
    )

    # Calculate the center and zoom level of the map
    bounds = suit_filtered.total_bounds
    center_lon = (bounds[0] + bounds[2]) / 2
    center_lat = (bounds[1] + bounds[3]) / 2
    view_state = pdk.ViewState(latitude=center_lat, longitude=center_lon, zoom=9)

    # Display the map to the page
    st.pydeck_chart(pdk.Deck(
        layers=[soil_layer],
        initial_view_state=view_state,
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
    ), use_container_width=True)

    # Suitability metric cards
    land_suitability_metric_cards(suit_filtered)
    
            
def show_wastewater(): 
    render_wastewater()


if __name__ == "__main__":
    show_wastewater()