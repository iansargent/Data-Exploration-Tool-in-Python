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

from app_utils.zoning import *
from app_utils.df_filtering import filter_wrapper
from app_utils.color import geojson_add_fill_colors, render_rgba_colormap_legend
from app_utils.color import rgba_to_hex, tab20_rgba, add_fill_colors
from app_utils.data_loading import masterload
from app_utils.streamlit_config import streamlit_config
from app_utils.census import get_geography_title
from app_utils.plot import bar_chart, histogram



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
    render_family_housing_type(df)


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


def render_family_housing_type(df):
    
    bar_col, hist_col = st.columns(2)
    
    house_types = {
        "One Family Unit": "1F",
        "Two Family Unit": "2F",
        "Three Family Unit": "3F",
        "Four Family Unit": "4F",
        "Five Family Unit": "5F",
        "Affordable Housing": "Affordable Housing",
        "Accessory Dwelling Units": "ADU",
        "Planned Residential Development": "PRD"
    }

    house_type = bar_col.selectbox(
        label="Family Housing Type",
        options=house_types.keys(),
        index=0,
        key="bar_type"
    )
    
    house_type_bar_chart = bar_chart(
        df, x_col=f"{house_types[house_type]} Allowance", x_label_angle=0,
        fill="mediumseagreen", title=f"{house_type} Allowance", title_size=20, distribution=True,
        sort_order=["Permitted", "Public Hearing", "Overlay", "Prohibited"], bar_width=75
    )

    zoning_family_regulation_metrics = {
        "Minimum Lot Size": "Min Lot",
        "Front Setback": "Front Setback",
        "Side Setback": "Side Setback", 
        "Rear Setback": "Rear Setback" , 
        "Frontage": "Frontage", 
        "Maximum Lot Building Coverage": "Max Lot Building Coverage", 
        "Maximum Lot Impervious Coverage": "Max Lot Impervious Coverage", 
        "Minimum Parking Spaces": "Min Parking Spaces", 
        "Minimum Parking Spaces per 1BR": "Min Parking Spaces per 1BR", 
        "Minimum Parking Spaces per mult BR": "Min Parking Spaces per mult BR", 
        "Maximum Stories": "Max Stories", 
        "Maximum Height": "Max Height" , 
        "Floor to Area Ratio": "Floor to Area Ratio", 
        "Minimum Unit Size": "Min Unit Size", 
        "Maximum Density": "Max Density", 
        "Maximum Bedrooms": "Max Bedrooms",
        "Maximum Units": "Max Units" 
    }

    zoning_metric = hist_col.selectbox(
        label="Zoning Regulation",
        options=zoning_family_regulation_metrics.keys(),
        index=0
    )

    x_col = f"{house_types[house_type]} {zoning_family_regulation_metrics[zoning_metric]}"
    metric_histogram = histogram(df, x_col, bins=10, count_name="Districts")

    bar_col, hist_col = st.columns(2)
    bar_col.altair_chart(house_type_bar_chart)
    hist_col.altair_chart(metric_histogram)


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
        filter_columns=['County', 'Jurisdiction', 'District Name'], 
        allow_all = {
            "County": False,
            "Jurisdiction": True,
            "District Name": True
        })
    # Apply the selected filters
    filtered_gdf = filter_state.apply_filters(zoning_gdf)
    
    # Define three zoning tabs
    mapping, report, compare = st.tabs(["Map", "Report", "Compare"])
    # Metrics displayed in the report tab
    metrics = compute_acerage_metrics(filtered_gdf)
    # The color map to use for the map legend
    color_map = dict(zip(zoning_gdf['District Type'], zoning_gdf['rgba_color']))
    
    with mapping:
        zoning_mapping_tab(filtered_gdf, color_map)  
    with report: 
        zoning_report_tab(filtered_gdf, metrics)
    with compare:
        zoning_comparison_tab(filtered_gdf)


if __name__ == "__main__":
    streamlit_config()
    main()