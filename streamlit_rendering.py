import streamlit as st
import pandas as pd

def filter_dataframe(df, filter_columns):
    """
    Create cascading selectboxes in two rows to filter a DataFrame.
    
    Args:
        df (pd.DataFrame): DataFrame to filter.
        filter_columns (list): Columns to filter on.
    
    Returns:
        pd.DataFrame: Filtered DataFrame.
    """
    filtered_df = df.copy()
    selected = {}

    # Split into two rows
    half = (len(filter_columns) + 1) // 2
    first_row = filter_columns[:half]
    second_row = filter_columns[half:]

    # First row of filters
    cols1 = st.columns(len(first_row))
    for i, col_name in enumerate(first_row):
        unique_values = filtered_df[col_name].dropna().unique()
        selected_value = cols1[i].selectbox(
            col_name,
            options=sorted(unique_values)
        )
        selected[col_name] = selected_value
        filtered_df = filtered_df[filtered_df[col_name] == selected_value]

    # Second row of filters
    cols2 = st.columns(len(second_row))
    for i, col_name in enumerate(second_row):
        unique_values = filtered_df[col_name].dropna().unique()
        selected_value = cols2[i].selectbox(
            col_name,
            options=sorted(unique_values)
        )
        selected[col_name] = selected_value
        filtered_df = filtered_df[filtered_df[col_name] == selected_value]

    return filtered_df
