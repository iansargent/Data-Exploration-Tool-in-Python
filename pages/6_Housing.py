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
import matplotlib.cm as cm
import matplotlib.colors as colors
import pydeck as pdk
import pyogrio
import requests
import io
from app_utils import (split_name_col, housing_metrics_vs_statewide, 
                       housing_pop_plot, housing_snapshot, load_med_value_by_year)


def census_housing():
    # Page title
    st.header("Housing", divider="grey")

    # Read the Census Housing Datasets
    housing_gdf_2023 = load_2023_housing()
    housing_gdf_2013 = load_2013_housing()
    med_val_df = load_med_value_by_year()
    
    # Split the "name" column into separate "County" and "Jurisdiction" columns
    housing_gdf_2023 = split_name_col(housing_gdf_2023)
    housing_gdf_2013 = split_name_col(housing_gdf_2013)
    med_val_df = split_name_col(med_val_df)
    # Compute statewide average median home value by year
    statewide_avg_val_df = (med_val_df.groupby("year", as_index=False)["estimate"].mean())
    statewide_avg_smoc_df = (med_smoc_df.groupby(["year", "variable"], as_index=False)["estimate"].mean())

    ##  The map section ## 
    st.subheader("Mapping")
    
    # select the combination of vars we're interested in
    filtered_2023 = filter_dataframe(tidy_2023, filter_columns=[ "Category", "Subcategory", "Variable", "Measure"])

    # Project geometry to latitude and longitude coordinates
    filtered_2023 = filtered_2023.to_crs(epsg=4326)

    # Normalize the housing variable for monochromatic coloring
    vmin = filtered_2023['Value'].min()
    vmax = filtered_2023['Value'].max()
    norm = colors.Normalize(vmin=vmin, vmax=vmax)
    cmap = cm.get_cmap("Reds")

    # Convert colors to [R, G, B, A] values
    filtered_2023["fill_color"] = filtered_2023['Value'].apply(
        lambda x: [int(c * 255) for c in cmap(norm(x))[:3]] + [180])

    # Convert the geometry column to GeoJSON coordinates
    filtered_2023["coordinates"] = filtered_2023.geometry.apply(
        lambda geom: geom.__geo_interface__["coordinates"])

    # Chloropleth map layer
    polygon_layer = pdk.Layer(
        "PolygonLayer",
        data=filtered_2023,
        get_polygon="coordinates[0]",
        get_fill_color="fill_color",
        pickable=True,
        auto_highlight=True)

    # Set the map center and zoom level
    view_state = pdk.ViewState(latitude=44.26, longitude=-72.57, min_zoom=6.5, zoom=7)

    # Display the map to the page
    st.pydeck_chart(pdk.Deck(
        layers=[polygon_layer],
        initial_view_state=view_state,
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
        tooltip={
             "text": "{Jurisdiction}: {Value}"
             }
    ), height=550)



    
    ## Census Snapshot section (Housing) ##
    st.markdown("---")

    st.subheader("Housing Snapshot")
    # Include a source for the dataset (Census DP04 2023 5-year estimates)
    st.markdown("***Data Source***: U.S. Census Bureau. (2023). DP04: Selected Housing Characteristics - " \
    "County Subdivisions, Vermont. 2019-2023 American Community Survey 5-Year Estimates. " \
    "Retrieved June 11, 2025, from https://data.census.gov/")

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
    response = requests.get(pop_url, verify=False)  # disables SSL verification
    pop_df = pd.read_csv(io.StringIO(response.text))    
    # Display the time series plot of population, housing units, and new housing units
    housing_pop_plot(county, jurisdiction, filtered_gdf_2023, pop_df)
    
    # Display formatted housing metrics vs statewide averages
    housing_snapshot(county, jurisdiction, 
                     filtered_gdf_2013, filtered_gdf_2023, housing_gdf_2023, 
                     filtered_med_val_df, filtered_med_smoc_df, 
                     statewide_avg_val_df, statewide_avg_smoc_df, compare_to)


def show_housing():
    # Display the page
    census_housing()


if __name__ == "__main__":
    show_housing()