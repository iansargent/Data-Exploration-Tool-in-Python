"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Table Preview Page
"""


import streamlit as st
from st_aggrid import AgGrid, ColumnsAutoSizeMode
from utils import get_user_files, file_hash, read_data, clean_data


def render_table_preview():
    st.title("📋 Table Preview")
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
        # df = clean_data(df) Gets messy with date type columns
        st.subheader(f"Preview of {file.name}")
        AgGrid(df, theme="material", columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)

render_table_preview()
