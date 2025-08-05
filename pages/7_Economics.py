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
from app_utils.data_loading import load_census_data
from app_utils.streamlit_config import streamlit_config


@st.cache_data
def census_economics():
    econ_df_2023 = load_census_data(
        "https://raw.githubusercontent.com/iansargent/Data-Exploration-Tool-in-Python/main/Data/Census/VT_ECONOMIC_ALL.fgb",
    )
    unemployment_df = load_census_data(
        "https://raw.githubusercontent.com/iansargent/Data-Exploration-Tool-in-Python/main/Data/Census/unemployment_rate_by_year.csv",
    )
    median_earnings_df = load_census_data(
        "https://raw.githubusercontent.com/iansargent/Data-Exploration-Tool-in-Python/refs/heads/main/Data/Census/median_earnings_by_year.csv",
    )
    commute_time_df = load_census_data(
        "https://raw.githubusercontent.com/iansargent/Data-Exploration-Tool-in-Python/refs/heads/main/Data/Census/commute_time_by_year.csv",
    )
    commute_habits_df = load_census_data(
        "https://raw.githubusercontent.com/iansargent/Data-Exploration-Tool-in-Python/refs/heads/main/Data/Census/commute_habits_by_year.csv",
    )
    
    econ_dfs = [econ_df_2023, unemployment_df, median_earnings_df, commute_time_df, commute_habits_df]

    return econ_dfs


def main():
    # Page title and tabs
    st.header("Economics", divider="grey")
    mapping, snapshot, compare = st.tabs(tabs=["Mapping", "Snapshot", "Compare"])

    econ_dfs = census_economics()
    economic_gdf_2023 = econ_dfs[0]
    tidy_2023 = rename_and_merge_census_cols(economic_gdf_2023)

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