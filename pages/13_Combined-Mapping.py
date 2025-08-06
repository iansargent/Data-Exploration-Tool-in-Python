"""
Author: Fitz Koch
Created: 2025-07-29
Description: Combined page for mapping lots of different variables.
"""

from app_utils.zoning import *
from app_utils.data_loading import *
from app_utils.color import *
from app_utils.mapping import *
from app_utils.df_filtering import *
from app_utils.wastewater import *
from app_utils.flooding import *
from app_utils.streamlit_config import streamlit_config

def combo_map(gdfs):
    map = multi_layer_map(gdfs)
    st.pydeck_chart(map)

def main ():

    ## get rpc
    st.header("Combined Mapping", divider="grey")
    filter_cols = [
        "Jurisdiction",
        "District Name"
        ]
    col1, *cols = st.columns(len(filter_cols)+1)
    rpc = get_soil_rpc(col1)

    ## load data
    zoning_gdf = process_zoning_data(load_zoning_data())
    flooding_gdf = process_flood_gdf(load_flood_data())
    soil_gdf = process_soil_data(load_soil_septic_single(rpc))

    ## filter the zoning_gdf 
    zoning_gdf = zoning_gdf[zoning_gdf['RPC'] == rpc]

    ## add filtering columns to the flooding and soil_gdfs
    flooding_gdf = add_cols_of_biggest_intersection(
        donor_gdf=zoning_gdf,
        altered_gdf=flooding_gdf,
        add_columns=["County", "Jurisdiction"]
    )

    soil_gdf = add_cols_of_biggest_intersection(
        donor_gdf=zoning_gdf,
        altered_gdf=soil_gdf,
        add_columns=['County']
    )

    # Layer selection
    layer_options = {
        "Zoning": zoning_gdf,
        "Flooding": flooding_gdf,
        "Wastewater": soil_gdf,
    }
    
    # selected_layers = st.multiselect("Select data sources to display", list(layer_options.keys()), default=list(layer_options.keys())[:2])
    
    # Use sidebar toggle buttons to switch layers "on" and "off"
    selected_layers_toggle = []
    st.sidebar.subheader("Map Layers")
    for option in layer_options.keys():
        layer = st.sidebar.toggle(label=f"{option}", value=False)
        if layer:
            selected_layers_toggle.append(option)
            st.sidebar.checkbox(label=f"{option} filter 1")
            st.sidebar.checkbox(label=f"{option} filter 2")
            st.sidebar.checkbox(label=f"{option} filter 3")

    ## get filters and then apply them
    filter_selections = collect_filter_selections(
        zoning_gdf,
        filter_columns=filter_cols,
        allow_all={
            "Jurisdiction" : True,
            "District Name" : True
        },
        passed_cols = cols
    )

    dfs = [
        apply_filter_selections(layer_options[name], filter_selections)
        for name in selected_layers_toggle
    ]
    combo_map(dfs)

if __name__ == "__main__":
    streamlit_config()
    main()
