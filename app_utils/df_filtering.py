import streamlit as st
import pandas as pd
import geopandas as gpd

## helper functions 
def ensure_list(x):
    return x if isinstance(x, list) else [x]

class FilterState:
    def __init__(self, df, filter_columns):
        self.df = df
        self.filter_columns = filter_columns
        self.selections = {col: None for col in filter_columns}
        self.raw_selections = {col: None for col in filter_columns}
        self.tree = self.dataframe_to_tree(self.df, self.filter_columns)

    def dataframe_to_tree(self, df, hierarchy_cols) -> dict:
        """Convert a DataFrame into a nested dict keyed by hierarchy_cols."""
        if not hierarchy_cols:
            return None

        col = hierarchy_cols[0]
        tree = {}
        for key, group in df.groupby(col):
            tree[key] = self.dataframe_to_tree(group, hierarchy_cols[1:])
        return tree

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
    """
    Class to handle **purely frontend** of cascading DF filtering. 
    """
    def __init__(
        self, 
        filter_state, 
        style="multi_select", 
        key_prefix="filter_dataframe", 
        presented_cols=None,
        defaults=None,
        passed_cols=None,
        header=None,
        allow_all=None
    ):
        self.filter_state = filter_state
        self.style = style
        self.key_prefix = key_prefix
        self.presented_cols = presented_cols or filter_state.filter_columns
        self.defaults = defaults or {}
        self.passed_cols = passed_cols or st.columns(len(filter_state.filter_columns))
        self.header = header
        self.allow_all = allow_all or {}
        self.raw_selections = {}
        self.selections = {} 


    def process_selection(self, col_name, raw_selection, options):
        """Process raw UI selection by storing it as raw list, then expanding it into everything
        that needs to be filtered on in cases ALL is in there.

        Stores results in 
        """
        # Store raw selection (what user saw)
        raw_selection = ensure_list(raw_selection)
        self.raw_selections[col_name] = raw_selection

        # store expanded  version
        selected_values = self.expand_all_selection(col_name, raw_selection, options)
        self.selections[col_name] = selected_values
        return selected_values

    def expand_all_selection(self, col_name, raw_selection, options):
        """Expand 'All' selection to actual values"""
        if "All" in raw_selection and self.allow_all.get(col_name, False):
            return options[1:]  # Skip "All" option itself
        else:
            return raw_selection
    
    def get_options(self, col_name, tree):
        unique = list(tree.keys())
        if self.allow_all.get(col_name, False):
            return ["All"] + unique
        return unique
    
    def get_default_selection(self, col_name, options):
        default = self.defaults.get(col_name, False)
        if default:
            return default
        else:
            if self.allow_all.get(col_name, False):
                return ["All"]
            else:
                return options[0] if options else []
            
    def get_options_default(self, col_name, tree):
        options = self.get_options(col_name, tree)
        default = self.get_default_selection(col_name, options)

        if default:
            default = [d for d in default if d in options]
        if not default and options:
            default = [options[0]]
        return options, default 
    
    def update_tree(self, tree, selected_values):
        sub = {} 
        for k in selected_values:
            sub.update(tree[k])
        return sub 
    
    def update_filterstate(self):
        self.filter_state.raw_selections = self.raw_selections
        self.filter_state.selections = self.selections

    def render(self):
        """
        NOTE: This is the only place that streamlit code should go
        """
        if self.header:
            st.markdown(self.header)

        tree = self.filter_state.tree
        for i, col_name in enumerate(self.filter_state.filter_columns):
            options, default = self.get_options_default(col_name, tree)

            key = f"{self.key_prefix}_{i}"
            col = self.passed_cols[i]
            label = self.presented_cols[i]

            if self.style == "selectbox":
                default_idx = options.index(default[0]) if default and default[0] in options else 0
                raw_selection = col.selectbox(label, options, index=default_idx, key=key)
            else:
                raw_selection = col.multiselect(label, options, default=default, key=key)

            selected_values = self.process_selection(col_name, raw_selection, options)
            if i < len(self.passed_cols)-1:
                tree = self.update_tree(tree, selected_values)
        self.update_filterstate()

### wrappers for utility ### 
def filter_wrapper(
    df : pd.DataFrame,
    filter_columns : list[str],
    allow_all : dict[str, bool] = None,
    style : str = "multi_select",
    presented_cols : list[str] = None,
    key_prefix : str = "filter_dataframe",
    defaults=None,
    passed_cols=None,
    header=None,
):
    filter_state = FilterState(
        df=df,
        filter_columns=filter_columns,
    )

    filter_ui = FilterUI(
        filter_state,
        style=style,
        presented_cols=presented_cols,
        key_prefix=key_prefix,
        passed_cols=passed_cols,
        defaults=defaults,
        header=header,
        allow_all=allow_all,

    )
    filter_ui.render()
    return filter_state


### area specific wrappers ### 
def filter_snapshot_data(dfs, key_df):
    filter_state = filter_wrapper(
        df=key_df, 
        filter_columns=["County", "Jurisdiction"],
        allow_all={
            "County":True,
            "Jurisdiction":True
        },
        style='selectbox',
        presented_cols=['County', 'Municipality'])
    filtered_dfs = {key: filter_state.apply_filters(df) for key, df in dfs.items()}
    selected_values = filter_state.raw_selections
    return filtered_dfs, selected_values