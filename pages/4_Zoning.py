"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Zoning Page
"""

# Necessary imports
import streamlit as st
import altair as alt
import geopandas as gpd
import json
from streamlit_extras.metric_cards import style_metric_cards 
from app_utils.zoning import filtered_zoning_df, district_comparison, zoning_comparison_table, zoning_district_map
from app_utils.df_filtering import filter_dataframe_multiselect
from app_utils.color import geojson_add_fill_colors, render_rgba_colormap_legend
import streamlit.components.v1 as components



@st.cache_data
def load_zoning_data():
    """
    Loads the Vermont Zoning dataset as a GeoDataFrame.

    @return: The geopandas zoning dataset as a GeoDataFrame object.
    """
    from io import BytesIO
    import requests
    
    zoning_url = 'https://raw.githubusercontent.com/VERSO-UVM/Vermont-Livability-Map/main/data/vt-zoning-update.fgb'

    # Stream download to avoid issues with large files
    response = requests.get(zoning_url)
    response.raise_for_status()  # raises an error if download failed

    gdf = gpd.read_file(BytesIO(response.content))
    
    gdf = gdf.drop(columns=["Bylaw Date"], errors="ignore")

    gdf["geometry"] = gdf["geometry"].simplify(0.0001, preserve_topology=True)

    return gdf
    

def zoning():
    # Page header
    st.header("Zoning")
    # Load the zoning data from GitHub and filter it
    zoning_gdf = load_zoning_data()
    # filtered_gdf, _ = filter_dataframe( dfs=zoning_gdf, filter_columns=['County', 'Jurisdiction', 'Jurisdiction District Name'], )
    filtered_gdf, _ = filter_dataframe_multiselect(
        dfs=zoning_gdf, filter_columns=['County', 'Jurisdiction', 'District Name'], 
        presented_cols=['County', 'Jurisdiction', 'District'],
        allow_all = {
            "County": False,
            "Jurisdiction": True,
            "District Name": True
        })
    

    ## Mapping Logic separated because we need colormap for all areas
    # Select only relevant columns to map
    filtered_gdf_map = filtered_gdf[["Jurisdiction District Name", "District Type", "geometry"]].copy()

    if filtered_gdf_map.empty:
        st.warning("No zoning data available for the selected filters.")
        return
    filtered_gdf_map = filtered_gdf_map.set_crs("EPSG:4326") if filtered_gdf_map.crs is None else filtered_gdf_map.to_crs("EPSG:4326")


    # Convert gdf into GeoJSON format and add colors
    filtered_geojson = json.loads(filtered_gdf_map.to_json())
    filtered_geojson, color_map = geojson_add_fill_colors(filtered_geojson, filtered_gdf_map, "District Type")

    map = zoning_district_map(filtered_geojson, filtered_gdf_map)
    
    mapping, report, compare = st.tabs(["Map", "Report", "Compare"])
    
    with mapping:
        map_col, legend_col = st.columns([4, 1])
        map_col.pydeck_chart(map, height=550)
        with legend_col:
            render_rgba_colormap_legend(color_map)
    
    # Total acres of land plotted on the map
    ## TODO: use the same colormap here.
    with report: 
        st.header("Land Area")
        
        col1, col2 = st.columns(2)
        col1.metric(label="**Zoning Districts**", value=f"{len(filtered_gdf):,}")
        total_acre = filtered_gdf["Acres"].sum()
        col2.metric(label="**Total Acreage**", value=f"{total_acre:,.0f} acres")

        # Acreage sum grouped by district type
        acres_by_type = filtered_gdf.groupby("District Type")["Acres"].sum().fillna(0)
        acres_df = acres_by_type.reset_index()
        # Pick relevant columns
        acres_df.columns = ["District Type", "Acres"]
        # Rename district type values to be short (for plotting)
        acres_df["District Type"] = acres_df["District Type"].replace({
            "Primarily Residential": "Residential",
            "Mixed with Residential": "Mixed",
            "Nonresidential": "Nonresidential",
            "Overlay not Affecting Use": "Overlay"
        })

        # Altair bar chart of district type distribution
        bar_chart = alt.Chart(acres_df).mark_bar().encode(
            x=alt.X("District Type:N", sort="-y", title="Zoning Type", axis=alt.Axis(labelAngle=0)),
            y=alt.Y("Acres:Q", title="Total Acres"),
            color=alt.Color("District Type:N", legend=None),
            tooltip=["District Type", alt.Tooltip("Acres:Q", format=",.0f")]
        ).properties(height=500, title="Zoning Acreage by District Type")

        # Display the bar chart to the page
        st.altair_chart(bar_chart, use_container_width=True)

        # Style cards to look better
        # style_metric_cards(background_color="whitesmoke", border_left_color="mediumseagreen")

        st.write("Bar Graph of Family Allowance (1F - 5F Dropdown)")
        st.write("Affordable Housing Allowance")

    # Selectable Table for comparisons
    with compare:
        st.subheader("Zoning Districts Table")
        districts = district_comparison(filtered_gdf)

        # If a district(s) is selected from the table above, show the comparison table
        if districts:
            zoning_comparison_table(filtered_gdf, districts)


def show_zoning():
    zoning()


if __name__ == "__main__":
    show_zoning()