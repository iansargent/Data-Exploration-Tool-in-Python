"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Visualize Page
"""

# Necessary imports
import streamlit as st
from app_utils import (get_user_files, get_columns, single_column_plot, 
                       two_column_plot, process_uploaded_files, group_by_plot)
import numpy as np
import pandas as pd


# The visualize page (with default arguments given)
def render_visualization(mode="single", processed_files=None):
    
    # For each processed file
    for df, filename in processed_files:
        # Initialize a unique key for certain page features
        key = 0
        # Manually convert any date/time columns from object to datetime here:
        # NOTE: Should be integrated into clean_data() at a later date.
        for col in df.columns:
            if any(k in col.lower() for k in ['date', 'time']):
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Get a list of column names for selection
        columns = get_columns(df)
        # Subheader for the plot section
        st.markdown(f"### {filename.upper()} Dataset")
        # In the single-variable tab
        if mode == "single":
            # Allow users to select a variable
            col = st.selectbox(
                f"Select a column to plot", 
                columns, 
                index=1,
                key=f"{filename}-single-{key}"
            )
            # Advance the unique key
            key += 1

            # Display plot(s) based on the variable type
            single_column_plot(df, col)
        
        # In the two-variable tab
        elif mode == "double":         
            # Define a set of 2 columns for formating the variable select boxes
            column1, column2 = st.columns(2)

            # In the first column
            with column1:
                # Selection box for the first variable
                col1 = st.selectbox(
                    f"Select a column to plot", 
                    columns, 
                    index=1,
                    key=f"{filename}-col1-{key}"
                    )
            # In the second column
            with column2:
                # Selection box for the second variable
                col2 = st.selectbox(
                    f"Select a second column to plot", 
                    columns, 
                    index=2,
                    key=f"{filename}-col2-{key+1}"
                    )
            
            # Display the set of plots based on the datatype combination
            two_column_plot(df, col1, col2)

        # In the "group-by" tab
        elif mode == "group-by":
            # Define a list of useful "group-by" operations
            operations = ["Total", "Average", "Median", "Count", "Unique Count", 'Standard Deviation']
            
            # Define a set of 3 columns for formating the select boxes
            column1, column2, column3 = st.columns(3)
            
            # In the first column
            with column1:
                # Selection box for numeric OPERATION (average, total, SD, etc.)
                num_op = st.selectbox(
                    f"Operation", 
                    operations, 
                    index=0,
                    key=f"{filename}-num_op-{key}"
                    )
            
            # Define a list of only numeric columns in the dataframe to select from
            numeric_columns = df.select_dtypes(include=[np.number])
            # Get the column names as a list
            numeric_column_names = numeric_columns.columns.tolist()
            # In the second column
            with column2:
                # Selection box for the numeric variable
                num_var = st.selectbox(
                    f"Numeric Column to Investigate", 
                    numeric_column_names, 
                    index=0,
                    key=f"{filename}-num_var-{key+1}"
                    )
            
            # Define a list of only categorical columns to summarize by
            categorical_columns = df.select_dtypes(include=["object", "category"])
            categorical_column_names = categorical_columns.columns.tolist()
            # In the third column
            with column3:
                # Selection box for the "group-by" variable
                grp_by = st.selectbox(
                    f"Variable to Summarize by", 
                    categorical_column_names, 
                    key=f"{filename}-grp_by-{key+2}"
                    )
                
            # Display a set of plots based on the combination of options
            group_by_plot(df, num_op, num_var, grp_by)

        # Advance the key offset to handle duplicate elements on the page
        key += 3

# The main function
def show_plots():
    # Apply a background color to the page
    st.markdown(
    """
    <style>
    html, body, [class*="css"]  {
        font-family: 'Avenir', 'Arial', sans-serif; font-weight: 300;
    }
    [data-testid="stAppViewContainer"] {
        background-image: url("https://t3.ftcdn.net/jpg/01/99/28/98/360_F_199289808_twlKOyrViuqfzyV5JFmYdly2GHihxqEh.jpg");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center;
    }
    [data-testid="stHeader"] {
        background: rgba(255, 255, 255, 0.0);
    }
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.5);
    }
    </style>
    """, unsafe_allow_html=True)

    # Set the page title
    st.markdown(
        "<h2 style='color: #4a4a4a; font-family: Helvetica; font-weight: 300;'>Visualize</h2>",
        unsafe_allow_html=True)
    
    # Apply global font settings
    st.markdown(
    """
    <style>
    /* Set Helvetica (fallback to Arial, sans-serif) globally */
    html, body, [class*="css"]  {
        font-family: 'Avenir', 'Arial', sans-serif; font-weight: 300;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Define the three plotting tabs
    tab1, tab2, tab3 = st.tabs(["Single Variable", "Two Variables", "Group By"])
    
    # Get the user files and process them
    user_files = get_user_files(key="shared")
    processed_files = process_uploaded_files(user_files)
    
    # Display the pages for each plotting mode (single, double, group-by)
    with tab1:
        render_visualization("single", processed_files)
    with tab2:
        render_visualization("double", processed_files)
    with tab3:
        render_visualization("group-by", processed_files)

if __name__ == "__main__":
    show_plots()
