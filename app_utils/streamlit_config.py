"""
Author: Fitz Koch
Created: 2025-07-30
Description: Script to hold the streamlit configuration that applies to multiple pages.
"""

import streamlit as st


def streamlit_config():
    st.set_page_config(
        page_title="Vermont Data App",
        layout="wide",
        page_icon="🍁"
    )