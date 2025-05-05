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


def get_file_name(file):
    filename = os.path.splitext(file.name)[0]
    return filename

def get_file_extension(file):
    file_extension = os.path.splitext(file.name)[1]
    return file_extension


def read_data(file):

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
    

def get_file_name(file):
    filename = os.path.splitext(file.name)[0]
    return filename


def get_columns(df):
    columns = df.columns.tolist()
    return columns

def clean_column_types(df):
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

    return df



def column_summaries(df, df_columns):
    # Three tables per row
    num_cols = 5

    for i in range(0, len(df_columns), num_cols):
        cols = st.columns(num_cols)
        for j, column_name in enumerate(df_columns[i:i+num_cols]):
            with cols[j]:
                # Table titles (cleaned)
                # st.markdown(f"**{column_name.strip()}**")
                # Pandas summary of the column (describe function)
                summary = df[column_name].describe(include='all')
                # Summary displayed as a table
                summary_df = pd.DataFrame(summary).rename(columns={0: "Value"})
                            
                # Use an expander for each column summary for clean display
                with st.expander(f"Summary of {column_name.strip()}"):
                    # Turn summary into a st.dataframe for interactive display
                    st.dataframe(summary_df.style.format(precision=2, na_rep="—"))


def single_column_plot(df, selected_column, column_type):
    source = df[[selected_column]].dropna()
    # If the column is categorical (object type)
    if column_type == 'object' or column_type.name == 'category':
        # Set plot title
        st.subheader(f"Bar Chart of {selected_column}")
        # Create a sorted bar chart using Altair (descending)
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

    # If the column is numerical
    elif column_type in ['int64', 'float64']:
        # Set plot title
        st.subheader(f"Histogram of {selected_column}")
        # Create a histogram using Altair
        chart = alt.Chart(source).mark_bar().encode(
            x=alt.X(f"{selected_column}:Q", bin=alt.Bin(), title=selected_column),
            y=alt.Y('count()', title ='Count'),
            tooltip=[alt.Tooltip('count()', title='Count')]
        ).configure_mark(
            color = "mediumseagreen"
        ).properties(
            width=600,
            height=400
        )
        # Add a slider to change the number of bins
        bin_slider = st.slider(
            "Select the Level of Detail", 
            min_value=2, 
            # Set maximum value to half the number of unique values--cap at 100
            max_value=min(len(np.unique(source)) // 2, 100), 
            value=30,
            help="Controls how many bars appear in the histogram. Higher = more detail."
        )
        chart = chart.encode(
            x=alt.X(f"{selected_column}:Q", bin=alt.Bin(maxbins=bin_slider), title=selected_column)
        )
        # Disply the chart
        st.altair_chart(chart, use_container_width=True)
        
        return chart

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

        # Create the line chart
        chart = alt.Chart(df).mark_line().encode(
            x=alt.X(f"{selected_column}:T", title="Time"),
            y=alt.Y(f"{y_column}:Q", title=y_column)
        ).properties(
            width=600,
            height=400
        )

        # Create the LOESS line chart with proper data transformation
        time_chart = chart + chart.transform_loess(
            f"{selected_column}", f"{y_column}", bandwidth=0.2
        ).mark_line()
        
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
            tooltip=['Count']
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


def main():
    # Set page width to wide
    st.set_page_config(page_title = "Vermont Livability Data Visualization App", layout="wide")

    # Header and body describing the app
    st.title("Vermont Livability Data Visualization")
    st.write("#### Give it a dataset and we will visualize it for you!")
   
    # Get user's dataset
    user_files = st.file_uploader("**Upload your CSV file below**", type=["csv", "json", "sav", "xlsx"], accept_multiple_files=True)
    
    unique_key = 0
    
    if user_files:
        try:
            for file in user_files:
                # Read each data file
                df = read_data(file)
                filename = get_file_name(file)

                unique_key += 1
                st.markdown("---")
                st.write(f"## {filename.upper()} Summary")
                # Clean the column types
                df = clean_column_types(df)
                    
                # Define the columns as a list
                df_columns = df.columns.tolist()

                # Display a preview of the dataframe
                with st.expander(f"Table Snapshot"):
                    st.dataframe(df.head(11))            

                # Calculate and display column summaries
                st.subheader(f"Column Summaries")
                column_summaries(df, df_columns)

                # Plots for each column (singular)
                st.subheader(f"Single Variable Plots")
                # User selects a column to visualize
                selected_column = st.selectbox("**Select a column to visualize**", df.columns.tolist(), key=unique_key)  
                    
                # Get the data type of the selected column for a customized plot 
                column_type = df[selected_column].dtype
                    
                # Single variable plot
                single_column_plot(df, selected_column, column_type)

                # Save to a temporary PNG file
                st.subheader("Next Section")
                    
        except Exception as e:  
            st.error("An error occurred while processing your file:", icon="🚨")
            st.write(e)


if __name__ == "__main__":
    main()

    # Testing
