"""
Open Research Community Accelorator
Vermont Data App

Wastewater Utility Functions
"""

import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards 
import pydeck as pdk
from app_utils.color import render_rgba_colormap_legend
import json



SOIL_COLOR = {
    "Well Suited": [44, 160, 44, 180],
    "Moderately Suited": [255, 204, 0, 180],
    "Marginally Suited" : [253, 126, 20, 180],
    "Not Suited" : [ 220, 53, 69, 180],
    "Not Rated" : [108, 117, 125, 180]
    }

def land_suitability_metric_cards(gdf, total_acres):
    """
    Displays metric cards for all present Suitability values,
    with % and acreage side-by-side for each category.
    """

    st.subheader("Land Suitability Overview")

    # Group and calculate stats
    summary = (
        gdf.groupby("Suitability")["Acres"]
        .sum()
        .reset_index()
        .sort_values("Acres", ascending=False)
    )
    summary["Percent"] = (summary["Acres"] / total_acres * 100) if total_acres > 0 else 0

    # create metrics  from df rows
    for _, row in summary.iterrows():
        col1, col2 = st.columns(2)
        col1.metric(label=f"**{row['Suitability']}** (%)", value=f"{row['Percent']:.1f}%")
        col2.metric(label=f"**{row['Suitability']}** Acreage", value=f"{row['Acres']:,.0f} acres")

    style_metric_cards(
        background_color="whitesmoke",
        border_left_color="#2ca02c",
        box_shadow=True,
        border_size_px=0.5
    )

def plot_wastewater(gdf):
    # Define soil suitability colors to be shown on the map
    gdf["rgba_color"] = gdf["Suitability"].apply(lambda x: SOIL_COLOR.get(x))
    gdf["polygon_coords"] = gdf.geometry.apply(extract_2d_coords)
    gdf["Acres_fmt"] = gdf["Acres"].map(lambda x: f"{x:,.0f}")
    gdf_map = gdf[['Suitability', 'Jurisdiction', 'Acres_fmt', 'geometry', 'rgba_color']].copy()
    geo_json = json.loads(gdf_map.to_json())

    # Land suitability map layer 
    soil_layer = pdk.Layer(
        "GeoJsonLayer",
        data=geo_json,
        get_fill_color="properties.rgba_color",
        get_line_color=[20, 20, 20, 180],
        pickable=True,
        auto_highlight=True,
        stroked=True,
        filled=True
    )

    # Calculate the center and zoom level of the map
    bounds = gdf.total_bounds
    center_lon = (bounds[0] + bounds[2]) / 2
    center_lat = (bounds[1] + bounds[3]) / 2
    view_state = pdk.ViewState(latitude=center_lat, longitude=center_lon, zoom=9)

    tooltip = {"html": "<b> Suitability: </b> {Suitability}  <br/> <b> Acreage: </b> {Acres_fmt} <br/> <b> Municipality: </b> {Jurisdiction}"}

    # create and return the map
    map = pdk.Deck(
        layers=[soil_layer],
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
    )
    return map


def extract_2d_coords(g):
    return [[ [x, y] for x, y in g.exterior.coords ]]


def render_soil_colormap():
    """
    Hard-coded wrapper to map our hardcoded soil_color global above. 
    """
    render_rgba_colormap_legend(SOIL_COLOR)