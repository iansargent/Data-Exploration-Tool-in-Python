"""
Author: Fitz Koch
Created: 2025-07-29
Description: centralized file for mapping functions.
NOTE: everything should be in espg=4326 when it gets here, as is set in data-loading.py
"""

import pydeck as pdk
import json
import geopandas as gpd
import streamlit as st
import pandas as pd


def build_layer(geojson, name="GeoJsonLayer"):
    """
    Function to take a geojson and make a layer from it. 
    NOTE: requires that geojson has the "properties.fill_rgba in it for a fill color. 
    """
    layer = pdk.Layer(
        name,
        data=geojson,
        get_fill_color="properties.rgba_color",
        get_line_color=[80, 80, 80, 80],
        highlight_color=[222, 102, 0, 200],
        line_width_min_pixels=0.5,
        pickable=True,
        auto_highlight=True,
        )

    return layer


def map_gdf_single_layer(gdf, view_state=None):
    """
    Function to convert gdf into geojson and then map it with tooltip. 
    """

    geojson = json.loads(gdf.to_json())

    ## create the layer
    layer = build_layer(geojson)

    # Calculate the center and zoom level of the map
    if not view_state:
        bounds = gdf.total_bounds
        center_lon = (bounds[0] + bounds[2]) / 2
        center_lat = (bounds[1] + bounds[3]) / 2
        view_state = pdk.ViewState(latitude=center_lat, longitude=center_lon, min_zoom=6.5, zoom=10)


    tooltip = {"html" : "{tooltip}"}
    map_style = st.session_state.map_style
    # return the map with layer
    return pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tooltip,
        map_style=map_style)


def add_tooltip_from_dict(gdf, label_to_col, gdf_name=None):
    """
    Adds a tooltip column (for pydeck) using a dictionary with format {"label": "column_name"}.
    Optionally includes the gdf_name as the top line with a separator.
    """
    gdf = gdf.copy()
    def format_tooltip(row):
        lines = []
        if gdf_name:
            lines.append(f"<b>{gdf_name}</b>")
            lines.append("<hr/>")
        lines += [f"<b>{label}:</b> {row[col]}" for label, col in label_to_col.items()]
        return "<br/>".join(lines)
    
    gdf['tooltip'] = gdf.apply(format_tooltip, axis=1)
    return gdf


def multi_layer_map(gdfs):
    geojsons = [json.loads(gdf.to_json()) for gdf in gdfs.values()]
    layers = [build_layer(jsn) for jsn in geojsons]
    view_state=pdk.ViewState(latitude=44.26, longitude=-72.57, min_zoom=6.5, zoom=7)
    tooltip = {"html" : "{tooltip}"}
    map_style = st.session_state.map_style

    return pdk.Deck(layers=layers, initial_view_state=view_state, tooltip=tooltip,
        map_style=map_style)


def add_cols_of_biggest_intersection(donor_gdf, altered_gdf, add_columns = ['County', 'District']):
    """
    Take add_columns from the donor frame and add them to the altered frame. 

    Adds 1 value per add_column per geometry in the altered_gdf.
    Gets those values from the geometry in the donor gdf with which the altered_gdf geometry 
        has the **largest intersection**

    Returns the altered_gdf with new columns. 
    """
    ## store original crs and set crs to a more easily calculable format
    og_crs = donor_gdf.crs
    donor_gdf = donor_gdf.copy().to_crs(epsg=3857)
    altered_gdf = altered_gdf.copy().to_crs(epsg=3857)

    ## save indices
    donor_gdf['donor_index'] = donor_gdf.index
    altered_gdf['alt_index'] = altered_gdf.index

    ## get largest intersections only (for each geometry in the alt_index)
    intersections = gpd.overlay(donor_gdf, altered_gdf, how="intersection")
    intersections['intersect_area'] = intersections.geometry.area
    largest = intersections.sort_values("intersect_area", ascending=False).drop_duplicates('alt_index', keep="first")

    ## merge relevant cols back into the og alt 
    merge_cols = ['alt_index'] + add_columns
    final_df = pd.merge(
        left = altered_gdf,
        right = largest[merge_cols],
        on=['alt_index'],
        how='left'
    )

    ## reset crs to original and return
    final_df = final_df.to_crs(og_crs)
    return final_df 



    
