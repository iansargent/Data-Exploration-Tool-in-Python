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


def main():
    # Set the page configuration settings
    st.set_page_config(
        page_title="Vermont Livability App",
        layout="wide",
        page_icon="🍁"
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

    page = st_navbar(["Table Preview", "Mapping", "Data Summary", "Visualize", "About"])
    
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

    st.sidebar.title("Welcome")
    st.sidebar.write("Upload your data files below to visualize them.")
    # Add a file uploader to the sidebar
    get_user_files()


if __name__ == "__main__":
    main()
