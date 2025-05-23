"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Run this in the terminal to launch the app:
-------------------------------------------
streamlit run Home.py
-------------------------------------------

"""

# Necessary imports
import streamlit as st
from app_utils import get_user_files


def main():
    # Set the page configuration settings
    st.set_page_config(
        page_title="Vermont Livability Data Visualization App",
        layout="wide",
        page_icon="🍁"
    )
    # Set the page title and sidebar settings
    st.title("Vermont Livability Data Visualization")
    st.sidebar.title("Welcome")
    st.sidebar.write("Upload your data files below to visualize them.")

    # Add a file uploader to the sidebar
    get_user_files()

if __name__ == "__main__":
    main()
