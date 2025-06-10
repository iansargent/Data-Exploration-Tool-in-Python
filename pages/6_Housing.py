"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Housing Page (Census)

This data was extracted from the DP04 
"Selected Housing Variables" Dataset
"""

# Necessary imports
import streamlit as st
import pandas as pd
import geopandas as gpd
import leafmap.foliumap as leafmap


def render_mapping():
    st.markdown("<h2 style='color: #4a4a4a;'>VT Housing</h2>", unsafe_allow_html=True)

    m = leafmap.Map(center=[44.26, -72.57], zoom=8, zoom_snap=0.5)
    m.add_basemap("CartoDB.Positron")

    housing_gdf = gpd.read_file('/Users/iansargent/Desktop/ORCA/Steamlit App Testing/Census/VT_HOUSING_ALL.fgb')

    numeric_cols = [col for col in housing_gdf.columns if housing_gdf[col].dtype in ['int64', 'float64']]
    housing_variable = st.selectbox("Select a Housing variable", numeric_cols)

    housing_gdf_map = housing_gdf[["NAME", housing_variable, "geometry"]].dropna()

    m.add_data(
        housing_gdf_map,
        column=housing_variable,
        scheme="NaturalBreaks",
        cmap="Reds",
        legend_title=housing_variable,
        layer_name="Housing",
        color = "pink")

    # --- Always Show the Map ---
    m.to_streamlit(height=600)

    st.subheader("Housing Data")
    st.dataframe(housing_gdf[["NAME", housing_variable]])

    return m

def show_mapping():
    # Display the page
    render_mapping()


if __name__ == "__main__":
    show_mapping()