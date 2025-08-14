import streamlit as st
import pandas as pd
import altair as alt
import requests
import io
from app_utils.census import get_geography_title
from app_utils.color import get_text_color
from app_utils.df_filtering import filter_snapshot_data
from app_utils.data_loading import load_metrics
from app_utils.plot import donut_chart, bar_chart, make_time_series_plot

from app_utils.constants.ACS import ACS_SOCIAL_METRICS


def social_snapshot_header():
    st.subheader("Social Snapshot")
    # Include a source for the dataset (Census DP04 2023 5-year estimates)
    st.markdown("***Data Source***: U.S. Census Bureau. (2023). DP05: Selected Social Characteristics - " \
    "County Subdivisions, Vermont. 2019-2023 American Community Survey 5-Year Estimates. " \
    "Retrieved from https://data.census.gov/")


def compute_social_metrics(df):
    return load_metrics(df, ACS_SOCIAL_METRICS)


def build_social_plot_dataframes(df, metrics):
    """
    Calculate a dictionary of social dataframes
    """

    return {
        "ex1_dist": pd.DataFrame({
            "EX1": ["ex"], 
            "Population": [metrics['example']]
        }),
        
        "ex2_dist": pd.DataFrame({
            "EX2": ["ex"],
            "Population": [metrics['example']]
        }),
        
        "ex3_dist": pd.DataFrame({
            "EX3": ["ex"],
            "Population": [metrics['example']]
        })
     }


def social_df_metric_dict(filtered_gdf_2023):
    metrics = compute_social_metrics(filtered_gdf_2023)
    dfs = build_social_plot_dataframes(filtered_gdf_2023, metrics)
    return metrics, dfs


def social_snapshot(social_dfs):
    # Display the Category Header with Data Source
    social_snapshot_header()
    # Filter the dataframes using select boxes for "County" and "Jurisdiction"
    filtered_dfs, selected_values = filter_snapshot_data(social_dfs, key_df=social_dfs['social_2023'])
    
    # Get the title of the geography for plotting
    title_geo = get_geography_title(selected_values)
    # Based on the system color theme, update the text color (only used in donut plots)
    text_color = get_text_color(key="social_snapshot")
    # Define two callable dictionaries: Metrics and Plot DataFrames
    metrics, plot_dfs = social_df_metric_dict(filtered_dfs["social_2023"])

    # Render section functions
    render_households(metrics, plot_dfs, title_geo)
    render_education(metrics, plot_dfs, title_geo)
    render_ancestry(metrics, plot_dfs, title_geo)
    render_computer_access(metrics, plot_dfs, title_geo)




def render_households(metrics, plot_dfs, title_geo):
    st.divider()
    st.subheader("Households")


def render_education(metrics, plot_dfs, title_geo):
    st.divider()
    st.subheader("Education")

    st.markdown("##### 1. School Enrollment")


def render_ancestry(metrics, plot_dfs, title_geo):
    st.divider()
    st.subheader("Ancenstry")


def render_computer_access(metrics, plot_dfs, title_geo):
    st.divider()
    st.subheader("Computer & Internet Access")