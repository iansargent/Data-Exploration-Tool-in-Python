"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Table Preview Page
"""

import streamlit as st
from st_aggrid import AgGrid, ColumnsAutoSizeMode
from app_utils import get_user_files, file_hash, read_data, get_columns, clean_data
import geopandas as gpd

def render_table_preview():
    st.title("Table Preview")
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
        cleaned_df = clean_data(df)
        
        st.subheader(f"Preview of {file.name}")

        if isinstance(df, gpd.GeoDataFrame):
            df_geo_aggrid = cleaned_df.drop(columns=["geometry"]).reset_index(drop=True)
            AgGrid(df_geo_aggrid, theme="material", 
                columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)

        else:
            if cleaned_df is not None:
                AgGrid(cleaned_df, theme="material", columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)


def main():
    render_table_preview()


if __name__ == "__main__":
    main()
