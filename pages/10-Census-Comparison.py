"""
Author: Fitz Koch
Created: 2025-07-18
Description: Creates a full comparison tab 
"""
from app_utils.census_sections import mapping_tab, compare_tab
from app_utils.streamlit_config import streamlit_config
from app_utils.data_loading import masterload


def main():
    tidy_full_data = masterload("census_combined")
    compare_tab({"All Census Data 2023" : tidy_full_data}, 
                drop_cols=['GEOID'], filter_columns=["Source", "Category", "Subcategory", "Variable", "Measure"])

if __name__ == "__main__":
    streamlit_config()
    main()