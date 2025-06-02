"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Mapping Page
"""

# Necessary imports
import streamlit as st
import pandas as pd
import geopandas as gpd
import leafmap.foliumap as leafmap
from app_utils import (get_user_files, is_latitude_longitude, 
                       convert_all_timestamps_to_str, process_uploaded_files, 
                       render_zoning_layer)
from st_aggrid import AgGrid, ColumnsAutoSizeMode, GridOptionsBuilder, GridUpdateMode
from streamlit_extras.dataframe_explorer import dataframe_explorer 



def render_mapping():
    """
    Render the mapping page of the Streamlit app.
    This function retrieves user-uploaded files, processes them, and displays
    them on a map. It also provides options for filtering and comparing data
    based on user selections.
    """
    # Set the page title
    st.markdown(
        "<h2 style='color: #4a4a4a; font-family: Helvetica; font-weight: 300;'>Mapping</h2>",
        unsafe_allow_html=True)
    
    # Get the user files from the uploader and process them
    user_files = get_user_files()
    # If no files are uploaded, show a warning message
    processed_files = process_uploaded_files(user_files)

    # Create an option bank of basemaps to choose from
    basemaps = {
    "Light": "CartoDB.Positron",
    "Standard": "OpenStreetMap",
    "Satellite": "Esri.WorldImagery",
    "Elevation": "OpenTopoMap",
    "Shaded Relief Map": "Esri.WorldShadedRelief",
    "Hillshade Map": "Esri.WorldHillshade",
    "National Geographic": "Esri.NatGeoWorldMap",
    "World Street Map": "Esri.WorldStreetMap"
    }
    
    # Display a selection box for the basemap type
    basemap_select_box = st.selectbox(
        label="**Basemap**",
        options=list(basemaps.keys()),
        index=0
    )

    # Retrieve the selected basemap as a string
    selected_basemap = basemaps[basemap_select_box]

    # Set a default map center (In Vermont)
    default_center = [44.45, -72.71]

    # Initialize a blank map centered on VT
    map = leafmap.Map(center=default_center)
    # Add the basemap configuration
    map.add_basemap(selected_basemap)
    
    # Create a on/off toggle to show VT Zoning Data
    vt_zoning = st.toggle(label = "Use the VT Zoning Data Dataset")
        
    if vt_zoning == True:
         render_zoning_layer(map)
    
    # Loop through each processed/uploaded dataframe and its filename
    for df, filename in processed_files:
        
        df = convert_all_timestamps_to_str(df)

        # Determine the layer style based on common words in the VTZA data folder
        if "border" in filename:
            style = {"color": "dodgerblue", "weight": 2}
        elif "linearfeatures" in filename:
            style = {"color": "blue", "weight": 2}
        elif "pointfeatures" in filename:
            style = {"color": "darkorange", "weight": 2}
        elif "servicearea" in filename:
            style = {"color": "darkred", "weight": 2}
        elif ("wwtf" in filename) or ("facilit" in filename):
            style = {"color": "darkgreen", "weight": 2}
        elif "zoning" in filename:
            style = {"color": "navy", "weight": 0.3, "fillOpacity": 0}
        else:
            style = {}

        # Check if the dataframe is a GeoDataFrame without longitude/latitude coordinates
        if isinstance(df, gpd.GeoDataFrame) and is_latitude_longitude(df) == False:   
            # Add other GeoDataFrames as separate layers
            map.add_gdf(
                df,
                layer_name=filename,
                style=style,
                info_mode='on_click',
                zoom_to_layer=True
            )
    
        # If the dataframe has latitude and longitude columns, create a HEATMAP
        elif is_latitude_longitude(df):
            # Define the latitude and longitude columns
            # NOTE: These could be returned in the is_latitude_longitud() function
            lat_col = [col for col in df.columns if "latitude" in col.lower()][0]
            lon_col = [col for col in df.columns if "longitude" in col.lower()][0]

            # Get all numeric columns to display in the heatmap
            numeric_cols = df.select_dtypes(include="number").columns.tolist()

            # Allow user to select a numeric variable to plot on the map
            heatmap_var = st.selectbox(
                "Select a variable to plot on the heatmap",
                numeric_cols,
                index=0
            )

            # Filter the dataframe to only include the latitude, longitude, and selected variable column
            heatmap_df = df[[lat_col, lon_col, heatmap_var]].dropna()
                
            # Add the heatmap layer to the map
            map.add_heatmap(
                data=heatmap_df,
                latitude=lat_col,
                longitude=lon_col,
                layer_name="Heatmap",
                value = heatmap_var,
                radius=10,
                blur=15
            )
            # Calculate bounding box and auto zoom
            min_lat = heatmap_df[lat_col].min()
            max_lat = heatmap_df[lat_col].max()
            min_lon = heatmap_df[lon_col].min()
            max_lon = heatmap_df[lon_col].max()

            map.fit_bounds([[min_lat, min_lon], [max_lat, max_lon]])
            
def show_mapping():
    
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
    
    # Set the global fonts 
    st.markdown(
    """
    <style>
    /* Set Helvetica (fallback to Arial, sans-serif) globally */
    html, body, [class*="css"]  {
        font-family: 'Avenir', 'Arial', sans-serif; font-weight: 300;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Display the page
    render_mapping()

if __name__ == "__main__":
    show_mapping()