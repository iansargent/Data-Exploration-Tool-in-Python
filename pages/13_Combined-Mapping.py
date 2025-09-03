"""
Author: Fitz Koch
Created: 2025-07-29
Description: Combined page for mapping lots of different variables.
"""

import streamlit as st

from app_utils.data_loading import masterload
from app_utils.df_filtering import filter_wrapper
from app_utils.mapping import multi_layer_map
from app_utils.streamlit_config import streamlit_config
from app_utils.wastewater import get_soil_rpc


def combo_map(gdfs):
    map = multi_layer_map(gdfs)
    st.pydeck_chart(map)


def main():
    ## get rpc
    st.header("Combined Mapping", divider="grey")
    filter_cols = ["Jurisdiction", "District Name"]
    col1, *cols = st.columns(len(filter_cols) + 1)
    rpc = get_soil_rpc(col1)

    ## load data
    zoning_gdf = masterload("zoning")
    flooding_gdf = masterload("flooding_with_zoning")
    soil_gdf = masterload("soil_septic", rpc=rpc)

    ## filter the zoning_gdf
    zoning_gdf = zoning_gdf[zoning_gdf["RPC"] == rpc]

    # Layer selection
    layer_options = {
        "Zoning": zoning_gdf,
        "Flooding": flooding_gdf,
        "Wastewater": soil_gdf,
    }

    # Use sidebar toggle buttons to switch layers "on" and "off"
    selected_layers_toggle = []
    st.sidebar.subheader("Map Layers")
    for option in layer_options.keys():
        layer = st.sidebar.toggle(label=f"{option}", value=False)
        if layer:
            selected_layers_toggle.append(option)
            # st.sidebar.checkbox(label=f"{option} filter 1")
            # st.sidebar.slider(label=f"{option} filter 2")
            # st.sidebar.radio(label=f"{option} filter 3", options=["", "", ""])

    ## get filters and then apply them
    filter_state = filter_wrapper(
        zoning_gdf,
        filter_columns=filter_cols,
        allow_all={"Jurisdiction": True, "District Name": True},
        passed_cols=cols,
    )

    dfs = {
        name: filter_state.apply_filters(layer_options[name])
        for name in selected_layers_toggle
    }
    combo_map(dfs)


if __name__ == "__main__":
    streamlit_config()
    main()
