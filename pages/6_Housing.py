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
from app_utils.data_loading import load_census_data
from app_utils.housing import housing_snapshot
from app_utils.census_sections import mapping_tab, compare_tab
from app_utils.streamlit_config import streamlit_config


def census_housing():
    housing_gdf_2023 = load_census_data(
        "https://raw.githubusercontent.com/iansargent/Data-Exploration-Tool-in-Python/main/Data/Census/VT_HOUSING_ALL.fgb",
    )
    housing_gdf_2013 = load_census_data(
        "https://raw.githubusercontent.com/iansargent/Data-Exploration-Tool-in-Python/main/Data/Census/VT_HOUSING_ALL_2013.fgb",
    )
    med_value_df = load_census_data(
    "https://raw.githubusercontent.com/iansargent/Data-Exploration-Tool-in-Python/main/Data/Census/med_home_value_by_year.csv"
    )
    med_smoc_df = load_census_data(
    "https://raw.githubusercontent.com/iansargent/Data-Exploration-Tool-in-Python/main/Data/Census/med_smoc_by_year.csv"
    )
    
    housing_dfs = [housing_gdf_2023, med_value_df, med_smoc_df, housing_gdf_2013]

    return housing_dfs


def main():
    # Page title and tabs
    st.header("Housing", divider="grey")
    mapping, snapshot, compare = st.tabs(tabs=["Mapping", "Snapshot", "Compare"])

    # Define a list of loaded datasets
    housing_dfs = census_housing()
    # The main DataFrame is the first in the list
    housing_gdf_2023 = housing_dfs[0]
    # Define the tidy dataset for map filtering
    tidy_2023 = rename_and_merge_census_cols(housing_gdf_2023)

    with mapping:
        mapping_tab(data=tidy_2023, map_color="Reds")
    
    with snapshot:
        housing_snapshot(housing_dfs)
        
    with compare:
        housing_gdf_2013 = housing_dfs[-1]
        housing_dict = {
            "Housing 2023" : tidy_2023,
            "Housing 2013" : rename_and_merge_census_cols(housing_gdf_2013)
        }
        compare_tab(housing_dict)


if __name__ == "__main__":
    streamlit_config()
    main()