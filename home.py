"""
Ian Sargent
ORCA
Streamlit Data Visualization Home Page

Run this in the terminal to launch the page:
-------------------------------------------
streamlit run home.py
"""



import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from utils import read_data

# --- Background image (optional) ---
def set_background_image():
    st.markdown(
        """
        <style>
        .stApp {
            background-image: url("https://example.com/your-background.jpg");
            background-size: cover;
            background-position: center;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# --- Example Dataset ---
def generate_example_dataset():
    n = 100
    return pd.DataFrame({
        "date": pd.date_range(datetime.now(), periods=n),
        "category": np.random.choice(["A", "B", "C"], size=n),
        "value": np.random.normal(50, 10, size=n),
        "flag": np.random.choice([True, False], size=n)
    })



# --- Main Home Page ---
def main():
    st.set_page_config(page_title="ORCA: Home", layout="wide")
    set_background_image()

    st.title("🏠 Welcome to the Data Visualization App")
    st.markdown("Upload one or more datasets to get started OR use the **example button** in the sidebar.")

    uploaded_files = st.file_uploader(
        "Upload your files",
        type=["csv", "xlsx", "xls", "json", "sav"],
        accept_multiple_files=True
    )

    with st.sidebar:
        st.header("Load Example")
        if st.button("Load Example Dataset"):
            df = generate_example_dataset()
            st.session_state["datasets"] = {"example.csv": df}
            st.success("Example dataset loaded.")
            st.switch_page("app.py")

    if uploaded_files:
        datasets = {}
        for file in uploaded_files:
            df = read_data(file)
            if df is not None:
                datasets[file.name] = df
            else:
                st.warning(f"Unsupported file: {file.name}")

        if datasets:
            st.session_state["datasets"] = datasets
            st.success("Files uploaded successfully. Redirecting...")
            st.switch_page("app.py")

if __name__ == "__main__":
    main()
