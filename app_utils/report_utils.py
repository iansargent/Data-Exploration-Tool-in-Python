"""
Open Research Community Accelorator
Vermont Data App

Report Utility Functions
"""
# Streamlit 
import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards 

# Data Processing / Plotting
import pandas as pd
import geopandas as gpd
import altair as alt
import numpy as np

# Standard Libraries
import os
import io

# Color Mapping 
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.colorbar import ColorbarBase


def exploratory_report(df):
    """
    Generate a tailored exploratory profile report 
    given a DataFrame using the ydata-profiling package.

    @param df: A pandas DataFrame object.
    @return: An exploratory ydata-profiling ProfileReport object.
    """
    from ydata_profiling import ProfileReport

    # Get the number of columns in the dataframe
    df_columns = get_columns(df)
    num_columns = len(df_columns)

    # If there are a large amount of columns (30)
    # Use a "minimal" report to decrease computation
    if num_columns > 30:
        report = ProfileReport(
            df,
            title="Exploratory Report",
            interactions=None,
            samples=None,
            missing_diagrams={"bar": False, "matrix": False, "dendrogram": False, "heatmap": False})
    # If there are less than 30 columns
    else:
        report = ProfileReport(
            df,
            title="Exploratory Report",
            explorative=True,
            missing_diagrams={"bar": False, "matrix": False, "dendrogram": False, "heatmap": False},
            samples=None)
    
    # Return the ydata-profiling report
    return report


def quality_report(df):
    """
    Generate a tailored data quality profile report 
    given a DataFrame using the ydata-profiling package.

    @param df: A pandas DataFrame object.
    @return: A data quality ydata-profiling ProfileReport object.
    """
    from ydata_profiling import ProfileReport

    report = ProfileReport(
            df,
            title="Data Quality",
            missing_diagrams={"bar": True,"matrix": True},
            duplicates={"head": 10},
            correlations=None,
            interactions=None)

    return report


def comparison_report(dfs):
    """
    Generates a comparison report given a list of 
    uploaded dataframes

    @param dfs: A list of pandas DataFrame objects.
    @return: A ydata-profiling comparison report.
    """
    from ydata_profiling import ProfileReport, compare
    
    reports = []
    for i, df in enumerate(dfs):
        report = ProfileReport(
            df,
            title = f"Report_{i}"
        )
        reports.append(report)
    
    comparison_report = compare(reports)

    return comparison_report

