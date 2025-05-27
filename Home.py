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
from streamlit_navigation_bar import st_navbar
from app_utils import get_user_files
from pages.table_preview import show_preview
from pages.mapping import show_mapping
from pages.data_summary import show_summary
from pages.visualize import show_plots
from pages.about import show_about

def home_main():
    # Set the page configuration settings
    st.set_page_config(
        page_title="Vermont Livability App",
        layout="wide",
        page_icon="🍁",
        initial_sidebar_state="collapsed"
    )

    st.markdown(
    """
    <style>
    /* Set Helvetica (fallback to Arial, sans-serif) globally */
    html, body, [class*="css"]  {
        font-family: 'Avenir', 'Arial', sans-serif; font-weight: 300;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Set the page title and sidebar settings
    st.markdown(
        "<h2 style='color: #4a4a4a; font-family: Helvetica; font-weight: 300;'>Vermont Livability: A Data Exploration App</h2>",
        unsafe_allow_html=True)
    
    page_bg_img = '''
        <style>
        [data-testid="stAppViewContainer"] {
            background-image: url("https://raw.githubusercontent.com/iansargent/Data-Exploration-Tool-in-Python/main/Images/HomePagePhoto.png");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
            background-position: center;
        }

        [data-testid="stHeader"] {
            background: rgba(255, 255, 255, 0.0);
        }

        [data-testid="stSidebar"] {
            background: rgba(255, 255, 255, 0.5);
        }
        </style>
        '''
    
    st.markdown(page_bg_img, unsafe_allow_html=True)

    page = st_navbar(["Home", "Mapping", "Data Summary", "Visualize", "About"])

    st.sidebar.title("Upload your Dataset(s)")
    # Add a file uploader to the sidebar
    get_user_files()


if __name__ == "__main__":
    home_main()
