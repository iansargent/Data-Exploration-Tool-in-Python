"""
Author: Fitz Koch
Created: 2025-07-30
Description: Script to hold the streamlit configuration that applies to multiple pages.
"""

import streamlit as st
from streamlit_theme import st_theme


def streamlit_config():
    st.set_page_config(page_title="Vermont Data App", layout="wide", page_icon="🍁")
    st.session_state.theme = get_streamlit_theme(key="theme_shade")
    st.session_state.map_style = pydeck_theme_basemap(key="mapping_basemap")


def get_streamlit_theme(key):
    theme_dict = st_theme(key=f"{key}")
    if theme_dict is not None:
        theme = theme_dict["base"]
    else:
        theme = "light"

    return theme


def pydeck_theme_basemap(key):
    theme = get_streamlit_theme(key=key)
    map_style = (
        "dark"
        if theme == "dark"
        else "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
    )
    return map_style
