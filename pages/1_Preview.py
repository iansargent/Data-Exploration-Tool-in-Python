"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Table Preview Page
"""


import streamlit as st
from st_aggrid import AgGrid, ColumnsAutoSizeMode
from app_utils import get_user_files, file_hash, read_data, clean_data
import geopandas as gpd
import leafmap.foliumap as leafmap


def render_preview():
    st.title("📋 Preview")
    user_files = get_user_files()
    seen_hashes = set()

    if not user_files:
        st.warning("No files uploaded.")
        return

    for file in user_files:
        fid = file_hash(file)
        if fid in seen_hashes:
            st.info(f"Duplicate skipped: {file.name}")
            continue
        seen_hashes.add(fid)

        df = read_data(file)
        
        if isinstance(df, gpd.GeoDataFrame):
     
            st.subheader(f"Map of {file.name}")

            map = leafmap.Map(zoom=10)
            
            if "border" in file.name.lower():
                style={"fillOpacity": 0.2, "color": "dodgerblue", "weight": 2}
            
            elif "linearfeatures" in file.name.lower():
                style={"color": "navy", "weight": 2}
            
            elif "pointfeatures" in file.name.lower():
                style={"color": "darkorange", "weight": 2}
            
            elif "servicearea" in file.name.lower():
                style={"color": "darkred", "weight": 2}
            
            elif "wwtf" in file.name.lower():
                style={"color": "darkgreen", "weight": 2}
            
            else:
                style = None
                 
            # Add the GeoDataFrame to the map
            map.add_gdf(
                df, 
                layer_name=file.name,
                style=style
            )

            # Display the map in Streamlit
            map.to_streamlit(use_container_width=True)
            
            st.write("Table Preview:")
            # If the file is a GeoDataFrame, convert it to a DataFrame
            df_geo_aggrid = df.drop(columns=["geometry"])
            df_geo_aggrid = df.reset_index(drop=True)
            
            AgGrid(df_geo_aggrid, theme="material", columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)
        
        else:
            st.subheader(f"Preview of {file.name}")
            AgGrid(df, theme="material", columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)
    

render_preview()
