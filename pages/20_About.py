"""
Ian Sargent
ORCA
Streamlit Data Visualization App

About Page
"""

import markdown
import streamlit as st

from app_utils.streamlit_config import streamlit_config


def about():
    # Set the page title
    st.markdown(
        "<h2 style='color: #4a4a4a; font-family: Helvetica; font-weight: 300;'>About the Project</h2>",
        unsafe_allow_html=True,
    )
    
    with open("pages/about.md") as f:
        html_content = markdown.markdown(f.read())

    # Display the 'about.md' content
    st.markdown(
        f"""
        <div class="custom-container">
            {html_content}
        </div>
        """,
        unsafe_allow_html=True,
    )


def main():
    # Set the global font settings and display a background image
    with open("main_page.css") as f:
        st.markdown(f"<style> {f.read()}<style>", unsafe_allow_html=True)

    # Show the about page
    about()


if __name__ == "__main__":
    streamlit_config()
    main()
