"""
Ian Sargent
ORCA
Streamlit Data Visualization Utility Functions
"""


import streamlit as st
from st_aggrid import AgGrid, ColumnsAutoSizeMode
from streamlit_extras.metric_cards import style_metric_cards 
import pandas as pd
import altair as alt
import numpy as np
import os
import hashlib
from statsmodels.stats.weightstats import DescrStatsW
import calendar
from ydata_profiling.config import Settings
from streamlit_pandas_profiling import st_profile_report
from ydata_profiling import ProfileReport
import geopandas as gpd
import leafmap.foliumap as lfm
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from st_aggrid import AgGrid, ColumnsAutoSizeMode, GridOptionsBuilder, GridUpdateMode
from streamlit_extras.dataframe_explorer import dataframe_explorer 


#--------------------------------------#
#######      File Handling      ########
#--------------------------------------#

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
        label_visibility="hidden"
    )

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
                        crs="EPSG:4326"
                )
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


#--------------------------------------#
# Reading, Handling, and Cleaning Data #
#--------------------------------------#


def load_zoning_file():
    """
    Loads the Vermont Zoning Data to the app session state.
    """
    
    demo_path = "/Users/iansargent/Desktop/ORCA/Steamlit App Testing/App Demo/vt-zoning-update.fgb"
    if "user_files" not in st.session_state:
        st.session_state.user_files = []

    if demo_path not in st.session_state.user_files:
        st.session_state.user_files.append(demo_path)


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


def get_columns(df):
    """
    Get the column names from the DataFrame as a list.

    @param df: A pandas DataFrame object.
    @return: A list of column names in the dataframe (string).
    """
    columns = df.columns.tolist()
    
    return columns


def get_column_type(df, column_name):
    """
    Get the data type of a specific column in the DataFrame.

    @param df: A pandas Dataframe object.
    @param column_name: The name of the column in the dataframe (string).
    @return: The pandas data type of the column (dtype).
    """
    column_type = df[column_name].dtype
    
    return column_type


def is_latitude_longitude(df):
    """
    Check if the DataFrame contains latitude and longitude columns.

    @param df: A pandas DataFrame object.
    @return: A boolean value of if latitude and longitude columns are found.
    """
    # Get the column names from the DataFrame
    df_columns = [col.strip().lower() for col in get_columns(df)]

    # Define both the latitude and longitude columns more generally
    lat_col = [col for col in df_columns if any(kw in col.lower() for kw in ["latitude", "lat"])]
    lon_col = [col for col in df_columns if any(kw in col.lower() for kw in ["longitude", "lon", "lng", "long"])]

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

    lat_col = next((original for norm, original in normalized_cols.items() if norm in candidates_lat), None)
    lon_col = next((original for norm, original in normalized_cols.items() if norm in candidates_lon), None)

    return lat_col, lon_col


def month_name_to_num(month_name):
    """
    Convert string-type month names into corresponding integers
    to make it easier to convert into datetime-type columns.

    @param month_name: The full name or abbrievation of a month (string).
    @return: The corresponding month number (int).
    """
    # Try to convert month string (like "May", "5", "05") to number 1-12
    if pd.isna(month_name):
        return None
    month_name = str(month_name).strip().lower()
    # Check if numeric string
    if month_name.isdigit():
        month_num = int(month_name)
        if 1 <= month_num <= 12:
            return month_num
        else:
            return None
    # Check if month name (short or full)
    month_abbrs = {m.lower(): i for i, m in enumerate(calendar.month_abbr) if m}
    month_names = {m.lower(): i for i, m in enumerate(calendar.month_name) if m}
    
    if month_name in month_abbrs:
        return month_abbrs[month_name]
    
    if month_name in month_names:
        return month_names[month_name]
    
    return None


def clean_data(df):
    """
    Clean the column types of the DataFrame.
    Convert binary numeric columns to boolean and parse datetime columns based on column name.

    @param df: A pandas DataFrame.
    @return: The cleaned pandas DataFrame.
    """
    # Replace "." name spacers with "_"
    df.columns = df.columns.str.replace('.', '_', regex=False)
    # Replace empty values with NA
    df = df.replace("", pd.NA, regex=True)

    for col in df.columns:
        # Get the column name
        col_name = col.lower()

        # Handle datetime-like columns based on column name
        if any(x in col_name for x in ["datetime", "date", "time"]):
            df[col] = pd.to_datetime(df[col], errors='coerce')
            continue  # Skip further checks
        # If the column is a year variable
        elif "year" in col_name:
            # Convert it into a datetime type
            df[col] = pd.to_datetime(df[col].astype(str) + "-01-01", errors='coerce')
            continue
        # If the column is a month variable
        elif "month" in col_name:
            # Convert month names into numbers
            df[col] = df[col].apply(month_name_to_num)
            # Convert it into a datetime type
            df[col] = pd.to_datetime(
                "2000-" + df[col].astype(int).astype(str).str.zfill(2) + "-01",
                format="%Y-%m-%d",
                errors='coerce'
            )
            continue

        # Convert binary numeric columns with values [0,1] to boolean
        if df[col].dropna().nunique() == 2:
            vals = set(str(v).strip().lower() for v in df[col].dropna().unique())
            if vals == {"yes", "no", " "} or vals == {"0", "1"} or vals == {0, 1} or vals == {"y", "n"}:
                df[col] = df[col].astype(bool)
        
        if isinstance(df, gpd.GeoDataFrame):
            convert_all_timestamps_to_str(df)
    
    # Return the cleaned dataframe
    return df


def convert_all_timestamps_to_str(gdf):
    """
    Converts all timestamp columns in a GeoDataFrame 
    into strings for mapping purposes.

    @param gdf: A pandas DataFrame or GeoDataFrame object.
    @return: The DataFrame.
    """
    # Convert all datetime columns to strings
    for col, dtype in gdf.dtypes.items():
        if "datetime" in str(dtype):
            gdf[col] = gdf[col].astype(str)
    
    # Return the GeoDataFrame
    return gdf


def split_name_col(census_gdf):
    """
    Splits the "NAME" columns in the census datasets into 
    "Jurisdiction" and "County" columns.

    @param census_gdf: A census style GeoDataFrame with a "NAME" column.
    @return: The cleaned dataset with the split "NAME" column.
    """

    # Split the NAME column
    census_gdf[['Jurisdiction', 'County']] = census_gdf['NAME'].str.extract(r'^(.*?),\s*(.*?) County,')

    # Drop the original NAME column if desired
    census_gdf = census_gdf.drop(columns='NAME')

    return census_gdf


#--------------------------------------#
#                Mapping               #
#--------------------------------------#


def load_zoning_data():
    """
    Loads the Vermont Zoning dataset as a GeoDataFrame.

    @return: The geopandas zoning dataset as a GeoDataFrame object.
    """

    from io import BytesIO
    import requests
    
    zoning_url = 'https://raw.githubusercontent.com/VERSO-UVM/Vermont-Livability-Map/main/data/vt-zoning-update.fgb'

    # Stream download to avoid issues with large files
    response = requests.get(zoning_url)
    response.raise_for_status()  # raises an error if download failed

    gdf = gpd.read_file(BytesIO(response.content))
    
    return gdf.drop(columns=["Bylaw Date"], errors="ignore")


def render_table(gdf):
    """
    Displays an interactive AgGrid table and returns selected rows.

    @param gdf: A GeoDataFrame.
    @return: The selected rows in the AgGrid Table.
    """
    
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


def render_comparison_table(selected_rows):
    """
    Takes selected rows from AgGrid, creates a comparison table, and displays it.

    @param selected_rows: The selected rows from an AgGrid interactive table.
    @return: The comparison table as a dataframe
    """
    if len(selected_rows) == 0:
        return

    selected_df = pd.DataFrame(selected_rows)
    dfs = []

    for _, row in selected_df.iterrows():
        district_name = row.get("Jurisdiction District Name", "District")
        df_long = pd.DataFrame(row).reset_index()
        df_long.columns = ["Variable", district_name]
        dfs.append(df_long)

    from functools import reduce

    combined_df = reduce(
        lambda left, right: pd.merge(left, right, on="Variable", how="outer"),
        dfs
    )

    combined_df_sorted = combined_df.copy()
    combined_df_sorted["na_count"] = combined_df_sorted.isna().sum(axis=1)
    combined_df_sorted = combined_df_sorted.sort_values("na_count").drop(columns="na_count")

    st.subheader("District Comparisons")
    filtered_combined_df_sorted = dataframe_explorer(combined_df_sorted, case=False)
    st.dataframe(filtered_combined_df_sorted, use_container_width=True)

    import io
    from datetime import datetime

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")

    st.download_button(
        label="Export Comparison Table to Excel",
        data= (lambda buf=io.BytesIO(): (filtered_combined_df_sorted.to_excel(buf, index=False, engine="openpyxl"), buf.seek(0), buf)[2])(),
        file_name=f"comparison_table_{timestamp}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    return combined_df_sorted


def filter_zoning_data(gdf, county, jurisdiction, districts):
    """
    Filters the zoning GeoDataFrame based on selected county, jurisdiction, and districts.

    @param gdf: The original GeoDataFrame containing zoning data.
    @param county: Selected county name as a string, or "All Counties" for no filter.
    @param jurisdiction: Selected jurisdiction name as a string, or "All Jurisdictions" for no filter.
    @param districts: List of selected district names, or a list containing "All Districts" for no filter.
    @return: A filtered GeoDataFrame based on the specified criteria.
    """
    df = gdf.copy()
    if county != "All Counties":
        df = df[df["County"] == county]
    if jurisdiction != "All Jurisdictions":
        df = df[df["Jurisdiction"] == jurisdiction]
    if "All Districts" not in districts:
        df = df[df["District Name"].isin(districts)]
    
    return df


def generate_district_color_map(gdf):
    """
    Generates a color map assigning a unique color to each district type.

    @param gdf: A GeoDataFrame containing a 'District Type' column.
    @return: A dictionary mapping each unique district type to a hex color code.
    """
    district_types = gdf["District Type"].dropna()
    # Ensure valid string keys, strip whitespace, remove "None" as string if present
    unique_types = sorted(set(str(dt).strip() for dt in district_types if str(dt).strip().lower() != "none"))

    cmap = plt.get_cmap("Set2")
    colors = [mcolors.rgb2hex(cmap(i % cmap.N)) for i in range(len(unique_types))]

    return dict(zip(unique_types, colors))


def render_zoning_layer(map):
    """
    Renders the zoning layer on a Leafmap map object based on user-selected filters.

    Displays dropdown filters in the Streamlit sidebar to filter by county, jurisdiction,
    and district(s), then styles and displays the filtered zoning districts on the map.

    @param map: A Leafmap Map object used to display the zoning layer.
    @return: A tuple containing the updated map and the filtered GeoDataFrame.
    """
    
    zoning_gdf = load_zoning_data()

    col1, col2, col3 = st.columns(3)
    with col1:
        county = st.selectbox("**County**", ["All Counties"] + sorted(zoning_gdf["County"].dropna().unique()))
    with col2:
        jurisdiction = st.selectbox("**Jurisdiction**", ["All Jurisdictions"] + sorted(
            zoning_gdf[zoning_gdf["County"] == county]["Jurisdiction"].dropna().unique()
        ) if county != "All Counties" else ["All Jurisdictions"] + sorted(zoning_gdf["Jurisdiction"].dropna().unique()))
    with col3:
        # Filter district options based on current county and jurisdiction selection
        district_filter = zoning_gdf.copy()
        if county != "All Counties":
            district_filter = district_filter[district_filter["County"] == county]
        if jurisdiction != "All Jurisdictions":
            district_filter = district_filter[district_filter["Jurisdiction"] == jurisdiction]

        district_opts = sorted(district_filter["District Name"].dropna().unique())
        districts = st.multiselect("**District(s)**", ["All Districts"] + district_opts, default=["All Districts"])

    filtered_gdf = filter_zoning_data(zoning_gdf, county, jurisdiction, districts)
    if filtered_gdf.empty:
        st.warning("No districts match your filters.")
        return

    center = filtered_gdf.geometry.unary_union.centroid
    map.set_center(center.x, center.y, zoom=10)

    color_map = generate_district_color_map(filtered_gdf)

    def style_fn(f):
        dt = f["properties"].get("District Type", "")
        return {"color": "navy", "weight": 0.3, "fillColor": color_map.get(dt, "gray"), "fillOpacity": 0.4}

    info_cols = ["Jurisdiction District Name", "Abbreviated District Name", "District Type", "geometry"]
    filtered_display = filtered_gdf[info_cols].copy()

    map.add_gdf(
        filtered_display, 
        "Districts by Type", 
        style_function=style_fn, 
        info_mode="on_click", 
        zoom_to_layer=True)
    
    map.add_legend(title="District Type", legend_dict=color_map)
    
    return map, filtered_gdf


def assign_layer_style(filename):
    """
    Assigns a style dictionary for rendering a map layer based on the filename.
    Matches keywords in the filename to predefined styles for color and line weight.

    @param filename: The name of the file as a string.
    @return: A dictionary specifying style properties for rendering (e.g., color, weight, fillOpacity).
    """

    if "border" in filename:
        style = {"color": "dodgerblue", "weight": 2}
    elif "linearfeatures" in filename:
        style = {"color": "blue", "weight": 2}
    elif "pointfeatures" in filename:
        style = {"color": "darkorange", "weight": 2}
    elif "servicearea" in filename:
        style = {"color": "darkred", "weight": 2}
    elif ("wwtf" in filename) or ("facilit" in filename):
        style = {"color": "darkgreen", "weight": 2}
    elif "zoning" in filename:
        style = {"color": "navy", "weight": 0.3, "fillOpacity": 0}
    else:
        style = {}
    
    return style


def land_suitability_metric_cards(gdf):
    """
    Creates and displays a set of metric cards for land suitability statistics:
    % Well Suited Land, Acreage of Well Suited Land,
    % Moderately Suited Land, Acreage of Moderately Suited Land.

    @param gdf: A geopandas GeoDataFrame object.
    """

    st.subheader("Land Suitability Overview")

    # Filter GeoDataFrame by Jurisdiction HERE!
    
    
    # Filter by suitability categories
    total_acres = gdf["Acres"].sum()

    well_suited = gdf[gdf["Suitability"] == "Well Suited"]
    mod_suited = gdf[gdf["Suitability"] == "Moderately Suited"]

    well_acres = well_suited["Acres"].sum()
    mod_acres = mod_suited["Acres"].sum()

    well_pct = (well_acres / total_acres) * 100 if total_acres > 0 else 0
    mod_pct = (mod_acres / total_acres) * 100 if total_acres > 0 else 0

    # Layout: 2 rows with 2 columns each
    col1, col2 = st.columns(2)

    col1.metric(label="**Well Suited** Land", value=f"{well_pct:.1f}%")
    col2.metric(label="**Well Suited Acreage**", value=f"{well_acres:,.0f} acres")

    style_metric_cards(
        background_color="whitesmoke",
        border_left_color="#2ca02c",
        box_shadow=True,
        border_size_px=0.5
    )
    
    col3, col4 = st.columns(2)
    
    col3.metric(label="**Moderately Suited** Land", value=f"{mod_pct:.1f}%")
    col4.metric(label="**Moderately Suited Acreage**", value=f"{mod_acres:,.0f} acres")


#--------------------------------------#
###   Exploring and Analyzing Data   ###
#--------------------------------------#

def get_dimensions(df):
    """
    Determines the numnber of rows and columns in the dataset.

    @param df: A pandas DataFrame object.
    @return: Number of columns (int), Number of rows (int) respectfully.
    """
    
    # Find the number of columns
    num_columns = len(get_columns(df))
    # Find the number of rows
    num_rows = len(df)

    # Return the dimensions as a tuple
    return num_columns, num_rows


def get_skew(df, variable):
    """
    Computes the sample skewness of a numeric variable in a DataFrame.
    
    @param df: A pandas DataFrame object.
    @param variable: The column name of the numeric variable (string).
    @return: The computed skewness metric (float).
    """
    import numpy as np

    x = df[variable].dropna()
    n = len(x)
    if n < 3:
        return np.nan  # skewness not defined for < 3 values

    mean = x.mean()
    std = x.std(ddof=0)  # population std for formula

    skewness = ((x - mean)**3).sum() / (n * (std**3))
    
    return skewness


def data_snapshot(df, filename):
    """
    Reports the overall structure of the dataset, including
    dimensions and the dataframe type.

    @param df: A pandas DataFrame object.
    @param filename: The name of the file (string)
    """
    # Add spacer between different files
    st.markdown("---")
    
    # Define the dimensions
    num_cols, num_rows = get_dimensions(df)
    
    # Find the unique column
    unique_columns = []
    
    # Finding the identifying (unique column)
    for col in df.columns:
        # Get the length of the column and the its number of unique values
        col_length = len(df[col])
        num_unique = df[col].nunique()

        # If every value in the column is unique
        if num_unique == col_length:
            # Get the column name
            col_name = df[col].name
            # Add it to the list of unique columns
            unique_columns.append(col_name)
    
    # Define the ID columns as the first name in the list of unique columns
    if unique_columns:
        unique_column = unique_columns[0]
    # If no unique columns are found, set ID column to "None"
    else:
        unique_column = "None"
    
    # Define columns to display each metric card
    col1, col2, col3, col4 = st.columns(4)

    # Define each metric card
    col1.metric(label="File", value=filename)
    col2.metric(label='Identifying Column', value=unique_column)
    col3.metric(label="Columns", value=num_cols)
    col4.metric(label='Rows', value=num_rows)

    # Styling the snapshot cards
    style_metric_cards(
        background_color="whitesmoke", 
        border_size_px=1, 
        border_left_color="mediumseagreen"
    )
    
    # Return
    return


def generate_exploratory_report(df):
    """
    Generate a tailored exploratory profile report 
    given a DataFrame using the ydata-profiling package.

    @param df: A pandas DataFrame object.
    @return: An exploratory ydata-profiling ProfileReport object.
    """
    # Get the number of columns in the dataframe
    df_columns = get_columns(df)
    num_columns = len(df_columns)

    # If there are a large amount of columns (30)
    # Use a "minimal" report to decrease computation
    if num_columns > 30:
        report = ProfileReport(
            df,
            title="Exploratory Report",
            interactions=None,
            samples=None,
            missing_diagrams={"bar": False, "matrix": False, "dendrogram": False, "heatmap": False})
    # If there are less than 30 columns
    else:
        report = ProfileReport(
            df,
            title="Exploratory Report",
            explorative=True,
            missing_diagrams={"bar": False, "matrix": False, "dendrogram": False, "heatmap": False},
            samples=None)
    
    # Return the ydata-profiling report
    return report


def generate_quality_report(df):
    """
    Generate a tailored data quality profile report 
    given a DataFrame using the ydata-profiling package.

    @param df: A pandas DataFrame object.
    @return: A data quality ydata-profiling ProfileReport object.
    """
    report = ProfileReport(
            df,
            title="Data Quality",
            missing_diagrams={"bar": True,"matrix": True},
            duplicates={"head": 10},
            correlations=None,
            interactions=None)

    return report


def generate_comparison_report(dfs):
    """
    Generates a comparison report given a list of 
    uploaded dataframes

    @param dfs: A list of pandas DataFrame objects.
    @return: A ydata-profiling comparison report.
    """
    
    from ydata_profiling import ProfileReport, compare
    
    reports = []
    for i, df in enumerate(dfs):
        report = ProfileReport(
            df,
            title = f"Report_{i}"
        )
        reports.append(report)
    
    comparison_report = compare(reports)

    return comparison_report


def parcel_flood_metrics():
    parcel_gdf = gpd.read_file("/Users/iansargent/Desktop/ORCA/Steamlit App Testing/VT_Parcel.geojson")
    
    parcel_gdf = parcel_gdf[["GIS SPAN", "PARCEL ID", "TOWN", "Grand-List Town-Name", 
                             "Property Description", "Category (Real Estate only)", 
                             "Resident Ownership Code", "Total Acres", "Listed Real Value (Full)",
                             "Non-Residential Value (Full)", "Listed Value of Land", "Housesite Value",
                             "Shape_Area", "Shape_Length"]]
    
    flood_gdf = gpd.read_file("/Users/iansargent/Desktop/ORCA/Steamlit App Testing/VT_Flood_Hazard.geojson")


    projected_crs = 'EPSG:3857' 

    parcels_proj = parcel_gdf.to_crs(projected_crs)
    flood_proj = flood_gdf.to_crs(projected_crs)

    parcel_flood = gpd.sjoin(parcels_proj, flood_proj, how='inner', predicate='within')  


#--------------------------------------#
###   Plotting and Displaying Data   ###
#--------------------------------------#


def single_column_plot(df, selected_column):
    """
    Create a single column plot based on the data type of the selected column.
    The plot type is determined by the data type of the column.

    @param df: A pandas DataFrame object.
    @param selected_column: The name of the column in the DataFrame (string).
    @return: The Altair plot objects associated with the data type of the column.
    """
    # Define the plotting source as the one selected column without missing values
    source = df[[selected_column]].dropna()
    # Get the column type
    column_type = get_column_type(df, selected_column)
    
    # If the column is categorical (object type)
    if column_type == 'object':
        # Create a sorted BAR CHART using Altair (descending)
        bar_title = alt.TitleParams(f"Bar Chart of {selected_column}", anchor='middle', dy=15, fontSize=18, font='Helvetica', fontWeight="bold")
        bar_chart = alt.Chart(source, title=bar_title).mark_bar().encode(
            x=alt.X(f"{selected_column}:N", sort='-y'),
            y='count()',
            tooltip=['count()']
        ).configure_mark(
            color = "tomato"
        ).properties(
            width=600,
            height=400
        )
        # Disply the chart
        st.altair_chart(bar_chart, use_container_width=True)
        
        # Return the bar chart
        return bar_chart

    # If the column is numeric
    elif column_type in ['int64', 'float64']:
        # Ensure the data type is numeric
        df[selected_column] = pd.to_numeric(df[selected_column], errors='coerce')
        # Redefine the plotting source
        source = df[[selected_column]].dropna()

        # Define the 95% confidence interval bounds
        d = DescrStatsW(source[selected_column])
        ci_low, ci_high = d.tconfint_mean()
        CI = (ci_low, ci_high)

        # Calculate descriptive statistics
        var_mean = source[selected_column].mean()
        var_med = source[selected_column].median()
        var_std_dev = source[selected_column].std()
        
        skew = get_skew(source, selected_column)

        if abs(skew) > 1:
            skew_warning = ("NOTE: This Distribution is **Slightly Skewed**. " +
                            "It is best to look at the **Median** instead of **Mean** in this case!")
            st.warning(skew_warning)
        
        
        # Display variable descriptive statistics
        column1, column2 = st.columns(2) 
        column3, column4 = st.columns(2)
        column1.metric(label="**Mean**", value = f"{var_mean:,.2f}", help="The *average* of the sample.")
        column2.metric(label="**Median**", value = f"{var_med:,.2f}", help="The *middle value* of the sample.")
        column3.metric(label="**Standard Deviation**", value = f"{var_std_dev:,.3f}", 
                       help="The average amount that each observation differs from the sample mean. " \
                       "Standard deviation also measures the overall spread of the sample for a given variable.")
        column4.metric(label="**95% Confidence Interval**", value = f"[{ci_low:,.1f}  -  {ci_high:,.1f}]",
                       help="The range of values in which we are 95% confident the variable's population " \
                       "mean falls into. In other words, if we repeatedly sampled this population, our " \
                       "sample means would fall within this interval 95% of the time.")

        style_metric_cards(
            background_color="whitesmoke",
            border_left_color="mediumseagreen",
            border_size_px=0.5
        )
        
        # Slider for number of bins in the histogram
        bin_slider = st.slider(
            "**Select the Level of Detail**", 
            min_value=2, 
            max_value=min(len(np.unique(source[selected_column])) // 2, 100), 
            value=30,
            help="Controls how many bars appear in the histogram. Higher = more detail.",
            key=f"bin_slider_{selected_column}"
        )

        # Histogram
        hist_title = alt.TitleParams(f"Histogram Distribution of {selected_column}", anchor='start', dy=15, fontSize=18, font='Helvetica', fontWeight="bold")
        histogram = alt.Chart(source, title=hist_title).mark_bar().encode(
            x=alt.X(f"{selected_column}:Q", bin=alt.Bin(maxbins=bin_slider), title=selected_column),
            y=alt.Y('count():Q', title='Count'),
            tooltip=[alt.Tooltip('count()', title='Count')]
        ).properties(height=450)

        # Density Plot
        dens_title = alt.TitleParams(f"Density Distribution of {selected_column}", anchor='start', dy=15, fontSize=18, font='Helvetica', fontWeight="bold")
        density = alt.Chart(source, title=dens_title).transform_density(
            f"{selected_column}",
            as_=[f"{selected_column}", "density"],
            extent=[source[selected_column].min(), source[selected_column].max()]
        ).mark_area(color='tomato').encode(
            x=alt.X(f"{selected_column}:Q", title=selected_column),
            y=alt.Y('density:Q', title='Density')
        ).interactive()

        # Boxplot
        box_title = alt.TitleParams(f"Boxplot Distribution of {selected_column}", anchor='start', dy=15, fontSize=18, font='Helvetica', fontWeight="bold")
        boxplot = alt.Chart(source, title=box_title).mark_boxplot(color='dodgerblue').encode(
            x=alt.X(f"{selected_column}:Q", title=selected_column)
        ).configure_mark().configure_boxplot(size=160
        ).properties(width=400, height=400)

        # Display the histogram
        st.altair_chart(histogram, use_container_width=True)
                
        # Display the density plot
        st.altair_chart(density, use_container_width=True)
        
        # Display the box plot below
        st.altair_chart(boxplot, use_container_width=True)

        # Return the plots and confidence interval
        return histogram, boxplot, CI, density

    # If the column is datetime
    elif pd.api.types.is_datetime64_any_dtype(df[selected_column]):
        # Clean the datetime column
        source[selected_column] = pd.to_datetime(source[selected_column])
        
        # Let user pick the numeric column to plot
        numeric_cols = df.select_dtypes(include=['int', 'float']).columns.tolist()
        numeric_cols = [col for col in numeric_cols if col != selected_column]
        
        # If there are no numeric columns to plot over time
        if not numeric_cols:
            st.warning("No numeric columns available to plot against time.")
            return
        
        # Define the variable to plot over time
        y_column = st.selectbox("Select a column to plot over time:", numeric_cols)

        # Create the LINE CHART
        line_title = alt.TitleParams(f"Plot of {y_column} Over Time", anchor='start', dy=15, fontSize=18, font='Helvetica', fontWeight="bold")
        chart = alt.Chart(df, title=line_title).mark_line().encode(
            x=alt.X(f"{selected_column}:T", title="Time"),
            y=alt.Y(f"{y_column}:Q", title=y_column),
            color = alt.value("dodgerblue"),
        )

        # Create the LOESS curve to add to the time series plot 
        time_chart = chart + chart.transform_loess(
            f"{selected_column}", f"{y_column}", bandwidth=0.2
        ).mark_line().encode(color = alt.value("tomato"))
        
        # Display the chart
        st.altair_chart(time_chart, use_container_width=True)
        
        # Return the time series chart
        return time_chart

    # If the column is boolean
    elif column_type == 'bool':
        # Create a pie chart using Altair
        pie_title = alt.TitleParams("Pie Chart of {selected_column}", anchor='middle', dy=15, fontSize=18, font='Helvetica', fontWeight="bold")
        pie_chart = alt.Chart(source, title=pie_title).mark_arc().encode(
            theta='count()',
            color=alt.Color(f"{selected_column}:N"),
            tooltip=[alt.Tooltip(f"{selected_column}:N", title="Category"),
                     alt.Tooltip(f"count()", title="Count")]
        )
        # Display the chart
        st.altair_chart(pie_chart, use_container_width=True)
        
        # Return the pie chart
        return pie_chart

    # If the column data type is not recognized (int, float, object, datetime, bool)
    else:
        st.write(f"Cannot visualize {selected_column}.")


def numeric_numeric_plots(df, col1, col2):
    """
    Create a scatterplot with regression line and heatmap 
    if two numeric variables are selected. Add a group by option
    for the scatterplots and use color as the grouping variable.

    @param df: A pandas DataFrame object.
    @param col1: The name of the first numeric column (string).
    @param col2: The name of the second numeric column (string).
    @return: Altair scatterplot, scatterplot with lines, residual plot, and heatmap (Chart type).
    """
    from sklearn.linear_model import LinearRegression


    # Define the plotting source
    source = df[[col1, col2]].dropna()

    # Select only categorical columns (including boolean type)
    categorical_columns = df.select_dtypes(include=["object", "category", "bool"])
    
    # Create a list to store categorical column names
    categorical_column_names = []
    for col in categorical_columns.columns:
        if df[col].nunique(dropna=True) <= 6:
            categorical_column_names.append(col)

    # Create a select box for the group-by variable for the scatterplot
    grp_by = st.selectbox(
        f"OPTIONAL: Select a variable to summarize by", 
        ["None"] + sorted(categorical_column_names), 
        index=0,
        key=f"num-num-grp_by_{categorical_column_names}"
    )

    # If they select a group-by variable
    if grp_by != "None":
        # Create a new plotting source including the grp-by column
        source = df[[col1, col2, grp_by]].dropna()
        # Define the point colors as a factor of the variable
        color = alt.Color(f"{grp_by}:N", title=grp_by)
    else:
        # Just use the default point color of "mediumseagreen"
        color = alt.value("mediumseagreen")

    # SCATTERPLOT
    scatter_title = alt.TitleParams(f"Scatterplot of {col1} v.s. {col2}", anchor='start', dy=15, fontSize=15, font='Helvetica', fontWeight="bold")
    scatterplot = alt.Chart(source, title=scatter_title).mark_square(
        opacity = 0.7
    ).encode(
        x = alt.X(f"{col1}:Q", title=col1).scale(zero=False),
        y = alt.Y(f"{col2}:Q", title=col2).scale(zero=False),
        color = color,
        tooltip=[col1, col2] + ([grp_by] if grp_by != "None" else [])
    )

    # REGRESSION LINE
    regression_line = scatterplot.transform_regression(
        f"{col1}", f"{col2}"
    ).mark_line().encode(
        color=alt.value("cornflowerblue"),
        size=alt.value(1.5)
    )

    # LOESS LINE
    loess_line = scatterplot.transform_loess(
        f"{col1}", f"{col2}"
    ).mark_line().encode(
        color=alt.value("tomato"),
        size=alt.value(1.5)
    )

    scatterplot_with_lines = scatterplot + regression_line + loess_line

    # RESIDUAL PLOT

    # Define the X and y columns for calculating metrics
    X = source[[col1]]
    y = source[col2]

    model = LinearRegression().fit(X, y)

    y_pred = model.predict(X)
    residuals = y  - y_pred

    # Add predictions and residuals to the DataFrame
    resid_df = pd.DataFrame({
        f'Predicted {col2}' : y_pred,
        'Prediction Error' : residuals
    })
    
    resids_title = alt.TitleParams(f"Residual Plot of {col2} Predictions", anchor='start', dy=15, fontSize=15, font='Helvetica', fontWeight="bold")
    resids = alt.Chart(resid_df, title=resids_title).mark_square(color = "tomato").encode(
        x = alt.X(f'Predicted {col2}', title = 'Predicted'),
        y = alt.Y('Prediction Error', title = 'Residual'),
        tooltip=[f'Predicted {col2}', 'Prediction Error']).interactive()

    # Optional horizontal zero line
    zero_line = alt.Chart(pd.DataFrame({'y': [0]})).mark_rule(color = 'black').encode(y='y')

    resid_plot = resids + zero_line

    # Create bins for the x and y axes
    col1_bins = np.linspace(df[col1].min(), df[col1].max(), 21).round().astype(int)
    col2_bins = np.linspace(df[col2].min(), df[col2].max(), 21).round().astype(int)

    # Ensure bins are unique and do not overlap
    col1_bins_unique = np.unique(col1_bins)
    col2_bins_unique = np.unique(col2_bins)
    col1_intervals = len(col1_bins_unique) - 1
    col2_intervals = len(col2_bins_unique) - 1

    # Create evenly-spaced labels for the bins
    col1_labels = range(1, col1_intervals + 1)
    col2_labels = range(1, col2_intervals + 1)

    # Create bins for the x axis
    df['x_bin'] = pd.cut(
        df[col1], 
        bins=col1_bins_unique, 
        labels=col1_labels, 
        include_lowest=True
    )
    # Create bins for the y axis
    df['y_bin'] = pd.cut(
        df[col2], 
        bins=col2_bins_unique, 
        labels=col2_labels, 
        include_lowest=True
    )

    # Save for changing the bin order
    x_order = df['x_bin'].cat.categories
    y_order = df['y_bin'].cat.categories

    # Convert bins to strings
    df['x_bin'] = df['x_bin'].astype(str)
    df['y_bin'] = df['y_bin'].astype(str)

    # Altair heatmap
    heatmap_title = alt.TitleParams(f"Heatmap Distribution of {col1} v.s. {col2}", anchor='start', dy=15, fontSize=15, font='Helvetica', fontWeight="bold")
    heatmap = alt.Chart(df, title=heatmap_title).mark_rect().encode(
        x=alt.X('x_bin:O', sort=[str(c) for c in x_order], title=col1),
        y=alt.Y('y_bin:O', sort=[str(c) for c in reversed(y_order)], title=col2),
        color=alt.Color('count():Q', scale=alt.Scale(scheme='blueorange'), title="Count"),
        tooltip=['count():Q']
    ).properties(
        width=500,
        height=400
    ).configure_view(
        strokeWidth=0
    )

    # Return all computed metrics and plots
    return scatterplot, scatterplot_with_lines, resid_plot, heatmap


def regression_metric_cards(df, col1, col2):
    """
    Calculates and displays regression metrics to a page. Metrics include
    sample size, correlation, R-squared, model strength, MAE, and p-value 
    (F statistic).

    @param df: A pandas DataFrame object.
    @param col1: The name of the first numeric column (string).
    @param col2: The name of the second numeric column (string).
    """

    from sklearn.linear_model import LinearRegression
    from sklearn.feature_selection import f_regression
    from sklearn.metrics import mean_absolute_error

    # Define the regression dataframe with the two columns of interest
    source = df[[col1, col2]].dropna()
    
    # Define the X and y columns for calculating metrics
    X = source[[col1]]
    y = source[col2]

    ## SAMPLE SIZE
    sample_size = len(source)

    ## CORRELATION
    corr_df = source[[col1, col2]].corr(min_periods=10, numeric_only=True)
    correlation = corr_df.loc[col1, col2]

    ## MODEL STRENGTH (Based on the correlation value)
    model_str = "No Relationship"
    if abs(correlation) < 0.1:
        model_str = "Weak"
    elif abs(correlation) < 0.3:
        model_str = "Mod -"
    elif abs(correlation) < 0.6:
        model_str = "Mod +"
    elif abs(correlation) <= 1:
        model_str = "Strong"

    # R-SQUARED
    r_squared = correlation ** 2

    ## MEAN ABSOLUTE ERROR (MAE)
    # Define a simple linear model
    model = LinearRegression().fit(X, y)
    # Obtain the predicted y values
    y_pred = model.predict(X)
    # Calculate the MAE using the observations and predictions
    mae = mean_absolute_error(y, y_pred)

    ## OVERALL MODEL P-VALUE
    _, p = f_regression(X, y)
    p_value = round(p[0], 4)
    # If the rounded p-value is still zero, display it as less than 0.0001
    display_value = f"{p_value:.4f}" if p_value > 0 else "p < 0.0001"

    
    st.subheader("Linear Regression Model Metrics")
    # Set up formatting columns for display (2 rows of 3)
    column3, column4, column5 = st.columns(3)
    column6, column7, column8 = st.columns(3)
    
    # Use metric cards to display each metric
    column3.metric(label="**Sample Size (N)**", value = f"{sample_size}", 
                   help="This is the number of observations in the sample. Typically, " \
                   "a larger sample size leads to more accurate results.")
    column4.metric(label="**Correlation (R)**", value=f"{correlation:.2f}", 
                   help="This value shows the strength and direction of the relationship between " \
                   "two variables. +1 indicates a perfect positive correlation, 0 indicates no " \
                   "correlation, and -1 indicates a perfect negative correlation.")
    column5.metric(label="**Model Strength**", value = f"{model_str}", 
                   help="Based on the correlation, we've determined to general stength of the relationship here.\n\n" \
                   "**Note**: Model strength is highly contextual and required further investigation.")    
    column6.metric(label="**R-Squared**", value = f"{r_squared * 100:.0f}%", 
                   help="This value shows the percent of variation seen in one variable that can be " \
                   "attributed to the other.")    
    column7.metric(label="**Mean Absolute Error**", value = f"{mae:,.2f}", 
                   help="On average, this is the margin that the linear model's predictions differ " \
                   "from the actual observations.")
    column8.metric(label="**Model Significance**", value = display_value, 
                   help="Generally, this value helps determine if there is any relationship between the two " \
                   "variables being investigated. If p < 0.05, we conclude that it is likely that there " \
                   "is some sort of relationship (at a 5% significance level).")

    # Metric card customizations
    style_metric_cards(
        background_color="whitesmoke",
        border_left_color="cornflowerblue",
        box_shadow=True,
        border_size_px=0.5
    )


def display_numeric_numeric_plots(df, col1, col2, scatterplot, scatterplot_with_lines, resid_plot, heatmap):
    """
    Display a scatterplot, regression line, heatmap, and correlation coefficient
    if two numeric variables are selected.

    @param df: A pandas DataFrame object.
    @param col1: The name of the first numeric column.
    @param col2: The name of the second numeric column.
    @param scatterplot: Altair scatterplot (Chart type).
    @param scatterplot_with_lines: Altair scatterplot with loess and linreg lines (Chart type).
    @param resid_plot: Altair residual plot (Chart type).
    @param heatmap: Altair heatmap (Chart type).
    """  
    # Define the plotting source
    source = df[[col1, col2]].dropna()
    
    # Set title for scatterplots
    st.subheader(f"Scatterplots", help="HELLO!")
    # Formatting plot output with two columns
    column1, column2 = st.columns(2)  
    # First, show the scatterplot
    with column1:
        st.altair_chart(scatterplot.interactive(), use_container_width=True)  
    # Next to it, show the regression line on top of the scatterplot
    with column2:
        st.altair_chart((scatterplot_with_lines).interactive(), use_container_width=True)

    # Display Regression Metrics
    regression_metric_cards(df, col1, col2)

    with st.container():
        st.subheader("Residuals")
        st.altair_chart(resid_plot, use_container_width=True)

    # Below the regression metrics, display the table and the heatmap
    with st.container():
        # Define the space ratio for the table and heatmap
        col_table, col_heatmap = st.columns([1, 3])

        # Display the table
        with col_table:
            st.subheader("Table")
            st.dataframe(
                data=source.style.format("{:.2f}"),
                hide_index=True,
                column_order=(col1, col2),
                use_container_width=True
            )
        # Display the heatmap
        with col_heatmap:
            st.subheader("Heatmap")
            st.altair_chart(heatmap, use_container_width=True)


def numeric_categorical_plots(df, col1, col2):
    """
    Create a boxplot and confidence interval plot 
    if both a numeric and categorical variable are selected.

    @param df: A pandas DataFrame object.
    @param col1: The name of the first column (string).
    @param col2: The name of the second column (string).
    @return: Boxplot (Chart), Confidence Interval Plot (Chart), numeric column name, and categorical column name.
    """
    # Get the needed columns from the DataFrame and drop missing values
    source = df[[col1, col2]].dropna()

    # Define the data types of the first selected column
    col1_type = get_column_type(df, col1)

    # If the first column is numeric and the second is categorical
    if col1_type in ['int64', 'float64']:
        # Define the numeric and non-numeric columns
        numeric_col = col1
        non_numeric_col = col2
            
        # MULTI BOXPLOT
        mbox_title1 = alt.TitleParams(f"Boxplot Distributions of {col1} by {col2}", anchor='start', dy=15, fontSize=15, font='Helvetica', fontWeight="bold")
        multi_box = alt.Chart(source, title=mbox_title1).mark_boxplot(size=40).encode(
            x = alt.X(f"{col2}:N", sort='-y', title=col2),
            y = alt.Y(f"{col1}:Q", title=col1),
            color = alt.Color(f"{col2}:N", title=col2, legend=None, scale=alt.Scale(scheme='category20')),
            tooltip=[f"{col2}:N", f"{col1}:Q"]
        )

        # CONFIDENCE INTERVALS WITH MEANS
        error_title1 = alt.TitleParams(f"95% Confidence Intervals of {col1} by {col2}", anchor='start', dy=15, fontSize=15, font='Helvetica', fontWeight="bold")
        error_bars = alt.Chart(source, title=error_title1).mark_errorbar(extent='ci').encode(
            alt.X(f"{col1}").scale(zero=False),
            alt.Y(f"{col2}:O", sort='-x', title=col2)
        )

        # Calculate the mean of col1 for each category in col2
        observed_points = alt.Chart(source).mark_point().encode(
            x = alt.X(f"{col1}:Q", aggregate='mean'),
            y = alt.Y(f"{col2}:O", sort='-x', title=col2)

        )

        # Combine the error bars and observed points into one plot
        confint_plot = error_bars + observed_points

        # Return both plots
        return multi_box, confint_plot, numeric_col, non_numeric_col

    # If the first column is categorical and the second is numeric
    else:
        # Define the numeric and non-numeric columns
        numeric_col = col2
        non_numeric_col = col1
        
        # MULTI BOXPLOT
        mbox_title2 = alt.TitleParams(f"Boxplot Distributions of {col2} by {col1}", anchor='start', dy=15, fontSize=15, font='Helvetica', fontWeight="bold")
        multi_box = alt.Chart(source, title=mbox_title2).mark_boxplot(size=40).encode(
            x = alt.X(f"{col1}:N", sort='-y', title=col1),
            y = alt.Y(f"{col2}:Q", title=col2),
            color = alt.Color(f"{col1}:N", title=col1, legend=None, scale=alt.Scale(scheme='category20')),
            tooltip=[f"{col1}:N", f"{col2}:Q"]
        )

        # CONFIDENCE INTERVALS WITH MEANS
        error_title2 = alt.TitleParams(f"95% Confidence Intervals of {col2} by {col1}", anchor='start', dy=15, fontSize=15, font='Helvetica', fontWeight="bold")
        error_bars = alt.Chart(source, title=error_title2).mark_errorbar(extent='ci').encode(
            alt.X(f"{col2}").scale(zero=False),
            alt.Y(f"{col1}:O", sort='-x', title=col1)
        )

        # Calculate the mean of col2 for each category in col1
        observed_points = alt.Chart(source).mark_point().encode(
            x = alt.X(f'{col2}:Q', aggregate='mean'),
            y = alt.Y(f"{col1}:O", sort='-x', title=col1)
        )
        
        # Combine the error bars and observed points into one plot
        confint_plot = error_bars + observed_points
        
        # Return both plots
        return multi_box, confint_plot, numeric_col, non_numeric_col


def display_numeric_categorical_plots(df, numeric_col, non_numeric_col, multi_box, confint_plot):
    """
    Display the boxplot and confidence interval plot 
    if both a numeric and categorical variable are selected.

    @param df: A pandas DataFrame object.
    @param numeric_col: The name of the numeric column.
    @param non_numeric_col: The name of the categorical column.
    @param multi_box: Altair boxplot grouped by category (Chart type).
    @param confint_plot: Altair chart showing mean with confidence interval bars (Chart type).
    """
    # Display the boxplot
    st.subheader("Boxplots")
    st.altair_chart(multi_box, use_container_width=True)
    # Display the confidence interval plot
    st.subheader("Confidence Intervals")
    st.altair_chart(confint_plot, use_container_width=True)


def categorical_categorical_plots(df, col1, col2):
    """
    Create a crosstab with raw counts and percentages for two categorical variables 
    if two categorical variables are selected.

    @param df: A pandas DataFrame object.
    @param col1: The name of the first categorical column (string).
    @param col2: The name of the second categorical column (string).
    @return: Frequency table, format dictionary, Altair heatmap, stacked bar chart, and 100% stacked bar chart.
    """
    # Define the plotting source
    source = df[[col1, col2]].dropna()

    # Crosstab with raw counts
    freq_table = pd.crosstab(source[col1], source[col2])

    # Turn to percentages aggregated by col1
    freq_table = freq_table.div(freq_table.sum(axis=1), axis=0) * 100

    # Table formatting
    freq_table.index.name = col1
    freq_table.columns.name = col2
    freq_table = freq_table.reset_index()
    freq_table = freq_table.rename_axis(None, axis=1)

    # Format percentage columns to only one decimal place
    format_dict = {col: "{:.1f}%" for col in freq_table.columns if pd.api.types.is_numeric_dtype(freq_table[col])}

    # HEATMAP
    heat_title = alt.TitleParams(f"Heatmap Table of {col1} and {col2}", anchor='start', dy=15, fontSize=15, font='Helvetica', fontWeight="bold")
    heatmap = alt.Chart(source, title=heat_title).mark_rect().encode(
        x=f'{col2}:O',
        y=f'{col1}:O',
        color=alt.Color('count():Q', scale=alt.Scale(scheme='blueorange')),
        tooltip=[f'{col1}:O', f'{col2}:O', 'count():Q']
    )
        
    # STACKED BAR CHARTS
    stacked_title = alt.TitleParams(f"Stacked Bar Chart of {col1} by {col2}", anchor='start', dy=15, fontSize=15, font='Helvetica', fontWeight="bold")
    stacked_bar = alt.Chart(source, title=stacked_title).mark_bar().encode(
        y=alt.Y(f"{col1}:N", title=col1),
        x=alt.X('count():Q', title='Count'),
        color=alt.Color(f"{col2}:N", title=col2),
        tooltip=[f"{col1}:O", f"{col2}:O", 'count():Q']
    )
    
    # Putting the frequecy table into a long format for plotting in the 100% stacked bar chart
    stacked_df_100 = freq_table.melt(id_vars=col1, var_name='Category', value_name='Percentage')

    # Altair 100% horizontal stacked bar chart
    stacked_100_title = alt.TitleParams(f"Percentage Distribution of {col2} by {col1}", anchor='start', dy=15, fontSize=15, font='Helvetica', fontWeight="bold")
    stacked_bar_100_pct = alt.Chart(stacked_df_100, title=stacked_100_title).mark_bar().encode(
        y=alt.Y(f'{col1}:O', title=None),
        x=alt.X('Percentage:Q', stack='normalize', title=f'{col2} Distribution'),
        color=alt.Color('Category:N'),
        tooltip=[alt.Tooltip(col1), alt.Tooltip('Category'), alt.Tooltip('Percentage:Q')]
    )

    # Return all tables and plots
    return freq_table, format_dict, heatmap, stacked_bar, stacked_bar_100_pct


def display_categorical_categorical_plots(df, col1, col2, freq_table, format_dict, heatmap, stacked_bar, stacked_bar_100_pct):
    """
    Display the crosstab, heatmap, and stacked bar charts 
    if two categorical variables are selected.

    @param df: A pandas DataFrame object.
    @param col1: The name of the first categorical column.
    @param col2: The name of the second categorical column.
    @param freq_table: Crosstab table showing frequency counts (DataFrame or displayable object).
    @param format_dict: A dictionary used to format the frequency table display.
    @param heatmap: Altair heatmap of joint frequencies (Chart type).
    @param stacked_bar: Altair stacked bar chart showing counts (Chart type).
    @param stacked_bar_100_pct: Altair 100% stacked bar chart showing proportions (Chart type).
    """
    
    # If the number of unique values of the two columns are reasonable for plotting
    if ((df[col1].nunique() > 2 and df[col2].nunique() > 2) and 
        (df[col1].nunique() <= 12 and df[col2].nunique() <= 12)):
        column1, column2 = st.columns(2)
        # Display the frequency table
        with column1:
            st.subheader(f"Frequency Table of {col1} and {col2}")
            st.dataframe(freq_table.style.format(format_dict, na_rep="—"), hide_index=True)
        # Display the heatmap
        with column2:
            st.altair_chart(heatmap, use_container_width=True)
    
    # If the number of unique values is NOT reasonable for plotting
    else:
        # Just display the frequency table
        st.subheader(f"Frequency Table of {col1} and {col2}")
        st.dataframe(freq_table.style.format(format_dict, na_rep="—"), hide_index=True)

    # Display the stacked bar chart
    st.altair_chart(stacked_bar, use_container_width=True)
    # Display the 100% stacked bar chart next to the other chart
    st.altair_chart(stacked_bar_100_pct, use_container_width=True)


def two_column_plot(df, col1, col2):
    """
    Create a series of two-variable plots based on the data types of each selected column.

    @param df: A pandas DataFrame object.
    @param col1: The first column to plot.
    @param col2: The second column to plot.
    @return: Respective combination of plots based on datatypes.
    """
    # Create a copy of the original dataset
    df = df.copy()
    # Define boolean variables as "object" type for plotting purposes
    df[df.select_dtypes(include='bool').columns] = df.select_dtypes(include='bool').astype('object')
    
    # Define the data types of both selected columns
    col1_type = get_column_type(df, col1)
    col2_type = get_column_type(df, col2)

    # If the selected columns are the same, no plots will be generated
    if col1 == col2:
        st.warning("Please select two different columns to visualize.")
        return None

    # If two NUMERIC variables are selected
    if pd.api.types.is_numeric_dtype(col1_type) and pd.api.types.is_numeric_dtype(col2_type): 
        # Define all the needed plots
        scatterplot, scatterplot_with_lines, resid_plot, heatmap = numeric_numeric_plots(df, col1, col2)
        # Display all plots
        display_numeric_numeric_plots(df, col1, col2, scatterplot, scatterplot_with_lines, resid_plot, heatmap)
        # Return all plots
        return scatterplot, scatterplot_with_lines, heatmap

    # If NUMERIC and CATEGORICAL variables are selected
    elif ((col1_type in ['int64', 'float64'] and (col2_type == 'object' or col2_type.name == 'category')) 
    or ((col1_type == 'object' or col1_type.name == 'category') and col2_type in ['int64', 'float64'])):

        # Create the boxplot and confidence interval plots
        multi_box, confint_plot, numeric_col, non_numeric_col = numeric_categorical_plots(df, col1, col2)
        # Display the plots
        display_numeric_categorical_plots(df, numeric_col, non_numeric_col, multi_box, confint_plot)
        # Return the plots
        return multi_box, confint_plot
        
    # If two CATEGORICAL variables are selected
    elif ((col1_type in ['object', 'bool'] or col1_type.name == 'category') and 
      (col2_type in ['object', 'bool'] or col2_type.name == 'category')):
        
        # Create the crosstab and heatmap
        freq_table, format_dict, heatmap, stacked_bar, stacked_bar_100_pct = categorical_categorical_plots(df, col1, col2)
        # Display the plots
        display_categorical_categorical_plots(df, col1, col2, freq_table=freq_table, format_dict=format_dict, 
                                               heatmap=heatmap, stacked_bar=stacked_bar, 
                                               stacked_bar_100_pct=stacked_bar_100_pct)
        # Return the plots
        return freq_table, format_dict, heatmap, stacked_bar, stacked_bar_100_pct

    # If combination of datatypes are not recognized
    else:
        st.write(f"Cannot visualize {col1} and {col2} together YET")
        return None


def group_by_plot(df, num_op, num_var, grp_by):
    """
    Groups data by a categorical variable and summarizes a numeric variable using a selected operation.
    Displays a corresponding bar chart and summary table.

    @param df: A pandas DataFrame object.
    @param num_op: The aggregation operation to apply ("Total", "Average", "Median", "Count", "Unique Count", or "Standard Deviation").
    @param num_var: The name of the numeric column to aggregate.
    @param grp_by: The name of the categorical column to group by.
    @return: A tuple containing the grouped DataFrame and the Altair bar chart.
    """
    # Create a new simple DataFrame with the two columns of interest
    df_simple = df[[grp_by, num_var]]

    # Group by the "grp_by" variable using the SELECTED OPERATION
    if num_op == "Total":
        df_grouped = df_simple.groupby(by = [grp_by]).sum()
        prefix = "Total "
    elif num_op == "Average":
        df_grouped = df_simple.groupby(by = [grp_by]).mean()
        prefix = "Average "
    elif num_op == "Median":
        df_grouped = df_simple.groupby(by = [grp_by]).median()
        prefix = "Median "
    elif num_op == "Count":
        df_grouped = df_simple.groupby(by = [grp_by]).count()
        prefix = "Count of "
    elif num_op == "Unique Count":
        df_grouped = df_simple.groupby(by = [grp_by]).nunique()
        prefix = "Unique Count of "
    elif num_op == "Standard Deviation":
        df_grouped = df_simple.groupby(by = [grp_by]).std()
        prefix = "Standard Deviation of "

    # Reset the DataFrame index for plotting
    df_grouped = df_grouped.reset_index()
    
    # Rename the existing column to reflect the applied operation
    num_var_name = f"{prefix}{num_var}"
    df_grouped.rename(columns={num_var: num_var_name}, inplace=True)

    # Use a select box to sort the plot (Defualt, Ascending, or Descending)
    sort_option = st.selectbox(
        label = "Select a sort option",
        options=["None", "Ascending", "Descending"],
        index=0,
        key=f"{num_op}_{num_var}_{grp_by}"
    )
    
    # Change the sort variable based on the sorting selection
    if sort_option == "Ascending":
        sort = 'y'
    elif sort_option == "Descending":
        sort = '-y' 
    else:
        sort = list(df_grouped[grp_by])
    
    # BAR CHART
    grouped_chart = alt.Chart(df_grouped, title=f"{num_var_name} by {grp_by}").mark_bar().encode(
        x=alt.X(f'{grp_by}:N', sort=sort),
        y=alt.Y(f'{num_var_name}:Q')
    )

    # Display the plot
    st.altair_chart(grouped_chart, use_container_width=True)

    # Display the summarized table
    st.subheader("Summarized Table")
    st.dataframe(df_grouped)

    # Return the aggregated DataFrame and the corresponsing bar chart
    return df_grouped, grouped_chart


#--------------------------------------#
###           Census Data            ###
#--------------------------------------#

def housing_metrics_vs_statewide(housing_gdf, filtered_gdf):

    # Housing Units Section
    st.subheader("Housing Units")
    c1 = st.container()
    c2, c3 = st.columns(2)

    # Total units
    c1.metric(
        label="**Total** Housing Units", 
        value=f"{filtered_gdf['DP04_0001E'].sum():,.0f}"
    )

    # Vacant Units  
    pct_vac = (filtered_gdf['DP04_0003E'].sum() / filtered_gdf['DP04_0001E'].sum()) * 100
    state_pct_vac = (housing_gdf['DP04_0003E'].sum() / housing_gdf['DP04_0001E'].sum()) * 100
    pct_vac_delta = pct_vac - state_pct_vac
    c2.metric(
        label="**Vacant** Units", 
        value=f"{filtered_gdf['DP04_0003E'].sum():,.0f}"
    )
    # Vacant Units %
    c2.metric(
        label="**Vacant** Units (%)", 
        value=f"{pct_vac:.1f}%",
        delta=f"{pct_vac_delta:.1f}%"
    )
    
    # Occupied Units
    pct_occ = (filtered_gdf['DP04_0002E'].sum() / filtered_gdf['DP04_0001E'].sum()) * 100
    state_pct_occ = (housing_gdf['DP04_0002E'].sum() / housing_gdf['DP04_0001E'].sum()) * 100
    pct_occ_delta = pct_occ - state_pct_occ
    c3.metric(
        label="**Occupied** Units", 
        value=f"{filtered_gdf['DP04_0002E'].sum():,.0f}"
    ) 
    # Occupied Units (%)
    c3.metric(
        label="**Occupied** Units (%)", 
        value=f"{pct_occ:.1f}%",
        delta=f"{pct_occ_delta:.1f}%"
    )   

    st.markdown("---")
    
    # HOUSING TENURE SECTION
    st.subheader("Occupied Housing Tenure")
    c4, c5, c6 = st.columns(3)    
    # Units Owned
    state_pct_own = (housing_gdf['DP04_0046E'].sum() / housing_gdf['DP04_0002E'].sum()) * 100
    pct_own = (filtered_gdf['DP04_0046E'].sum() / filtered_gdf['DP04_0002E'].sum()) * 100
    pct_own_delta = pct_own - state_pct_own
    c4.metric(
        label="**Owned**", 
        value=f"{filtered_gdf['DP04_0046E'].sum():,.0f}"
    )
    # Units Owned (%)
    c4.metric(
        label="**Owned** (%)", 
        value=f"{pct_own:.1f}%",
        delta=f"{pct_own_delta:.1f}%"
    )
    
    # Units Rented
    state_pct_rent = (housing_gdf['DP04_0047E'].sum() / housing_gdf['DP04_0002E'].sum()) * 100
    pct_rent = (filtered_gdf['DP04_0047E'].sum() / filtered_gdf['DP04_0002E'].sum()) * 100
    pct_rent_delta = pct_rent - state_pct_rent
    c5.metric(
        label="**Rented**", 
        value=f"{filtered_gdf['DP04_0047E'].sum():,.0f}"
    )
    # Units Rented (%)
    c5.metric(
        label="**Rented** (%)", 
        value=f"{pct_rent:.1f}%",
        delta=f"{pct_rent_delta:.1f}%"
    )

    # Units Lacking Complete Plumbing
    state_pct_lack_plumbing = (housing_gdf['DP04_0073E'].sum() / housing_gdf['DP04_0002E'].sum()) * 100
    pct_lack_plumbing = (filtered_gdf['DP04_0073E'].sum() / filtered_gdf['DP04_0002E'].sum()) * 100
    pct_lack_plumbing_delta = pct_lack_plumbing - state_pct_lack_plumbing
    c6.metric(
        label="Units **Lacking Plumbing**", 
        value=f"{filtered_gdf['DP04_0073E'].sum():,.0f}"
    )
    # Units with Lack of Complete Plumbing (%)
    c6.metric(
        label="Units **Lacking Plumbing** (%)", 
        value=f"{pct_lack_plumbing:.1f}%",
        delta=f"{pct_lack_plumbing_delta:.1f}%",
        delta_color="inverse"
    )
    
    st.markdown("---")

    # OWNER-OCCUPIED SECTION
    st.subheader("Owner Occupied Units")
    c7, c8 = st.columns(2)
    
    # Average Median Home Value
    state_avg_med_val = housing_gdf['DP04_0089E'].mean()
    avg_med_val = filtered_gdf['DP04_0089E'].mean()
    avg_med_val_delta = avg_med_val - state_avg_med_val
    c7.metric(
        label="(Average) Median **Home Value**", 
        value=f"${avg_med_val:,.2f}",
        delta=f"{avg_med_val_delta:,.2f}",
        delta_color="inverse"
    )
    
    # Average Median Mortgage Payment
    state_avg_med_mort = housing_gdf['DP04_0101E'].mean()
    avg_med_mort = filtered_gdf['DP04_0101E'].mean()
    avg_med_mort_delta = avg_med_mort - state_avg_med_mort
    c8.metric(
        label="(Average) Median **Mortgage Payment**", 
        value=f"${avg_med_mort:,.2f}",
        delta=f"{avg_med_mort_delta:,.2f}",
        delta_color="inverse"
    )

    st.markdown("---")

    # RENTER-OCCUPIED SECTION
    st.subheader("Rented Units")
    c9, c10 = st.columns(2)
    
    # Average Median Gross Rent
    state_avg_med_gross_rent = housing_gdf['DP04_0134E'].mean()
    avg_med_gross_rent = filtered_gdf['DP04_0134E'].mean()
    avg_med_gross_rent_delta = avg_med_gross_rent - state_avg_med_gross_rent
    c9.metric(
        label="(Average) Median **Gross Rent**", 
        value=f"${avg_med_gross_rent:,.2f}",
        delta=f"{avg_med_gross_rent_delta:,.2f}",
        delta_color="inverse"
    )
    
    # Households where rent takes up 35% or more of their household income
    state_rent_burden_pct = (housing_gdf['DP04_0142E'].sum() / housing_gdf['DP04_0126E'].sum()) * 100
    rent_burden_pct = (filtered_gdf['DP04_0142E'].sum() / filtered_gdf['DP04_0126E'].sum()) * 100
    rent_burden_pct_delta = rent_burden_pct - state_rent_burden_pct
    c10.metric(
        label="Occupied Units paying 35%+ of Income on Rent", 
        value=f"{filtered_gdf['DP04_0142E'].sum():,.0f}"
    )
    # Percentage of households where rent takes up 35% or more of their household income
    c10.metric(
        label="Occupied Units paying 35%+ of Income on Rent", 
        value=f"{rent_burden_pct:.1f}%",
        delta=f"{rent_burden_pct_delta:.1f}%",
        delta_color="inverse"
    )

    st.markdown("---")

    # Style the metric cards
    style_metric_cards(
        background_color="whitesmoke",
        border_left_color="thistle",
        box_shadow=True,
        border_size_px=0.5
    )


def housing_metrics_vs_10yr(filtered_gdf_2013, filtered_gdf_2023):
        
    # Housing Units Section
    st.subheader("Occupancy")
    left_col1, right_col2 = st.columns(2)
    
    with left_col1:
        
        total_units_2023 = filtered_gdf_2023['DP04_0001E'].sum()
        total_units_2013 = filtered_gdf_2013['DP04_0001E'].sum()
        total_units_delta = total_units_2023 - total_units_2013

        vacant_units_2023 = filtered_gdf_2023['DP04_0003E'].sum()
        vacant_units_2013 = filtered_gdf_2013['DP04_0003E'].sum()
        pct_vac_2023 = (vacant_units_2023 / total_units_2023) * 100
        pct_vac_2013 = (vacant_units_2013 / total_units_2013) * 100
        pct_vac_delta = pct_vac_2023 - pct_vac_2013

        occupied_units_2023 = filtered_gdf_2023['DP04_0002E'].sum()
        occupied_units_2013 = filtered_gdf_2013['DP04_0002E'].sum()
        pct_occ_2023 = (occupied_units_2023 / total_units_2023) * 100
        pct_occ_2013 = (occupied_units_2013 / total_units_2013) * 100
        pct_occ_delta = pct_occ_2023 - pct_occ_2013

        # Top metric: Total units
        st.metric(
            label="**Total Housing Units**", 
            value=f"{total_units_2023:,.0f}",
            delta=f"{total_units_delta:,.0f}",
            help="Hi"
        )

        # Below: split metrics for vacant and occupied
        subcol1, subcol2 = st.columns(2)

        with subcol1:
            st.metric(
                label="**Occupied Units**", 
                value=f"{occupied_units_2023:,.0f}", 
                delta=f"{occupied_units_2023 - occupied_units_2013:,.0f}",
                help="Hi"
            )
            st.metric(
                label="**Occupied Units (%)**", 
                value=f"{pct_occ_2023:.1f}%", 
                delta=f"{pct_occ_delta:.1f}%",
                help="Hi"
            )

        with subcol2:
            st.metric(
                label="**Vacant Units**", 
                value=f"{vacant_units_2023:,.0f}", 
                delta=f"{vacant_units_2023 - vacant_units_2013:,.0f}",
                help="Hi"
            )
            st.metric(
                label="**Vacant Units (%)**", 
                value=f"{pct_vac_2023:.1f}%", 
                delta=f"{pct_vac_delta:.1f}%",
                help="Hi"
            )


    with right_col2:
        pie_df = pd.DataFrame({
            'Status': ['Occupied', 'Vacant'],
            'Units': [occupied_units_2023, vacant_units_2023]
        })

        pie_chart = alt.Chart(pie_df).mark_arc(innerRadius=130).encode(
            theta=alt.Theta(field="Units", type="quantitative", aggregate="sum"),
            color=alt.Color(field="Status", type="nominal", scale=alt.Scale(
                domain=["Occupied", "Vacant"],
                range=["cornflowerblue", "whitesmoke"])),
                tooltip=[alt.Tooltip("Status:N"), alt.Tooltip("Units")]
        ).properties(width=300, height=440).configure_legend(orient='top-left')

        st.altair_chart(pie_chart, use_container_width=True)

    # Divider
    st.markdown("---")
    
    st.subheader("Housing Tenure")
    
    left_col2, right_col2 = st.columns(2)
    
    # HOUSING TENURE SECTION
    with right_col2:
        c4, c5 = st.columns(2)
        
        # Owner-Occupied Units
        owned_units_2023 = filtered_gdf_2023['DP04_0046E'].sum()
        owned_units_2013 = filtered_gdf_2013['DP04_0045E'].sum()
        pct_own_2023 = (owned_units_2023 / occupied_units_2023) * 100
        pct_own_2013 = (owned_units_2013 / occupied_units_2013) * 100
        pct_own_delta = pct_own_2023 - pct_own_2013
        c4.metric(
            label="**Owner-Occupied**", 
            value=f"{owned_units_2023:,.0f}",
            delta=f"{owned_units_2023 - owned_units_2013:,.0f}",
            help="Hi"
        )
        # Units Owned (%)
        c4.metric(
            label="**Owner-Occupied** (%)", 
            value=f"{pct_own_2023:.1f}%",
            delta=f"{pct_own_delta:.1f}%",
            help="Hi"
        )
    
        # Renter-Occupied Units
        rented_units_2023 = filtered_gdf_2023['DP04_0047E'].sum()
        rented_units_2013 = filtered_gdf_2013['DP04_0046E'].sum()
        pct_rent_2023 = (rented_units_2023 / occupied_units_2023) * 100
        pct_rent_2013 = (rented_units_2013 / occupied_units_2013) * 100
        pct_rent_delta = pct_rent_2023 - pct_rent_2013
        c5.metric(
            label="**Renter-Occupied**", 
            value=f"{rented_units_2023:,.0f}",
            delta=f"{rented_units_2023 - rented_units_2013:,.0f}",
            help="Hi"
        )
        # Units Rented (%)
        c5.metric(
            label="**Renter-Occupied** (%)", 
            value=f"{pct_rent_2023:.1f}%",
            delta=f"{pct_rent_delta:.1f}%",
            help="Hi"
        )

    with left_col2:
        # Pie chart for Housing Tenure
        pie_df = pd.DataFrame({
            'Occupied Tenure': ['Owner', 'Renter'],
            'Units': [owned_units_2023, rented_units_2023]
        })

        pie_chart = alt.Chart(pie_df).mark_arc(innerRadius=75).encode(
            theta=alt.Theta(field="Units", type="quantitative", aggregate="sum"),
            color=alt.Color(field="Occupied Tenure", scale=alt.Scale(
                domain=["Owner", "Renter"],
                range=['cornflowerblue', 'whitesmoke'])), 
                tooltip=[alt.Tooltip("Occupied Tenure:N"), alt.Tooltip("Units")]
                ).properties(width=250, height=300).configure_legend(orient="top-left")
        
        st.altair_chart(pie_chart)
    
    st.markdown("---")
    
    # OWNER-OCCUPIED SECTION
    st.subheader("Owner-Occupied Units")
    c7 = st.container()
    st.subheader("Monthly Owner Costs")
    c8, c8_2 = st.columns(2)
    
    # Average Median Home Value
    avg_med_val_2023 = filtered_gdf_2023['DP04_0089E'].mean()
    avg_med_val_2013 = filtered_gdf_2013['DP04_0088E'].mean()
    avg_med_val_delta = avg_med_val_2023 - avg_med_val_2013
    c7.metric(
        label="(Average) Median **Home Value**", 
        value=f"${avg_med_val_2023:,.2f}",
        delta=f"{avg_med_val_delta:,.2f}",
        delta_color="off",
        help="Hi"
    )

    with c7:
        # Bar chart for Median Home Value
        bar_chart_df = pd.DataFrame({
            'Year': ['2013', '2023'],
            'Median Home Value': [avg_med_val_2013, avg_med_val_2023]
        })

        bar_chart = alt.Chart(bar_chart_df).mark_bar().encode(
            x=alt.X('Year:N', title='Year'),
            y=alt.Y('Median Home Value:Q', title='Median Home Value ($)'),
            color=alt.Color('Year:N'),
            tooltip=[alt.Tooltip('Year:N'), alt.Tooltip('Median Home Value:Q')]
        ).properties(
            title="Median Home Value Comparison (2013 vs 2023)",
            height=550, width=600)

        st.altair_chart(bar_chart)
        


    # Average Median Monthly Owner Cost (SMOC) (For units with a mortgage)
    avg_med_SMOC_2023 = filtered_gdf_2023['DP04_0101E'].mean()
    avg_med_SMOC_2013 = filtered_gdf_2013['DP04_0100E'].mean()
    avg_med_SMOC_delta = avg_med_SMOC_2023 - avg_med_SMOC_2013
    c8.metric(
        label="Selected Monthly **Owner Costs** for *mortgaged* units",
        value=f"${avg_med_SMOC_2023:,.2f}",
        delta=f"{avg_med_SMOC_delta:,.2f}",
        delta_color="inverse",
        help="Hi"
    )

    # Average Median Monthly Owner Cost (SMOC) (For units with a mortgage)
    avg_med_SMOC2_2023 = filtered_gdf_2023['DP04_0109E'].mean()
    avg_med_SMOC2_2013 = filtered_gdf_2013['DP04_0107E'].mean()
    avg_med_SMOC2_delta = avg_med_SMOC2_2023 - avg_med_SMOC2_2013
    c8_2.metric(
        label="Selected Monthly **Owner Costs** for *non-mortgaged* units",
        value=f"${avg_med_SMOC2_2023:,.2f}",
        delta=f"{avg_med_SMOC2_delta:,.2f}",
        delta_color="inverse",
        help="Hi"
    )

    
    con = st.container()
    con.markdown(
        "***Note***: The Selected Monthly Owner Costs (SMOC) include costs such as mortgage," \
        " property taxes, insurance, and utilities. "
        "The values for 2013 are adjusted for inflation to 2023 dollars." \
        "The SMOC for non-mortgaged units includes costs such as property taxes, insurance, and utilities.")
    
    # Create a chart for the SMOC comparison
    with con:

        mort_nonmort = st.selectbox(
            label="Select SMOC Type",
            options=['Mortgaged', 'Non-Mortgaged'],
            index=0)

        SMOC_bar_df = pd.DataFrame({
            'Year': ['2013', '2023'],
            'Median SMOC (Mortgaged)': [avg_med_SMOC_2013, avg_med_SMOC_2023],
            'Median SMOC (Non-Mortgaged)': [avg_med_SMOC2_2013, avg_med_SMOC2_2023]
        })

        SMOC_bar_chart = alt.Chart(SMOC_bar_df).mark_bar().encode(
            x=alt.X('Year:N', title='Year'),
            y=alt.Y(f'Median SMOC ({mort_nonmort}):Q', title=f'Median SMOC ($)'),
            color=alt.Color('Year:N'),
            tooltip=[alt.Tooltip('Year:N'), alt.Tooltip(f'Median SMOC ({mort_nonmort}):Q')]
        ).properties(
            title=f"Median SMOC Comparison for {mort_nonmort} Units (2013 vs 2023)",
            height=550, width=600
        )

        st.altair_chart(SMOC_bar_chart)

    st.markdown("---")

    # RENTER-OCCUPIED SECTION
    st.subheader("Renter-Occupied Units")
    c9, c10 = st.columns(2)
    
    # Average Median Gross Rent
    avg_med_gross_rent_2023 = filtered_gdf_2023['DP04_0134E'].mean()
    avg_med_gross_rent_2013 = filtered_gdf_2013['DP04_0132E'].mean()
    avg_med_gross_rent_delta = avg_med_gross_rent_2023 - avg_med_gross_rent_2013
    c9.metric(
        label="Median **Gross Rent**", 
        value=f"${avg_med_gross_rent_2023:,.2f}",
        delta=f"{avg_med_gross_rent_delta:,.2f}",
        delta_color="inverse",
        help="Hi"
    )
    
    # Count of Households where rent takes up 35% or more of their household income
    units_paying_rent_2023 = filtered_gdf_2023['DP04_0126E'].sum()
    units_paying_rent_2013 = filtered_gdf_2013['DP04_0124E'].sum()
    rent_burden35_2023 = filtered_gdf_2023['DP04_0142E'].sum()
    rent_burden35_2013 = filtered_gdf_2013['DP04_0140E'].sum()
    rent_burden35_pct_2023 = (rent_burden35_2023 / units_paying_rent_2023) * 100
    rent_burden35_pct_2013 = (rent_burden35_2013 / units_paying_rent_2013) * 100
    rent_burden35_pct_delta = rent_burden35_pct_2023 - rent_burden35_pct_2013
    c10.metric(
        label="Occupied Units paying 35%+ of Income on Rent", 
        value=f"{rent_burden35_2023:,.0f}",
        delta=rent_burden35_2023 - rent_burden35_2013,
        delta_color="inverse",
        help="Hi"
    )
    # Percentage of households where rent takes up 35% or more of their household income
    c10.metric(
        label="% Occupied Units paying 35%+ of Income on Rent", 
        value=f"{rent_burden35_pct_2023:.1f}%",
        delta=f"{rent_burden35_pct_delta:.1f}%",
        delta_color="inverse",
        help="Hi"
    )

    st.markdown("---")

    # Style the metric cards
    style_metric_cards(
        background_color="whitesmoke",
        border_left_color="whitesmoke",
        box_shadow=True,
        border_size_px=0.5
    )


def housing_pop_plot(county, jurisdiction, filtered_gdf, pop_df):
    # Define a set of year ranges corresponding to new unit construction data
    year_bins = [
        "1939 and Prior", "1940 - 1949", "1950 - 1959", "1960 - 1969",
        "1970 - 1979", "1980 - 1989", "1990 - 1999", "2000 - 2009",
        "2010 - 2019", "2020 - Present"
    ]

    # Convert the "Geo-ID" column in both datasets to string type
    filtered_gdf["GEOID"] = filtered_gdf["GEOID"].astype("string")
    filtered_gdf["GEOID"] = filtered_gdf["GEOID"].str.strip()
    pop_df["_geoid"] = pop_df["_geoid"].astype("string")
    pop_df["_geoid"] = pop_df["_geoid"].str.strip()
    
    # Perform a left join on the two dataframes, joining on the respective "Geo-ID" column
    filtered_gdf_pop = pd.merge(left=filtered_gdf, right=pop_df, how="left", left_on="GEOID", right_on="_geoid")
    
    # For the plot title, dynamically change the area of interest based on user filter selections
    if county == "All Counties":
        title_geo = "Vermont (Statewide)"
    elif county != "All Counties" and jurisdiction == "All Jurisdictions":
        title_geo = f"{county} County"
    elif jurisdiction != "All Jurisdictions":
        title_geo = f"{jurisdiction}, Vermont"
    
    # Define a list of housing counts for each year range
    raw_housing_counts = [
        filtered_gdf_pop["DP04_0026E"].sum(), # Total units built 1939 or earlier
        filtered_gdf_pop["DP04_0025E"].sum(), # Total units built 1940-1949
        filtered_gdf_pop["DP04_0024E"].sum(), # Total units built 1950-1959
        filtered_gdf_pop["DP04_0023E"].sum(), # Total units built 1960-1969
        filtered_gdf_pop["DP04_0022E"].sum(), # Total units built 1970-1979
        filtered_gdf_pop["DP04_0021E"].sum(), # Total units built 1980-1989
        filtered_gdf_pop["DP04_0020E"].sum(), # Total units built 1990-1999
        filtered_gdf_pop["DP04_0019E"].sum(), # Total units built 2000-2009
        filtered_gdf_pop["DP04_0018E"].sum(), # Total units built 2010-2019
        filtered_gdf_pop["DP04_0017E"].sum()  # Total units built 2020 or later
    ]
    # Calculate the cumulative sum (as a list) to plot total progression over time
    cumulative_housing_counts = pd.Series(raw_housing_counts).cumsum().tolist()

    # From the population dataset, gather tract-level population data for the respective years
    population_counts = [
        filtered_gdf_pop["year1930"].sum(), # Total Population in 1930
        filtered_gdf_pop["year1940"].sum(), # Total Population in 1940
        filtered_gdf_pop["year1950"].sum(), # Total Population in 1950
        filtered_gdf_pop["year1960"].sum(), # Total Population in 1960
        filtered_gdf_pop["year1970"].sum(), # Total Population in 1970
        filtered_gdf_pop["year1980"].sum(), # Total Population in 1980
        filtered_gdf_pop["year1990"].sum(), # Total Population in 1990
        filtered_gdf_pop["year2000"].sum(), # Total Population in 2000
        filtered_gdf_pop["year2010"].sum(), # Total Population in 2010
        filtered_gdf_pop["year2020"].sum()  # Total Population in 2020
    ]

    # Gather population and housing data into one dataframe
    house_pop_plot_df = pd.DataFrame({
        "Year Range": year_bins,
        "Census Year": [1930, 1940, 1950, 1960, 1970, 1980, 1990, 2000, 2010, 2020],
        "Population": population_counts,
        "Total Housing Units": cumulative_housing_counts,
        "New Housing Units": raw_housing_counts
    }).melt( # Melt / transpose the dataset (long format) for time-series plotting
        id_vars=['Year Range', 'Census Year'],
        value_vars=['Population', 'Total Housing Units', 'New Housing Units'],
        var_name='Metric',
        value_name='Value'
    )

    # Define an interactive selection feature to the plot
    selection = alt.selection_point(fields=['Metric'], bind='legend')
    # The base plot with 3 lines, one for each metric
    base = alt.Chart(house_pop_plot_df).encode(
        x=alt.X('Year Range:N', title="Year", axis=alt.Axis(labelAngle=-45)),
        color=alt.Color('Metric:N', legend=alt.Legend(
            title="", orient="top-left", direction='horizontal', offset=-38)),
        tooltip=[alt.Tooltip('Metric'), alt.Tooltip('Value', title="Count")],
        opacity=alt.when(selection).then(alt.value(1)).otherwise(alt.value(0.2))
    ).add_params(selection)

    # Add the line markings with tooltip support
    line = base.mark_line().encode(
        y=alt.Y('Value:Q', title='')
    )
    # Add the points on the lines for better visibility
    points = base.mark_point(filled=True, size=100).encode(
        y='Value:Q',
    )
    # Layer all the features into one plot with a title
    chart = alt.layer(line, points).properties(
        title=f"Housing Units vs Population Over Time for {title_geo}",
        height=600).configure_title(fontSize=19,offset=45).interactive()

    # Display the plot on the page
    st.altair_chart(chart, use_container_width=True)