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
                       render_zoning_layer, assign_layer_style, render_table,
                       render_comparison_table, get_lat_lon_cols, load_zoning_data)
from st_aggrid import AgGrid, ColumnsAutoSizeMode, GridOptionsBuilder, GridUpdateMode
from streamlit_extras.dataframe_explorer import dataframe_explorer 


filtered_gdf = pd.DataFrame()
vt_zoning = False

def render_mapping():
    st.markdown("<h2 style='color: #4a4a4a;'>Mapping</h2>", unsafe_allow_html=True)
    user_files = get_user_files()
    processed_files = process_uploaded_files(user_files)
    vt_zoning = st.toggle(label="Use the VT Zoning Data Dataset")

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
    basemap_select_box = st.selectbox("**Basemap**", list(basemaps.keys()), index=0)
    selected_basemap = basemaps[basemap_select_box]

    m = leafmap.Map(center=[44.26, -72.57], zoom=8, zoom_snap=0.5)
    m.add_basemap(selected_basemap)

    # Add uploaded user files layers (both GeoDataFrames and lat/lon heatmaps)
    for df, filename in processed_files:
        df = convert_all_timestamps_to_str(df)
        style = assign_layer_style(filename)

        if isinstance(df, gpd.GeoDataFrame) and not is_latitude_longitude(df):
            m.add_gdf(df, layer_name=filename, style=style, info_mode='on_click', zoom_to_layer=True)

        elif is_latitude_longitude(df):
            lat_col, lon_col = get_lat_lon_cols(df)
            if not lat_col or not lon_col:
                st.warning(f"Could not identify lat/lon columns in {filename}. Skipping heatmap.")
                continue

            numeric_cols = df.select_dtypes(include="number").columns.tolist()
            circle_var = st.selectbox(f"Select a variable to plot from {filename}", numeric_cols, index=0, key=f"{filename}_circle_var")

            circle_df = df[[lat_col, lon_col, circle_var]].dropna()

            from sklearn.preprocessing import MinMaxScaler
            
            scaler = MinMaxScaler(feature_range=(0.5, 10))
            scaled_values = scaler.fit_transform(circle_df[[circle_var]])
            circle_df["scaled_radius"] = scaled_values.flatten()

            for _, row in circle_df.iterrows():
                m.add_circle_markers_from_xy(
                    data=pd.DataFrame([row]),
                    x=lon_col,
                    y=lat_col,
                    radius=row["scaled_radius"],
                    fill_color="mediumseagreen",
                    tooltip=[circle_var]
                )

            min_lat, max_lat = circle_df[lat_col].min(), circle_df[lat_col].max()
            min_lon, max_lon = circle_df[lon_col].min(), circle_df[lon_col].max()
            m.fit_bounds([[min_lat, min_lon], [max_lat, max_lon]])

        # --- Add Zoning File if Toggle is ON ---
    if vt_zoning:
        zoning_gdf = load_zoning_data()
        _, filtered_gdf = render_zoning_layer(m)

    # --- Always Show the Map ---
    m.to_streamlit(height=600)

    # --- Zoning Table and Comparison Below ---
    if vt_zoning:
        st.markdown("### Zoning Districts Table")
        selected = render_table(filtered_gdf)
        try:
            if not selected.empty:
                render_comparison_table(selected)
        except:
            st.warning("No Selected Districts to Compare")

    return m
            
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
    map = render_mapping()


if __name__ == "__main__":
    show_mapping()