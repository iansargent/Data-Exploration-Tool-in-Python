
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


def show_about():
    st.markdown(
    """
    <style>
    /* Set Helvetica (fallback to Arial, sans-serif) globally */
    html, body, [class*="css"]  {
        font-family: 'Avenir', 'Arial', sans-serif; font-weight: 300;
    }
    </style>
    """, unsafe_allow_html=True)
    render_about()


if __name__ == "__main__":
    show_about()
