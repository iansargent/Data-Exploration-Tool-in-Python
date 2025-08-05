"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Demographics Page (Census)
"""

# Necessary imports
import streamlit as st
from app_utils.census import rename_and_merge_census_cols
from app_utils.census_sections import mapping_tab, compare_tab
from app_utils.data_loading import load_census_data
from app_utils.streamlit_config import streamlit_config
from app_utils.demographic import demographic_snapshot


def census_demographics():
    demog_gdf_2023 = load_census_data(
        "https://raw.githubusercontent.com/iansargent/Data-Exploration-Tool-in-Python/main/Data/Census/VT_DEMOGRAPHIC_ALL.fgb",
        )
    demog_dfs = [demog_gdf_2023]
    return demog_dfs


def main():
    # Page title and tabs
    st.header("Demographics", divider="grey")   
    
    mapping, snapshot, compare = st.tabs(tabs=["Mapping", "Snapshot", "Compare"])

    demog_dfs = census_demographics()
    demographics_gdf_2023 = demog_dfs[0]
    tidy_2023 = rename_and_merge_census_cols(demographics_gdf_2023)

    with mapping:
        mapping_tab(data=tidy_2023, map_color="Blues")

    ## Census Snapshot section (Housing) ##
    with snapshot:
        demographic_snapshot(demog_dfs)
        st.subheader("Demographic Snapshot")

    with compare:
        data_dict = {"Demographics 2023" : tidy_2023}
        compare_tab(data_dict)   

if __name__ == "__main__":
    streamlit_config()
    main()