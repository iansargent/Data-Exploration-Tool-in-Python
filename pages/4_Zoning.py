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
from app_utils.zoning import filtered_zoning_df, selection_table, zoning_comparison_table, zoning_district_map


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
    filtered_gdf = filtered_zoning_df(zoning_gdf)
    # Select only relevant columns to map
    filtered_gdf_map = filtered_gdf[["Jurisdiction District Name", "District Type", "geometry"]]
    filtered_gdf_map = filtered_gdf_map.to_crs(epsg=4326)
    # Convert gdf into GeoJSON format
    filtered_geojson = json.loads(filtered_gdf_map.to_json())
    # Define the pydeck map object and display it
    map = zoning_district_map(filtered_geojson, filtered_gdf_map)
    st.pydeck_chart(map, height=550)
    
    st.markdown("---")

    # Total acres of land plotted on the map
    st.header("Land Area")
    
    col1, col2 = st.columns(2)
    col1.metric(label="Districts", value=f"{len(filtered_gdf):,}")
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
    style_metric_cards(background_color="whitesmoke", border_left_color="mediumseagreen")

    # Selectable Table for comparisons
    st.subheader("Zoning Districts Table")
    selected = selection_table(filtered_gdf)
    
    try:
        # If a district(s) is selected from the table above, show the comparison table
        if not selected.empty:
            zoning_comparison_table(selected)
    except:
        st.warning(f"No Selected Districts to Compare")


def show_zoning():
    zoning()


if __name__ == "__main__":
    show_zoning()