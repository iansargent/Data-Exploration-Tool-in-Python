"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Zoning Page
"""

# Necessary imports
import streamlit as st
import pandas as pd
import leafmap.foliumap as leafmap
from app_utils import (render_zoning_layer, render_table, render_comparison_table, load_zoning_data)
import geopandas as gpd
from streamlit_extras.metric_cards import style_metric_cards 


def render_mapping():
    st.markdown("<h2 style='color: #4a4a4a;'>VT Zoning</h2>", unsafe_allow_html=True)
    
    m = leafmap.Map(center=[44.26, -72.57], zoom_snap=0.5)
    m.add_basemap("CartoDB.Positron")
    
    load_zoning_data()
    _, filtered_gdf = render_zoning_layer(m)

    # --- Always Show the Map ---
    m.to_streamlit(height=600)
    
    st.header("Land Area")
    c1 = st.container()
    total_acre = filtered_gdf['Acres'].sum()
    c1.metric(label="**Total Acreage**", value=f"{total_acre:,.1f}")
    
    st.subheader("District Type Land Distribution")
    c2, c3, c4 = st.columns(3)
    
    # NOTE: Turn this section into a bar graph
    residential_acre = filtered_gdf[filtered_gdf['District Type'] == "Primarily Residential"]['Acres'].sum()
    c2.metric(label="**Primarily Residential**", value=f"{residential_acre:,.0f} acres")
    c2.metric(label="**Primarily Residential** (%)", value=f"{(residential_acre/total_acre)*100:.1f}%")
    
    mixed_residential_acre = filtered_gdf[filtered_gdf['District Type'] == "Mixed with Residential"]['Acres'].sum()
    c3.metric(label="**Mixed with Residential**", value=f"{mixed_residential_acre:,.0f} acres")
    c3.metric(label="**Mixed with Residential** (%)", value=f"{(mixed_residential_acre/total_acre)*100:.1f}%")
    
    non_residential_acre = filtered_gdf[filtered_gdf['District Type'] == "Nonresidential"]['Acres'].sum()
    c4.metric(label="**Nonresidential**", value=f"{non_residential_acre:,.0f} acres")
    c4.metric(label="**Nonresidential** (%)", value=f"{(non_residential_acre/total_acre)*100:.1f}%")

    style_metric_cards(background_color="whitesmoke", border_left_color="mediumseagreen",)

    # --- Zoning Table and Comparison Below ---
    st.markdown("### Zoning Districts Table")
    selected = render_table(filtered_gdf)
    try:
        if not selected.empty:
            render_comparison_table(selected)
    except Exception as e:
        st.warning(f"No Selected Districts to Compare: {e}")

    return m
            
def show_mapping():
    render_mapping()


if __name__ == "__main__":
    show_mapping()