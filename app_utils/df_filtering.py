import streamlit as st
import pandas as pd
import geopandas as gpd


def filter_dataframe(dfs, filter_columns, key_prefix="filter_dataframe", header=None, allow_all=None):
    """
    Create cascading selectboxes to filter a DataFrame.
    
    Args:
        dfs (pd.DataFrame or list): DataFrame to filter, OR a list of frames to filter. 
        filter_columns (list): Columns to filter on.
        key_prefix (str): Prefix for Streamlit widget keys.
        header (str): Optional header to display.
        allow_all (dict): Optional dict specifying whether to include an "All" option for specific columns.
    
    Returns:
        tuple: (pd.DataFrame: Filtered DataFrame, selected values)
    """

    keys = [f"{key_prefix}_{i}" for i in range(len(filter_columns))] ## so that we can have multiple layers of filter on same page

    dfs = ensure_list(dfs) 
    df = dfs[0]

    filter_selections = {}

    if header:
        st.markdown(header)
    
    cols1 = st.columns(len(filter_columns))
    for i, col_name in enumerate(filter_columns):
        unique_values = df[col_name].dropna().unique()
        allow_all_option = allow_all.get(col_name, False) if allow_all else False
        options = ["All"] + sorted(unique_values.tolist()) if allow_all_option else sorted(unique_values)

        selected_value = cols1[i].selectbox(
            col_name,
            options=options, 
            key=keys[i]
        )
        filter_selections[col_name] = selected_value
        if selected_value != "All":
            dfs = [df[df[col_name] == selected_value] for df in dfs]
            df = dfs[0]
        
    return (dfs[0], filter_selections) if len(dfs) == 1 else [(df, filter_selections) for df in dfs]


def filter_dataframe_multiselect(
        dfs, 
        filter_columns, 
        key_prefix="filter_dataframe",

        ## keyword arguments
        header=None, 
        passed_cols=None,
        defaults=None,
        allow_all=None, 
        presented_cols=None,
        ):
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
    filter_selections = {}

    if header:
        st.markdown(header)


    keys = [f"{key_prefix}_{i}" for i in range(len(filter_columns))]

    #keyword arguments
    presented_cols = presented_cols or filter_columns
    cols = passed_cols or st.columns(len(filter_columns))
    defaults = defaults or {}
    allow_all = allow_all or {}


    for i, col_name in enumerate(filter_columns):
        unique_values = sorted(df[col_name].dropna().unique())
        col_allow_all = allow_all.get(col_name, False)

        options = ["All"] + unique_values if col_allow_all else unique_values
        default = defaults.get(col_name) if defaults.get(col_name) else ["All"] if col_allow_all else unique_values[0]  ## could also just default to first

        selected = cols[i].multiselect(presented_cols[i], options=options, default=default, key=keys[i])
        selected = unique_values if "All" in selected else selected
        filter_selections[col_name] = selected

        dfs = [df[df[col_name].isin(selected)] for df in dfs]
        df = dfs[0]

    return (dfs[0], filter_selections) if len(dfs) == 1 else [(df, filter_selections) for df in dfs]


def collect_filter_selections(
        df, 
        filter_columns, 
        key_prefix="filter_dataframe",

        ##keyword args
        header=None, 
        passed_cols=None,
        defaults=None,
        allow_all=None, 
        presented_cols=None,
    ):
    """
    Build cascading multiselect filters and return selected values only. 
    Does not apply the filters to the actual dataframe; to do so, call apply_filter_selections
    
    Args:
        df (pd.DataFrame): DataFrame to use for populating filter options.
        filter_columns (list): Columns to filter on.
    
    Returns:
        dict: Selected values per filter column.
    """
    filter_selections = {}

    if header:
        st.markdown(header)

    keys = [f"{key_prefix}_{i}" for i in range(len(filter_columns))]

    presented_cols = presented_cols or filter_columns
    cols = passed_cols or st.columns(len(filter_columns))
    defaults = defaults or {}
    allow_all = allow_all or {}

    df = df[filter_columns].copy()

    for i, col_name in enumerate(filter_columns):
        unique_values = sorted(df[col_name].dropna().unique())
        col_allow_all = allow_all.get(col_name, False)

        options = ["All"] + unique_values if col_allow_all else unique_values
        default = defaults.get(col_name) if defaults.get(col_name) else (["All"] if col_allow_all else unique_values[:1])

        selected = cols[i].multiselect(presented_cols[i], options=options, default=default, key=keys[i])
        selected_values = unique_values if "All" in selected else selected
        filter_selections[col_name] = selected_values

        # Update df to reflect current selection (cascading logic)
        df = df[df[col_name].isin(selected_values)]
    return filter_selections

def apply_filter_selections(df, filter_selections):
    for col, values in filter_selections.items():
        if col in df.columns and values:     
            df = df.loc[df[col].isin(set(values))]
    return df



def ensure_list(x):
    return x if isinstance(x, list) else [x]

