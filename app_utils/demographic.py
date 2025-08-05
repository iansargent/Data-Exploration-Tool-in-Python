import streamlit as st
import pandas as pd
import altair as alt
import requests
import io
from app_utils.census import get_geography_title, split_name_col
from app_utils.census_sections import select_census_geography, filter_census_geography
from app_utils.color import get_text_color
from app_utils.plot import donut_chart, bar_chart


def demographic_snapshot_header():
    st.subheader("Demographic Snapshot")
    # Include a source for the dataset (Census DP04 2023 5-year estimates)
    st.markdown("***Data Source***: U.S. Census Bureau. (2023). DP05: Demographic and Housing Estimates - " \
    "County Subdivisions, Vermont. 2019-2023 American Community Survey 5-Year Estimates. " \
    "Retrieved from https://data.census.gov/")


def demographic_snapshot(demog_dfs):
    # Display the Category Header with Data Source
    demographic_snapshot_header()
    # Define county and jurisdiction selections with select boxes
    county, jurisdiction = select_census_geography(demog_dfs[0])
    # Filter each dataset in "demog_dfs" to the geography needed for the snapshot 
    # Returns a LIST of filtered DataFrames
    filtered_demog_dfs = filter_census_geography(demog_dfs, county, jurisdiction)
    
    # Unpack each dataset from "filtered_demog_dfs" by index
    # TODO: This unpacking process could be more reliable with a dictionary
    filtered_gdf_2023 = filtered_demog_dfs[0]

    # Get the title of the geography for plotting
    title_geo = get_geography_title(county, jurisdiction)
    # Based on the system color theme, update the text color (only used in donut plots)
    text_color = get_text_color(key="demographic_snapshot")
