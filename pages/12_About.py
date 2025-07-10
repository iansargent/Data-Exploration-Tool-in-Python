
"""
Ian Sargent
ORCA
Streamlit Data Visualization App

About Page
"""

import streamlit as st
import markdown
import requests

def about():
    # Set the page title
    st.markdown(
        "<h2 style='color: #4a4a4a; font-family: Helvetica; font-weight: 300;'>About the Project</h2>",
        unsafe_allow_html=True)

    # Open the 'about.md' file and read its content
    url = "https://raw.githubusercontent.com/iansargent/Data-Exploration-Tool-in-Python/main/pages/about.md"
    response = requests.get(url)
    response.raise_for_status()  # optional, to raise error on bad response

    about_content = response.text
    html_content = markdown.markdown(about_content)

    # Display the 'about.md' content in a container 
    with st.container():        
        st.markdown(
            f"""
            <div class="custom-container">
                <p>{html_content}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

def show_about():
    # Set the global font settings and display a background image
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
            background-color: cornsilk;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            font-family: 'Avenir', 'Arial';
            font-weight: 300;
            color: #333333;
        }
        </style>
        """, unsafe_allow_html=True)
    
    # Show the about page
    about()


if __name__ == "__main__":
    show_about()
