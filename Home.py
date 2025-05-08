"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Run this in the terminal to launch the app:
-------------------------------------------
streamlit run Home.py

"""

import streamlit as st
from utils import get_user_files

def main():
    st.set_page_config(
        page_title="Vermont Livability Data Visualization App",
        layout="wide",
        page_icon="🍁"
    )

    st.title("Vermont Livability Data Visualization")
    st.sidebar.title("Welcome")
    st.sidebar.write("Upload your data files below to visualize them.")

    get_user_files()  # Prepares files for use in other pages

if __name__ == "__main__":
    main()
