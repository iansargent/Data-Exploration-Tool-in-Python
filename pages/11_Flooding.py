"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Flooding Page (FEMA)
"""

# Necessary imports
import streamlit as st
import geopandas as gpd
from app_utils.data_loading import load_flood_data
from app_utils.flooding import *
from app_utils.streamlit_config import streamlit_config

def main():
    # Page header
    st.header("Mandatory Flood Insurance")

    # Load the FEMA flood hazard zones dataset and clean it 
    flood_gdf = load_flood_data()
    flood_gdf = process_flood_gdf(flood_gdf)

    # create and display map
    map = plot_flood_gdf(flood_gdf)
    st.pydeck_chart(map)


if __name__ == "__main__":
    streamlit_config()
    main()
