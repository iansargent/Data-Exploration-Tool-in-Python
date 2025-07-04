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

    # Read the Census DP04 Housing Characteristics Dataset
    housing_gdf_2023 = pyogrio.read_dataframe('https://raw.githubusercontent.com/iansargent/Data-Exploration-Tool-in-Python/main/Data/Census/VT_HOUSING_ALL.fgb')
    housing_gdf_2013 = pyogrio.read_dataframe('https://raw.githubusercontent.com/iansargent/Data-Exploration-Tool-in-Python/main/Data/Census/VT_HOUSING_ALL_2013.fgb')
    med_val_df = load_med_value_by_year()
    
    # Split the "name" column into separate "County" and "Jurisdiction" columns
    housing_gdf_2023 = split_name_col(housing_gdf_2023)
    housing_gdf_2013 = split_name_col(housing_gdf_2013)
    med_val_df = split_name_col(med_val_df)
    # Compute statewide average median home value by year
    statewide_avg_df = (med_val_df.groupby("year", as_index=False)["estimate"].mean())

    # The map section
    st.subheader("Mapping")
    # Define the numerical columns in the GeoDataFrame for mapping
    numeric_cols = [col for col in housing_gdf_2023.columns if housing_gdf_2023[col].dtype in ['int64', 'float64']]
    # Add a user select box to choose which variable they want to map
    housing_variable = st.selectbox("Select a Housing variable", numeric_cols)

    # Project geometry to latitude and longitude coordinates
    housing_gdf_2023 = housing_gdf_2023.to_crs(epsg=4326)
    # Select only necessary columns for the dataframe being mapped. Drop any NA values
    housing_gdf_2023_map = housing_gdf_2023[["County", "Jurisdiction", housing_variable, "geometry"]].dropna().copy()

    # Normalize the housing variable for monochromatic coloring
    vmin = housing_gdf_2023_map[housing_variable].min()
    vmax = housing_gdf_2023_map[housing_variable].max()
    norm = colors.Normalize(vmin=vmin, vmax=vmax)
    cmap = cm.get_cmap("Reds")

    # Convert colors to [R, G, B, A] values
    housing_gdf_2023_map["fill_color"] = housing_gdf_2023_map[housing_variable].apply(
        lambda x: [int(c * 255) for c in cmap(norm(x))[:3]] + [180])

    # Convert the geometry column to GeoJSON coordinates
    housing_gdf_2023_map["coordinates"] = housing_gdf_2023_map.geometry.apply(
        lambda geom: geom.__geo_interface__["coordinates"])

    # Chloropleth map layer
    polygon_layer = pdk.Layer(
        "PolygonLayer",
        data=housing_gdf_2023_map,
        get_polygon="coordinates[0]",
        get_fill_color="fill_color",
        pickable=True,
        auto_highlight=True)

    # Set the map center and zoom level
    view_state = pdk.ViewState(latitude=44.26, longitude=-72.57, zoom=7)

    # Display the map to the page
    st.pydeck_chart(pdk.Deck(
        layers=[polygon_layer],
        initial_view_state=view_state,
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
        tooltip={"text": "{Jurisdiction}: {" + housing_variable + "}"}
    ), height=550)

    st.markdown("---")
    
    # Census Snapshot section (Housing)
    st.subheader("Housing Snapshot")
    # Include a source for the dataset (Census DP04 2023 5-year estimates)
    st.markdown("***Data Source***: U.S. Census Bureau. (2023). DP04: Selected Housing Characteristics - " \
    "County Subdivisions, Vermont. 2019-2023 American Community Survey 5-Year Estimates. " \
    "Retrieved June 11, 2025, from https://data.census.gov/")

    # Allow user to filter on the county and jurisdiction level for tailored reports 
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
    if county != "All Counties":
        filtered_gdf_2023 = filtered_gdf_2023[filtered_gdf_2023["County"] == county]
        filtered_gdf_2013 = filtered_gdf_2013[filtered_gdf_2013["County"] == county]
        filtered_med_val_df = filtered_med_val_df[filtered_med_val_df["County"] == county]
    
    if jurisdiction != "All Jurisdictions":
        filtered_gdf_2023 = filtered_gdf_2023[filtered_gdf_2023["Jurisdiction"] == jurisdiction]
        filtered_gdf_2013 = filtered_gdf_2013[filtered_gdf_2013["Jurisdiction"] == jurisdiction]
        filtered_med_val_df = filtered_med_val_df[filtered_med_val_df["Jurisdiction"] == jurisdiction]
    
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
    housing_snapshot(county, jurisdiction, filtered_gdf_2013, filtered_gdf_2023, 
                     housing_gdf_2023, filtered_med_val_df, statewide_avg_df, compare_to)

def show_housing():
    # Display the page
    census_housing()


if __name__ == "__main__":
    show_housing()