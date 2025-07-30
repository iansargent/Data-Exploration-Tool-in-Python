"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Social Page (Census)
"""

# Necessary imports
import streamlit as st
from app_utils.census import rename_and_merge_census_cols
from app_utils.census_sections import mapping_tab, compare_tab
from app_utils.data_loading import load_census_data
from app_utils.streamlit_config import streamlit_config


def load_2023_social():
    return load_census_data(
        'https://raw.githubusercontent.com/iansargent/Data-Exploration-Tool-in-Python/main/Data/Census/VT_SOCIAL_ALL.fgb',
    )

def main():
    # Page header
    st.header("Social", divider="grey")
    mapping, snapshot, compare = st.tabs(tabs=["Mapping", "Snapshot", "Compare"])

    social_gdf_2023 = load_2023_social()
    tidy_2023 = rename_and_merge_census_cols(social_gdf_2023)

    with mapping:
        mapping_tab(data=tidy_2023)
        

    # Social Snapshot
    with snapshot:
        st.subheader("Social Snapshot")

    with compare:
        data_dict = {
            "Social 2023" : tidy_2023,
        }
        compare_tab(data_dict)

if __name__ == "__main__":
    streamlit_config()
    main()