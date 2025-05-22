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


def render_mapping():
    st.title("Mapping")
    user_files = get_user_files()
    seen_hashes = set()
    
    has_geodata = False
    map = leafmap.Map(zoom=10)

    if not user_files:
        st.warning("No files uploaded.")
        return

    for file in user_files:
        fid = file_hash(file)
        if fid in seen_hashes:
            continue
        seen_hashes.add(fid)

        df = read_data(file)
        df = clean_data(df)
        
        if isinstance(df, gpd.GeoDataFrame):
            has_geodata = True
        
        filename = get_file_name(file)

        # Style logic
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

        df_columns = get_columns(df)

    if has_geodata == True and "zoning" in filename:
        
        col1, col2, col3 = st.columns(3)

        with col1:
            county_selection = st.selectbox(
                "Select a county to view",
                ["All Counties"] + sorted(df["County"].unique()),
                index=0,
            )

        df_filtered_county = df if county_selection == "All Counties" else df[df["County"] == county_selection]

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
            map.set_center(center_long, center_lat)

            map.add_gdf(
                selected_district,
                layer_name=f"{district_selection} Geometry" if district_selection != "All Districts" else "Selected Area",
                style=style,
                info_mode='on_click',
                zoom_to_layer=True
            )

        with st.spinner("Loading map..."):
            map.add_layer_control()
            map.to_streamlit(use_container_width=True)
    
    
    elif has_geodata == True and is_latitude_longitude(df) and "zoning" not in filename:

        # Get actual lat/lon column names
        lat_col = [col for col in df.columns if "latitude" in col.lower()][0]
        lon_col = [col for col in df.columns if "longitude" in col.lower()][0]

        numeric_cols = df.select_dtypes(include="number").columns.tolist()

        # User selects one numeric column to map
        heatmap_var = st.selectbox(
            "Select a numeric column to map:",
            numeric_cols,
            index=0
        )

        heatmap_df = df[[lat_col, lon_col, heatmap_var]].dropna()

        if not heatmap_df.empty:
            # Set map center
            bounds = heatmap_df[[lon_col, lat_col]].agg(['min', 'max']).values
            min_x, max_x = bounds[0]
            min_y, max_y = bounds[1]
            
            center_long = (min_x + max_x) / 2
            center_lat = (min_y + max_y) / 2
            
            heatmap = leafmap.Map(zoom=10)
            heatmap.set_center(center_long, center_lat)
            heatmap.fit_bounds([[min_y, min_x], [max_y, max_x]])

            # Add heatmap
            heatmap.add_heatmap(
                data=heatmap_df,
                latitude=lat_col,
                longitude=lon_col,
                value=heatmap_var,
                radius=15,
                blur=20
            )

            with st.spinner("Loading heatmap..."):
                heatmap.add_layer_control()
                heatmap.to_streamlit(use_container_width=True)
        else:
            st.warning("No valid lat/lon data to plot a heatmap.")
        
        
        # Add the GeoDataFrame to the map
        map.add_gdf(
            df,
            layer_name=filename,
            style=style,
            info_mode='on_click',
            zoom_to_layer=True
        )
        # Set the map center and zoom level
        bounds = df.total_bounds
        minx, miny, maxx, maxy = bounds
        center_long = (minx + maxx) / 2
        center_lat = (miny + maxy) / 2
        map.set_center(center_long, center_lat)
        # Display the map
        with st.spinner("Loading map..."):
            map.add_layer_control()
            map.to_streamlit(use_container_width=True)
    
    else:
        # No GeoDataFrame object found
        st.info("No GeoJSON or FGB files detected. Mapping not available for uploaded files.")


def main():
    render_mapping()

if __name__ == "__main__":
    main()

