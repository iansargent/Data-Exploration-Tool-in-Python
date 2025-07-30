"""
Author: Fitz Koch
Created: 2025-07-18
Description: Creates a full comparison tab 

Credits: Created as part of a Masters with VERSO
"""
import streamlit as st
import pandas as pd
from app_utils.census import rename_and_merge_census_cols
from app_utils.housing import housing_pop_plot, housing_snapshot
from app_utils.census_sections import mapping_tab, compare_tab
from urllib.parse import urljoin
from app_utils.streamlit_config import streamlit_config
from app_utils.data_loading import load_census_data



# TODO: We should make a dictionary like that below, maybe with more complicated logic, where we store all our data.
# That way we have a clean place ot put it all.
@st.cache_data
def load_combine_census():
    base_name = "https://raw.githubusercontent.com/iansargent/Data-Exploration-Tool-in-Python/main/Data/Census/"
    label_to_file = {
        "Housing": "VT_HOUSING_ALL.fgb",
        "Economic": "VT_ECONOMIC_ALL.fgb",
        "Demographic": "VT_DEMOGRAPHIC_ALL.fgb",
        "Social": "VT_SOCIAL_ALL.fgb"
    }

    dfs = []
    for label, fname in label_to_file.items():
        gdf = load_census_data(urljoin(base_name, fname))
        df = rename_and_merge_census_cols(gdf).drop(columns=gdf.geometry.name)
        df["Source"] = label
        dfs.append(df)

    df_combined = pd.concat(dfs, ignore_index=True, sort=False)
    return df_combined


def main():
    tidy_full_data = load_combine_census()
    compare_tab({"All Census Data 2023" : tidy_full_data}, 
                drop_cols=['GEOID'], filter_columns=["Source", "Category", "Subcategory", "Variable", "Measure"])


if __name__ == "__main__":
    streamlit_config()
    main()