"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Wastewater Page
"""

# Necessary imports
import streamlit as st
import geopandas as gpd
from app_utils.data_cleaning import convert_all_timestamps_to_str
from app_utils.wastewater import *
from app_utils.df_filtering import filter_wrapper
from app_utils.data_loading import load_soil_septic_single
from app_utils.streamlit_config import streamlit_config


def main():
    st.header("Wastewater Infrastructure", divider="grey")
    column1, *cols = st.columns(3)
    rpc = get_soil_rpc(column1)
    suit_gdf = load_soil_septic_single(rpc)

    filter_state = filter_wrapper(
        df = suit_gdf,
        filter_columns=["Jurisdiction", "Suitability"],
        presented_cols=["Municipality", "Soil Suitability"],
        allow_all={
            "Jurisdiction" : True,
            "Suitability": True
        },
        defaults = {
            "Suitability": ['Well Suited', 'Moderately Suited']
        },
        passed_cols=cols ## so that we start at col2 
    )
    filtered_gdf = filter_state.apply_filters(suit_gdf)
    filtered_gdf = process_soil_data(filtered_gdf)

    map_col, legend_col = st.columns([4, 1])
    map = plot_wastewater(filtered_gdf)
    map_col.pydeck_chart(map)
    with legend_col:
        render_soil_colormap()

    # Suitability metric cards
    total_acreage = filtered_gdf[filtered_gdf['Jurisdiction'].isin(filter_state.selections['Jurisdiction'])]['Acres'].sum()
    land_suitability_metric_cards(filtered_gdf, total_acreage)


if __name__ == "__main__":
    streamlit_config()
    main()