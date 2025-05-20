
"""
Ian Sargent
ORCA
Streamlit Data Visualization App

About Page
"""


import streamlit as st

def render_about():
    st.title("About the App")
    st.markdown("""
    This interactive app is designed to help users and planners explore and visualize their municipal datasets
    for the Vermont Livability Project. Upload your data files to get started!

    Built with ❤️\n\n- Ian.
    """)
    
    st.markdown("[GitHub Repository Link](https://github.com/iansargent/Data-Exploration-Tool-in-Python)")

render_about()
