"""
Author: Fitz Koch
Created: 2025-07-29
Description: centralized page for data loading
"""

import io
import threading
from pathlib import Path

import geopandas as gpd
import pandas as pd
import pyogrio
import requests

from app_utils.census import split_name_col
from app_utils.constants.dataset_sources import (
    COMBINED_CENSUS,
    DEMO_SOURCES,
    ECON_SOURCES,
    HOUSING_SOURCES,
    SOCIAL_SOURCES,
)
from app_utils.data_cleaning import strip_all_whitespace
from app_utils.flooding import process_flood_gdf
from app_utils.mapping import add_cols_of_biggest_intersection
from app_utils.wastewater import process_soil_data
from app_utils.zoning import process_zoning_data


DATADIR = Path(__file__).parent.parent / "Data"

def load_data(path, simplify_tolerance=None, drop_cols=None, postprocess_fn=None):
    """
    General-purpose data loader for CSV or GeoDataFrame.

    Args:
        path (str): Data source. Note: uses the file extension to dictate how to read it, so it better be right.
        simplify_tolerance (float): Optional geometry simplification.
        drop_cols (list): Optional list of columns to drop.
        postprocess_fn (callable): Optional function to apply to the dataframe.

    Returns:
        pd.DataFrame or gpd.GeoDataFrame
    """


    match path.suffix.lstrip(".").casefold():
        case "fgb":
            df = safe_read(lambda: pyogrio.read_dataframe(path))
            df = crs_set(df)
        case "geojson":
            df = safe_read(lambda: gpd.read_file(path))
            df = crs_set(df)
        case "csv": 
            df = safe_read(lambda: pd.read_csv(path))
        case _:
            df = safe_read(lambda: pd.read_csv(io.StringIO(requests.get(path).text)))

    if drop_cols:
        df = df.drop(columns=drop_cols, errors="ignore")

    if simplify_tolerance:
        df["geometry"] = df["geometry"].simplify(
            simplify_tolerance, preserve_topology=True
        )

    if postprocess_fn:
        df = postprocess_fn(df)

    df = strip_all_whitespace(df)
    return df.copy()

def safe_read(func):
    """
    Helper func to catch exceptions
    """
    try:
        return func()
    except Exception as exc:
        raise RuntimeError(f"Failed to read data: {exc}") from exc

def crs_set(df):
    if df.crs:
        df.to_crs(epsg=4326)
    else:
        df.set_crs(epsg=4326)
    return df


### hard-coded wrappers for particular paths ###
def load_zoning_data(county=None):
    gdf = load_data(
        path=DATADIR / "zoning" / "vt-zoning-update.fgb", 
        simplify_tolerance=0.0001,
        drop_cols=["Bylaw Date"],
    )
    return gdf.copy() if not county else gdf[gdf["County"] == county].copy()


def load_soil_septic_single(rpc):
    try: 
        return load_data(
            path= DATADIR / "soil-suitability" / f"{rpc}_Soil_Septic.fgb",
            simplify_tolerance=0.0001,
        )
    except:
        import streamlit as st
        st.markdown("There is no wastewater soil suitability for that RPC at this time", unsafe_allow_html=True)
        st.stop()

def load_soil_septic_multi(rpcs):
    dfs = [load_soil_septic_single(rpc) for rpc in rpcs]
    return pd.concat(dfs, ignore_index=True, sort=False)


## TODO: update with actual path. once in stored place.
def load_flood_data():
    return load_data(
        path= DATADIR / "large-data" / "Flood_Hazard_Areas_(Only_FEMA_-_digitized_data).geojson",
        simplify_tolerance=0.0001,
    )


def load_census_data(path):
    return load_data(path=path, postprocess_fn=split_name_col)


def load_census_data_dict(sources, basename=DATADIR / "Census"):
    """
    Caching a census dictionary.
    If dictionary includes derived, this caches them from the original raw.
    """
    data = {}
    for label, src in sources.items():
        if isinstance(src, tuple):
            filename, func = src
            if filename not in data:
                data[filename] = load_census_data(
                    Path(basename) / filename
                )  # cache raw
            data[label] = func(
                data[filename]
            )  # derive and cache from cached raw via func
        else:
            data[label] = load_census_data(
                Path(basename) / src
            )  # cache raw sans func
    return data


def load_combine_census(label_to_file):
    """
    Function to load many census files given a dictionary.
    """
    dfs = []
    for label, (cache, selection) in label_to_file.items():
        df_dict = masterload(cache)
        if selection not in df_dict:
            raise KeyError(f"{selection} not found in cache {cache}")
        df = df_dict[selection].copy()
        df["Source"] = label
        dfs.append(df)
    df_combined = pd.concat(dfs, ignore_index=True, sort=False)
    return df_combined


### load metrics we've defined
def load_metrics(df, metric_source):
    """
    Compute, rename, and scale metrics.
    Supports:
      - callable: custom function(df) -> value
    """
    metrics = {}
    for name, source in metric_source.items():
        try:
            metrics[name] = source(df)
        except Exception as e:
            print(f"Error {e} loading metric {name}, {source}")
    return metrics


def load_and_process_soil_septic(rpc):
    raw_data = load_soil_septic_single(rpc)  # load raw data for that rpc
    processed = process_soil_data(raw_data)  # then process it
    return processed


LOADERS = {}
_DATA_CACHE = {}
_LOCK = threading.RLock()


def masterload(name, rpc=None):
    """
    function to lazy load / clean data into a cache.
    LOADERS tells how to load the data if not already cached.
    If already present in cache, we just access.

    Note that even if rpc is not used, it's part of the key, so don't pass unless needed
    to avoid duplicate storage!

    The plan is to eventually replace this with other logic from a more sophisticated caching logic.
    """
    key = (name, rpc)
    with _LOCK:
        if key not in _DATA_CACHE:
            if name not in LOADERS:
                raise KeyError(f"No loader registered under '{name}'")
            if rpc is not None:
                _DATA_CACHE[key] = LOADERS[name](rpc)
            else:
                _DATA_CACHE[key] = LOADERS[name]()
        return _DATA_CACHE[key]


# Map dataset names to loader functions
LOADERS = {
    "zoning": lambda: process_zoning_data(load_zoning_data()),
    "soil_septic": load_and_process_soil_septic,
    "flood_legal": lambda: process_flood_gdf(load_flood_data()),
    # Census
    "census_housing": lambda: load_census_data_dict(HOUSING_SOURCES),
    "census_economics": lambda: load_census_data_dict(ECON_SOURCES),
    "census_demographics": lambda: load_census_data_dict(DEMO_SOURCES),
    "census_social": lambda: load_census_data_dict(SOCIAL_SOURCES),
    "census_combined": lambda: load_combine_census(COMBINED_CENSUS),
    # Joins
    "flooding_with_zoning": lambda: add_cols_of_biggest_intersection(
        donor_gdf=masterload("zoning"),
        altered_gdf=masterload("flood_legal"),
        add_columns=["County", "Jurisdiction"],
    ),
    "soil_septic_with_zoning": lambda rpc=None: add_cols_of_biggest_intersection(
        donor_gdf=masterload("zoning"),
        altered_gdf=masterload("flood_legal", rpc),
        add_columns=["County"],
    ),
}


def register_loader(name, func):
    LOADERS[name] = func
