"""
Author: Fitz Koch
Created: 2025-07-29
Description: centralized page for data loading
"""



import streamlit as st
import geopandas as gpd 
import pandas as pd 
import requests
import io
import pyogrio 
from pathlib import Path
from app_utils.data_cleaning import strip_all_whitespace


def load_data(
    url,
    simplify_tolerance=None,
    drop_cols=None,
    postprocess_fn=None
):
    """
    General-purpose data loader for CSV or GeoDataFrame.

    Args:
        url (str): Data source. Note: uses the file extension to dictate how to read it, so it better be right. 
        simplify_tolerance (float): Optional geometry simplification.
        drop_cols (list): Optional list of columns to drop.
        postprocess_fn (callable): Optional function to apply to the dataframe.

    Returns:
        pd.DataFrame or gpd.GeoDataFrame
    """

    extension = Path(url).suffix.lstrip('.')
    if extension=='fgb':
        try:
            df = pyogrio.read_dataframe(url)
            df= crs_set(df)
        except Exception as e:
            raise RuntimeError(f"Failed to read geospatial data: {e}")
    elif extension == 'geojson':
        try: 
            df = gpd.read_file(url)
            df = crs_set(df)
        except Exception as e:
            raise RuntimeError(f"Failed to read geospatial data: {e}")
    else:
        try:
            response = requests.get(url, verify=True)
            response.raise_for_status()
            df = pd.read_csv(io.StringIO(response.text))
        except Exception as e:
            raise RuntimeError(f"Failed to load tabular data: {e}")

    if drop_cols:
        df = df.drop(columns=drop_cols, errors="ignore")

    if simplify_tolerance:
        df["geometry"] = df["geometry"].simplify(simplify_tolerance, preserve_topology=True)

    if postprocess_fn:
        df = postprocess_fn(df)

    df = strip_all_whitespace(df)
    return df

def crs_set(df):
    if df.crs:
        df.to_crs(epsg=4326)
    else:
        df.set_crs(epsg=4326)
    return df

### hard-coded wrappers for particular URLs ### 

@st.cache_data
def load_zoning_data(county=None):
    gdf = load_data(
        url='https://raw.githubusercontent.com/VERSO-UVM/Vermont-Livability-Map/main/data/vt-zoning-update.fgb',
        simplify_tolerance=0.0001,
        drop_cols=["Bylaw Date"]
    )
    return gdf if not county else gdf[gdf["County"] == county].copy()

@st.cache_data
def load_soil_septic_single(rpc):
    return load_data(
        url = f"https://github.com/VERSO-UVM/Vermont-Livability-Map/raw/main/data/{rpc}_Soil_Septic.fgb",
        simplify_tolerance=0.0001
    )

def load_soil_septic_multi(rpcs):
    dfs = [load_soil_septic_single(rpc) for rpc in rpcs]
    return pd.concat(dfs, ignore_index=True, sort=False)


# @st.cache_data
# def load_soil_septic_full():
#     # try:
#     #     return gpd.read_file("Data/large-data/combined-wastewater.fgb", driver="Parquet")
#     # except:
#     rpcs = {
#         "Addison County": "ACRPC",
#         "Bennington County": "BCRC",
#         "Chittenden County": "CCRPC",
#         "Central Vermont": "CVRPC",
#         "Lamoille County": "LCPC",
#         "Mount Ascutney": "MARC",
#         "Northeastern Vermont": "NVDA",
#         "Northwest Regional": "NWRPC",
#         "Rutland Regional": "RRPC",
#         "Two Rivers-Ottauquechee": "TRORC",
#         "Windham": "WRC",
#     }

#     gdfs = []
#     for label, rpc in rpcs.items():
#         gdf = load_soil_septic_partial(rpc)
#         gdf['Source'] = label
#         gdfs.append(gdf)
    
#     gdf_combined = pd.concat(gdfs, ignore_index=True, sort=False)
#     gdf_combined.to_file("Data/large-data/combined-wastewater.fgb", driver="Parquet")
#     return gdf_combined 

## TODO: update with actual URL. once in stored place.
@st.cache_data
def load_flood_data():
    return load_data(
        url = "Data/large-data/Flood_Hazard_Areas_(Only_FEMA_-_digitized_data).geojson",
        simplify_tolerance=0.0001
    )

@st.cache_data
def load_census_data(url):
    from app_utils.census import split_name_col
    return load_data(
        url = url,
        postprocess_fn=split_name_col
    )