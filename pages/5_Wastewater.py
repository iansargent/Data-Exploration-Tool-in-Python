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
from app_utils.df_filtering import filter_dataframe_multiselect
from app_utils.data_loading import load_soil_septic
from app_utils.streamlit_config import streamlit_config



def select_soil_suitability():
    ## dictionary of RPCs to select from
    rpcs = {
        "Addison County": "ACRPC",
        "Bennington County": "BCRC",
        "Chittenden County": "CCRPC",
        "Central Vermont": "CVRPC",
        "Lamoille County": "LCPC",
        "Mount Ascutney": "MARC",
        "Northeastern Vermont": "NVDA",
        "Northwest Regional": "NWRPC",
        "Rutland Regional": "RRPC",
        "Two Rivers-Ottauquechee": "TRORC",
        "Windham": "WRC",
    }
    
    # Set columns to display the filter boxes
    column1, column2, column_3= st.columns(3)

    # On the left, display the RPC selection
    with column1:
        rpc = st.selectbox("Regional Planning Comission", options=rpcs.keys(), index=0)
        selected_rpc = rpcs.get(rpc)

    # LAND SUITABILITY DATA
    suit_gdf = load_soil_septic(selected_rpc)

    # Filter by Jurisdiction (or All Jurisdictions)
    filtered_gdf, filter_selections = filter_dataframe_multiselect(
        suit_gdf,
        filter_columns=["Jurisdiction", "Suitability"],
        presented_cols=["Municipality", "Soil Suitability"],
        allow_all={
            "Jurisdiction" : True,
            "Suitability": True
        },
        defaults = {
            "Suitability": ['Well Suited', 'Moderately Suited']
        },
        passed_cols=[column2, column_3]
    )
    # get a total_acerage of all the jurisdictions selected. re-filter the gdf JUST on jurisdiction
    total_acreage = suit_gdf[suit_gdf['Jurisdiction'].isin(filter_selections['Jurisdiction'])]['Acres'].sum()
    return filtered_gdf, total_acreage

def main():
    # Page header
    st.header("Wastewater Infrastructure", divider="grey")
    suit_gdf, total_acreage = select_soil_suitability()
    suit_gdf = process_soil_data(suit_gdf)

    map_col, legend_col = st.columns([4, 1])
    map = plot_wastewater(suit_gdf)
    map_col.pydeck_chart(map)
    with legend_col:
        render_soil_colormap()

    # Suitability metric cards
    land_suitability_metric_cards(suit_gdf, total_acreage)


if __name__ == "__main__":
    streamlit_config()
    main()