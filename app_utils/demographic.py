import streamlit as st
import pandas as pd
import altair as alt
import requests
import io
from app_utils.census import get_geography_title, split_name_col
from app_utils.df_filtering import filter_dataframe
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
    # Filter the dataframes using select boxes for "County" and "Jurisdiction"
    filtered_demog_dfs = filter_dataframe(
        demog_dfs, 
        filter_columns=["County", "Jurisdiction"],
        key_prefix="demog_snapshot", 
        allow_all={
            "County": True, 
            "Jurisdiction": True
        }
    )

    # Unpack each dataset from "filtered_demog_dfs" by index
    # TODO: This unpacking process could be more reliable with a dictionary
    filtered_gdf_2023 = filtered_demog_dfs[0]
    st.dataframe(filtered_gdf_2023)
    selected_values = filtered_demog_dfs[1]

    # Get the title of the geography for plotting
    county = selected_values["County"]
    jurisdiction = selected_values["Jurisdiction"]
    title_geo = get_geography_title(county, jurisdiction)
    
    # Based on the system color theme, update the text color (only used in donut plots)
    text_color = get_text_color(key="demographic_snapshot")
