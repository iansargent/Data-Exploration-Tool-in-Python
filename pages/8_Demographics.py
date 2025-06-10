"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Demographics Page (Census)
"""

# Necessary imports
import streamlit as st
import pandas as pd
import geopandas as gpd
import leafmap.foliumap as leafmap


def render_mapping():
    st.markdown("<h2 style='color: #4a4a4a;'>VT Demographics</h2>", unsafe_allow_html=True)

    m = leafmap.Map(center=[44.26, -72.57], zoom=8, zoom_snap=0.5)
    m.add_basemap("CartoDB.Positron")

    demographic_gdf = gpd.read_file('/Users/iansargent/Desktop/ORCA/Steamlit App Testing/Census/VT_DEMOGRAPHIC_ALL.fgb')

    numeric_cols = [col for col in demographic_gdf.columns if demographic_gdf[col].dtype in ['int64', 'float64']]
    demographic_variable = st.selectbox("Select a Demographic variable", numeric_cols)

    demographic_gdf_map = demographic_gdf[["NAME", demographic_variable, "geometry"]].dropna()

    m.add_data(
        demographic_gdf_map,
        column=demographic_variable,
        scheme="NaturalBreaks",
        cmap="Blues",
        legend_title=demographic_variable,
        layer_name="Demographics",
        color="lightblue")

    # --- Always Show the Map ---
    m.to_streamlit(height=600)

    st.subheader("Demographic Data")
    st.dataframe(demographic_gdf[["NAME", demographic_variable]])

    return m
            
def show_mapping():
    # Display the page
    render_mapping()


if __name__ == "__main__":
    show_mapping()