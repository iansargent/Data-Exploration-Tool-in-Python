"""
Open Research Community Accelorator
Vermont Data App

File Handling Utility Functions
"""

import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards 
import pandas as pd
import geopandas as gpd
import os


def clean_data(df):
    """
    Clean the column types of the DataFrame.
    Convert binary numeric columns to boolean and parse datetime columns based on column name.

    @param df: A pandas DataFrame.
    @return: The cleaned pandas DataFrame.
    """
    # Replace "." name spacers with "_"
    df.columns = df.columns.str.replace('.', '_', regex=False)
    # Replace empty values with NA
    df = df.replace("", pd.NA, regex=True)

    for col in df.columns:
        # Get the column name
        col_name = col.lower()

        # Handle datetime-like columns based on column name
        if any(x in col_name for x in ["datetime", "date", "time"]):
            df[col] = pd.to_datetime(df[col], errors='coerce')
            continue  # Skip further checks
        # If the column is a year variable
        elif "year" in col_name:
            # Convert it into a datetime type
            df[col] = pd.to_datetime(df[col].astype(str) + "-01-01", errors='coerce')
            continue
        # If the column is a month variable
        elif "month" in col_name:
            # Convert month names into numbers
            df[col] = df[col].apply(month_name_to_num)
            # Convert it into a datetime type
            df[col] = pd.to_datetime(
                "2000-" + df[col].astype(int).astype(str).str.zfill(2) + "-01",
                format="%Y-%m-%d",
                errors='coerce'
            )
            continue

        # Convert binary numeric columns with values [0,1] to boolean
        if df[col].dropna().nunique() == 2:
            vals = set(str(v).strip().lower() for v in df[col].dropna().unique())
            if vals == {"yes", "no", " "} or vals == {"0", "1"} or vals == {0, 1} or vals == {"y", "n"}:
                df[col] = df[col].astype(bool)
        
        if isinstance(df, gpd.GeoDataFrame):
            convert_all_timestamps_to_str(df)
    
    # Return the cleaned dataframe
    return df



def convert_all_timestamps_to_str(gdf):
    """
    Converts all timestamp columns in a GeoDataFrame 
    into strings for mapping purposes.

    @param gdf: A pandas DataFrame or GeoDataFrame object.
    @return: The DataFrame.
    """
    # Convert all datetime columns to strings
    for col, dtype in gdf.dtypes.items():
        if "datetime" in str(dtype):
            gdf[col] = gdf[col].astype(str)
    
    # Return the GeoDataFrame
    return gdf



def month_name_to_num(month_name):
    """
    Convert string-type month names into corresponding integers
    to make it easier to convert into datetime-type columns.

    @param month_name: The full name or abbrievation of a month (string).
    @return: The corresponding month number (int).
    """
    import calendar

    # Try to convert month string (like "May", "5", "05") to number 1-12
    if pd.isna(month_name):
        return None
    month_name = str(month_name).strip().lower()
    # Check if numeric string
    if month_name.isdigit():
        month_num = int(month_name)
        if 1 <= month_num <= 12:
            return month_num
        else:
            return None
    # Check if month name (short or full)
    month_abbrs = {m.lower(): i for i, m in enumerate(calendar.month_abbr) if m}
    month_names = {m.lower(): i for i, m in enumerate(calendar.month_name) if m}
    
    if month_name in month_abbrs:
        return month_abbrs[month_name]
    
    if month_name in month_names:
        return month_names[month_name]
    
    return None

