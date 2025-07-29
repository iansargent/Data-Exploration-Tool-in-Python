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

def combo_map(gdfs):
    map = mulit_layer_map(gdfs)
    st.pydeck_chart(map)

def main ():
    zoning_gdf = clean_zoning_gdf(load_zoning_data())
    zoning_gdf, zoning_color = add_fill_colors(zoning_gdf, column="District Type", cmap="tab20")

    soil_gdf = load_soil_septic("ACRPC")


    gdf, _ = filter_dataframe_multiselect(
        dfs=zoning_gdf, filter_columns=['County', 'Jurisdiction', 'District Name'], 
        presented_cols=['County', 'Municipality', 'District'],
        allow_all = {
            "County": False,
            "Jurisdiction": True,
            "District Name": True
        })
    gdf, _ = process_zoning_data(gdf)
    gdfs = [gdf] + [process_soil_data(soil_gdf)]
    combo_map(gdfs)

if __name__ == "__main__":
    st.set_page_config(
    page_title="Vermont Data App",
    layout="wide",
    page_icon="🍁"
)
    main()
