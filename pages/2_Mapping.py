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
from app_utils import (get_user_files, file_hash, read_data, 
                       get_file_name, get_columns, is_latitude_longitude,
                       clean_data, convert_all_timestamps_to_str, process_uploaded_files)
from statistics import mean
from st_aggrid import AgGrid, ColumnsAutoSizeMode, GridOptionsBuilder, GridUpdateMode
import math


def render_mapping():
    """
    Render the mapping page of the Streamlit app.
    This function retrieves user-uploaded files, processes them, and displays
    them on a map. It also provides options for filtering and comparing data
    based on user selections.
    """
    # Set the page title
    st.title("Mapping")

    # Get the user files from the uploader and process them
    user_files = get_user_files()
    # If no files are uploaded, show a warning message
    processed_files = process_uploaded_files(user_files)
    
    # If no geo-dataframes are found, show a warning message
    geo_df_found = False
    for df, filename in processed_files:
        if isinstance(df, gpd.GeoDataFrame):
            geo_df_found = True
            break
    
    # If no GeoDataFrames were found, just display a warning message
    if geo_df_found == False:
        st.warning("""
        Mapping is not available because no valid GeoDataFrames were found in the uploaded files.\n
        Please ensure that you have uploaded files with geographic data 
        (e.g., shapefiles, GeoJSON, FlatGeobuf, etc.) or files that contain latitude and longitude coordinates.
        """)
        return

    # Initialize zoning dataframe and specific map style
    zoning_gdf = None
    zoning_style = {}

    # Create an option bank of basemaps to choose from
    basemaps = {
    "Standard": "OpenStreetMap",
    "Satellite View": "Esri.WorldImagery",
    "CartoDB Light": "CartoDB.Positron",
    "Elevation": "OpenTopoMap",
    "Shaded Relief Map": "Esri.WorldShadedRelief",
    "Hillshade Map": "Esri.WorldHillshade",
    "National Geographic Style": "Esri.NatGeoWorldMap",
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

    # Initialize a blank map object to add layers onto later
    map = leafmap.Map(center=default_center, zoom=7)
    map.add_basemap(selected_basemap)
    
    # Loop through each processed dataframe and its filename
    for df, filename in processed_files:
        
        df = convert_all_timestamps_to_str(df)

        # Determine the layer style based on common words in the VTZA data folder
        if "border" in filename:
            style = {"fillOpacity": 0.2, "color": "dodgerblue", "weight": 2}
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

        # Initialize selected_district variable for use in filtering the dataset
        selected_district = None
        # Check if the dataframe is a GeoDataFrame without longitude/latitude coordinates
        if isinstance(df, gpd.GeoDataFrame) and is_latitude_longitude(df) == False:
            
            # If the dataframe is a zoning file
            if "zoning" in filename.lower():
                zoning_gdf = df
                zoning_style = style
                # NOTE: This is hardcoded for now (date column cannot be mapped), but could be made dynamic
                zoning_gdf = zoning_gdf.drop(columns=["Bylaw Date"])


                # Create three columns to display the three selection boxes (County, Jurisdiction, District)
                col1, col2, col3 = st.columns(3)

                # On the left column, create a selection box for the county
                with col1:
                    county_selection = st.selectbox(
                        "**County**",
                        ["All Counties"] + sorted(zoning_gdf["County"].dropna().unique()),
                        index=0,
                    )

                # Filter the zoning dataframe based on the county selection
                df_filtered_county = zoning_gdf if county_selection == "All Counties" else zoning_gdf[zoning_gdf["County"] == county_selection]

                # On the middle column, create a selection box for the jurisdiction
                with col2:
                    jurisdiction_selection = st.selectbox(
                        "**Jurisdiction**",
                        ["All Jurisdictions"] + sorted(df_filtered_county["Jurisdiction"].dropna().unique()),
                        index=0,
                    )

                # Filter the zoning dataframe based on the jurisdiction selection
                df_filtered_jurisdiction = (
                    df_filtered_county if jurisdiction_selection == "All Jurisdictions"
                    else df_filtered_county[df_filtered_county["Jurisdiction"] == jurisdiction_selection]
                )

                # On the right column, create a selection box for the district
                with col3:
                    district_options = sorted(df_filtered_jurisdiction["District Name"].dropna().unique())
                    all_district_option = "All Districts"
                    multiselect_options = [all_district_option] + district_options
                    
                    district_selection = st.multiselect(
                        "**District(s)**",
                        options=multiselect_options,
                        default=[all_district_option]
                    )

                # Filter the zoning dataframe based on the district selection
                if all_district_option in district_selection or not district_selection:
                    selected_district = df_filtered_jurisdiction
                else:
                    selected_district = df_filtered_jurisdiction[
                        df_filtered_jurisdiction["District Name"].isin(district_selection)
                    ]

                # If a district is selected, set the map center and zoom level
                if not selected_district.empty:
                    bounds = selected_district.total_bounds
                    minx, miny, maxx, maxy = bounds
                    center_long = (minx + maxx) / 2
                    center_lat = (miny + maxy) / 2
                    map.set_center(center_long, center_lat, zoom=10)
                    
                    # Add the user-filtered zoning layer to the map
                    map.add_gdf(
                        selected_district,
                        layer_name=f"{district_selection} Geometry" if district_selection != "All Districts" else "Selected Area",
                        style=zoning_style,
                        info_mode='on_click',
                        zoom_to_layer=True
                    )
                    
                # If it is not a zoning file, add it as a layer to the map
                else:
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
                    st.dataframe(combined_df_sorted)
            
            # If the user has not selected any rows, show a warning and do not display any comparisons
            except AttributeError:
                st.warning("No rows selected. Please select at least one row to compare district data.")

def map_main():
    st.markdown(
    """
    <style>
    /* Set Helvetica (fallback to Arial, sans-serif) globally */
    html, body, [class*="css"]  {
        font-family: 'Avenir', 'Arial', sans-serif; font-weight: 300;
    }
    </style>
    """, unsafe_allow_html=True)
    render_mapping()

if __name__ == "__main__":
    map_main()