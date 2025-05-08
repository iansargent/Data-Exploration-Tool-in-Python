
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
    This interactive app is designed to help users explore and visualize their datasets
    for the Vermont Livability Project. Upload your CSV, Excel, or JSON data to generate:
    
    - Cleaned previews
    - Column-level summaries
    - Interactive plots

    Built with ❤️ using Streamlit, Altair, and AgGrid.
    """)
    
    st.markdown("[GitHub Repository](https://github.com/iansargent/Data-Exploration-Tool-in-Python)")

render_about()
