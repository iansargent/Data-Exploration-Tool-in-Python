"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Zoning Page
"""

# Necessary imports

import streamlit as st

from app_utils.color import render_rgba_colormap_legend
from app_utils.data_loading import masterload
from app_utils.df_filtering import filter_wrapper
from app_utils.streamlit_config import streamlit_config
from app_utils.zoning import (
    compute_acerage_metrics,
    district_comparison,
    plot_acreage,
    zoning_comparison_table,
    zoning_district_map,
)


def zoning_mapping_tab(df, color_map):
    map = zoning_district_map(df)
    map_col, legend_col = st.columns([4, 1])
    map_col.pydeck_chart(map, height=550)
    with legend_col:
        render_rgba_colormap_legend(color_map) 


def zoning_report_tab(df, metrics):
    st.header("Zoning Report")
    render_general_metrics(df, metrics)
    render_district_type_acreage(df)


def render_general_metrics(df, metrics):
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(
        label="**Districts**",
        value=metrics['num_districts']
    )
    col2.metric(
        label="**Total Acreage**",
        value=f"{metrics['total_acreage']:,.0f}"
    )
    col3.metric(
        label="**Residential Districts**",
        value=metrics['num_residential_districts']
    )
    col4.metric(
        label="**Residential Acreage**",
        value=f"{metrics['residential_acreage']:,.0f}"
    )


def render_district_type_acreage(df):
    acre_chart = plot_acreage(df)
    st.divider()
    st.altair_chart(acre_chart, use_container_width=True)
    st.divider()


def zoning_comparison_tab(df):
    st.subheader("Zoning Districts Table")

    districts = district_comparison(df.drop(columns=["rgba_color", "hex_color"]))

    # If a district(s) is selected from the table above, show the comparison table
    if districts:
        zoning_comparison_table(df.drop(columns=["rgba_color", "hex_color"]), districts)


def main():
    # Page header
    st.header("Zoning", divider="grey")

    # Load the zoning data from GitHub, clean it, add colors,
    zoning_gdf = masterload("zoning")

    # User filter selections
    filter_state = filter_wrapper(
        zoning_gdf,
        filter_columns=["County", "Jurisdiction", "District Name"],
        allow_all={"County": False, "Jurisdiction": True, "District Name": True},
    )
    # Apply the selected filters
    filtered_gdf = filter_state.apply_filters(zoning_gdf)
    
    # Define zoning tabs
    mapping, report = st.tabs(["Map", "Report",])
    
    # The color map to use for the map legend
    color_map = dict(zip(zoning_gdf['District Type'], zoning_gdf['rgba_color'], strict=False))
    
    with mapping:
        zoning_mapping_tab(filtered_gdf, color_map)  
    with report: 
        zoning_report_tab(filtered_gdf, compute_acerage_metrics(filtered_gdf))

if __name__ == "__main__":
    streamlit_config()
    main()
