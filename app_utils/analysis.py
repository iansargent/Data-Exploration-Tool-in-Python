"""
Open Research Community Accelorator
Vermont Data App

DataFrame Analysis Utility Functions
"""

import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards
import pandas


def get_columns(df):
    """
    Get the column names from the DataFrame as a list.

    @param df: A pandas DataFrame object.
    @return: A list of column names in the dataframe (string).
    """
    columns = df.columns.tolist()
    return columns


def get_column_type(df, column_name):
    """
    Get the data type of a specific column in the DataFrame.

    @param df: A pandas Dataframe object.
    @param column_name: The name of the column in the dataframe (string).
    @return: The pandas data type of the column (dtype).
    """
    column_type = df[column_name].dtype
    return column_type


def get_dimensions(df):
    """
    Determines the numnber of rows and columns in the dataset.

    @param df: A pandas DataFrame object.
    @return: Number of columns (int), Number of rows (int) respectfully.
    """
    
    # Find the number of columns
    num_columns = len(get_columns(df))
    # Find the number of rows
    num_rows = len(df)

    # Return the dimensions as a tuple
    return num_columns, num_rows


def get_skew(df, variable):
    """
    Computes the sample skewness of a numeric variable in a DataFrame.
    
    @param df: A pandas DataFrame object.
    @param variable: The column name of the numeric variable (string).
    @return: The computed skewness metric (float).
    """
    import numpy as np

    x = df[variable].dropna()
    n = len(x)
    if n < 3:
        return np.nan  # skewness not defined for < 3 values

    mean = x.mean()
    std = x.std(ddof=0)  # population std for formula

    skewness = ((x - mean)**3).sum() / (n * (std**3))
    
    return skewness


def descriptive_metrics(df, filename):
    """
    Reports the overall structure of the dataset, including
    dimensions and the dataframe type.

    @param df: A pandas DataFrame object.
    @param filename: The name of the file (string)
    """
    # Add spacer between different files
    st.markdown("---")
    
    # Define the dimensions
    num_cols, num_rows = get_dimensions(df)
    
    # Find the unique column
    unique_columns = []
    
    # Finding the identifying (unique column)
    for col in df.columns:
        # Get the length of the column and the its number of unique values
        col_length = len(df[col])
        num_unique = df[col].nunique()

        # If every value in the column is unique
        if num_unique == col_length:
            # Get the column name
            col_name = df[col].name
            # Add it to the list of unique columns
            unique_columns.append(col_name)
    
    # Define the ID columns as the first name in the list of unique columns
    if unique_columns:
        unique_column = unique_columns[0]
    # If no unique columns are found, set ID column to "None"
    else:
        unique_column = "None"
    
    # Define columns to display each metric card
    col1, col2, col3, col4 = st.columns(4)

    # Define each metric card
    col1.metric(label="File", value=filename)
    col2.metric(label='Identifying Column', value=unique_column)
    col3.metric(label="Columns", value=num_cols)
    col4.metric(label='Rows', value=num_rows)

    # Styling the snapshot cards
    style_metric_cards(
        background_color="whitesmoke", 
        border_size_px=1, 
        border_left_color="mediumseagreen")    

