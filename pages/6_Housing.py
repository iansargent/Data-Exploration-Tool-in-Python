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
from app_utils import split_name_col, housing_metrics_vs_statewide, housing_pop_plot, housing_metrics_vs_10yr


def census_housing():
    # Page Title
    st.header("Housing", divider="grey")

    # Read the Census DP04 Housing Characteristics Dataset
    housing_gdf = gpd.read_file('/Users/iansargent/Desktop/ORCA/Steamlit App Testing/Census/VT_HOUSING_ALL.fgb')
    housing_2013 = gpd.read_file('/Users/iansargent/Desktop/ORCA/Steamlit App Testing/Census/VT_HOUSING_ALL_2013.fgb')
    # Split the "name" column into separate "County" and "Jurisdiction" columns
    housing_gdf = split_name_col(housing_gdf)
    housing_2013 = split_name_col(housing_2013)

    st.subheader("Mapping")
    # Define the numerical columns in the GeoDataFrame for mapping
    numeric_cols = [col for col in housing_gdf.columns if housing_gdf[col].dtype in ['int64', 'float64']]
    # Add a user select box to choose which variable they want to map
    housing_variable = st.selectbox("Select a Housing variable", numeric_cols)

    # Project to lat/lon for Pydeck
    housing_gdf = housing_gdf.to_crs(epsg=4326)
    housing_gdf_map = housing_gdf[["County", "Jurisdiction", housing_variable, "geometry"]].dropna().copy()

    # Normalize the housing variable
    vmin = housing_gdf_map[housing_variable].min()
    vmax = housing_gdf_map[housing_variable].max()
    norm = colors.Normalize(vmin=vmin, vmax=vmax)
    cmap = cm.get_cmap("Reds")

    # Convert to [R, G, B, A] values
    housing_gdf_map["fill_color"] = housing_gdf_map[housing_variable].apply(
        lambda x: [int(c * 255) for c in cmap(norm(x))[:3]] + [180])

    # Convert geometry to GeoJSON-style coordinates
    housing_gdf_map["coordinates"] = housing_gdf_map.geometry.apply(
        lambda geom: geom.__geo_interface__["coordinates"])

    # Pydeck PolygonLayer
    polygon_layer = pdk.Layer(
        "PolygonLayer",
        data=housing_gdf_map,
        get_polygon="coordinates[0]",
        get_fill_color="fill_color",
        pickable=True,
        auto_highlight=True)

    # Set view state
    view_state = pdk.ViewState(latitude=44.26, longitude=-72.57, zoom=7)

    # Display map
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
            label = "**Comparison Basis**",
            options = ["2013 Local Data (10-Year Change)", "2023 Vermont Statewide Averages"],
            index=0)

    # Read in VT historical population data on the census tract level
    # NOTE: Include a source for this as well (VT Open Data Portal)
    pop_df = pd.read_csv('/Users/iansargent/Desktop/ORCA/Steamlit App Testing/Census/VT_Municipal_Pop.csv')
    
    # Display the time series plot of population, housing units, and new housing units
    housing_pop_plot(county, jurisdiction, filtered_gdf, pop_df)
    # If comparison to 10 years ago
    if compare_to == "2013 Local Data (10-Year Change)":
        st.markdown("***Data Source***: U.S. Census Bureau. (2013). DP04: Selected Housing Characteristics - " \
    "County Subdivisions, Vermont. 2009-2013 American Community Survey 5-Year Estimates. " \
    "Retrieved June 13, 2025, from https://data.census.gov/")
        # Remind user that delta values are compared to 2013 Census data
        st.markdown("*Note*: The displayed deviations in the metric cards are comparing values to 2013 Census Data.")
        # Display formatted housing metrics vs statewide averages
        housing_metrics_vs_10yr(county, jurisdiction, filtered_gdf_2013, filtered_gdf)
    # If comparison to current statewide averages
    elif compare_to == "2023 Vermont Statewide Averages":
        # Remind user that delta values are compared to statewide averages
        st.markdown("*Note*: The displayed deviations in the metric cards are comparing values to VT statewide averages.")
        # Display formatted housing metrics vs statewide averages
        housing_metrics_vs_statewide(county, jurisdiction, housing_gdf, filtered_gdf)
    

def main():
    # Display the page
    census_housing()


if __name__ == "__main__":
    main()