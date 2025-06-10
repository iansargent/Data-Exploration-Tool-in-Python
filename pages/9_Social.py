"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Social Page (Census)
"""

# Necessary imports
import streamlit as st
import pandas as pd
import geopandas as gpd
import leafmap.foliumap as leafmap


def render_mapping():
    st.markdown("<h2 style='color: #4a4a4a;'>VT Social</h2>", unsafe_allow_html=True)

    m = leafmap.Map(center=[44.26, -72.57], zoom=8, zoom_snap=0.5)
    m.add_basemap("CartoDB.Positron")

    social_gdf = gpd.read_file('/Users/iansargent/Desktop/ORCA/Steamlit App Testing/Census/VT_SOCIAL_ALL.fgb')

    numeric_cols = [col for col in social_gdf.columns if social_gdf[col].dtype in ['int64', 'float64']]
    social_variable = st.selectbox("Select a Social variable", numeric_cols)

    social_gdf_map = social_gdf[["NAME", social_variable, "geometry"]].dropna()

    m.add_data(
        social_gdf_map,
        column=social_variable,
        scheme="NaturalBreaks",
        cmap="Purples",
        legend_title=social_variable,
        layer_name="Social",
        color="lavender")

    # --- Always Show the Map ---
    m.to_streamlit(height=600)

    st.subheader("Social Data")
    st.dataframe(social_gdf[["NAME", social_variable]])

    return m
            
def show_mapping():
    # Display the page
    render_mapping()


if __name__ == "__main__":
    show_mapping()