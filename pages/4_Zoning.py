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


def render_mapping():
    st.markdown("<h2 style='color: #4a4a4a;'>VT Zoning</h2>", unsafe_allow_html=True)
    
    m = leafmap.Map(center=[44.26, -72.57], zoom_snap=0.5)
    m.add_basemap("CartoDB.Positron")
    
    load_zoning_data()
    _, filtered_gdf = render_zoning_layer(m)

    # --- Always Show the Map ---
    m.to_streamlit(height=600)

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