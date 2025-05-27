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
from app_utils import get_user_files


def main():
    # Set the page configuration settings
    st.set_page_config(
        page_title="Vermont Livability Data Visualization App",
        layout="wide",
        page_icon="🍁"
    )
    # Set the page title and sidebar settings
    st.title("Vermont Livability Data Visualization")
    
    page_bg_img = '''
        <style>
        [data-testid="stAppViewContainer"] {
            background-image: url("https://sdmntprwestus2.oaiusercontent.com/files/00000000-8974-61f8-853c-bac74c759908/raw?se=2025-05-27T16%3A30%3A50Z&sp=r&sv=2024-08-04&sr=b&scid=d4663d63-abb0-54b6-9db9-ae460e10a52c&skoid=24a7dec3-38fc-4904-b888-8abe0855c442&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2025-05-27T08%3A12%3A53Z&ske=2025-05-28T08%3A12%3A53Z&sks=b&skv=2024-08-04&sig=O7wlqzDvlowzmbzCyhKVJGEnMovTc0d3oR2q05EI2x8%3D");
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
