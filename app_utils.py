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
import leafmap as lfm


#--------------------------------------#
#######      File Handling      ########
#--------------------------------------#

def get_user_files(key="main"):
    # Define a file uploader object accepting various file types
    uploaded_files = st.sidebar.file_uploader(
        label="Upload Data Files Here", 
        type=["geojson", "fgb", "csv", "xlsx", 'xls', 'json', 'sav'],
        accept_multiple_files=True,
        key = f"data_upload_{key}",
        label_visibility="hidden"
    )

    # If the user uploads a file
    if uploaded_files:
        # Add it the to session state
        st.session_state["user_files"] = uploaded_files

    # Keep track of the uploaded file names in the sidebar
    user_files = st.session_state.get("user_files", [])
    if user_files:
        st.sidebar.markdown("### Uploaded Files:")
        for file in user_files:
            st.sidebar.write(f"📄 {file.name}")

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
    """
    # Create an empty set of seen hash codes
    seen_hashes = set()
    # Define an empty list to store processed files
    processed = []

    # If the user has not uploaded any files
    if not user_files:
        st.warning("No files uploaded.")
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
                lat_col = [col for col in df.columns if "latitude" in col.lower()][0]
                lon_col = [col for col in df.columns if "longitude" in col.lower()][0]

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
    Generate a unique hash for the file content to check for duplicates.
    """
    file.seek(0)
    content = file.read()
    file.seek(0)
    
    return hashlib.md5(content).hexdigest()


def get_file_name(file):
    """
    Get the file name without the extension.
    """
    filename = os.path.splitext(file.name)[0].lower()
    
    return filename


def get_file_extension(file):
    """
    Extract the file extension of the uploaded file.
    """
    file_extension = os.path.splitext(file.name)[1]
    
    return file_extension


#--------------------------------------#
# Reading, Handling, and Cleaning Data #
#--------------------------------------#


@st.cache_data
def read_data(file):
    """
    Read the uploaded file and return a DataFrame or GeoDataFrame.
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
    """
    columns = df.columns.tolist()
    
    return columns


def get_column_type(df, column_name):
    """
    Get the data type of a specific column in the DataFrame.
    """
    column_type = df[column_name].dtype
    
    return column_type


def is_latitude_longitude(df):
    """
    Check if the DataFrame contains latitude and longitude columns.
    """
    # Get the column names from the DataFrame
    df_columns = [col.strip().lower() for col in get_columns(df)]

    # Define both the latitude and longitude columns
    lat_col = [col for col in df_columns if "latitude" in col.lower()]
    lon_col = [col for col in df_columns if "longitude" in col.lower()]

    # If both columns are found, return True
    if lat_col and lon_col:
        return True
    # If one or no columns are found, return false
    else:
        return False


def month_name_to_num(month_name):
    """
    Convert string-type month names into corresponding integers
    to make it easier to convert into datetime-type columns.
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
    """
    # Replace "." name spacers with "_"
    df.columns = df.columns.str.replace('.', '_', regex=False)
    # Replace empty values with NA
    df = df.replace(r'^\s*$', pd.NA, regex=True)

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
            if vals == {"yes", "no"} or vals == {"0", "1"} or vals == {0, 1} or vals == {"y", "n"}:
                df[col] = df[col].astype(bool)
        
        if isinstance(df, gpd.GeoDataFrame):
            convert_all_timestamps_to_str(df)
    
    # Return the cleaned dataframe
    return df


def convert_all_timestamps_to_str(gdf):
    """
    Converts all timestamp columns in a GeoDataFrame 
    into strings for mapping purposes.
    """
    # Convert all datetime columns to strings
    for col, dtype in gdf.dtypes.items():
        if "datetime" in str(dtype):
            gdf[col] = gdf[col].astype(str)
    
    # Return the GeoDataFrame
    return gdf


#--------------------------------------#
###   Exploring and Analyzing Data   ###
#--------------------------------------#

def get_dimensions(df):
    # Find the number of columns
    num_columns = len(get_columns(df))
    # Find the number of rows
    num_rows = len(df)

    # Return the dimensions as a tuple
    return num_columns, num_rows


def data_snapshot(df, filename):
    """
    Reports the overall structure of the dataset, including
    dimensions and the dataframe type.
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


def column_summaries(df, df_columns, filename):
    """
    Display summaries of each column in the DataFrame.
    Each summary includes the column name, data type, and a description of the column.
    """
    total_columns = len(df_columns)
    max_columns = 5

    # Set number of columns per row
    if total_columns > 30:
        return
    else:
        num_cols = max(
            [n for n in range(1, max_columns + 1) if total_columns % n == 0],
            default=1
        )
        if total_columns % num_cols != 0:
            num_cols = max(
                [n for n in range(1, total_columns + 1) if total_columns % n == 0 and n <= max_columns],
                default=1
            )
    
    st.subheader(f"Column Summaries for {filename}")
    # Render summaries
    for i in range(0, total_columns, num_cols):
        cols = st.columns(min(num_cols, total_columns - i))
        for j, column_name in enumerate(df_columns[i:i + num_cols]):
            with cols[j]:
                summary = df[column_name].describe(include='all')
                summary_df = pd.DataFrame(summary).rename(columns={0: "Value"})

                with st.expander(f"**{column_name.strip()}**"):
                    st.dataframe(summary_df.style.format(precision=2, na_rep="—"))


def generate_exploratory_report(df):
    """
    Generate a tailored exploratory profile report 
    given a DataFrame using the ydata-profiling package.
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
            minimal=True,
            correlations=None,
            interactions=None,
            samples=None
        )
    # If there are less than 30 columns
    else:
        report = ProfileReport(
            df,
            title="Exploratory Report",
            explorative=True
        )
    
    # Return the ydata-profiling report
    return report


def generate_quality_report(df):
    """
    Generate a tailored data quality profile report 
    given a DataFrame using the ydata-profiling package.
    """
    report = ProfileReport(
            df,
            title="Data Quality",
            minimal=True,
            correlations=None,
            interactions=None,
            samples=None
        )

    return report

def generate_comparison_report(dfs):
    """
    Generates a comparison report given a list of 
    uploaded dataframes
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
    # Obtain merged statistics
    # statistics = comparison_report.get_description()

    return comparison_report


#--------------------------------------#
###   Plotting and Displaying Data   ###
#--------------------------------------#

def single_column_plot(df, selected_column):
    """
    Create a single column plot based on the data type of the selected column.
    The plot type is determined by the data type of the column.
    """
    # Define the plotting source as the one selected column without missing values
    source = df[[selected_column]].dropna()
    # Get the column type
    column_type = get_column_type(df, selected_column)
    
    # If the column is categorical (object type)
    if column_type == 'object':
        # Set plot title
        st.subheader(f"Bar Chart of {selected_column}")
        # Create a sorted BAR CHART using Altair (descending)
        bar_chart = alt.Chart(source).mark_bar().encode(
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

        # Slider for number of bins in the histogram
        bin_slider = st.slider(
            "Select the Level of Detail", 
            min_value=2, 
            max_value=min(len(np.unique(source[selected_column])) // 2, 100), 
            value=30,
            help="Controls how many bars appear in the histogram. Higher = more detail.",
            key=f"bin_slider_{selected_column}"
        )

        # Histogram
        histogram = alt.Chart(source).mark_bar().encode(
            x=alt.X(f"{selected_column}:Q", bin=alt.Bin(maxbins=bin_slider), title=selected_column),
            y=alt.Y('count():Q', title='Count'),
            tooltip=[alt.Tooltip('count()', title='Count')]
        ).properties(
            width=400,
            height=300
        )

        # Density Plot
        density = alt.Chart(source).transform_density(
            f"{selected_column}",
            as_=[f"{selected_column}", "density"],
            extent=[source[selected_column].min(), source[selected_column].max()]
        ).mark_area(color='tomato').encode(
            x=alt.X(f"{selected_column}:Q", title=selected_column),
            y=alt.Y('density:Q', title='Density')
        )

        # Define the 95% confidence interval bounds
        d = DescrStatsW(source[selected_column])
        ci_low, ci_high = d.tconfint_mean()
        CI = (ci_low, ci_high)

        # Boxplot
        boxplot = alt.Chart(source).mark_boxplot(color='dodgerblue').encode(
            x=alt.X(f"{selected_column}:Q", title=selected_column)
        ).configure_mark(
            color="mediumseagreen"
        ).configure_boxplot(
            size=160
        ).properties(
            width=400,
            height=300
        )

        # Display the histogram
        st.altair_chart(histogram, use_container_width=True)
        
        # Create two columns for formattinf the density plot and confidence interval
        col1, col2 = st.columns(2)
        
        # On the left
        with col1:
            # Display the density plot
            st.subheader(f"Density Plot")
            st.altair_chart(density, use_container_width=True)
        # On the right
        with col2:
            # Display the confidence interval
            with st.container():
                st.subheader(f"95% Confidence Interval")
            st.markdown(f"{ci_low:,.1f} to {ci_high:,.1f}")

            st.markdown(
                f"We are 95% confident that the true population ***{selected_column}*** lies between\n "
                f"{ci_low:.1f} and {ci_high:.1f} based on this sample."
            )
        
        # Display the box plot below
        st.subheader(f"Box Plot")
        st.altair_chart(boxplot, use_container_width=True)

        # Return the plots and confidence interval
        return histogram, boxplot, CI, density

    # If the column is datetime
    elif pd.api.types.is_datetime64_any_dtype(df[selected_column]):
        # Set plot title
        st.subheader(f"Time Series Plot of {selected_column}")
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
        chart = alt.Chart(df).mark_line().encode(
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
        # Set plot title
        st.subheader(f"Pie Chart of {selected_column}")
        # Create a pie chart using Altair
        pie_chart = alt.Chart(source).mark_arc().encode(
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
    """

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
    scatterplot = alt.Chart(source).mark_square(
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
        color=alt.value("tomato"),
        size=alt.value(1.5)
    )

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
    heatmap = alt.Chart(df).mark_rect().encode(
        x=alt.X('x_bin:O', sort=[str(c) for c in x_order], title=col1),
        y=alt.Y('y_bin:O', sort=[str(c) for c in reversed(y_order)], title=col2),
        color=alt.Color('count():Q', scale=alt.Scale(scheme='blueorange')),
        tooltip=['count():Q']
    ).properties(
        width=500,
        height=400
    ).configure_view(
        strokeWidth=0
    )

    # Return all computed metrics and plots
    return scatterplot, regression_line, heatmap


def regression_metric_cards(df, col1, col2):
    """
    Calculates and displays regression metrics to a page. Metrics include
    sample size, correlation, R-squared, model strength, MAE, and p-value 
    (F statistic)
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
    F_stat, p = f_regression(X, y)
    p_value = round(p[0], 4)
    # If the rounded p-value is still zero, display it as less than 0.0001
    display_value = f"{p_value:.4f}" if p_value > 0 else "p < 0.0001"

    # Set up formatting columns for display (2 rows of 3)
    column3, column4, column5 = st.columns(3)
    column6, column7, column8 = st.columns(3)
    
    # Use metric cards to display each metric
    column3.metric(label="**Sample Size (N)**", value = f"{sample_size}")
    column4.metric(label="**Correlation (R)**", value=f"{correlation:.2f}")
    column5.metric(label="**Model Strength**", value = f"{model_str}")    
    column6.metric(label="**R-Squared**", value = f"{r_squared * 100:.0f}%")    
    column7.metric(label="**Mean Absolute Error**", value = f"{mae:.2f}")
    column8.metric(label="**Model Significance**", value = display_value)

    # Metric card customizations
    style_metric_cards(
        background_color="whitesmoke",
        border_left_color="mediumseagreen",
        box_shadow=True,
        border_size_px=0.5
    )


def display_numeric_numeric_plots(df, col1, col2, scatterplot, regression_line, heatmap):
    """
    Display a scatterplot, regression line, heatmap, and correlation coefficient
    if two numeric variables are selected.
    """  

    # Define the plotting source
    source = df[[col1, col2]].dropna()
    
    # Set title for scatterplots
    st.subheader(f"Scatterplot of {col1} and {col2}")
    # Formatting plot output with two columns
    column1, column2 = st.columns(2)  
    # First, show the scatterplot
    with column1:
        st.altair_chart(scatterplot, use_container_width=True)  
    # Next to it, show the regression line on top of the scatterplot
    with column2:
        st.altair_chart(scatterplot + regression_line, use_container_width=True)

    regression_metric_cards(df, col1, col2)
    
    # Below the regression metrics, display the table and the heatmap
    with st.container():
        st.subheader(f"Heatmap and Table: {col1} vs {col2}")
        # Define the space ratio for the table and heatmap
        col_table, col_heatmap = st.columns([1, 3])

        # Display the table
        with col_table:
            st.dataframe(
                data=source.style.format("{:.2f}"),
                hide_index=True,
                column_order=(col1, col2),
                use_container_width=True
            )
        # Display the heatmap
        with col_heatmap:
            st.altair_chart(heatmap, use_container_width=True)



def numeric_categorical_plots(df, col1, col2):
    """
    Create a boxplot and confidence interval plot 
    if both a numeric and categorical variable are selected.
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
        multi_box = alt.Chart(source).mark_boxplot(size=40).encode(
            x = alt.X(f"{col2}:N", sort='-y', title=col2),
            y = alt.Y(f"{col1}:Q", title=col1),
            color = alt.Color(f"{col2}:N", title=col2, legend=None, scale=alt.Scale(scheme='category20')),
            tooltip=[f"{col2}:N", f"{col1}:Q"]
        )

        # CONFIDENCE INTERVALS WITH MEANS
        error_bars = alt.Chart(source).mark_errorbar(extent='ci').encode(
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
        multi_box = alt.Chart(source).mark_boxplot(size=40).encode(
            x = alt.X(f"{col1}:N", sort='-y', title=col1),
            y = alt.Y(f"{col2}:Q", title=col2),
            color = alt.Color(f"{col1}:N", title=col1, legend=None, scale=alt.Scale(scheme='category20')),
            tooltip=[f"{col1}:N", f"{col2}:Q"]
        )

        # CONFIDENCE INTERVALS WITH MEANS
        error_bars = alt.Chart(source).mark_errorbar(extent='ci').encode(
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
    """
    
    # Display the boxplot
    st.subheader(f"Distribution of {numeric_col} by {non_numeric_col}")
    st.altair_chart(multi_box, use_container_width=True)
    
    # Display the confidence interval plot
    st.subheader(f"95% Confidence Interval of {numeric_col} by {non_numeric_col}")
    st.altair_chart(confint_plot, use_container_width=True)


def categorical_categorical_plots(df, col1, col2):
    """
    Create a crosstab with raw counts and percentages for two categorical variables 
    if two categorical variables are selected.
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
    heatmap = alt.Chart(source).mark_rect().encode(
        x=f'{col2}:O',
        y=f'{col1}:O',
        color=alt.Color('count():Q', scale=alt.Scale(scheme='blueorange')),
        tooltip=[f'{col1}:O', f'{col2}:O', 'count():Q']
    )
        
    # STACKED BAR CHARTS
    stacked_bar = alt.Chart(source).mark_bar().encode(
        y=alt.Y(f"{col1}:N", title=col1),
        x=alt.X('count():Q', title='Count'),
        color=alt.Color(f"{col2}:N", title=col2),
        tooltip=[f"{col1}:O", f"{col2}:O", 'count():Q']
    )
    
    # Putting the frequecy table into a long format for plotting in the 100% stacked bar chart
    stacked_df_100 = freq_table.melt(id_vars=col1, var_name='Category', value_name='Percentage')

    # Altair 100% horizontal stacked bar chart
    stacked_bar_100_pct = alt.Chart(stacked_df_100).mark_bar().encode(
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
            st.subheader(f"Heatmap of {col1} and {col2}")
            st.altair_chart(heatmap, use_container_width=True)
    
    # If the number of unique values is NOT reasonable for plotting
    else:
        # Just display the frequency table
        st.subheader(f"Frequency Table of {col1} and {col2}")
        st.dataframe(freq_table.style.format(format_dict, na_rep="—"), hide_index=True)

    # Display the stacked bar chart
    st.subheader(f"Stacked Bar Chart of {col2} by {col1}")
    st.altair_chart(stacked_bar, use_container_width=True)
    
    # Display the 100% stacked bar chart next to the other chart
    st.subheader(f"100% Stacked Bar Chart of {col1} by {col2}")
    st.altair_chart(stacked_bar_100_pct, use_container_width=True)


def two_column_plot(df, col1, col2):
    """
    Create a series of two-variable plots based on the data types of each selected column.
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
        scatterplot, regression_line, heatmap = numeric_numeric_plots(df, col1, col2)
        # Display all plots
        display_numeric_numeric_plots(df, col1, col2, scatterplot, regression_line, heatmap)
        # Return all plots
        return scatterplot, regression_line, heatmap


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
    
    # Create a new simple DataFrame with the two columns of interest
    df_simple = df[[grp_by, num_var]]

    # Group by the "grp_by" variable using the SELECTED OPERATION
    if num_op == "Total":
        df_grouped = df_simple.groupby(by = [grp_by]).sum()
        prefix = "total_"
    elif num_op == "Average":
        df_grouped = df_simple.groupby(by = [grp_by]).mean()
        prefix = "avg_"
    elif num_op == "Median":
        df_grouped = df_simple.groupby(by = [grp_by]).median()
        prefix = "median_"
    elif num_op == "Count":
        df_grouped = df_simple.groupby(by = [grp_by]).count()
        prefix = "count of"
    elif num_op == "Unique Count":
        df_grouped = df_simple.groupby(by = [grp_by]).nunique()
        prefix = "unique count of"
    elif num_op == "Standard Deviation":
        df_grouped = df_simple.groupby(by = [grp_by]).std()
        prefix = "std_dev_"

    # Reset the DataFrame index for plotting
    df_grouped = df_grouped.reset_index()
    
    # Rename the existing column to reflect the applied operation
    num_var_name = f"{prefix}{num_var}"
    df_grouped.rename(columns={num_var: num_var_name}, inplace=True)

    # Use a select box to sort the plot (Defualt, Ascending, or Descending)
    sort_option = st.selectbox(
        label = "",
        options=["Defualt", "Ascending", "Descending"],
        index=0,
        label_visibility="hidden"
    )
    
    # Change the sort variable based on the sorting selection
    if sort_option == "Ascending":
        sort = 'y'
    elif sort_option == "Descending":
        sort = '-y' 
    else:
        sort = list(df_grouped[grp_by])
    
    # BAR CHART
    grouped_chart = alt.Chart(df_grouped).mark_bar().encode(
        x=alt.X(f'{grp_by}:N', sort=sort),
        y=alt.Y(f'{num_var_name}:Q')
    )

    # Display the plot
    st.subheader("Plot")
    st.altair_chart(grouped_chart, use_container_width=True)

    # Display the summarized table
    st.subheader("Table")
    st.dataframe(df_grouped)

    # Return the aggregated DataFrame and the corresponsing bar chart
    return df_grouped, grouped_chart

