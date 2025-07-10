"""
Open Research Community Accelorator
Vermont Data App

Wastewater Utility Functions
"""

import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards 


def land_suitability_metric_cards(gdf):
    """
    Creates and displays a set of metric cards for land suitability statistics:
    % Well Suited Land, Acreage of Well Suited Land,
    % Moderately Suited Land, Acreage of Moderately Suited Land.

    @param gdf: A geopandas GeoDataFrame object.
    """

    st.subheader("Land Suitability Overview")

    # Filter GeoDataFrame by Jurisdiction HERE!
    
    
    # Filter by suitability categories
    total_acres = gdf["Acres"].sum()

    well_suited = gdf[gdf["Suitability"] == "Well Suited"]
    mod_suited = gdf[gdf["Suitability"] == "Moderately Suited"]

    well_acres = well_suited["Acres"].sum()
    mod_acres = mod_suited["Acres"].sum()

    well_pct = (well_acres / total_acres) * 100 if total_acres > 0 else 0
    mod_pct = (mod_acres / total_acres) * 100 if total_acres > 0 else 0

    # Layout: 2 rows with 2 columns each
    col1, col2 = st.columns(2)

    col1.metric(label="**Well Suited** Land", value=f"{well_pct:.1f}%")
    col2.metric(label="**Well Suited Acreage**", value=f"{well_acres:,.0f} acres")

    style_metric_cards(
        background_color="whitesmoke",
        border_left_color="#2ca02c",
        box_shadow=True,
        border_size_px=0.5
    )
    
    col3, col4 = st.columns(2)
    
    col3.metric(label="**Moderately Suited** Land", value=f"{mod_pct:.1f}%")
    col4.metric(label="**Moderately Suited Acreage**", value=f"{mod_acres:,.0f} acres")

