"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Table Preview Page
"""

# Necessary imports
import streamlit as st
import geopandas as gpd
from streamlit_extras.dataframe_explorer import dataframe_explorer 

from app_utils.streamlit_config import streamlit_config
from app_utils.file_handling import get_user_files, process_uploaded_files
from app_utils.analysis import descriptive_metrics, get_columns

def main():
    # Set the page title
    st.header("Table Preview")
        
    # Get the uploaded files and process them
    user_files = get_user_files()
    processed = process_uploaded_files(user_files)
        
    # For each uploaded file
    for i, (df, filename) in enumerate(processed):
        # Data information (dimensions and filename)
        descriptive_metrics(df, filename)
        # If the dataframe is a GeoDataFrame, drop the geometry column in order to display the table
        if isinstance(df, gpd.GeoDataFrame):
            # Drop the geometry column
            df = df.drop(columns=["geometry"]).reset_index(drop=True)
        
        # Allow for specific column selections in the table (multiselect)
        column_selection = st.multiselect(
            label="Select columns to include in the table",
            options=["All Columns"] + get_columns(df),
            default="All Columns")
        
        # If the user selects a specific column(s)
        if "All Columns" not in column_selection:
            df=df[column_selection]
        
        # Use a dataframe explorer object from streamlit extras for table filtering 
        filtered_df = dataframe_explorer(df, case=False)
        
        # Display the dataframe on the page
        st.dataframe(filtered_df, use_container_width=True)

if __name__ == "__main__":
    streamlit_config()
    main()
    