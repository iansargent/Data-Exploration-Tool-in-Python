"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Data Summary Page
"""

# Necessary imports
import streamlit as st
from app_utils import get_user_files, file_hash, read_data, clean_data, get_columns, column_summaries, generate_profile_report
import ydata_profiling
from streamlit_pandas_profiling import st_profile_report
import geopandas as gpd


def render_data_summary():
    st.title("Data Summary")
    user_files = get_user_files()
    seen_hashes = set()

    if not user_files:
        st.warning("No files uploaded.")
        return

    # Check if the user has already uploaded this file using hash codes
    for file in user_files:
        file_id = file_hash(file)
        # If it is a duplicate, skip it
        if file_id in seen_hashes:
            st.info(f"Duplicate skipped: {file.name}")
            continue
        # Add the file ID to the set of uploaded hashes
        seen_hashes.add(file_id)

        # Read the data
        df = read_data(file)
        # Clean the data
        df_clean = clean_data(df)

        # If the file is a GeoDataFrame
        if isinstance(df_clean, gpd.GeoDataFrame):
            # Drop the geometry column
            df_clean = df_clean.drop(columns=["geometry"]).reset_index(drop=True)
        
        # Get a list of the column names
        columns = get_columns(df_clean)

        # Display a column summary for each column in the dataframe
        column_summaries(df_clean, columns, file.name)
        st.markdown("---")

        # Subheader for the ydata-profiling report
        st.subheader("Data Report")
        
        # Add a loading spinner icon to ensure the user knows the report is being generated
        with st.spinner(text = "Generating report..."):
            # Create the ydata-profiling report
            profile = generate_profile_report(df_clean)
            # Allow for an html export
            report_export = profile.to_html()
            # Add a download button for the HTML report
            st.download_button(label="View Full Report", data=report_export, file_name='data_report.html')
            # Display the report on the page
            st_profile_report(profile)
        st.markdown("---")

# Run the data summary page
render_data_summary()
