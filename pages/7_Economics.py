"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Economics Page (Census)
"""

# Necessary imports
import streamlit as st
import pydeck as pdk
import pyogrio
from app_utils.economic import economic_snapshot
from app_utils.census import rename_and_merge_census_cols, load_census_data
from app_utils.st_sections import mapping_tab, compare_tab


@st.cache_data
def load_2023_economics():
    return load_census_data(
        "https://raw.githubusercontent.com/iansargent/Data-Exploration-Tool-in-Python/main/Data/Census/VT_ECONOMIC_ALL.fgb",
        is_geospatial=True
        )


def census_economics_page():
    # Page header
    st.header("Economics", divider="grey")

    mapping, snapshot, compare = st.tabs(tabs=["Mapping", "Snapshot", "Compare"])

    econ_gdf_2023 = load_2023_economics()
    tidy_2023 = rename_and_merge_census_cols(econ_gdf_2023)

    with mapping:
        mapping_tab(tidy_2023)

    ## Economic Snapshot
    with snapshot:
        st.subheader("Economic Snapshot")
        st.markdown("***Data Source***: U.S. Census Bureau. (2023). DP03: Selected Economic Characteristics - " \
        "County Subdivisions, Vermont. 2019-2023 American Community Survey 5-Year Estimates. " \
        "Retrieved from https://data.census.gov/")
        # Allow user to filter on the county and jurisdiction level for tailored reports 
        # TODO: (maybe) put the filtering into it's own logic so that we can use it across pages. 
        col1, col2, col3 = st.columns(3)
        # County selection
        with col1:
            county = st.selectbox("**County**", ["All Counties"] + sorted(econ_gdf_2023["County"].dropna().unique()))
        # Jurisdiction selection
        with col2:
            if county != "All Counties":
                jurisdiction_list = sorted(econ_gdf_2023[econ_gdf_2023["County"] == county]["Jurisdiction"].dropna().unique())
            else:
                jurisdiction_list = sorted(econ_gdf_2023["Jurisdiction"].dropna().unique())
            jurisdiction = st.selectbox("**Jurisdiction**", ["All Jurisdictions"] + jurisdiction_list)

        # Create a "filtered" 2023 dataset with the selected county and jurisdiction options
        filtered_gdf_2023 = econ_gdf_2023.copy()
        
        if county != "All Counties":
            filtered_gdf_2023 = filtered_gdf_2023[filtered_gdf_2023["County"] == county]
        
        if jurisdiction != "All Jurisdictions":
            filtered_gdf_2023 = filtered_gdf_2023[filtered_gdf_2023["Jurisdiction"] == jurisdiction]
        
        # Selection for the baseline comparison (same area 10 years ago OR current statewide averages)
        with col3:
            # Add a selection for the baseline metrics to compare to
            compare_to = st.selectbox(
                label = "**Comparison Basis**",
                options = ["2013 Local Data (10-Year Change)", "2023 Vermont Statewide Averages"],
                index=0)

        
        # Display formatted housing metrics vs statewide averages
        economic_snapshot(county, jurisdiction, filtered_gdf_2023)

    with compare:
        econ_dict = {
            "Economics 2023" : tidy_2023,
        }
        compare_tab(econ_dict)
            
def show_economics():
    # Display the page
    census_economics_page()


if __name__ == "__main__":
    show_economics()