"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Visualize Page
"""


import streamlit as st
from utils import (
    get_user_files, file_hash, read_data, clean_column_types,
    get_columns, get_column_type, single_column_plot, two_column_plot
)

def render_visualization(mode="single"):
    title = "Single Variable" if mode == "single" else "Two Variables"
    st.title(f"\U0001F4C8 Visualize Your Data ({title})")

    user_files = get_user_files()
    if not user_files:
        st.warning("No files uploaded.")
        return

    seen_hashes = set()
    key_offset = 0

    for file in user_files:
        fid = file_hash(file)
        if fid in seen_hashes:
            st.info(f"Duplicate skipped: {file.name}")
            continue
        seen_hashes.add(fid)

        df = clean_column_types(read_data(file))
        columns = get_columns(df)

        st.subheader(f"Plots for {file.name}")

        if mode == "single":
            col = st.selectbox(f"Select a column to plot ({file.name})", columns, key=f"{file.name}-single-{key_offset}")
            ctype = get_column_type(df, col)
            single_column_plot(df, col, ctype)
        else:
            col1 = st.selectbox(f"Select a column to plot ({file.name})", columns, key=f"{file.name}-col1-{key_offset}")
            col2 = st.selectbox(f"Select a second column to plot ({file.name})", columns, key=f"{file.name}-col2-{key_offset+1}")
            two_column_plot(df, col1, col2)

        key_offset += 2

def main():
    tab1, tab2 = st.tabs(["Single Variable", "Two Variables"])

    with tab1:
        render_visualization("single")
    with tab2:
        render_visualization("double")


if __name__ == "__main__":
    main()
