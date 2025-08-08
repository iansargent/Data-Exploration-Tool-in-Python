"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Housing Page (Census)

"""

# Necessary imports
import streamlit as st
import pandas as pd
from app_utils.census import rename_and_merge_census_cols
from app_utils.data_loading import load_census_data_dict, load_data
from app_utils.housing import housing_snapshot
from app_utils.census_sections import mapping_tab, compare_tab
from app_utils.streamlit_config import streamlit_config



def census_housing():
    census_data_dict = load_census_data_dict(
        sources = {
            "Housing_2023" : "VT_HOUSING_ALL.fgb",
            "Housing_2013" : "VT_HOUSING_ALL_2013.fgb",
            "median_value" : "med_home_value_by_year.csv",
            "median_smoc" : "med_smoc_by_year.csv",
            "vt_historic_population": "VT_Historic_Population.csv"
        }
    )

    return census_data_dict

def main():
    # Page title and tabs
    st.header("Housing", divider="grey")
    
    mapping, snapshot, compare = st.tabs(tabs=["Mapping", "Snapshot", "Compare"])

    # Define a list of loaded datasets
    housing_dfs = census_housing()

    # Define the tidy dataset for map filtering
    tidy_2023 = rename_and_merge_census_cols(housing_dfs["Housing_2023"])

    with mapping:
        mapping_tab(data=tidy_2023, map_color="Reds")
    
    with snapshot:
        housing_snapshot(housing_dfs)
        
    with compare:
        housing_gdf_2013 = housing_dfs["Housing_2023"]
        housing_dict = {
            "Housing 2023" : tidy_2023,
            "Housing 2013" : rename_and_merge_census_cols(housing_gdf_2013)
        }
        compare_tab(housing_dict)


if __name__ == "__main__":
    streamlit_config()
    main()