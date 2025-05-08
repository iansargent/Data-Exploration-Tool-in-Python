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
from st_aggrid import AgGrid
import pandas as pd
import altair as alt
import numpy as np
import os
import hashlib
from utils import (get_user_files, file_hash, get_file_name, 
                  get_file_extension, read_data, get_columns, 
                  get_column_type, clean_column_types, column_summaries, 
                  single_column_plot)
    

def main():
    """
    Main function to run the Streamlit app.
    """
    # Set page width to wide and page title
    st.set_page_config(page_title = "Vermont Livability Data Visualization App", 
                       layout="wide",
                       page_icon="🍁",
                       menu_items={
                           "GitHub Repositorty": "https://github.com/iansargent/Data-Exploration-Tool-in-Python",
                           "About": "Write the about text here!!!"
                       })

    # Header and body describing the app
    st.title("Vermont Livability Data Visualization")
    st.write("#### Give it a dataset and we will visualize it for you!")
   
    # Get the user's dataset(s)
    user_files = get_user_files()
    
    # Define a unique key number for each plot to avoid duplicate conflicts
    unique_key = 0
    
    # If the user has uploaded at least one file
    if user_files:
        # Set of seen hashes to avoid duplicate files
        seen_hashes = set()
        # List to store unique files
        unique_files = []
        
        for file in user_files:
            file_id = file_hash(file)
            
            if file_id not in seen_hashes:
                seen_hashes.add(file_id)
                unique_files.append(file)
            
            else:
                st.warning(f"Duplicate file ignored: {file.name}")

        # Attempt to read the files
        try:
            # Iterate through each uploaded file
            for file in unique_files:
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
                    #st.dataframe(df.head(11))
                    AgGrid(df, theme="material", fit_columns_on_grid_load=True)        

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
