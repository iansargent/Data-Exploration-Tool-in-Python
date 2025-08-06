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

    # keyword args
    style="multi_select",  # "selectbox" or "multi_select"
    header=None, 
    passed_cols=None,
    defaults=None,
    allow_all=None, 
    presented_cols=None,
):
    """
    Build cascading filters using selectbox or multiselect, returning selected values only.
    Does not apply the filters to the DataFrame; use apply_filter_selections for that.

    Args:
        df (pd.DataFrame): DataFrame to extract filter options from.
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
        default = defaults.get(col_name)
        if not default:
            default = "All" if col_allow_all else unique_values[0] if style == "selectbox" else [unique_values[0]]

        if style == "selectbox":
            selected = cols[i].selectbox(presented_cols[i], options=options, index=options.index(default) if default in options else 0, key=keys[i])
            selected_values = unique_values if selected == "All" else [selected]
        else:
            selected = cols[i].multiselect(presented_cols[i], options=options, default=default, key=keys[i])
            selected_values = unique_values if "All" in selected else selected

        filter_selections[col_name] = selected_values
        df = df[df[col_name].isin(selected_values)]

    return filter_selections






def apply_filter_selections(df, filter_selections):
    for col, values in filter_selections.items():
        if col in df.columns and values:     
            df = df.loc[df[col].isin(set(values))]
    return df



def ensure_list(x):
    return x if isinstance(x, list) else [x]


### Object Oriented Style ### 
class FilterState:
    def __init__(self, df, filter_columns, allow_all=None):
        self.df = df
        self.filter_columns = filter_columns
        self.allow_all = allow_all or {}
        self.selections = {col: None for col in filter_columns}
        self.raw_selections = {col: None for col in filter_columns}

    def get_options(self, col_name, filtered_df=None):
        """Get available options for a filter column"""
        source_df = filtered_df if filtered_df is not None else self.df
        unique_values = sorted(source_df[col_name].dropna().unique())
        if self.allow_all.get(col_name, False):
            return ["All"] + unique_values
        return unique_values

    def get_default_selection(self, col_name, custom_defaults=None):
        """Get default selection for a column"""
        if custom_defaults and col_name in custom_defaults:
            return custom_defaults[col_name]
        
        options = self.get_options(col_name)
        if self.allow_all.get(col_name, False):
            return ["All"]
        return [options[0]] if options else []

    def process_selection(self, col_name, raw_selection, options):
        """Process raw UI selection by storing it as raw list, then expanding it into everything
        that needs to be filtered on in cases ALL is in there
        """
        # Store raw selection
        raw_selection = ensure_list(raw_selection)
        self.raw_selections[col_name] = raw_selection

        # store newer version
        selected_values = self.expand_all_selection(col_name, raw_selection, options)
        self.selections[col_name] = selected_values
        return selected_values

    def expand_all_selection(self, col_name, raw_selection, options):
        """Expand 'All' selection to actual values"""
        if "All" in raw_selection and self.allow_all.get(col_name, False):
            return options[1:]  # Skip "All" option itself
        else:
            return raw_selection
    
    def apply_filter(self, df, col_name, selected_values):
        if selected_values:
           return  df[df[col_name].isin(selected_values)]
        else:
            return df

    def apply_filters(self, df=None):
        """Apply current filter selections to dataframe"""
        if df is None:
            df = self.df.copy()
        
        for col, selected_values in self.selections.items():
            if selected_values is None or not selected_values:
                continue
            if col not in df.columns:
                continue
            df = df[df[col].isin(selected_values)]
        return df


class FilterUI:
    def __init__(
        self, 
        filter_state, 
        style="multi_select", 
        key_prefix="filter_dataframe", 
        presented_cols=None,
        defaults=None,
        passed_cols=None,
        header=None,
    ):
        self.filter_state = filter_state
        self.style = style
        self.key_prefix = key_prefix
        self.presented_cols = presented_cols or filter_state.filter_columns
        self.defaults = defaults or {}
        self.passed_cols = passed_cols or st.columns(len(filter_state.filter_columns))
        self.header = header

    def render(self):
        """Render the filter UI with cascading filtering"""
        if self.header:
            st.markdown(self.header)

        # Start with full dataframe and progressively filter (cascading)
        filtered_df = self.filter_state.df.copy()

        for i, col_name in enumerate(self.filter_state.filter_columns):
            # Get options based on current filtered state (cascading)
            options = self.filter_state.get_options(col_name, filtered_df)
            default = self.filter_state.get_default_selection(col_name, self.defaults)
            
            # Ensure default is valid for current options
            if default:
                default = [d for d in default if d in options]
            if not default and options:
                default = [options[0]]

            key = f"{self.key_prefix}_{i}"
            col = self.passed_cols[i]
            label = self.presented_cols[i]

            if self.style == "selectbox":
                default_idx = options.index(default[0]) if default and default[0] in options else 0
                raw_selection = col.selectbox(label, options, index=default_idx, key=key)
            else:
                raw_selection = col.multiselect(label, options, default=default, key=key)

            selected_values = self.filter_state.process_selection(col_name, raw_selection, options)
            filtered_df = self.filter_state.apply_filter(filtered_df, col_name, selected_values)

        return filtered_df