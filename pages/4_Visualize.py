"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Visualize Page
"""

# Necessary imports
import streamlit as st
from app_utils import (
    get_user_files, file_hash, read_data, clean_data,
    get_columns, get_column_type, single_column_plot, two_column_plot
)
from st_aggrid import AgGrid

# The visualize page (with default arguments given)
def render_visualization(mode = "single", user_files = None):
    title = "Single Variable" if mode == "single" else "Two Variables"
    st.title(f"\U0001F4C8 Visualize Your Data ({title})")
    
    if not user_files:
        st.warning("No files uploaded.")
        return

    seen_hashes = set()
    key_offset = 0

    unique_files = []
    for file in user_files:
        fid = file_hash(file)
        
        if fid not in seen_hashes:
            seen_hashes.add(fid)
            unique_files.append(file)
    
    for file in unique_files:
        # Read and clean the uploaded data
        df = clean_data(read_data(file))
        # Get a list of the column names
        columns = get_columns(df)

        # Subheader for the plot section
        st.subheader(f"Plots for {file.name}")

        # In the single-variable tab
        if mode == "single":
            # Allow users to select a variable
            col = st.selectbox(f"Select a column to plot ({file.name})", 
                               columns, 
                               index=1,
                               key=f"{file.name}-single-{key_offset}")
            # Display plot(s) based on the variable type
            single_column_plot(df, col)
        
        # In the two-variable tab
        elif mode == "double":         
            # Selection box for the first variable
            col1 = st.selectbox(
                f"Select a column to plot ({file.name})", 
                columns, 
                index=1,
                key=f"{file.name}-col1-{key_offset}"
                )
            # Selection box for the second variable
            col2 = st.selectbox(
                f"Select a second column to plot ({file.name})", 
                columns, 
                index=2,
                key=f"{file.name}-col2-{key_offset+1}"
                )
            # Display the set of plots based on the datatype combination
            two_column_plot(df, col1, col2)

        # Advance the key offset to handle duplicate elements on the page
        key_offset += 2

# The main function
def main():
    # Get the user files
    user_files = get_user_files()
    
    # Use tabs to separate single and two variable plotting sections
    tab1, tab2 = st.tabs(["Single Variable", "Two Variables"])

    # In the first tab
    with tab1:
        # Single variable plots
        render_visualization("single", user_files)
    # In the second tab
    with tab2:
        # Two-variable plots
        render_visualization("double", user_files)


if __name__ == "__main__":
    main()
