"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Social Page (Census)
"""

# Necessary imports
import streamlit as st

from app_utils.census_sections import mapping_tab, compare_tab
from app_utils.data_loading import masterload
from app_utils.streamlit_config import streamlit_config
# from app_utils.social import social_snapshot ##TODO: fix to use std filering (see others for example)

def main():
    # Page title and tabs
    st.header("Social", divider="grey")
    mapping, snapshot, compare = st.tabs(tabs=["Mapping", "Snapshot", "Compare"])

    social_dfs = masterload("census_social")
    tidy_2023 = social_dfs["social_2023_tidy"]

    with mapping:
        mapping_tab(data=tidy_2023, map_color="Purples")
        
    # with snapshot:
    #     social_snapshot(social_dfs)

    with compare:
        data_dict = {"Social 2023" : tidy_2023}
        compare_tab(data_dict)

if __name__ == "__main__":
    streamlit_config()
    main()