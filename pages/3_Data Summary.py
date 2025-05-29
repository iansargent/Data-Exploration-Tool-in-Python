"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Data Summary Page
"""

# Necessary imports
import streamlit as st
from app_utils import (get_user_files, get_columns, column_summaries, 
                       generate_profile_report, process_uploaded_files)
import ydata_profiling
from streamlit_pandas_profiling import st_profile_report
import geopandas as gpd


def render_data_summary():
    # Set the page title
    st.markdown(
        "<h2 style='color: #4a4a4a; font-family: Helvetica; font-weight: 300;'>Data Summary</h2>",
        unsafe_allow_html=True)
    
    # Get the user files and process them
    user_files = get_user_files()
    processed_files = process_uploaded_files(user_files)

    # Define a list of divider colors that will visually separate each file report on the page
    dividers = ["red", "blue", "green", "orange", "violet", "red", "grey"]
    
    # For each processed file
    for i, (df, filename) in enumerate(processed_files):
        # Initialize a unique key for each download file
        key = 0
        # Header section for each uploaded file with a new divider color
        st.header(f"Summary of {filename}", divider=dividers[i])
        # If the file is a GeoDataFrame
        if isinstance(df, gpd.GeoDataFrame):
            # Drop the geometry column
            df = df.drop(columns=["geometry"]).reset_index(drop=True)
        
        # Get a list of the column names
        columns = get_columns(df)

        # Display a column summary for each column in the dataframe
        column_summaries(df, columns, filename)
        st.markdown("---")

        # Subheader for the ydata-profiling report
        st.subheader("Data Report")
        
        # Add a loading spinner icon to ensure the user knows the report is being generated
        with st.spinner(text = "Generating report..."):
            # Create the ydata-profiling report
            profile = generate_profile_report(df)
            # Allow for an html export
            report_export = profile.to_html()
            # Add a download button for the HTML report
            st.download_button(label="View Full Report", data=report_export, file_name=f'data_report_{filename}_{key}.html')
            # Advance the unique key
            key += 1
        
        # Using an expander-type button
        with st.expander("View Report Preview"):
            # Display the report on the page
            st_profile_report(profile)
        
        # Add a visual divider
        st.markdown("---")

# Run the data summary page
def show_summary():
    
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
    
    # Set the global font settings
    st.markdown(
    """
    <style>
    /* Set Helvetica (fallback to Arial, sans-serif) globally */
    html, body, [class*="css"]  {
        font-family: 'Avenir', 'Arial', sans-serif; font-weight: 300;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Show the data summary page
    render_data_summary()


if __name__ == "__main__":
    show_summary()
