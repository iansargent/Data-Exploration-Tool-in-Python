"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Demographics Page (Census)
"""

# Necessary imports
import streamlit as st

from app_utils.census_sections import mapping_tab, compare_tab
from app_utils.data_loading import masterload
from app_utils.streamlit_config import streamlit_config
from app_utils.demographic import demographic_snapshot


def main():
    # Page title and tabs
    st.header("Demographics", divider="grey")   
    
    mapping, snapshot, compare = st.tabs(tabs=["Mapping", "Snapshot", "Compare"])

    demog_dfs = masterload("census_demographics")
    tidy_2023 = demog_dfs["demogs_2023_tidy"]

    with mapping:
        mapping_tab(data=tidy_2023, map_color="Blues")

    ## Census Snapshot section (Housing) ##
    with snapshot:
        demographic_snapshot(demog_dfs)

    with compare:
        data_dict = {"Demographics 2023" : tidy_2023}
        compare_tab(data_dict)   

if __name__ == "__main__":
    streamlit_config()
    main()