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
                       clean_data)
from statistics import mean
from st_aggrid import AgGrid, ColumnsAutoSizeMode, GridOptionsBuilder, GridUpdateMode


def render_mapping():
    """
    Render the mapping page of the Streamlit app.
    This function retrieves user-uploaded files, processes them, and displays
    them on a map. It also provides options for filtering and comparing data
    based on user selections.
    """
    # Set the page title
    st.title("Mapping")
    # Get the user files from the uploader
    user_files = get_user_files()
    # Initialize a set to keep track of seen file hashes
    seen_hashes = set()
    
    # Initialize a blank map object to add layers onto later
    map = leafmap.Map(zoom=10)

    # Check if the user has uploaded any files
    if not user_files:
        st.warning("No files uploaded.")
        return

    # Initialize zoning dataframe and specific map style
    zoning_gdf = None
    zoning_style = {}

    # Loop through each uploaded file
    for file in user_files:
        # Give each file a unique ID
        fid = file_hash(file)

        # If the file ID is already seen, skip it
        if fid in seen_hashes:
            continue
        # and add it to the set of seen IDs
        seen_hashes.add(fid)

        # Read the data
        df = read_data(file)
        if df is None:
            continue
        # Clean the data
        df = clean_data(df)
        # NOTE: This is hardcoded for now (date column cannot be mapped), but could be made dynamic
        df = df.drop(columns=["Bylaw Date"])
        
        # Get the filename to use for map layer settings
        filename = get_file_name(file)

        # Determine the layer style based on common words in the VTZA data folder
        if "border" in filename:
            style = {"fillOpacity": 0.2, "color": "dodgerblue", "weight": 2}
        elif "linearfeatures" in filename:
            style = {"color": "navy", "weight": 2}
        elif "pointfeatures" in filename:
            style = {"color": "darkorange", "weight": 2}
        elif "servicearea" in filename:
            style = {"color": "darkred", "weight": 2}
        elif "wwtf" in filename:
            style = {"color": "darkgreen", "weight": 2}
        elif "zoning" in filename:
            style = {"color": "blue", "weight": 0.5}
        else:
            style = {}

        # Check if the dataframe is a GeoDataFrame without longitude/latitude coordinates
        if isinstance(df, gpd.GeoDataFrame) and is_latitude_longitude(df) == False:
            
            # If the dataframe is a zoning file
            if "zoning" in filename.lower():
                zoning_gdf = df
                zoning_style = style
            
            # If it is not a zoning file, add it as a layer to the map
            else:
                # Add other GeoDataFrames as separate layers
                map.add_gdf(
                    df,
                    layer_name=filename,
                    style=style,
                    info_mode='on_click',
                    zoom_to_layer=False
                )

    # Initialize selected_district variable for use in filtering the dataset
    selected_district = None
    
    # If it is a zoning dataframe, show filtering options
    if zoning_gdf is not None:
        
        # Create three columns to display the three selection boxes (County, Jurisdiction, District)
        col1, col2, col3 = st.columns(3)

        # On the left column, create a selection box for the county
        with col1:
            county_selection = st.selectbox(
                "Select a county to view",
                ["All Counties"] + sorted(zoning_gdf["County"].dropna().unique()),
                index=0,
            )

        # Filter the zoning dataframe based on the county selection
        df_filtered_county = zoning_gdf if county_selection == "All Counties" else zoning_gdf[zoning_gdf["County"] == county_selection]

        # On the middle column, create a selection box for the jurisdiction
        with col2:
            jurisdiction_selection = st.selectbox(
                "Select a jurisdiction to view",
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
                "Select district(s) to view",
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

    # If the dataframe has latitude and longitude columns, create a heatmap
    elif is_latitude_longitude(df):
        # Define the latitude and longitude columns
        # NOTE: This is hardcoded for now, but could be returned in the is_latitude_longitude function
        lat_col = [col for col in df.columns if "latitude" in col.lower()][0]
        lon_col = [col for col in df.columns if "longitude" in col.lower()][0]

        # Get all numeric columns to display in the heatmap
        numeric_cols = df.select_dtypes(include="number").columns.tolist()

        # Allow user to select a numeric variable to plot on the map
        heatmap_var = st.selectbox(
            "Select a variable to plot on the map",
            numeric_cols,
            index=0
        )

        # Filter the dataframe to only include the latitude, longitude, and selected variable column
        heatmap_df = df[[lat_col, lon_col, heatmap_var]].dropna()
        
        # Set the map center based on the average latitude and longitude of the data
        center_lat = mean(heatmap_df[lat_col])
        center_lon = mean(heatmap_df[lon_col])
        map.set_center(center_lon, center_lat, zoom=7.5)

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
            
            # Display the filtered table
            grid_response = AgGrid(
                selected_district,
                theme='material', 
                gridOptions=grid_options, 
                update_mode=GridUpdateMode.SELECTION_CHANGED,
                columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,)

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
                        district_name = row["District Name"]

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
                    # Subheader for the comparison table
                    st.subheader("District Comparisons")
                    # Display the comparison table
                    st.write(combined_df)
            
            # If the user has not selected any rows, show a warning and do not display any comparisons
            except AttributeError:
                st.warning("No rows selected. Please select at least one row to compare district data.")

                
                
                




            


    

render_mapping()