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
    get_columns, get_column_type, single_column_plot, two_column_plot,
    process_uploaded_files
)
from st_aggrid import AgGrid

# The visualize page (with default arguments given)
def render_visualization(mode="single"):
    
    title = "Single Variable" if mode == "single" else "Two Variables"

    st.title(f"Visualize Your Data ({title})")
    
    user_files = get_user_files(key=mode)
    processed_files = process_uploaded_files(user_files)
    
    for df, filename in processed_files:
        key_offset = 0
        # Get a list of column names for selection
        columns = get_columns(df)

        # Subheader for the plot section
        st.subheader(f"Plots for {filename}")

        # In the single-variable tab
        if mode == "single":
            # Allow users to select a variable
            col = st.selectbox(f"Select a column to plot ({filename})", 
                               columns, 
                               index=1,
                               key=f"{filename}-single-{key_offset}")
            # Display plot(s) based on the variable type
            single_column_plot(df, col)
        
        # In the two-variable tab
        elif mode == "double":         
            # Selection box for the first variable
            col1 = st.selectbox(
                f"Select a column to plot ({filename})", 
                columns, 
                index=1,
                key=f"{filename}-col1-{key_offset}"
                )
            # Selection box for the second variable
            col2 = st.selectbox(
                f"Select a second column to plot ({filename})", 
                columns, 
                index=2,
                key=f"{filename}-col2-{key_offset+1}"
                )
            # Display the set of plots based on the datatype combination
            two_column_plot(df, col1, col2)

        # Advance the key offset to handle duplicate elements on the page
        key_offset += 2

# The main function
def main():

    # Use tabs to separate single and two variable plotting sections
    tab1, tab2 = st.tabs(["Single Variable", "Two Variables"])

    # In the first tab
    with tab1:
        # Single variable plots
        render_visualization("single")
    # In the second tab
    with tab2:
        # Two-variable plots
        render_visualization("double")


if __name__ == "__main__":
    main()
