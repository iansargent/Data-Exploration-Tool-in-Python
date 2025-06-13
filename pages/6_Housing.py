"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Housing Page (Census)

"""

# Necessary imports
import streamlit as st
import pandas as pd
import geopandas as gpd
import leafmap.foliumap as leafmap
from app_utils import split_name_col, housing_metrics_vs_statewide, housing_pop_plot, housing_metrics_vs_10yr


def census_housing():
    # Page Title
    st.markdown("<h2 style='color: #4a4a4a;'>VT Housing</h2>", unsafe_allow_html=True)
    # Initialize a leafmap(foliumap) map object centered VT State
    map = leafmap.Map(center=[44.26, -72.57], zoom=8, zoom_snap=0.5)
    # Change the basemap to a light color for contrast
    map.add_basemap("CartoDB.Positron")

    # Read the Census DP04 Housing Characteristics Dataset
    housing_gdf = gpd.read_file('/Users/iansargent/Desktop/ORCA/Steamlit App Testing/Census/VT_HOUSING_ALL.fgb')
    housing_2013 = gpd.read_file('/Users/iansargent/Desktop/ORCA/Steamlit App Testing/Census/VT_HOUSING_ALL_2013.fgb')

    # Split the "name" column into separate "County" and "Jurisdiction" columns
    housing_gdf = split_name_col(housing_gdf)
    housing_2013 = split_name_col(housing_2013)

    # Define the numerical columns in the GeoDataFrame for mapping
    numeric_cols = [col for col in housing_gdf.columns if housing_gdf[col].dtype in ['int64', 'float64']]
    # Add a user select box to choose which variable they want to map
    housing_variable = st.selectbox("Select a Housing variable", numeric_cols)

    # Only include necessary variables for the map dataset to avoid "hover-crowding"
    housing_gdf_map = housing_gdf[["County", "Jurisdiction", housing_variable, "geometry"]].dropna()

    # Add the data to the map (Chloropleth) with a red color scheme
    # NOTE: Using the "NaturalBreaks" system to define color categories (A subjective decision)
    map.add_data(
        housing_gdf_map,
        column=housing_variable,
        scheme="NaturalBreaks",
        cmap="Reds",
        legend_title=housing_variable,
        layer_name="Housing",
        color = "pink")

    # Display the map to the page
    map.to_streamlit(height=600)

    # Census Snapshot section (Housing)
    st.header("Housing Snapshot")
    # Include a source for the dataset (Census DP04 2023 5-year estimates)
    st.markdown("***Data Source***: U.S. Census Bureau. (2023). DP04: Selected Housing Characteristics - " \
    "County Subdivisions, Vermont. 2019-2023 American Community Survey 5-Year Estimates. " \
    "Retrieved June 11, 2025, from https://data.census.gov/")
    # Remind user that delta values are compared to statewide averages
    st.markdown("*Note*: The displayed deviations in the metric cards are comparing values to VT statewide averages.")

    # Allow user to filter on the county and jurisdiction level for tailored reports 
    col1, col2, col3 = st.columns(3)
    with col1:
        county = st.selectbox("**County**", ["All Counties"] + sorted(housing_gdf["County"].dropna().unique()))
    with col2:
        if county != "All Counties":
            jurisdiction_list = sorted(housing_gdf[housing_gdf["County"] == county]["Jurisdiction"].dropna().unique())
        else:
            jurisdiction_list = sorted(housing_gdf["Jurisdiction"].dropna().unique())
        jurisdiction = st.selectbox("**Jurisdiction**", ["All Jurisdictions"] + jurisdiction_list)

    # Create a "filtered" dataset with the selected county and jurisdiction options
    filtered_gdf = housing_gdf.copy()
    if county != "All Counties":
        filtered_gdf = filtered_gdf[filtered_gdf["County"] == county]
    if jurisdiction != "All Jurisdictions":
        filtered_gdf = filtered_gdf[filtered_gdf["Jurisdiction"] == jurisdiction]

    filtered_gdf_2013 = housing_2013.copy()
    if county != "All Counties":
        filtered_gdf_2013 = filtered_gdf_2013[filtered_gdf_2013["County"] == county]
    if jurisdiction != "All Jurisdictions":
        filtered_gdf_2013 = filtered_gdf_2013[filtered_gdf_2013["Jurisdiction"] == jurisdiction]
    
    with col3:
        # Add a selection for the baseline metrics to compare to
        compare_to = st.selectbox(
            label = "**Compared to**",
            options = ["10 Years Ago", "2023 Statewide Averages"],
            index=0
        )

    # If comparison to 10 years ago
    if compare_to == "10 Years Ago":
        # Display formatted housing metrics vs statewide averages
        housing_metrics_vs_10yr(filtered_gdf_2013, filtered_gdf)
    # If comparison to current statewide averages
    elif compare_to == "2023 Statewide Averages":
        # Display formatted housing metrics vs statewide averages
        housing_metrics_vs_statewide(housing_gdf, filtered_gdf)

    # Read in VT historical population data on the census tract level
    # NOTE: Include a source for this as well (VT Open Data Portal)
    pop_df = pd.read_csv('/Users/iansargent/Desktop/ORCA/Steamlit App Testing/Census/VT_Municipal_Pop.csv')
    
    # Display the time series plot of population, housing units, and new housing units
    housing_pop_plot(county, jurisdiction, filtered_gdf, pop_df)
    
    st.markdown("---")

def main():
    # Display the page
    census_housing()


if __name__ == "__main__":
    main()