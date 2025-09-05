"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Economics Page (Census)
"""

# Necessary imports
import streamlit as st

from app_utils.census_sections import compare_tab, mapping_tab
from app_utils.data_loading import masterload
from app_utils.economic import economic_snapshot
from app_utils.streamlit_config import streamlit_config


def main():
    # Page title and tabs
    st.header("Economics", divider="grey")
    mapping, snapshot, compare = st.tabs(tabs=["Mapping", "Snapshot", "Compare"])

    econ_dfs = masterload("census_economics")
    tidy_2023 = econ_dfs["econ_2023_tidy"]

    with mapping:
        mapping_tab(data=tidy_2023, map_color="Greens")

    with snapshot:
        economic_snapshot(econ_dfs)

    with compare:
        econ_dict = {"Economics 2023": tidy_2023}
        compare_tab(econ_dict)


if __name__ == "__main__":
    streamlit_config()
    main()
