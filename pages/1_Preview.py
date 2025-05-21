"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Table Preview Page
"""


import streamlit as st
from st_aggrid import AgGrid, ColumnsAutoSizeMode
from app_utils import get_user_files, file_hash, read_data, clean_data, get_columns, is_latitude_longitude
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

        # GeoDataFrame handling
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

            # Add GeoDataFrame to map
            map.add_gdf(df, layer_name=file.name, style=style)

            # Save preview without geometry
            df_preview = df.drop(columns=["geometry"], errors="ignore").reset_index(drop=True)
            table_previews.append((file.name, df_preview))

        # Non-spatial data
        else:
            df_columns = get_columns(df)
            lat_col = [col for col in df_columns if "latitude" in col.lower()]
            lon_col = [col for col in df_columns if "longitude" in col.lower()]

            # If lat/lon columns exist, create heatmap
            if lat_col and lon_col:
                lat = lat_col[0]
                lon = lon_col[0]

                center_lat = df[lat].mean()
                center_lon = df[lon].mean()
                                
                st.subheader(f"Heatmap of {file.name}")

                numeric_cols = df.select_dtypes(include="number").columns.tolist()
                
                weight_col = st.selectbox(
                    f"Select a numeric column for heatmap weighting ({file.name})",
                    options=["(None)"] + numeric_cols,
                    key=file.name
                )

                if weight_col == "(None)":
                    heat_data = df[[lat, lon]].dropna().values.tolist()
                else:
                    heat_data = df[[lat, lon, weight_col]].dropna().values.tolist()

                map.add_heatmap(heat_data, name=f"{file.name} Heatmap", radius=15)
                map.set_center(center_lon, center_lat, zoom=10)

                # Save table preview
                table_previews.append((file.name, df.reset_index(drop=True)))

            # If no lat/lon, show normal table
            else:
                st.subheader(f"Preview of {file.name}")
                AgGrid(df, theme="material", columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)

    # Show map
    if table_previews:
        st.subheader("Map of Uploaded Layers")
        map.to_streamlit(use_container_width=True)

        # Show table previews
        st.subheader("Table Previews for Each Layer")
        for name, df_preview in table_previews:
            with st.expander(f"**{name}**"):
                st.write("This is a preview of the data.")
                st.dataframe(df_preview, use_container_width=True)

render_preview()
