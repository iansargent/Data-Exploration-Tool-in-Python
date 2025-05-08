"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Visualize Page
"""


import streamlit as st
from utils import (
    get_user_files, file_hash, read_data, clean_column_types,
    get_columns, get_column_type, single_column_plot
)

def render_visualization():
    st.title("📈 Visualize Your Data")
    user_files = get_user_files()
    seen_hashes = set()
    unique_key = 0

    if not user_files:
        st.warning("No files uploaded.")
        return

    for file in user_files:
        fid = file_hash(file)
        if fid in seen_hashes:
            st.info(f"Duplicate skipped: {file.name}")
            continue
        seen_hashes.add(fid)
        unique_key += 1

        df = read_data(file)
        df = clean_column_types(df)
        columns = get_columns(df)

        st.subheader(f"Plots for {file.name}")
        col = st.selectbox(f"Select a column to plot ({file.name})", columns, key=unique_key)
        ctype = get_column_type(df, col)

        single_column_plot(df, col, ctype)

render_visualization()
