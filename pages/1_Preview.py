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

    map = leafmap.Map(zoom=10)
    table_previews = []

    for file in user_files:
        fid = file_hash(file)
        if fid in seen_hashes:
            st.info(f"Duplicate skipped: {file.name}")
            continue
        seen_hashes.add(fid)

        df = read_data(file)

        if isinstance(df, gpd.GeoDataFrame):
            fname = file.name.lower()

            # Style logic
            if "border" in fname:
                style = {"fillOpacity": 0.2, "color": "dodgerblue", "weight": 2}
            elif "linearfeatures" in fname:
                style = {"color": "navy", "weight": 2}
            elif "pointfeatures" in fname:
                style = {"color": "darkorange", "weight": 2}
            elif "servicearea" in fname:
                style = {"color": "darkred", "weight": 2}
            elif "wwtf" in fname:
                style = {"color": "darkgreen", "weight": 2}
            else:
                style = None

            # Add to map
            map.add_gdf(df, layer_name=file.name, style=style)

            # Save table (without geometry)
            df_preview = df.drop(columns=["geometry"], errors="ignore").reset_index(drop=True)
            table_previews.append((file.name, df_preview))

        else:
            st.subheader(f"Preview of {file.name}")
            AgGrid(df, theme="material", columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)

    # Show map once
    if table_previews:
        st.subheader("Map of Uploaded Layers")
        map.to_streamlit(use_container_width=True)

        # Show all GeoDF tables
        st.subheader("Table Previews for Each Layer")
        for name, df_preview in table_previews:            
            with st.expander(f"**{name}**"):
                st.write("This is a preview of the data without geometry.")
                st.dataframe(df_preview, use_container_width=True)

render_preview()
