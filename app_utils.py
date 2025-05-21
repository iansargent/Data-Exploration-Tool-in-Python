"""
Ian Sargent
ORCA
Streamlit Data Visualization Utility Functions
"""


import streamlit as st
from st_aggrid import AgGrid, ColumnsAutoSizeMode
import pandas as pd
import altair as alt
import numpy as np
import os
import hashlib
from statsmodels.stats.weightstats import DescrStatsW
import calendar



def get_user_files():
    uploaded_files = st.sidebar.file_uploader(
        "Upload your dataset(s)", 
        type=["csv", "xlsx", "xls", "json"], 
        accept_multiple_files=True,
        key = "data_upload"
    )

    if uploaded_files:
        st.session_state["user_files"] = uploaded_files

    # Show uploaded file names
    user_files = st.session_state.get("user_files", [])
    if user_files:
        st.sidebar.markdown("### Uploaded Files:")
        for file in user_files:
            st.sidebar.write(f"📄 {file.name}")

        if st.sidebar.button("🔁 Clear Data Uploads"):
            st.session_state.pop("user_files", None)
            st.rerun()

    return user_files


# Helper to get a unique hash of file content (For duplicate file issues)
def file_hash(file):
    file.seek(0)
    content = file.read()
    file.seek(0)
    return hashlib.md5(content).hexdigest()


def get_file_name(file):
    """
    Get the file name without the extension.
    """
    filename = os.path.splitext(file.name)[0]
    return filename


def get_file_extension(file):
    """
    Extract the file extension of the uploaded file.
    """
    file_extension = os.path.splitext(file.name)[1]
    return file_extension


@st.cache_data
def read_data(file):
    """
    Read the uploaded file and return a DataFrame.
    """
    file_extension = get_file_extension(file)
    
    # Reading the properly formatted file
    if file_extension == '.csv':
        df = pd.read_csv(file)
        
    elif file_extension == '.json':
        df = pd.read_json(file)
                
    elif file_extension == '.sav':
        import pyreadstat as prs
        import tempfile

        with tempfile.NamedTemporaryFile(delete=False, suffix=".sav") as tmp:
            tmp.write(file.read())
            tmp_path = tmp.name

        df, _ = prs.read_sav(tmp_path)
                
    elif file_extension == '.xlsx':
        import openpyxl
        df = pd.read_excel(file, engine='openpyxl')
                
    elif file_extension == '.xls':
        df = pd.read_excel(file, engine='xlrd')
        
    else:
        st.error("Unsupported file format. Please upload a CSV, JSON, SAV, or XLSX file.")

    return df


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


def month_name_to_num(month_name):
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
    for col in df.columns:
        # Convert binary numeric columns with values [0,1] to boolean
        if df[col].dropna().nunique() == 2:
            unique_vals = sorted(df[col].dropna().unique())
            if unique_vals == [0, 1]:
                df[col] = df[col].astype(bool)

        # Handle datetime-like columns based on column name
        col_name = col.lower()
        if any(x in col_name for x in ["datetime", "date", "time"]):
            df[col] = pd.to_datetime(df[col], errors='coerce')

        elif "year" in col_name:
            # Convert year to datetime (Jan 1 of that year)
            df[col] = pd.to_datetime(df[col].astype(str) + "-01-01", errors='coerce')

        elif "month" in col_name:
            # Convert string month to month number
            df[col] = df[col].apply(month_name_to_num)
            # Then to datetime with fixed year
            df[col] = pd.to_datetime(
                "2000-" + df[col].astype(int).astype(str).str.zfill(2) + "-01",
                format="%Y-%m-%d",
                errors='coerce'
            )

    return df


def column_summaries(df, df_columns):
    """
    Display summaries of each column in the DataFrame.
    Each summary includes the column name, data type, and a description of the column.
    """
    total_columns = len(df_columns)
    max_columns = 5
    num_cols = max([n for n in range(1, max_columns + 1) if total_columns % n == 0], default=1)

    # Choose num_cols as a factor of total_columns (e.g., 2, 3, 4, 5, etc.)
    # Make sure there's no remainder
    if total_columns % num_cols != 0:
        # Adjust num_cols so it divides evenly (you can also choose the greatest factor ≤ 5, etc.)
        num_cols = max([n for n in range(1, total_columns + 1) if total_columns % n == 0 and n <= 5])

    # Create a grid of columns for the summaries
    for i in range(0, total_columns, num_cols):
        cols = st.columns(min(num_cols, total_columns - i))
        for j, column_name in enumerate(df_columns[i:i+num_cols]):
            with cols[j]:
                # Table titles (cleaned)
                # st.markdown(f"**{column_name.strip()}**")
                # Pandas summary of the column (describe function)
                summary = df[column_name].describe(include='all')
                # Summary displayed as a table
                summary_df = pd.DataFrame(summary).rename(columns={0: "Value"})
                            
                # Use an expander for each column summary for clean display
                with st.expander(f"**{column_name.strip()}**"):
                    # Turn summary into a st.dataframe for interactive display
                    st.dataframe(summary_df.style.format(precision=2, na_rep="—"))


def single_column_plot(df, selected_column):
    """
    Create a single column plot based on the data type of the selected column.
    The plot type is determined by the data type of the column.
    """
    source = df[[selected_column]].dropna()
    

    column_type = get_column_type(df, selected_column)
    # If the column is categorical (object type)
    if column_type == 'object' or column_type.name == 'category':
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
        
        return bar_chart

    # If the column is numeric
    elif column_type in ['int64', 'float64']:

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
            y=alt.Y('count()', title='Count'),
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

        # Confidence Interval
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
        
        # Create two columns for density plot and confidence interval
        col1, col2 = st.columns(2)
        with col1:
            st.subheader(f"Density Plot")
            st.altair_chart(density, use_container_width=True)
        with col2:
            with st.container():
                st.subheader(f"95% Confidence Interval")
            st.markdown(f"{ci_low:,.1f} to {ci_high:,.1f}")

            st.markdown(
                f"We are 95% confident that the true population ***{selected_column}*** lies between\n "
                f"{ci_low:.1f} and {ci_high:.1f} based on this sample."
            )
        
        # Display the box plot
        st.subheader(f"Box Plot")
        st.altair_chart(boxplot, use_container_width=True)

        return histogram, boxplot, CI, density

    # If the column is datetime
    elif pd.api.types.is_datetime64_any_dtype(column_type):
        # Set plot title
        st.subheader(f"Time Series Plot of {selected_column}")
        # Clean the datetime column
        source[selected_column] = pd.to_datetime(source[selected_column])
        
        # Let user pick the numeric column to plot
        numeric_cols = df.select_dtypes(include=['int', 'float']).columns.tolist()
        numeric_cols = [col for col in numeric_cols if col != selected_column]
        
        if not numeric_cols:
            st.warning("No numeric columns available to plot against time.")
            return
        
        y_column = st.selectbox("Select a column to plot over time:", numeric_cols)

        # Create the LINE CHART
        chart = alt.Chart(df).mark_line().encode(
            x=alt.X(f"{selected_column}:T", title="Time"),
            y=alt.Y(f"{y_column}:Q", title=y_column),
            color = alt.value("dodgerblue"),
        ).properties(
            width=600,
            height=400
        )

        # Create the LOESS line chart with proper data transformation
        time_chart = chart + chart.transform_loess(
            f"{selected_column}", f"{y_column}", bandwidth=0.2
        ).mark_line().encode(color = alt.value("tomato"))
        
        # Display the chart
        st.altair_chart(time_chart, use_container_width=True)
        
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
        ).properties(
            width=400,
            height=400
        )
        # Display the chart
        st.altair_chart(pie_chart, use_container_width=True)
        
        return pie_chart

    # If the column data type is not recognized (int, float, object, datetime, bool)
    else:
        st.write(f"Cannot visualize {selected_column}.")


def numeric_numeric_plots(df, col1, col2):
    """
    Create a scatterplot with regression line and heatmap 
    if two numeric variables are selected.
    """
    source = df[[col1, col2]].dropna()

    # SCATTERPLOT
    scatterplot = alt.Chart(source).mark_square(
        color = "mediumseagreen",
        opacity = 0.7
    ).encode(
        x = alt.X(f"{col1}:Q", title=col1).scale(zero=False),
        y = alt.Y(f"{col2}:Q", title=col2).scale(zero=False),
        tooltip=[f"{col1}:Q", f"{col2}:Q"]
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

    col1_bins_unique = np.unique(col1_bins)
    col2_bins_unique = np.unique(col2_bins)

    col1_intervals = len(col1_bins_unique) - 1
    col2_intervals = len(col2_bins_unique) - 1

    col1_labels = range(1, col1_intervals + 1)
    col2_labels = range(1, col2_intervals + 1)

    df['x_bin'] = pd.cut(
        df[col1], 
        bins=col1_bins_unique, 
        labels=col1_labels, 
        include_lowest=True
    )
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

    # CORRELATION COEFFICIENT
    corr_df = source[[col1, col2]].corr(min_periods=10, numeric_only=True)
    correlation = corr_df.loc[col1, col2]


    return scatterplot, regression_line, heatmap, correlation


def display_numeric_numeric_plots(df, col1, col2, scatterplot, regression_line, heatmap, correlation):
    """
    Display a scatterplot, regression line, heatmap, and correlation coefficient
    if two numeric variables are selected.
    """
    
    source = df[[col1, col2]].dropna()
    
    # Set title for scatterplots
    st.subheader(f"Scatterplot of {col1} and {col2}")
    
    # Formatting plot output with two columns
    column_one, column_two = st.columns(2)
        
    # First, show the scatterplot
    with column_one:
        st.altair_chart(scatterplot, use_container_width=True)
        
    # Next to it, show the regression line on top of the scatterplot
    with column_two:
        st.altair_chart(scatterplot + regression_line, use_container_width=True)
    
    # Below the scatterplots, show the heatmap   
    with st.container():
        st.subheader(f"Heatmap of {col1} and {col2}")
        st.altair_chart(heatmap, use_container_width=True)


    # Below the heatmap, show the correlation coefficient
    with st.container():
        st.subheader(f"Correlation Coefficient")
        # Backround of what a correlation coefficient actually is
        st.markdown(f"""
            ***Note:*** A *correlation coefficient* of 1 indicates a perfect positive relationship, 
            while a coefficient of -1 indicates a perfect negative relationship. A coefficient of 
            0 indicates no relationship."
            """
        )
        # Display the correlation coefficient
        st.markdown(f"**{col1}** and **{col2}** have a correlation coefficient of **{correlation:.2f}**.")

    # Show Aggrid table display of the two plotted columns
    st.subheader(f"Data Table of {col1} and {col2}")
    st.dataframe(data=source.style.format("{:.2f}"), hide_index=True, column_order=(col1, col2))


def numeric_categorical_plots(df, col1, col2):
    """
    Create a boxplot and confidence interval plot 
    if both a numeric and categorical variable are selected.
    """
    source = df[[col1, col2]].dropna()

    col1_type = get_column_type(df, col1)
    col2_type = get_column_type(df, col2)

    # If the first column is numeric and the second is categorical
    if col1_type in ['int64', 'float64']:
        # Set plot title
        st.subheader(f"Boxplot of {col1} by {col2}")
            
        # MULTI BOXPLOT
        multi_box = alt.Chart(source).mark_boxplot().encode(
            x = alt.X(f"{col2}:O", sort='-y', title=col2),
            y = alt.Y(f"{col1}:Q", title=col1),
            color = alt.Color(f"{col2}:O", title=col2),
            tooltip=[f"{col2}:O", f"{col1}:Q"]
        )

        # CONFIDENCE INTERVALS WITH MEANS
        error_bars = alt.Chart(source).mark_errorbar(extent='ci').encode(
            alt.X(f"{col1}").scale(zero=False),
            alt.Y(f"{col2}", sort='-x', title=col2)
        )

        # Calculate the mean of col1 for each category in col2
        observed_points = alt.Chart(source).mark_point().encode(
            x = alt.X('mean(col1)'),
            y = alt.Y(f"{col2}", sort='-x', title=col2)

        )

        # Combine the error bars and observed points into one plot
        confint_plot = error_bars + observed_points

        # Return both plots
        return multi_box, confint_plot

    # If the first column is categorical and the second is numeric
    else:
        # MULTI BOXPLOT
        multi_box = alt.Chart(source).mark_boxplot().encode(
            x = alt.X(f"{col1}:O", sort='-y', title=col1),
            y = alt.Y(f"{col2}:Q", title=col2),
            color = alt.Color(f"{col1}:O", title=col1),
            tooltip=[f"{col1}:O", f"{col2}:Q"]
        )

        # CONFIDENCE INTERVALS WITH MEANS
        error_bars = alt.Chart(source).mark_errorbar(extent='ci').encode(
            alt.X(f"{col2}").scale(zero=False),
            alt.Y(f"{col1}:O", sort='-x', title=col1)
        )

        # Calculate the mean of col2 for each category in col1
        observed_points = alt.Chart(source).mark_point().encode(
            x = alt.X('mean(col2)'),
            y = alt.Y(f"{col1}:O", sort='-x', title=col1)

        )
        
        # Combine the error bars and observed points into one plot
        confint_plot = error_bars + observed_points
        
        # Return both plots
        return multi_box, confint_plot


def display_numeric_categorical_plots(df, col1, col2, multi_box, confint_plot):
    """
    Display the boxplot and confidence interval plot 
    if both a numeric and categorical variable are selected.
    """
    
    # Display the boxplot
    st.subheader(f"Distribution of {col2} by {col1}")
    st.altair_chart(multi_box, use_container_width=True)
    
    # Display the confidence interval plot
    st.subheader(f"95% Confidence Interval of {col2} by {col1}")
    st.altair_chart(confint_plot, use_container_width=True)


def categorical_categorical_plots(df, col1, col2):
    """
    Create a crosstab with raw counts and percentages for two categorical variables 
    if two categorical variables are selected.
    """
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
    stacked_bar1 = alt.Chart(source).mark_bar().encode(
        y=alt.Y(f"{col1}:O", title=col1),
        x=alt.X('count():Q', title='Count'),
        color=alt.Color(f"{col2}:O", title=col2),
        tooltip=[f"{col1}:O", f"{col2}:O", 'count():Q']
    )
    
    stacked_df = freq_table.melt(id_vars=col1, var_name='Category', value_name='Percentage')

    # Altair 100% horizontal stacked bar chart
    stacked_bar_100_pct = alt.Chart(stacked_df).mark_bar().encode(
        y=alt.Y(f'{col1}:O', title=None),
        x=alt.X('Percentage:Q', stack='normalize', title=f'{col2} Distribution'),
        color=alt.Color('Category:N'),
        tooltip=[alt.Tooltip(col1), alt.Tooltip('Category'), alt.Tooltip('Percentage:Q')]
    )

    # Return all tables and plots
    return freq_table, format_dict, heatmap, stacked_bar1, stacked_bar_100_pct


def display_categorical_categorical_plots(df, col1, col2, freq_table, format_dict, heatmap, stacked_bar1, stacked_bar_100_pct):
    """
    Display the crosstab, heatmap, and stacked bar charts 
    if two categorical variables are selected.
    """
    
    # Set two columns for formatted output
    column1, column2 = st.columns(2)

    with column1:
        # Display the frequency table
        st.subheader(f"Frequency Table of {col1} and {col2}")
        st.dataframe(freq_table.style.format(format_dict, na_rep="—"), hide_index=True)
    
    with column2:
        # The the unique values of the two columns are reasonable for plotting
        if ((df[col1].nunique() > 2 and df[col2].nunique() > 2) and 
        (df[col1].nunique() <= 12 and df[col2].nunique() <= 12)):
            # Display the heatmap
            st.subheader(f"Heatmap of {col1} and {col2}")
            st.altair_chart(heatmap, use_container_width=True)

    # Display the stacked bar charts
    column3, column4 = st.columns(2)
    
    with column3:
        # Display the stacked bar chart
        st.subheader(f"Stacked Bar Chart of {col2} by {col1}")
        st.altair_chart(stacked_bar1, use_container_width=True)
    
    with column4:
        # Display the 100% stacked bar chart next to the other chart
        st.subheader(f"100% Stacked Bar Chart of {col1} by {col2}")
        st.altair_chart(stacked_bar_100_pct, use_container_width=True)


def two_column_plot(df, col1, col2):
    """
    Create a series of two-variable plots based on the data types of each selected column.
    """
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
        scatterplot, regression_line, heatmap, correlation = numeric_numeric_plots(df, col1, col2)
        # Display all plots
        display_numeric_numeric_plots(df, col1, col2, scatterplot, regression_line, heatmap, correlation)
        # Return all plots
        return scatterplot, regression_line, heatmap, correlation


    # If NUMERIC and CATEGORICAL variables are selected
    elif ((col1_type in ['int64', 'float64'] and (col2_type == 'object' or col2_type.name == 'category')) 
    or ((col1_type == 'object' or col1_type.name == 'category') and col2_type in ['int64', 'float64'])):

        # Create the boxplot and confidence interval plots
        multi_box, confint_plot = numeric_categorical_plots(df, col1, col2)
        # Display the plots
        display_numeric_categorical_plots(df, col1, col2, multi_box, confint_plot)
        # Return the plots
        return multi_box, confint_plot
        

    # If two CATEGORICAL variables are selected
    elif ((col1_type in ['object', 'bool'] or col1_type.name == 'category') and 
      (col2_type in ['object', 'bool'] or col2_type.name == 'category')):
        
        # Create the crosstab and heatmap
        freq_table, format_dict, heatmap, stacked_bar1, stacked_bar_100_pct = categorical_categorical_plots(df, col1, col2)
        # Display the plots
        display_categorical_categorical_plots(df, col1, col2, freq_table=freq_table, format_dict=format_dict, 
                                               heatmap=heatmap, stacked_bar1=stacked_bar1, 
                                               stacked_bar_100_pct=stacked_bar_100_pct)
        # Return the plots
        return freq_table, format_dict, heatmap, stacked_bar1, stacked_bar_100_pct

    # If combination of datatypes are not recognized
    else:
        st.write(f"Cannot visualize {col1} and {col2} together YET")
        return None