"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Table Preview Page
"""

# Necessary imports
import streamlit as st
from st_aggrid import AgGrid, ColumnsAutoSizeMode
from streamlit_extras.metric_cards import style_metric_cards 
from app_utils import get_user_files, process_uploaded_files, data_snapshot
import geopandas as gpd

from streamlit_extras.dataframe_explorer import dataframe_explorer 


def render_table_preview():
    
    # Set the page title
    st.markdown(
        "<h2 style='color: #4a4a4a; font-family: Helvetica; font-weight: 300;'>Table Preview</h2>",
        unsafe_allow_html=True)
    
    # Get the uploaded files and process them
    user_files = get_user_files()
    processed = process_uploaded_files(user_files)
    
    # Define the divider colors for each file uploaded
    # dividers = ["red", "blue", "green", "orange", "violet", "red", "grey"]
    
    # For each uploaded file
    for i, (df, filename) in enumerate(processed):
        # Data information (dimensions and filename)
        data_snapshot(df, filename)
        
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

                # NOTE: TEMPORARY COMPARISON USING DATAFRAME_EXPLORER
                filtered_df = dataframe_explorer(df, case=False)
                st.dataframe(filtered_df, use_container_width=True)


def show_preview():
    # Apply a background color to the page
    st.markdown(
    """
    <style>
    html, body, [class*="css"]  {
        font-family: 'Avenir', 'Arial', sans-serif; font-weight: 300;
    }
    [data-testid="stAppViewContainer"] {
        background-image: url("https://t3.ftcdn.net/jpg/01/99/28/98/360_F_199289808_twlKOyrViuqfzyV5JFmYdly2GHihxqEh.jpg");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center;
    }
    [data-testid="stHeader"] {
        background: rgba(255, 255, 255, 0.0);
    }
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.5);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Show the table page
    render_table_preview()


if __name__ == "__main__":
    show_preview()
