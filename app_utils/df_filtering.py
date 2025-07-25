import streamlit as st
import pandas as pd

def filter_dataframe(dfs, filter_columns, key_prefix="filter_dataframe", header=None ):
    """
    Create cascading selectboxes to filter a DataFrame.
    
    Args:
        dfs (pd.DataFrame): DataFrame to filter, OR a list of frames to filter. 
        filter_columns (list): Columns to filter on.
    
    Returns:
        tupel: (pd.DataFrame: Filtered DataFrame, selected values)
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


def filter_dataframe_multiselect(dfs, filter_columns, key_prefix="filter_dataframe", header=None, allow_all=None, presented_cols=None):
    """
    Create cascading multiselect filters for a DataFrame, with optional 'All' support per column.
    
    Args:
        dfs (pd.DataFrame or list): DataFrame(s) to filter.
        filter_columns (list): Columns to filter on.
        key_prefix (str): Streamlit key prefix.
        header (str): Optional header markdown.
        allow_all (dict): Dict of {column_name: bool} to allow "All" selection.
    
    Returns:
        tuple: (Filtered DataFrame or list of DataFrames, selected values)
    """
    dfs = ensure_list(dfs)
    df = dfs[0]
    selected_values = {}
    allow_all = allow_all or {}

    if header:
        st.markdown(header)

    cols1 = st.columns(len(filter_columns))
    keys = [f"{key_prefix}_{i}" for i in range(len(filter_columns))]

    presented_cols = presented_cols if presented_cols else filter_columns

    for i, col_name in enumerate(filter_columns):
        unique_values = sorted(df[col_name].dropna().unique())
        col_allow_all = allow_all.get(col_name, False)

        options = ["All"] + unique_values if col_allow_all else unique_values
        default = ["All"] if col_allow_all else unique_values[0]  ## could also just default to first

        selected = cols1[i].multiselect(presented_cols[i], options=options, default=default, key=keys[i])
        selected_values[col_name] = selected

        if "All" in selected: 
            pass
        else:
            dfs = [df[df[col_name].isin(selected)] for df in dfs]
            df = dfs[0]

    return (dfs[0], selected_values) if len(dfs) == 1 else [(df, selected_values) for df in dfs]


def ensure_list(x):
    return x if isinstance(x, list) else [x]