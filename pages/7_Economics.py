"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Economics Page (Census)
"""

# Necessary imports
import streamlit as st
from app_utils.economic import economic_snapshot
from app_utils.census import rename_and_merge_census_cols
from app_utils.census_sections import mapping_tab, compare_tab
from app_utils.data_loading import load_census_data_dict
from app_utils.streamlit_config import streamlit_config

from app_utils.constants.ACS import ACS_BASENAME


@st.cache_data
def census_economics():
    return load_census_data_dict(
        basename=ACS_BASENAME,
        sources={
            "econ_2023" : "VT_ECONOMIC_ALL.fgb",
            "unemployment" : "unemployment_rate_by_year.csv",
            "median_earnings" : "median_earnings_by_year.csv",
            "commute_time" : "commute_time_by_year.csv",
            "commute_habits" : "commute_habits_by_year.csv"
        },
    )


def main():
    # Page title and tabs
    st.header("Economics", divider="grey")
    mapping, snapshot, compare = st.tabs(tabs=["Mapping", "Snapshot", "Compare"])

    econ_dfs = census_economics()
    tidy_2023 = rename_and_merge_census_cols(econ_dfs["econ_2023"])

    with mapping:
        mapping_tab(data=tidy_2023, map_color="Greens")

    with snapshot:
        economic_snapshot(econ_dfs)

    with compare:
        econ_dict = {"Economics 2023" : tidy_2023}
        compare_tab(econ_dict)
            
if __name__ == "__main__":
    streamlit_config()
    main()