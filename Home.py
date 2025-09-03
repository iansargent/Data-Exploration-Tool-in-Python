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
from app_utils.streamlit_config import streamlit_config


def main():
    # Set page configurations
    st.set_page_config(page_title="Vermont Data App", layout="wide", page_icon="🍁")

    # Set the page title
    st.header("Vermont Data Exploration App")

    with open("main_page.html") as f:
        st.markdown(f.read(), unsafe_allow_html=True)

    # Display a background photo for the page
    with open("main_page.css") as f:
        st.markdown(f"<style>{f.read()}<style>", unsafe_allow_html=True)


if __name__ == "__main__":
    streamlit_config()
    main()
