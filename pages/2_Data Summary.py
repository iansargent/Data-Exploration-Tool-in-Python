"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Data Summary Page
"""


import streamlit as st
from utils import get_user_files, file_hash, read_data, clean_column_types, get_columns, column_summaries

def render_data_summary():
    st.title("📊 Data Summary")
    user_files = get_user_files()
    seen_hashes = set()

    if not user_files:
        st.warning("No files uploaded.")
        return

    for file in user_files:
        fid = file_hash(file)
        if fid in seen_hashes:
            st.info(f"Duplicate skipped: {file.name}")
            continue
        seen_hashes.add(fid)

        df = read_data(file)
        df = clean_column_types(df)
        columns = get_columns(df)

        st.subheader(f"Summary for {file.name}")
        column_summaries(df, columns)

render_data_summary()
