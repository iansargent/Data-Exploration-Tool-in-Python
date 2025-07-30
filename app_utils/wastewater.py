"""
Open Research Community Accelorator
Vermont Data App

Wastewater Utility Functions
"""

import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards 
from app_utils.color import render_rgba_colormap_legend
from app_utils.mapping import *
from app_utils.data_cleaning import convert_all_timestamps_to_str

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


### cleaning and mapping functions  ## 
def add_soil_tooltip(gdf):
    return add_tooltip_from_dict(gdf, label_to_col={
        "Suitability" : "Suitability",
        "Acreage": "Acres_fmt",
        "Municipality":"Jurisdiction"
    })

def define_soil_colors(gdf):
    gdf["rgba_color"] = gdf["Suitability"].apply(lambda x: SOIL_COLOR.get(x))
    return gdf

def clean_soil_frame(gdf):
    gdf["polygon_coords"] = gdf.geometry.apply(extract_2d_coords)
    gdf["Acres_fmt"] = gdf["Acres"].map(lambda x: f"{x:,.0f}")
    gdf = gdf[['Suitability', 'Jurisdiction', 'Acres_fmt', 'geometry', 'rgba_color', "Acres"]].copy()
    return gdf

def plot_wastewater(gdf):
    return map_gdf_single_layer(gdf)

def extract_2d_coords(g):
    return [[ [x, y] for x, y in g.exterior.coords ]]

def render_soil_colormap():
    """
    Hard-coded wrapper to map our hardcoded soil_color global above. 
    """
    render_rgba_colormap_legend(SOIL_COLOR)

def process_soil_data(gdf):
    """
    Wrapper for multiple functions to clean and add colors to a soil frame
    """
    gdf = define_soil_colors(gdf)
    gdf = clean_soil_frame(gdf)
    gdf = add_soil_tooltip(gdf)
    gdf = convert_all_timestamps_to_str(gdf)
    return gdf
