"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Table Preview Page
"""

# Necessary imports
import streamlit as st
from st_aggrid import AgGrid, ColumnsAutoSizeMode
from app_utils import get_user_files, file_hash, read_data, get_columns, clean_data, process_uploaded_files
import geopandas as gpd


def render_table_preview():
    
    # Set the page title
    st.title("Table Preview")
    
    user_files = get_user_files()
    processed = process_uploaded_files(user_files)
    
    for df, filename in processed:
        # Subheader for the table preview
        st.subheader(f"Preview of {filename}")
        
        # If the dataframe is a GeoDataFrame, drop the geometry column in order to display the table
        if isinstance(df, gpd.GeoDataFrame):
            # Drop the geometry column
            df_geo_aggrid = df.drop(columns=["geometry"]).reset_index(drop=True)
            # Display the table using AgGrid
            AgGrid(df_geo_aggrid, theme="material", 
                columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)
        
        # If it is NOT a GeoDataFrame, no further cleaning is necessary
        else:
            if df is not None:
                # Display the table using AgGrid
                AgGrid(df, theme="material", columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)


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
    render_table_preview()


if __name__ == "__main__":
    main()
