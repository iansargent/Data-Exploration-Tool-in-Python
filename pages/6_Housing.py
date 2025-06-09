"""
Ian Sargent
ORCA
Streamlit Data Visualization App

General Mapping Page
"""

# Necessary imports
import streamlit as st
import pandas as pd
import geopandas as gpd
import leafmap.foliumap as leafmap
from app_utils import (get_user_files, is_latitude_longitude, 
                       convert_all_timestamps_to_str, process_uploaded_files, 
                       render_zoning_layer, assign_layer_style, render_table,
                       render_comparison_table, get_lat_lon_cols, load_zoning_data)
from st_aggrid import AgGrid, ColumnsAutoSizeMode, GridOptionsBuilder, GridUpdateMode
from streamlit_extras.dataframe_explorer import dataframe_explorer 


filtered_gdf = pd.DataFrame()
vt_zoning = False

def render_mapping():
    st.markdown("<h2 style='color: #4a4a4a;'>VT Housing</h2>", unsafe_allow_html=True)

    m = leafmap.Map(center=[44.26, -72.57], zoom=8, zoom_snap=0.5)
    m.add_basemap("CartoDB.Positron")

    housing_gdf = gpd.read_file("/Users/iansargent/Desktop/ORCA/house_geo_update.fgb")
    SQ_METERS_TO_SQ_MILES = 1 / 2589988.11 
    housing_gdf["ALAND"] = housing_gdf["ALAND"] * SQ_METERS_TO_SQ_MILES
    housing_gdf["AWATER"] = housing_gdf["AWATER"] * SQ_METERS_TO_SQ_MILES
    housing_gdf = housing_gdf.rename(columns={"ALAND": "Land_Square_Miles", "AWATER": "Water_Square_Miles"})

    numeric_cols = [col for col in housing_gdf.columns if housing_gdf[col].dtype in ['int64', 'float64']]
    housing_variable = st.selectbox("Select a Housing variable", numeric_cols)

    housing_gdf_map = housing_gdf[["NAME.y", housing_variable, "geometry"]].dropna()

    m.add_data(
        housing_gdf_map,
        column=housing_variable,
        scheme="NaturalBreaks",
        cmap="Blues",
        legend_title=housing_variable,
        layer_name="Housing")

    # --- Always Show the Map ---
    m.to_streamlit(height=600)

    st.subheader("Housing Data")
    st.dataframe(housing_gdf[["NAME.y", housing_variable]])

    return m
            
def show_mapping():
    # Display the page
    map = render_mapping()


if __name__ == "__main__":
    show_mapping()