"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Housing Page (Census)

"""

# Necessary imports
import streamlit as st

from app_utils.census_sections import compare_tab, mapping_tab
from app_utils.data_loading import masterload
from app_utils.housing import housing_snapshot
from app_utils.streamlit_config import streamlit_config


def main():
    # Page title and tabs
    st.header("Housing", divider="grey")
    mapping, snapshot, compare = st.tabs(tabs=["Mapping", "Snapshot", "Compare"])

    # Define a list of loaded datasets
    housing_dfs = masterload("census_housing")
    # Define the tidy dataset for map filtering
    tidy_2023 = housing_dfs["housing_2023_tidy"]

    with mapping:
        mapping_tab(data=tidy_2023, map_color="Reds")

    with snapshot:
        housing_snapshot(housing_dfs)

    with compare:
        housing_dict = {
            "Housing 2023": tidy_2023,
            "Housing 2013": housing_dfs["housing_2013_tidy"],
        }
        compare_tab(housing_dict)


if __name__ == "__main__":
    streamlit_config()
    main()
