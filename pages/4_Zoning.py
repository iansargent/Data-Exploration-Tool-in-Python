"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Zoning Page
"""

# Necessary imports
import streamlit as st

from app_utils.color import render_rgba_colormap_legend
from app_utils.data_loading import masterload
from app_utils.df_filtering import filter_wrapper
from app_utils.streamlit_config import streamlit_config
from app_utils.zoning import (
    district_comparison,
    get_acerage_metrics,
    plot_acreage,
    zoning_comparison_table,
    zoning_district_map,
)


def main():
    # Page header
    st.header("Zoning", divider="grey")

    # Load the zoning data from GitHub, clean it, add colors,
    zoning_gdf = masterload("zoning")

    ## user selections
    filter_state = filter_wrapper(
        zoning_gdf,
        filter_columns=["County", "Jurisdiction", "District Name"],
        allow_all={"County": False, "Jurisdiction": True, "District Name": True},
    )
    filtered_gdf = filter_state.apply_filters(zoning_gdf)

    mapping, report, compare = st.tabs(["Map", "Report", "Compare"])
    color_map = dict(
        zip(zoning_gdf["District Type"], zoning_gdf["rgba_color"], strict=False)
    )

    with mapping:
        map = zoning_district_map(filtered_gdf)
        map_col, legend_col = st.columns([4, 1])
        map_col.pydeck_chart(map, height=550)
        with legend_col:
            render_rgba_colormap_legend(color_map)

    with report:
        st.header("Land Area")
        get_acerage_metrics(filtered_gdf)

        acre_chart = plot_acreage(filtered_gdf)
        st.altair_chart(acre_chart, use_container_width=True)

        st.write("Bar Graph of Family Allowance (1F - 5F Dropdown)")
        st.write("Affordable Housing Allowance")

    # Selectable Table for comparisonsAC
    with compare:
        st.subheader("Zoning Districts Table")

        districts = district_comparison(
            filtered_gdf.drop(columns=["rgba_color", "hex_color"])
        )

        # If a district(s) is selected from the table above, show the comparison table
        if districts:
            zoning_comparison_table(
                filtered_gdf.drop(columns=["rgba_color", "hex_color"]), districts
            )


if __name__ == "__main__":
    streamlit_config()
    main()
