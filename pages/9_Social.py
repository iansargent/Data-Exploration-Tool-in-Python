"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Social Page (Census)
"""

# Necessary imports
import streamlit as st
from app_utils.census import load_census_data, rename_and_merge_census_cols
from app_utils.st_sections import mapping_tab, compare_tab

@st.cache_data
def load_2023_social():
    return load_census_data(
        'https://raw.githubusercontent.com/iansargent/Data-Exploration-Tool-in-Python/main/Data/Census/VT_SOCIAL_ALL.fgb',
        is_geospatial=True)


def render_social():
    # Page header
    st.header("Social", divider="grey")
    mapping, snapshot, compare = st.tabs(tabs=["Mapping", "Report", "Compare"])

    social_gdf_2023 = load_2023_social()
    tidy_2023 = rename_and_merge_census_cols(social_gdf_2023)

    with mapping:
        mapping_tab(data=tidy_2023)
        

    # Social Report
    with snapshot:
        st.subheader("Social Report")

    with compare:
        data_dict = {
            "Social 2023" : tidy_2023,
        }
        compare_tab(data_dict)

            
def show_social():
    # Display the page
    render_social()


if __name__ == "__main__":
    show_social()