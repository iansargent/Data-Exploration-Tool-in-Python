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
def render_visualization(mode="single", processed_files=None):

    # Set the page title
    st.markdown(
        "<h2 style='color: #4a4a4a; font-family: Helvetica; font-weight: 300;'>Visualize</h2>",
        unsafe_allow_html=True)


    dividers = ["red", "blue", "green", "orange", "violet", "red", "grey"]

    for i, (df, filename) in enumerate(processed_files):
        key = 0
        # Get a list of column names for selection
        columns = get_columns(df)
        # Subheader for the plot section
        st.header(f"Plots for {filename}", divider=dividers[i])
        # In the single-variable tab
        if mode == "single":
            # Allow users to select a variable
            col = st.selectbox(f"Select a column to plot ({filename})", 
                               columns, 
                               index=1,
                               key=f"{filename}-single-{key}")
            # Display plot(s) based on the variable type
            single_column_plot(df, col)
        
        # In the two-variable tab
        elif mode == "double":         
            # Selection box for the first variable
            col1 = st.selectbox(
                f"Select a column to plot ({filename})", 
                columns, 
                index=1,
                key=f"{filename}-col1-{key}"
                )
            # Selection box for the second variable
            col2 = st.selectbox(
                f"Select a second column to plot ({filename})", 
                columns, 
                index=2,
                key=f"{filename}-col2-{key+1}"
                )
            # Display the set of plots based on the datatype combination
            two_column_plot(df, col1, col2)

        # Advance the key offset to handle duplicate elements on the page
        key += 2

# The main function
def show_plots():
    st.markdown(
    """
    <style>
    /* Set Helvetica (fallback to Arial, sans-serif) globally */
    html, body, [class*="css"]  {
        font-family: 'Avenir', 'Arial', sans-serif; font-weight: 300;
    }
    </style>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Single Variable", "Two Variables"])
    user_files = get_user_files(key="shared")  # use a shared key
    processed_files = process_uploaded_files(user_files)
    
    with tab1:
        render_visualization("single", processed_files)
    with tab2:
        render_visualization("double", processed_files)

if __name__ == "__main__":
    show_plots()
