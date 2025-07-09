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
from app_utils import get_user_files, process_uploaded_files


def main():
    # Set page configurations
    st.set_page_config(
        page_title="Vermont Data App",
        layout="wide",
        page_icon="🍁"
    )
    
    # Set the page title
    st.markdown(
        "<h2 style='color: #4a4a4a; font-family: Helvetica; font-weight: 300;'>Vermont Data Exploration App</h2>",
        unsafe_allow_html=True)

    # Display a background photo for the page
    with open("main_page.css") as f:
        st.markdown(f"<style>{f.read()}<style>", unsafe_allow_html=True)
    
    # Display the file uploader in the side panel
    user_files = get_user_files()
    processed_files = process_uploaded_files(user_files)
    
    # navigation_placeholder = "Placeholder for app navigation / directions"

    # with st.container():        
    #     st.markdown(
    #         f"""
    #         <div class="custom-container">
    #             <p>{navigation_placeholder}</p>
    #         </div>
    #         """,
    #         unsafe_allow_html=True)


if __name__ == "__main__":
    main()