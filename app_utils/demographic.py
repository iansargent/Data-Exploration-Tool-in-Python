import streamlit as st
import pandas as pd
import altair as alt
import requests
import io
from app_utils.census import get_geography_title, split_name_col
from app_utils.df_filtering import filter_snapshot_data
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

    filtered_dfs, selected_values = filter_snapshot_data(
        dfs = demog_dfs,
        key_df=demog_dfs['demogs_2023']
    )

    # Unpack each dataset from "filtered_demog_dfs" by index
    # TODO: This unpacking process could be more reliable with a dictionary
    st.dataframe(filtered_dfs['demogs_2023'])

    # Get the title of the geography for plotting
    title_geo = get_geography_title(selected_values)
    
    # Based on the system color theme, update the text color (only used in donut plots)
    text_color = get_text_color(key="demographic_snapshot")
