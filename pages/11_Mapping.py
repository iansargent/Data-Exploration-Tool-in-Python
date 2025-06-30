"""
Ian Sargent
ORCA
Streamlit Data Visualization App

General Mapping Page (For uploaded files)
"""

# Necessary imports
import streamlit as st
import pandas as pd
import geopandas as gpd
import leafmap.foliumap as leafmap
from sklearn.preprocessing import MinMaxScaler
from app_utils import (get_user_files, is_latitude_longitude, 
                       convert_all_timestamps_to_str, process_uploaded_files, 
                       assign_layer_style, get_lat_lon_cols)


def render_mapping():
    # Page header
    st.header("General Mapping")
    # Get the user files from the file uploader
    user_files = get_user_files()
    # Read and clean the uploaded files
    processed_files = process_uploaded_files(user_files)

    # Options for different basemaps
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
    # Select box for user to change the basemap
    basemap_select_box = st.selectbox("**Basemap**", list(basemaps.keys()), index=0)
    selected_basemap = basemaps[basemap_select_box]

    # Define a leafmap Map object centered at Vermont
    m = leafmap.Map(center=[44.26, -72.57], zoom=8, zoom_snap=0.5)
    # Add the user-selected basemap
    m.add_basemap(selected_basemap)

    # Add uploaded user files layers (both GeoDataFrames and datasets with lat/lon columns)
    for df, filename in processed_files:
        # Convert any datetime variables to string type
        df = convert_all_timestamps_to_str(df)
        # Based on the filename, assign a color if it is a keyword
        style = assign_layer_style(filename)

        # If it is a GeoDataFrame but does not have lat/lon columns
        if isinstance(df, gpd.GeoDataFrame) and not is_latitude_longitude(df):
            # Add the layer to the map
            m.add_gdf(df, layer_name=filename, style=style, info_mode='on_click', zoom_to_layer=True)

        # If there are lat/lon columns, define them respectfully
        elif is_latitude_longitude(df):
            lat_col, lon_col = get_lat_lon_cols(df)
            if not lat_col or not lon_col:
                st.warning(f"Could not identify lat/lon columns in {filename}. Skipping heatmap.")
                continue
            
            # Get a list of the numeric column names for user selection
            numeric_cols = df.select_dtypes(include="number").columns.tolist()
            # Selection box of which numeric variables the user wants to layer onto the map
            circle_var = st.selectbox(f"Select a variable to plot from {filename}", numeric_cols, index=0, key=f"{filename}_circle_var")
            # Filter the dataset for only the coords and selected variable (dropping NAs)
            circle_df = df[[lat_col, lon_col, circle_var]].dropna()
            
            # Scale the selected variable on a range of 0.5 to 10
            scaler = MinMaxScaler(feature_range=(0.5, 10))
            scaled_values = scaler.fit_transform(circle_df[[circle_var]])
            circle_df["scaled_radius"] = scaled_values.flatten()

            # For each observation, add a circle with its respective size (A graduated symbol map)
            for _, row in circle_df.iterrows():
                m.add_circle_markers_from_xy(
                    data=pd.DataFrame([row]),
                    x=lon_col,
                    y=lat_col,
                    radius=row["scaled_radius"],
                    fill_color="mediumseagreen",
                    tooltip=[circle_var]
                )

            # Define the geographic boundaries for the map
            min_lat, max_lat = circle_df[lat_col].min(), circle_df[lat_col].max()
            min_lon, max_lon = circle_df[lon_col].min(), circle_df[lon_col].max()
            m.fit_bounds([[min_lat, min_lon], [max_lat, max_lon]])

    # Display the map to the page
    m.to_streamlit(height=600)

    return

      
def show_mapping():
    # Display the page
    render_mapping()


if __name__ == "__main__":
    show_mapping()