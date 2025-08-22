"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Data Summary Page
"""

# Necessary imports
import geopandas as gpd
import streamlit as st
from streamlit_pandas_profiling import st_profile_report

from app_utils.file_handling import get_user_files, process_uploaded_files
from app_utils.report import comparison_report, exploratory_report, quality_report
from app_utils.streamlit_config import streamlit_config


def main():
    # Set the page title
    st.header("Data Summary")

    # Get the user files and process (read + clean) them
    user_files = get_user_files()
    processed_files = process_uploaded_files(user_files)

    # Initialize a unique key for each download file
    key = 0
    # For each processed file
    for _, (df, filename) in enumerate(processed_files):
        # Header section for each uploaded file with a new divider color
        st.header(f"Summary of {filename}")
        # If the file is a GeoDataFrame
        if isinstance(df, gpd.GeoDataFrame):
            # Drop the geometry column
            df = df.drop(columns=["geometry"]).reset_index(drop=True)

        # Set columns for formatting
        column1, column2 = st.columns(2)
        column3, column4 = st.columns(2)

        # Initialize session state
        expl_key = f"{filename}_expl_profile"
        qual_key = f"{filename}_qual_profile"
        expl_html_key = f"{filename}_expl_html"
        qual_html_key = f"{filename}_qual_html"

        for k in [expl_key, qual_key, expl_html_key, qual_html_key]:
            if k not in st.session_state:
                st.session_state[k] = None

        # Set columns for formatting
        column1, column2 = st.columns(2)

        # Exploratory Report
        with column1:
            if st.button(
                label="Generate Exploratory Summary", key=f"{filename}_expl_{key}"
            ):
                with st.spinner("Generating report..."):
                    ex_profile = exploratory_report(df)
                    st.session_state[expl_key] = ex_profile
                    st.session_state[expl_html_key] = ex_profile.to_html()

            if st.session_state[expl_html_key] is not None:
                st.download_button(
                    label="View Full Report",
                    data=st.session_state[expl_html_key],
                    file_name=f"data_report_{filename}_expl.html",
                    key=f"{filename}_expl_dl",
                )

        # Data Quality Report
        with column2:
            if st.button(
                label="Generate Data Quality Summary", key=f"{filename}_qual_{key}"
            ):
                with st.spinner("Generating report..."):
                    qual_profile = quality_report(df)
                    st.session_state[qual_key] = qual_profile
                    st.session_state[qual_html_key] = qual_profile.to_html()

            if st.session_state[qual_html_key] is not None:
                st.download_button(
                    label="View Full Report",
                    data=st.session_state[qual_html_key],
                    file_name=f"data_report_{filename}_qual.html",
                    key=f"{filename}_qual_dl",
                )

        # Set columns for formatting
        column3, column4 = st.columns(2)

        # Display reports side-by-side
        with column3:
            with st.expander("View Exploratory Report"):
                if st.session_state[expl_key] is not None:
                    st_profile_report(st.session_state[expl_key])

        with column4:
            with st.expander("View Quality Report"):
                if st.session_state[qual_key] is not None:
                    st_profile_report(st.session_state[qual_key])

        # Visual divider
        st.divider()

    # If there are 2 or more uploaded files, provide a comparison report
    if len(processed_files) >= 2:
        st.header("Comparison Report")
        if st.button(label="Generate Comparison Report"):
            dfs = [item[0] for item in processed_files]
            comp_report = comparison_report(dfs)
            st_profile_report(comp_report)


if __name__ == "__main__":
    streamlit_config()
    main()
