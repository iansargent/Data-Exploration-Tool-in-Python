"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Housing Page (Census)

"""

# Necessary imports
import streamlit as st
import pandas as pd
import requests
import io
from app_utils.census import rename_and_merge_census_cols, load_census_data
from app_utils.housing import housing_pop_plot, housing_snapshot
from app_utils.st_sections import mapping_tab, compare_tab


@st.cache_data
def census_housing():
    housing_gdf_2023 = load_census_data(
        "https://raw.githubusercontent.com/iansargent/Data-Exploration-Tool-in-Python/main/Data/Census/VT_HOUSING_ALL.fgb",
        is_geospatial=True
    )
    
    housing_gdf_2013 = load_census_data(
        "https://raw.githubusercontent.com/iansargent/Data-Exploration-Tool-in-Python/main/Data/Census/VT_HOUSING_ALL_2013.fgb",
        is_geospatial=True
    )
    
    med_value_df = load_census_data(
    "https://raw.githubusercontent.com/iansargent/Data-Exploration-Tool-in-Python/main/Data/Census/med_home_value_by_year.csv")
    
    med_smoc_df = load_census_data(
    "https://raw.githubusercontent.com/iansargent/Data-Exploration-Tool-in-Python/main/Data/Census/med_smoc_by_year.csv")

    tidy_2023 = rename_and_merge_census_cols(housing_gdf_2023)
    return housing_gdf_2023, housing_gdf_2013, med_value_df, med_smoc_df, tidy_2023


def census_housing_page():
    # Page title and tabs
    st.header("Housing", divider="grey")
    mapping, snapshot, compare = st.tabs(tabs=["Mapping", "Snapshot", "Compare"])

    # Define and load the datasets
    housing_gdf_2023, housing_gdf_2013, med_val_df, med_smoc_df, tidy_2023 = census_housing()
    
    # Compute statewide average median home value by year
    statewide_avg_val_df = (med_val_df.groupby("year", as_index=False)["estimate"].mean())
    statewide_avg_smoc_df = (med_smoc_df.groupby(["year", "variable"], as_index=False)["estimate"].mean())

    # st.write(housing_gdf_2023.columns) debug
    ##  The map section ## 
    with mapping:
        mapping_tab(tidy_2023, )
    
    # Housing Snapshot
    with snapshot:
        st.subheader("Housing Snapshot")
        # Include a source for the dataset (Census DP04 2023 5-year estimates)
        st.markdown("***Data Source***: U.S. Census Bureau. (2023). DP04: Selected Housing Characteristics - " \
        "County Subdivisions, Vermont. 2019-2023 American Community Survey 5-Year Estimates. " \
        "Retrieved from https://data.census.gov/")

        # Allow user to filter on the county and jurisdiction level for tailored reports 
        # TODO: (maybe) put the filtering into it's own logic so that we can use it across pages. 
        col1, col2, col3 = st.columns(3)
        # County selection
        with col1:
            county = st.selectbox("**County**", ["All Counties"] + sorted(housing_gdf_2023["County"].dropna().unique()))
        # Jurisdiction selection
        with col2:
            if county != "All Counties":
                jurisdiction_list = sorted(housing_gdf_2023[housing_gdf_2023["County"] == county]["Jurisdiction"].dropna().unique())
            else:
                jurisdiction_list = sorted(housing_gdf_2023["Jurisdiction"].dropna().unique())
            jurisdiction = st.selectbox("**Jurisdiction**", ["All Jurisdictions"] + jurisdiction_list)

        # Create a "filtered" 2023 dataset with the selected county and jurisdiction options
        filtered_gdf_2023 = housing_gdf_2023.copy()
        filtered_gdf_2013 = housing_gdf_2013.copy()
        filtered_med_val_df = med_val_df.copy()
        filtered_med_smoc_df = med_smoc_df.copy()
        if county != "All Counties":
            filtered_gdf_2023 = filtered_gdf_2023[filtered_gdf_2023["County"] == county]
            filtered_gdf_2013 = filtered_gdf_2013[filtered_gdf_2013["County"] == county]
            filtered_med_val_df = filtered_med_val_df[filtered_med_val_df["County"] == county]
            filtered_med_smoc_df = filtered_med_smoc_df[filtered_med_smoc_df["County"] == county]
        
        if jurisdiction != "All Jurisdictions":
            filtered_gdf_2023 = filtered_gdf_2023[filtered_gdf_2023["Jurisdiction"] == jurisdiction]
            filtered_gdf_2013 = filtered_gdf_2013[filtered_gdf_2013["Jurisdiction"] == jurisdiction]
            filtered_med_val_df = filtered_med_val_df[filtered_med_val_df["Jurisdiction"] == jurisdiction]
            filtered_med_smoc_df = filtered_med_smoc_df[filtered_med_smoc_df["Jurisdiction"] == jurisdiction]
        
        # Selection for the baseline comparison (same area 10 years ago OR current statewide averages)
        with col3:
            # Add a selection for the baseline metrics to compare to
            compare_to = st.selectbox(
                label = "**Comparison Basis**",
                options = ["2013 Local Data (10-Year Change)", "2023 Vermont Statewide Averages"],
                index=0)

        # Read in VT historical population data on the census tract level
        # NOTE: Include a source for this as well (VT Open Data Portal)
        pop_url = "https://raw.githubusercontent.com/iansargent/Data-Exploration-Tool-in-Python/main/Data/Census/VT_Historical_Population.csv"
        response = requests.get(pop_url, verify=False)
        pop_df = pd.read_csv(io.StringIO(response.text))    
        # Display the time series plot of population, housing units, and new housing units
        housing_pop_plot(county, jurisdiction, filtered_gdf_2023, pop_df)
        
        # Display formatted housing metrics vs statewide averages
        housing_snapshot(county, jurisdiction, 
                        filtered_gdf_2013, filtered_gdf_2023, housing_gdf_2023, 
                        filtered_med_val_df, filtered_med_smoc_df, 
                        statewide_avg_val_df, statewide_avg_smoc_df, compare_to)
        
    with compare:
        data_dict = {
            "Housing 2023" : tidy_2023,
            "Housing 2013" : rename_and_merge_census_cols(housing_gdf_2013)
        }
        compare_tab(data_dict)
        
def show_housing():
    # Display the page
    census_housing_page()


if __name__ == "__main__":
    show_housing()