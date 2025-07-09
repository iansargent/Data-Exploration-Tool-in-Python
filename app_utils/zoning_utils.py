"""
Open Research Community Accelorator
Vermont Data App

Zoning Utility Functions
"""

# Streamlit 
import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards 

# Data Processing / Plotting
import pandas as pd
import geopandas as gpd
import altair as alt
import numpy as np

# Standard Libraries
import os
import io

# Color Mapping 
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.colorbar import ColorbarBase


def zoning_district_map(filtered_geojson, filtered_gdf_map):
    import pydeck as pdk
    
    layer = pdk.Layer(
        "GeoJsonLayer",
        data=filtered_geojson,
        get_fill_color=[95, 165, 231, 200],
        get_line_color=[80, 80, 80, 80],
        highlight_color=[222, 102, 0, 200],
        line_width_min_pixels=0.5,
        pickable=True,
        auto_highlight=True)

    # Calculate the center and zoom level of the map
    bounds = filtered_gdf_map.total_bounds
    center_lon = (bounds[0] + bounds[2]) / 2
    center_lat = (bounds[1] + bounds[3]) / 2
    view_state = pdk.ViewState(latitude=center_lat, longitude=center_lon, min_zoom=6.5)
   
    # Display the map to the page
    map = pdk.Deck(layers=[layer], initial_view_state=view_state,
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json")
    
    return map


def selection_table(gdf):
    """
    Displays an interactive AgGrid table and returns selected rows.

    @param gdf: A GeoDataFrame.
    @return: The selected rows in the AgGrid Table.
    """
    from st_aggrid import AgGrid, ColumnsAutoSizeMode, GridOptionsBuilder, GridUpdateMode
    
    df = gdf.copy()
    if "geometry" in df.columns:
        df = df.drop(columns=["geometry"])

    first_cols = ["OBJECTID", "Jurisdiction District Name", "Abbreviated District Name", "County"]
    remaining_cols = [col for col in df.columns if col not in first_cols]
    df = df[first_cols + remaining_cols].sort_values(by="Jurisdiction District Name")

    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_selection(selection_mode="multiple", use_checkbox=True)
    grid_options = gb.build()

    grid_height = 40 * (len(df) + 1.45)
    grid_height = min(grid_height, 600)

    grid_response = AgGrid(
        df,
        theme="material",
        gridOptions=grid_options,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
        height=grid_height
    )
    
    selected_rows = grid_response.get("selected_rows", [])

    return selected_rows


def zoning_comparison_table(selected_rows):
    """
    Takes selected rows from AgGrid, creates a comparison table, and displays it.

    @param selected_rows: The selected rows from an AgGrid interactive table.
    @return: The comparison table as a dataframe
    """
    from datetime import datetime
    from functools import reduce
    from streamlit_extras.dataframe_explorer import dataframe_explorer

    if len(selected_rows) == 0:
        return

    selected_df = pd.DataFrame(selected_rows)
    dfs = []

    for _, row in selected_df.iterrows():
        district_name = row.get("Jurisdiction District Name", "District")
        df_long = pd.DataFrame(row).reset_index()
        df_long.columns = ["Variable", district_name]
        dfs.append(df_long)

    combined_df = reduce(lambda left, right: pd.merge(left, right, on="Variable", how="outer"), dfs)
    # # If you wanted to sort with empty rows at the bottom
    # combined_df_sorted = combined_df.copy()
    # combined_df_sorted["na_count"] = combined_df_sorted.isna().sum(axis=1)
    # combined_df_sorted = combined_df_sorted.sort_values("na_count").drop(columns="na_count")

    st.subheader("District Comparisons")
    filtered_combined_df_sorted = dataframe_explorer(combined_df, case=False)
    st.dataframe(filtered_combined_df_sorted, use_container_width=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")

    st.download_button(
        label="Export Comparison Table to Excel",
        data= (lambda buf=io.BytesIO(): (filtered_combined_df_sorted.to_excel(buf, index=False, engine="openpyxl"), buf.seek(0), buf)[2])(),
        file_name=f"comparison_table_{timestamp}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    return combined_df


def filter_zoning_data(_gdf, county, jurisdiction, districts):
    """
    Filters the zoning GeoDataFrame based on selected county, jurisdiction, and districts.

    @param gdf: The original GeoDataFrame containing zoning data.
    @param county: Selected county name as a string, or "All Counties" for no filter.
    @param jurisdiction: Selected jurisdiction name as a string, or "All Jurisdictions" for no filter.
    @param districts: List of selected district names, or a list containing "All Districts" for no filter.
    @return: A filtered GeoDataFrame based on the specified criteria.
    """
    df = _gdf.copy()
    if county != "All Counties":
        df = df[df["County"] == county]
    if jurisdiction != "All Jurisdictions":
        df = df[df["Jurisdiction"] == jurisdiction]
    if "All Districts" not in districts:
        df = df[df["District Name"].isin(districts)]
    
    return df


def zoning_geography(zoning_gdf):
    col1, col2, col3 = st.columns(3)
    with col1:
        county = st.selectbox("**County**", ["All Counties"] + sorted(zoning_gdf["County"].dropna().unique()))
    with col2:
        if county != "All Counties":
            jurisdiction_opts = sorted(zoning_gdf[zoning_gdf["County"] == county]["Jurisdiction"].dropna().unique())
        else:
            jurisdiction_opts = sorted(zoning_gdf["Jurisdiction"].dropna().unique())
        jurisdiction = st.selectbox("**Jurisdiction**", ["All Jurisdictions"] + jurisdiction_opts)
    with col3:
        # Filter district options based on current county and jurisdiction selection
        district_filter = zoning_gdf.copy()
        if county != "All Counties":
            district_filter = district_filter[district_filter["County"] == county]
        if jurisdiction != "All Jurisdictions":
            district_filter = district_filter[district_filter["Jurisdiction"] == jurisdiction]

        district_opts = sorted(district_filter["District Name"].dropna().unique())
        districts = st.multiselect("**District(s)**", ["All Districts"] + district_opts, default=["All Districts"])

        return county, jurisdiction, districts


def filtered_zoning_df(zoning_gdf):
    """
    Applies filters to the zoning GeoDataFrame and returns the filtered results.

    @return: Filtered GeoDataFrame based on sidebar selections.
    """
    from streamlit_extras.dataframe_explorer import dataframe_explorer

    # Define the filtered geography
    county, jurisdiction, districts = zoning_geography(zoning_gdf)
    # Apply all filters
    filtered_gdf = filter_zoning_data(zoning_gdf, county, jurisdiction, districts)

    if filtered_gdf.empty:
        st.warning("No districts match your filters.")
        return gpd.GeoDataFrame()

    # Allow user filtering via dataframe_explorer
    filtered_pd = dataframe_explorer(filtered_gdf, case=False)

    # Re-attach geometry from original GeoDataFrame using index
    filtered_gdf = gpd.GeoDataFrame(
        filtered_pd,
        geometry=zoning_gdf.loc[filtered_pd.index, "geometry"],
        crs=zoning_gdf.crs)

    return filtered_gdf

