"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Mapping Page
"""


import streamlit as st
import geopandas as gpd
import leafmap.foliumap as leafmap
from app_utils import (get_user_files, file_hash, read_data, 
                       get_file_name, get_columns, is_latitude_longitude,
                       clean_data)
from statistics import mean


def render_mapping():
    st.title("Mapping")
    user_files = get_user_files()
    seen_hashes = set()
    
    map = leafmap.Map(zoom=10)

    if not user_files:
        st.warning("No files uploaded.")
        return

    zoning_gdf = None
    zoning_style = {}

    for file in user_files:
        fid = file_hash(file)
        if fid in seen_hashes:
            continue
        seen_hashes.add(fid)

        df = read_data(file)
        if df is None:
            continue
        df = clean_data(df)
        
        filename = get_file_name(file)

        # Determine style based on filename
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

        if isinstance(df, gpd.GeoDataFrame) and is_latitude_longitude(df) == False:
            
            if "zoning" in filename.lower():
                zoning_gdf = df
                zoning_style = style
            else:
                # Add other GeoDataFrames as separate layers
                map.add_gdf(
                    df,
                    layer_name=filename,
                    style=style,
                    info_mode='on_click',
                    zoom_to_layer=True
                )

    # If zoning geodata found, show filtering options and add filtered layer
    if zoning_gdf is not None:
        col1, col2, col3 = st.columns(3)

        with col1:
            county_selection = st.selectbox(
                "Select a county to view",
                ["All Counties"] + sorted(zoning_gdf["County"].unique()),
                index=0,
            )

        df_filtered_county = zoning_gdf if county_selection == "All Counties" else zoning_gdf[zoning_gdf["County"] == county_selection]

        with col2:
            jurisdiction_selection = st.selectbox(
                "Select a jurisdiction to view",
                ["All Jurisdictions"] + sorted(df_filtered_county["Jurisdiction"].unique()),
                index=0,
            )

        df_filtered_jurisdiction = (
            df_filtered_county if jurisdiction_selection == "All Jurisdictions"
            else df_filtered_county[df_filtered_county["Jurisdiction"] == jurisdiction_selection]
        )

        with col3:
            district_selection = st.selectbox(
                "Select a district to view",
                ["All Districts"] + sorted(df_filtered_jurisdiction["Full_District_Name"].unique()),
                index=0,
            )

        if district_selection == "All Districts":
            selected_district = df_filtered_jurisdiction
        else:
            selected_district = df_filtered_jurisdiction[df_filtered_jurisdiction["Full_District_Name"] == district_selection]

        if not selected_district.empty:
            bounds = selected_district.total_bounds
            minx, miny, maxx, maxy = bounds
            center_long = (minx + maxx) / 2
            center_lat = (miny + maxy) / 2
            map.set_center(center_long, center_lat, zoom=10)

            map.add_gdf(
                selected_district,
                layer_name=f"{district_selection} Geometry" if district_selection != "All Districts" else "Selected Area",
                style=zoning_style,
                info_mode='on_click',
                zoom_to_layer=True
            )
    elif is_latitude_longitude(df):
        
        lat_col = [col for col in df.columns if "latitude" in col.lower()][0]
        lon_col = [col for col in df.columns if "longitude" in col.lower()][0]

        numeric_cols = df.select_dtypes(include="number").columns.tolist()

        heatmap_var = st.selectbox(
            "Select a variable to plot on the map",
            numeric_cols,
            index=0
        )

        heatmap_df = df[[lat_col, lon_col, heatmap_var]].dropna()
        
        center_lat = mean(heatmap_df[lat_col])
        center_lon = mean(heatmap_df[lon_col])

        map.set_center(center_lon, center_lat, zoom=7.5)

        map.add_heatmap(
            data=heatmap_df,
            latitude=lat_col,
            longitude=lon_col,
            layer_name="Heatmap",
            value = heatmap_var,
            radius=10,
            blur=15
        )
        
    
    with st.spinner("Loading map..."):
        map.add_layer_control()
        map.to_streamlit(use_container_width=True)
    

render_mapping()