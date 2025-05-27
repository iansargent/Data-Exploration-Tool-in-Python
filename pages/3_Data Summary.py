"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Data Summary Page
"""

# Necessary imports
import streamlit as st
from app_utils import (get_user_files, file_hash, read_data, clean_data, 
                       get_columns, column_summaries, generate_profile_report,
                       process_uploaded_files)
import ydata_profiling
from streamlit_pandas_profiling import st_profile_report
import geopandas as gpd


def render_data_summary():
    st.title("Data Summary")
    
    user_files = get_user_files()
    processed_files = process_uploaded_files(user_files)

    for df, filename in processed_files:
    
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
            st.download_button(label="View Full Report", data=report_export, file_name='data_report.html')
            # Display the report on the page
            st_profile_report(profile)
        st.markdown("---")

# Run the data summary page
def main():
    st.markdown(
    """
    <style>
    /* Set Helvetica (fallback to Arial, sans-serif) globally */
    html, body, [class*="css"]  {
        font-family: 'Avenir', 'Arial', sans-serif; font-weight: 300;
    }
    </style>
    """, unsafe_allow_html=True)
    render_data_summary()


if __name__ == "__main__":
    main()
