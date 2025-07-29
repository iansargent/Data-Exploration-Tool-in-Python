"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Zoning Page
"""

# Necessary imports
import streamlit as st
import altair as alt
import geopandas as gpd
import json
from streamlit_extras.metric_cards import style_metric_cards 
from app_utils.zoning import (
    district_comparison, zoning_comparison_table, zoning_district_map, get_acerage_metrics,
    plot_acreage, clean_zoning_gdf
)
from app_utils.df_filtering import filter_dataframe_multiselect
from app_utils.color import geojson_add_fill_colors, render_rgba_colormap_legend
from app_utils.color import rgba_to_hex, tab20_rgba, add_fill_colors
from app_utils.data_loading import load_zoning_data


def zoning():
    # Page header
    st.header("Zoning")
    # Load the zoning data from GitHub, clean it, add colors, and filter it
    zoning_gdf = load_zoning_data()
    zoning_gdf = clean_zoning_gdf(zoning_gdf)
    zoning_gdf, color_map = add_fill_colors(zoning_gdf, column="District Type", cmap='tab20')
    filtered_gdf, _ = filter_dataframe_multiselect(
        dfs=zoning_gdf, filter_columns=['County', 'Jurisdiction', 'District Name'], 
        presented_cols=['County', 'Municipality', 'District'],
        allow_all = {
            "County": False,
            "Jurisdiction": True,
            "District Name": True
        })
    
    # Select only relevant columns to map
    filtered_gdf['Acres_fmt' ] = filtered_gdf['Acres'].map(lambda x: f"{x:,.0f}")
    filtered_gdf_map = filtered_gdf[["Jurisdiction District Name", "District Type", "geometry", 'rgba_color', 'Acres_fmt']].copy()

    # Check CRS and data quality 
    if filtered_gdf_map.empty:
        st.warning("No zoning data available for the selected filters.")
        return
    filtered_gdf_map = filtered_gdf_map.set_crs("EPSG:4326") if filtered_gdf_map.crs is None else filtered_gdf_map.to_crs("EPSG:4326")

    # Convert gdf into GeoJSON 
    filtered_geojson = json.loads(filtered_gdf_map.to_json())

    mapping, report, compare = st.tabs(["Map", "Report", "Compare"])
    
    with mapping:
        map = zoning_district_map(filtered_geojson, filtered_gdf_map)
        map_col, legend_col = st.columns([4, 1])
        map_col.pydeck_chart(map, height=550)
        with legend_col:
            render_rgba_colormap_legend(color_map)  
    
    with report: 
        st.header("Land Area")
        get_acerage_metrics(filtered_gdf)

        acre_chart = plot_acreage(filtered_gdf)
        st.altair_chart(acre_chart, use_container_width=True)

        style_metric_cards(background_color="whitesmoke", border_left_color="mediumseagreen")
        st.write("Bar Graph of Family Allowance (1F - 5F Dropdown)")
        st.write("Affordable Housing Allowance")

    # Selectable Table for comparisons
    with compare:
        st.subheader("Zoning Districts Table")

        districts = district_comparison(filtered_gdf.drop(columns=["rgba_color", "hex_color"]))

        # If a district(s) is selected from the table above, show the comparison table
        if districts:
            zoning_comparison_table(filtered_gdf.drop(columns=["rgba_color", "hex_color"]), districts)


def show_zoning():
    zoning()

if __name__ == "__main__":
    st.set_page_config(
    page_title="Vermont Data App",
    layout="wide",
    page_icon="🍁"
)
    show_zoning()