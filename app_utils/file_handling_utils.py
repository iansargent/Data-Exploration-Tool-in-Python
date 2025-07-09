"""
Open Research Community Accelorator
Vermont Data App

File Handling Utility Functions
"""

import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards 
import pandas as pd
import geopandas as gpd
import altair as alt
import numpy as np


@st.cache_data
def read_data(file):
    """
    Read the uploaded file and return a DataFrame or GeoDataFrame.

    @param file: An UploadedFile or file path.
    @return: The read data file as a pandas DataFrame or geopandas GeoDataFrame object.
    """
    # Get the file extension of the uploaded file
    # This will determine how the data is read
    file_extension = get_file_extension(file)
    
    # For CSV files, use pandas
    if file_extension == '.csv':
        df = pd.read_csv(file)
        return df
    # For SPSS files, use pyreadstat
    elif file_extension == '.sav':
        import pyreadstat as prs
        import tempfile

        with tempfile.NamedTemporaryFile(delete=False, suffix=".sav") as tmp:
            tmp.write(file.read())
            tmp_path = tmp.name

        df, _ = prs.read_sav(tmp_path)
        return df
    # For XLSX files, use pandas with the openpyxl engine
    elif file_extension == '.xlsx':
        import openpyxl
        df = pd.read_excel(file, engine='openpyxl')
        return df
    # For XLS files, use pandas with the xlrd engine
    elif file_extension == '.xls':
        df = pd.read_excel(file, engine='xlrd')
        return df
    # For 'geographic' file types, use geopandas with the pyogrio engine
    elif file_extension in [".geojson", ".json", ".fgb", ".shp"]:
        import pyogrio
        gdf = gpd.read_file(file, engine="pyogrio")
        return gdf
    # If the file extension is not listed above, return an error
    else:
        st.error("Unsupported file format. Please upload a CSV, JSON, GEOJSON, SAV, XLS, or XLSX file.")
        return None


def get_user_files(key="main"):
    """
    Handles file upload interaction from the Streamlit sidebar.

    Allows users to upload multiple data files via the sidebar interface, displays 
    uploaded files, and provides an option to clear them from session state.

    @param key: Optional key to uniquely identify the file uploader widget. Default is "main".
    @return: A list of uploaded files (Streamlit UploadedFile objects).
    """
    st.sidebar.markdown("### Upload Data")
    
    # Define a file uploader object accepting various file types
    uploaded_files = st.sidebar.file_uploader(
        label="Upload Data Files Here", 
        type=["geojson", "fgb", "csv", "xlsx", 'xls', 'json', 'sav'],
        accept_multiple_files=True,
        key = f"data_upload_{key}",
        label_visibility="hidden")

    # url_upload = st.sidebar.text_input(
    #     label = "URL Uploader",
    #     placeholder = "Enter a URL Dataset to Analyze",
    #     label_visibility="hidden")

    # If the user uploads a file
    if uploaded_files:
        # Add it the to session state
        st.session_state["user_files"] = uploaded_files

    # Keep track of the uploaded file names in the sidebar
    user_files = st.session_state.get("user_files", [])
    if user_files:
        st.sidebar.markdown("### Uploaded Files:")
        for file in user_files:
            st.sidebar.write(f"📄 {get_file_name(file)}")

        # Set a 'clear uploads' buttton that clears the files from memory
        if st.sidebar.button("🔁 Clear Data Uploads"):
            st.session_state.pop("user_files", None)
            st.rerun()
            
    # Return a list of the uploaded files
    return user_files


def process_uploaded_files(user_files):
    """
    Process the uploaded files and return a list of unique file names.
    This function generates a unique hash for each file to check for duplicates.
    It also reads the data, cleans it, and returns a list of tuples containing 
    the DataFrame and the corresponding file name.

    @param user_files: A list of UploadedFile objects from the file uploader.
    @return: A list of tuples in the form of (DataFrame df, str filename).
    """
    # Create an empty set of seen hash codes
    seen_hashes = set()
    # Define an empty list to store processed files
    processed = []

    # If the user has not uploaded any files
    if not user_files:
        return []

    # For each uploaded file
    for file in user_files:
        # Give it a unique hash code for validation purposes
        fid = file_hash(file)
        # If it is already recognized, continue
        if fid in seen_hashes:
            continue
        # Add the file hash to the set of seen hash codes
        seen_hashes.add(fid)

        # Read the dataset using the read_data() function
        df = read_data(file)
        if df is None:
            continue
        
        # Clean the data using the clean_data() function
        df = clean_data(df)

        # If longitude and latitude coordinate columns are found in the file        
        if is_latitude_longitude(df):
            # Attempt to convert it into a GeoDataFrame
            try:
                # Define the latitude and longitude columns
                lat_col, lon_col = get_lat_lon_cols(df)

                # Convert into a GeoDataFrame with geometry
                df = gpd.GeoDataFrame(df, 
                        geometry=gpd.points_from_xy(df[lon_col], df[lat_col]), 
                        crs="EPSG:4326")
            # If it cannot convert it
            except Exception as e:
                st.warning(f"Error converting to GeoDataFrame: {e}")
                continue
        
        # Get the file name as a string
        filename = get_file_name(file)
        # Add the DataFrame and filename to the list of processed files
        processed.append((df, filename))
    
    # Return the list of processed DataFrames and their file names
    return processed


def file_hash(file):
    """
    Generates a SHA-256 hash for either a Streamlit UploadedFile or a local file path (str).

    @param file: File object that you would like to generate a hash code for.
    @return: A Unique hash code.
    """
    import hashlib

    hasher = hashlib.sha256()
    
    if isinstance(file, str):
        # It's a local path
        with open(file, 'rb') as f:
            content = f.read()
            hasher.update(content)
    else:
        # It's an UploadedFile
        file.seek(0)
        content = file.read()
        hasher.update(content)
        file.seek(0)  # Reset after reading

    return hasher.hexdigest()


def get_file_name(file):
    """
    Extracts the name of the file.

    @param file: A FileUploader object or path-string.
    @return: File name as a string.
    """
    if isinstance(file, str):
        return os.path.basename(file)
    elif hasattr(file, "name"):
        return file.name
    else:
        return "unknown"


def get_file_extension(file):
    """
    Extracts the extension of a file.

    @param file: A FileUploader object or file path as a string.
    @return: File extension as a string (e.g., '.csv', '.txt').
    """
    if isinstance(file, str):
        return os.path.splitext(file)[1].lower()
    elif hasattr(file, "name"):
        return os.path.splitext(file.name)[1].lower()
    else:
        return ""

