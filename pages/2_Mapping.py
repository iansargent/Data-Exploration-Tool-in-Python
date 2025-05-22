"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Mapping Page
"""


import streamlit as st
import geopandas as gpd
import leafmap.foliumap as leafmap
from app_utils import get_user_files, file_hash, read_data, get_file_name, get_columns


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
        if not isinstance(df, gpd.GeoDataFrame):
            continue

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

    if has_geodata == True:
        district_selection = st.selectbox(
            label="Select a district to view", 
            options=["All Districts"] + df['Full_District_Name'].unique().tolist(),
            index=0,
        )

        if district_selection == "All Districts":
            selected_district = df
            zoom = 6
            bounds = selected_district.total_bounds
            minx, miny, maxx, maxy = bounds
            center_long = (minx + maxx) / 2
            center_lat = (miny + maxy) / 2

            map.set_center(center_long, center_lat, zoom=zoom)

        else:
            selected_district = df[df['Full_District_Name'] == district_selection]
            zoom = 15


        if not selected_district.empty:
            geom = selected_district.geometry.iloc[0]
            centroid = geom.centroid
            long, lat = centroid.x, centroid.y

            map.set_center(long, lat, zoom=zoom)

            map.add_gdf(
                selected_district,  # only the selected district, not full df
                layer_name=f"{district_selection} Geometry",
                style=style,
                info_mode='on_click',
                zoom_to_layer=False
            )

        with st.spinner(text="Loading map..."):
            # Add a layer control to the map
            map.add_layer_control()
            # Display the map in Streamlit
            map.to_streamlit(use_container_width=True)
    
    else:
        st.info("No GeoJSON or FGB files detected. Mapping not available for uploaded files.")

def main():
    render_mapping()

if __name__ == "__main__":
    main()

