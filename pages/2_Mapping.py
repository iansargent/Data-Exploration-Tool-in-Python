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
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import io
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
    
    # Initialize selected_district variable for use in filtering the dataset
    selected_district = None
    
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
    
        # If the dataframe has latitude and longitude columns, create a heatmap
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
    

    # Display the map with a loading "spinner" icon
    with st.spinner("Loading map..."):
        # Add a layer control to the map
        map.add_layer_control()
        # Display the map on the page
        map.to_streamlit(use_container_width=True)
        
        # If the user has selected a district, show the selected areas they might want to compare
        if selected_district is not None:
            # Section title
            st.subheader("Selected Areas to Compare")

            # Drop the geometry column to allow for table display to work
            selected_district = selected_district.drop(columns=["geometry"]).reset_index(drop=True)
            
            # Building a custom table display using AgGrid
            # NOTE: This will show what is on the map in table form
            # NOTE: This table allows for users to select certain rows to make comparisons
            gb = GridOptionsBuilder.from_dataframe(selected_district)
            gb.configure_selection(selection_mode="multiple", use_checkbox=True)
            grid_options = gb.build()
            
            # Set the grid height to dynamically change with the number of rows
            grid_height = 40 * (len(selected_district) + 1.45)
            grid_height = min(grid_height, 600)

            # Display the filtered table
            grid_response = AgGrid(
                selected_district,
                theme='material', 
                gridOptions=grid_options, 
                update_mode=GridUpdateMode.SELECTION_CHANGED,
                columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
                height=grid_height
            )

            # Define the selected rows from the AgGrid table
            selected_rows = grid_response["selected_rows"]
            
            try:
                # If the user has selected rows, show the comparison table
                if selected_rows.empty == False:
                    # Turn the selected rows into a DataFrame
                    selected_df = pd.DataFrame(selected_rows)
                    # Initialize an empty list to hold the melted rows for each district (for comparison)
                    dfs = []

                    # Loop through each selected row
                    for _, row in selected_df.iterrows():
                        # Get the district name to use in the comparison table
                        district_name = row["Jurisdiction District Name"]

                        # Reset the indeces
                        df_long = row.reset_index()
                        # Define the column names for the "long" format rows (should look like two column)
                        df_long.columns = ["Variable", "Value"]

                        # Rename Value column only, keep Variable as is
                        df_long = df_long.rename(columns={"Value": district_name})
                        # Add each 
                        dfs.append(df_long)

                    # Import functools reduce to merge each separate row into a single comparison dataframe
                    from functools import reduce

                    # Merge all dfs on the "Variable" column
                    combined_df = reduce(
                        lambda left, right: pd.merge(left, right, on="Variable", how="outer"),
                        dfs
                    )

                    # Sort the comparison table to show non-empty rows at the top of the table 
                    combined_df_sorted = combined_df.copy()
                    combined_df_sorted["na_count"] = combined_df_sorted.isna().sum(axis=1)
                    combined_df_sorted = combined_df_sorted.sort_values("na_count").drop(columns="na_count")

                    # Subheader for the comparison table
                    st.subheader("District Comparisons")
                    # Display the comparison table
                    filtered_combined_df_sorted = dataframe_explorer(combined_df_sorted, case=False)
                    st.dataframe(filtered_combined_df_sorted, use_container_width=True)
            
            # If the user has not selected any rows, show a warning and do not display any comparisons
            except AttributeError:
                st.warning("No rows selected. Please select at least one row to compare district data.")

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