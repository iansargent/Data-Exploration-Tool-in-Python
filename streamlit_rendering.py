import streamlit as st
import pandas as pd

def filter_dataframe(dfs, filter_columns, key_prefix="filter_dataframe", header=None, ):
    """
    Create cascading selectboxes in two rows to filter a DataFrame.
    
    Args:
        dfs (pd.DataFrame): DataFrame to filter, OR a list of frames to filter. 
        filter_columns (list): Columns to filter on.
    
    Returns:
        pd.DataFrame: Filtered DataFrame.
    """
    keys = [f"{key_prefix}_{i}" for i in range(len(filter_columns))] ## so that we can have multiple layers of filter on same page

    dfs = ensure_list(dfs) 
    df = dfs[0]

    selected_values = {}

    if header:
        st.markdown(header)
    cols1 = st.columns(len(filter_columns))
    for i, col_name in enumerate(filter_columns):
        unique_values = df[col_name].dropna().unique()
        selected_value = cols1[i].selectbox(
            col_name,
            options=sorted(unique_values), 
            key=keys[i]
        )
        selected_values[col_name] = selected_value
        dfs = [df[df[col_name] == selected_value] for df in dfs]
        df = dfs[0]
        
    return (dfs[0], selected_values) if len(dfs) == 1 else [(df, selected_values) for df in dfs]

def ensure_list(x):
    return x if isinstance(x, list) else [x]