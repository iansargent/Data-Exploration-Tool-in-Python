"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Data Summary Page
"""


import streamlit as st
from utils import get_user_files, file_hash, read_data, clean_column_types, get_columns, column_summaries
import ydata_profiling




def render_data_summary():
    st.title("📊 Data Summary")
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

        # Read, clean, and summarize the data
        df = read_data(file)
        df = clean_column_types(df)
        columns = get_columns(df)

        # Display column summaries
        st.subheader(f"Summary for {file.name}")
        column_summaries(df, columns)

        # Display the ydata-profiling report
        st.title("📊 Data Report")
        profile = ydata_profiling.ProfileReport(df)
        st.write(profile)

render_data_summary()
