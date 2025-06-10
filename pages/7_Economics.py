"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Economics Page (Census)
"""

# Necessary imports
import streamlit as st
import pandas as pd
import geopandas as gpd
import leafmap.foliumap as leafmap


def render_mapping():
    st.markdown("<h2 style='color: #4a4a4a;'>VT Economics</h2>", unsafe_allow_html=True)

    m = leafmap.Map(center=[44.26, -72.57], zoom=8, zoom_snap=0.5)
    m.add_basemap("CartoDB.Positron")

    econ_gdf = gpd.read_file('/Users/iansargent/Desktop/ORCA/Steamlit App Testing/Census/VT_ECONOMIC_ALL.fgb')

    numeric_cols = [col for col in econ_gdf.columns if econ_gdf[col].dtype in ['int64', 'float64']]
    econ_variable = st.selectbox("Select an economic variable", numeric_cols)

    econ_gdf_map = econ_gdf[["NAME", econ_variable, "geometry"]].dropna()

    m.add_data(
        econ_gdf_map,
        column=econ_variable,
        scheme="NaturalBreaks",
        cmap="Greens",
        legend_title=econ_variable,
        layer_name="Economics",
        color="palegreen")

    # --- Always Show the Map ---
    m.to_streamlit(height=600)

    st.subheader("Economic Data")
    st.dataframe(econ_gdf[["NAME", econ_variable]])

    return m
            
def show_mapping():
    # Display the page
    render_mapping()


if __name__ == "__main__":
    show_mapping()