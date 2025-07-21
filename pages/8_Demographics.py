"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Demographics Page (Census)
"""

# Necessary imports
import streamlit as st
from app_utils.census import rename_and_merge_census_cols, load_census_data
from app_utils.st_sections import mapping_tab, compare_tab


@st.cache_data
def load_2023_demographics():
    return load_census_data(
        "https://raw.githubusercontent.com/iansargent/Data-Exploration-Tool-in-Python/main/Data/Census/VT_DEMOGRAPHIC_ALL.fgb",
        is_geospatial=True
        )

def render_demographics():
    # Page header
    st.header("Demographics", divider="grey")   
    mapping, snapshot, compare = st.tabs(tabs=["Mapping", "Report", "Compare"])

    demographics_gdf_2023 = load_2023_demographics()
    tidy_2023 = rename_and_merge_census_cols(demographics_gdf_2023)

    with mapping:
        mapping_tab(data=tidy_2023)

    # Demographic Report
    with snapshot:
        st.subheader("Demographic Report")

    with compare:
        data_dict = {
            "Demographics 2023" : tidy_2023,
        }
        compare_tab(data_dict)   

if __name__ == "__main__":
    render_demographics()