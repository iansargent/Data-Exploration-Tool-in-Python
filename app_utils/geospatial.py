"""
Open Research Community Accelorator
Vermont Data App

Geospatial Utility Functions
"""

from app_utils.analysis import get_columns


def is_latitude_longitude(df):
    """
    Check if the DataFrame contains latitude and longitude columns.

    @param df: A pandas DataFrame object.
    @return: A boolean value of if latitude and longitude columns are found.
    """
    # Get the column names from the DataFrame
    df_columns = [col.strip().lower() for col in get_columns(df)]

    # Define both the latitude and longitude columns more generally
    lat_col = [
        col
        for col in df_columns
        if any(kw in col.lower() for kw in ["latitude", "lat"])
    ]
    lon_col = [
        col
        for col in df_columns
        if any(kw in col.lower() for kw in ["longitude", "lon", "lng", "lon", "long"])
    ]

    # If both columns are found, return True
    if lat_col and lon_col:
        return True
    # If one or no columns are found, return false
    else:
        return False


def get_lat_lon_cols(df):
    """
    Extracts the latitude and longitude columns in a dataframe.

    @param df: A pandas DataFrame.
    @return: The latitude and longitude columns respectfully.
    """

    candidates_lat = ["latitude", "lat", "internal point (latitude)"]
    candidates_lon = ["longitude", "lon", "lng", "long", "internal point (longitude)"]

    normalized_cols = {col.lower().strip(): col for col in df.columns}

    lat_col = next(
        (
            original
            for norm, original in normalized_cols.items()
            if norm in candidates_lat
        ),
        None,
    )
    lon_col = next(
        (
            original
            for norm, original in normalized_cols.items()
            if norm in candidates_lon
        ),
        None,
    )

    return lat_col, lon_col
