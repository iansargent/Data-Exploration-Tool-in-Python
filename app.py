"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Run this in the terminal to launch the app:
-------------------------------------------
streamlit run app.py

"""


# Necessary Packages
import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import os



def get_user_files():
    """
    Get the user's uploaded files. Returns a list of files.
    """
    user_files = st.sidebar.file_uploader(
        "**Upload your CSV file below**", 
        type=["csv", "json", "sav", "xlsx"], 
        accept_multiple_files=True
    )
    return user_files


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
    Get the columns of the DataFrame as a list.
    """
    columns = df.columns.tolist()
    return columns


def get_column_type(df, column_name):
    """
    Get the data type of a specific column in the DataFrame.
    """
    column_type = df[column_name].dtype
    return column_type


def clean_column_types(df):
    """
    Clean the column types of the DataFrame.
    Convert binary numeric columns to true/false and parse datetime columns.
    """
    for col in df.columns:
        # Binary numeric to boolean
        if df[col].dropna().nunique() == 2:
            unique_vals = sorted(df[col].dropna().unique())
            if unique_vals == [0, 1]:
                df[col] = df[col].astype(bool)

        # Handle datetime-like columns based on column name
        col_lower = col.lower()
        if "datetime" in col_lower:
            df[col] = pd.to_datetime(df[col], errors='coerce')
        elif "date" in col_lower:
            df[col] = pd.to_datetime(df[col], errors='coerce')
        elif "time" in col_lower:
            df[col] = pd.to_datetime(df[col], errors='coerce')
        elif "year" in col_lower:
            df[col] = pd.to_datetime(df[col], format='%Y', errors='coerce')
        elif "month" in col_lower:
            df[col] = pd.to_datetime(df[col], format='%m', errors='coerce')
            
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


def single_column_plot(df, selected_column, column_type):
    """
    Create a single column plot based on the data type of the selected column.
    The plot type is determined by the data type of the column.
    """
    source = df[[selected_column]].dropna()
    
    # If the column is categorical (object type)
    if column_type == 'object' or column_type.name == 'category':
        # Set plot title
        st.subheader(f"Bar Chart of {selected_column}")
        # Create a sorted BAR CHART using Altair (descending)
        chart = alt.Chart(source).mark_bar().encode(
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
        st.altair_chart(chart, use_container_width=True)
        
        return chart

    # If the column is numeric
    elif column_type in ['int64', 'float64']:
        st.subheader(f"Histogram and Boxplot of {selected_column}")

        # Slider for bins
        bin_slider = st.slider(
            "Select the Level of Detail", 
            min_value=2, 
            max_value=min(len(np.unique(source[selected_column])) // 2, 100), 
            value=30,
            help="Controls how many bars appear in the histogram. Higher = more detail."
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

        # Boxplot
        boxplot = alt.Chart(source).mark_boxplot(color='dodgerblue').encode(
            x=alt.X(f"{selected_column}:Q", title=selected_column)
        ).configure_mark(
            color="dodgerblue"
        ).configure_boxplot(
            size=160
        ).properties(
            width=400,
            height=300
        )

        # Display the two charts
        st.altair_chart(histogram, use_container_width=True)
        st.altair_chart(boxplot, use_container_width=True)

        return histogram, boxplot

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
        
        y_column = st.selectbox("Select a column to plot against time:", numeric_cols)

        # Create the LINE CHART
        chart = alt.Chart(df).mark_line().encode(
            x=alt.X(f"{selected_column}:T", title="Time"),
            y=alt.Y(f"{y_column}:Q", title=y_column),
            color = alt.value("steelblue"),
        ).properties(
            width=600,
            height=400
        )

        # Create the LOESS line chart with proper data transformation
        time_chart = chart + chart.transform_loess(
            f"{selected_column}", f"{y_column}", bandwidth=0.2
        ).mark_line().encode(color = alt.value("tomato"))
        
        # Disply the chart
        st.altair_chart(time_chart, use_container_width=True)
        
        return time_chart

    # If the column is boolean
    elif column_type == 'bool':
        # Set plot title
        st.subheader(f"Pie Chart of {selected_column}")
        # Create a pie chart using Altair
        chart = alt.Chart(source).mark_arc().encode(
            theta='count()',
            color=alt.Color(f"{selected_column}:N"),
            tooltip=[alt.Tooltip(f"{selected_column}:N", title="Category"),
                     alt.Tooltip(f"count()", title="Count")]
        ).properties(
            width=400,
            height=400
        )
        # Display the chart
        st.altair_chart(chart, use_container_width=True)
        
        return chart

    # If the column data type is not recognized (int, float, object, datetime, bool)
    else:
        st.write(f"Cannot visualize {selected_column}.")


#####################################################################################
##########################        THE MAIN FUNCTION        ##########################
#####################################################################################

def main():
    """
    Main function to run the Streamlit app.
    """
    # Set page width to wide and page title
    st.set_page_config(page_title = "Vermont Livability Data Visualization App", layout="wide")

    # Header and body describing the app
    st.title("Vermont Livability Data Visualization")
    st.write("#### Give it a dataset and we will visualize it for you!")
   
    # Get the user's dataset(s)
    user_files = get_user_files()
    
    # Define a unique key number for each plot to avoid duplicate conflicts
    unique_key = 0
    
    # If the user has uploaded at least one file
    if user_files:
        # Attempt to read the files
        try:
            # Iterate through each uploaded file
            for file in user_files:
                # Increment the unique plot key number
                unique_key += 1
                # Read each data file
                with st.spinner(f"Loading {file.name}..."):
                    df = read_data(file)
                st.success("Data loaded successfully!")
                
                # Clean the column types
                df = clean_column_types(df)
                # Define the columns as a list
                df_columns = get_columns(df)
                # Extract the file name without the extension
                filename = get_file_name(file)

                # File section header 
                st.markdown("---")
                st.write(f"## {filename.upper()} Summary")
                
                # Display a table preview of the dataframe
                with st.expander(f"Table Snapshot"):
                    st.dataframe(df.head(11))            

                # Calculate and display column summaries
                st.subheader(f"Column Summaries")
                column_summaries(df, df_columns)

                # Single plots section
                st.subheader(f"Single Variable Plots")
                # User selects a column to visualize
                selected_column = st.selectbox("**Select a column to visualize**", df_columns, key=unique_key)  
                    
                # Find the data type of the selected column for the correct plot 
                column_type = get_column_type(df, selected_column)
                
                # Single variable plot
                single_column_plot(df, selected_column, column_type)

                # Two-variable plots section
                st.subheader(f"Two Variable Plots")
                    
        except Exception as e:  
            st.error("An error occurred while processing your file:", icon="🚨")
            st.write(e)


if __name__ == "__main__":
    main()
