"""
Author: Fitz Koch
Created: 2025-07-29
Description: layer for all the non-streamlit logic for the flooding page
"""


import streamlit as st
import pandas as pd
import geopandas as gpd
from app_utils.mapping import map_gdf_single_layer, add_tooltip_from_dict

def explode_flood_polygons(gdf):
    def get_coordinates(geom):
        if geom.geom_type == 'Polygon':
            return [list(geom.exterior.coords)]
        elif geom.geom_type == 'MultiPolygon':
            return [list(poly.exterior.coords) for poly in geom.geoms]
        return []
    
    # Define a new "coordinates" column derived from geometry
    gdf["coordinates"] = gdf["geometry"].apply(get_coordinates)

    gdf.explode(index_parts=False)
    gdf.explode("coordinates", ignore_index=True)
    return gdf

def add_flood_color(gdf):
    gdf['rgba_color'] = [[255, 0, 0, 100]] * len(gdf)
    return gdf

def clean_flood_gdf(gdf):
    """
    Function to format columns for tooltip display and prune unneeded columns
    """
    gdf = gdf[gdf['SFHA_TF'] == 'T']
    gdf['ZONE_SUBTY_DISPLAY'] = gdf['ZONE_SUBTY'].fillna('None')
    gdf["STATIC_BFE_DISPLAY"] = gdf["STATIC_BFE"].where(gdf["STATIC_BFE"] != -9999, "N/A")
    gdf = gdf[['SFHA_TF', "FLD_ZONE", 'ZONE_SUBTY_DISPLAY', "STATIC_BFE_DISPLAY", "geometry", "rgba_color"]].copy()
    return gdf

def add_flood_tooltip(gdf):
    return add_tooltip_from_dict(gdf, gdf_name="Flooding", label_to_col={
        "Zone" : "FLD_ZONE",
        "Additional Info" : "ZONE_SUBTY_DISPLAY"
    })

def plot_flood_gdf(gdf):
    return map_gdf_single_layer(gdf)


def process_flood_gdf(gdf):
    """"
    Wrapper for adding colors, cleaning, and tooltipping logic, etc. 
    """
    gdf = add_flood_color(gdf)
    gdf = clean_flood_gdf(gdf)
    gdf = add_flood_tooltip(gdf)
    gdf = explode_flood_polygons(gdf)
    return gdf
