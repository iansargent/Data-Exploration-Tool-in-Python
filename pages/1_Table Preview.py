"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Table Preview Page
"""

# Necessary imports
import streamlit as st
from st_aggrid import AgGrid, ColumnsAutoSizeMode
from app_utils import get_user_files, file_hash, read_data, get_columns, clean_data
import geopandas as gpd


def render_table_preview():
    # Set the page title
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
        
        # Read the data
        df = read_data(file)
        # Clean the data
        cleaned_df = clean_data(df)
        
        # Subheader for the table preview
        st.subheader(f"Preview of {file.name}")
        
        # If the dataframe is a GeoDataFrame, drop the geometry column in order to display the table
        if isinstance(df, gpd.GeoDataFrame):
            # Drop the geometry column
            df_geo_aggrid = cleaned_df.drop(columns=["geometry"]).reset_index(drop=True)
            # Display the table using AgGrid
            AgGrid(df_geo_aggrid, theme="material", 
                columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)
        
        # If it is NOT a GeoDataFrame, no further cleaning is necessary
        else:
            if cleaned_df is not None:
                # Display the table using AgGrid
                AgGrid(cleaned_df, theme="material", columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)


def main():
    render_table_preview()


if __name__ == "__main__":
    main()
