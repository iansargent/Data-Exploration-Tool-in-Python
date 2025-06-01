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
    # Set page configurations
    st.set_page_config(
        page_title="Vermont Livability App",
        layout="wide",
        page_icon="🍁"
    )
    
    # Set the page title
    st.markdown(
        "<h2 style='color: #4a4a4a; font-family: Helvetica; font-weight: 300;'>Vermont Livability: A Data Exploration App</h2>",
        unsafe_allow_html=True)

    # Display a background photo for the page
    st.markdown(
        """
        <style>
        html, body, [class*="css"]  {
            font-family: 'Avenir', 'Arial', sans-serif;
            font-weight: 300;
        }

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

        /* Custom container style */
        .custom-container {
            background-color: whitesmoke;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            font-family: 'Avenir', 'Arial';
            font-weight: 300;
            color: #333333;
        }
        </style>
        """, unsafe_allow_html=True)
    
    # Display the file uploader in the side panel
    get_user_files()

    navigation_placeholder = "Placeholder for app navigation / directions"

    with st.container():        
        st.markdown(
            f"""
            <div class="custom-container">
                <p>{navigation_placeholder}</p>
            </div>
            """,
            unsafe_allow_html=True
        )


if __name__ == "__main__":
    main()