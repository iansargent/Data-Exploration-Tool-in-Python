"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Mapping Page
"""


import streamlit as st
import geopandas as gpd
import leafmap.foliumap as leafmap
from app_utils import get_user_files, file_hash, read_data, get_file_name


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
        else:
            style = None


        map.add_gdf(df, layer_name=file.name, style=style)

    if has_geodata == True:
        map.to_streamlit(use_container_width=True)
    
    else:
        st.info("No GeoJSON or FGB files detected. Mapping not available for uploaded files.")

def main():
    render_mapping()

if __name__ == "__main__":
    main()

