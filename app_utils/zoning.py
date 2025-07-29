"""
Open Research Community Accelorator
Vermont Data App

Zoning Utility Functions
"""

# Streamlit 
import streamlit as st
import pandas as pd
import geopandas as gpd
import io
import pydeck as pdk
import altair as alt 


def zoning_district_map(filtered_geojson, filtered_gdf_map):

    layer = pdk.Layer(
        "GeoJsonLayer",
        data=filtered_geojson,
        get_fill_color="properties.rgba_color",
        get_line_color=[80, 80, 80, 80],
        highlight_color=[222, 102, 0, 200],
        line_width_min_pixels=0.5,
        pickable=True,
        auto_highlight=True,
        )

    # Calculate the center and zoom level of the map
    bounds = filtered_gdf_map.total_bounds
    center_lon = (bounds[0] + bounds[2]) / 2
    center_lat = (bounds[1] + bounds[3]) / 2
    view_state = pdk.ViewState(latitude=center_lat, longitude=center_lon, min_zoom=6.5, zoom=10)

    ## generate tooltip
    tooltip={"html": "<b>District:</b> {Jurisdiction District Name} <br/> <b>Type:</b> {District Type} <br/> <b> Acreage: </b> {Acres_fmt} "}

    # Display the map to the page
    map = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tooltip,
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json")
    
    return map


def district_comparison(filtered_gdf):
    """
    Displays an interactive AgGrid table and returns selected rows.

    @param gdf: A GeoDataFrame.
    @return: The selected rows in the AgGrid Table.
    """
    
    df = filtered_gdf.copy()
    if "geometry" in df.columns:
        df = df.drop(columns=["geometry"])

    districts = st.multiselect(
        label="Select Districts to Compare",
        options=sorted(df["Jurisdiction District Name"].dropna().unique()))

    return districts


def zoning_comparison_table(filtered_gdf, selected_districts):
    """
    Takes selected rows from AgGrid, creates a comparison table, and displays it.

    @param selected_rows: The selected rows from an AgGrid interactive table.
    @return: The comparison table as a dataframe
    """
    from datetime import datetime
    from functools import reduce
    from streamlit_extras.dataframe_explorer import dataframe_explorer

    if len(selected_districts) == 0:
        return

    filtered_gdf = filtered_gdf[filtered_gdf["Jurisdiction District Name"].isin(selected_districts)]
    
    dfs = []
    for _, row in filtered_gdf.iterrows():
        district_name = row.get("Jurisdiction District Name", "District")
        df_long = pd.DataFrame(row).reset_index()
        df_long.columns = ["Variable", district_name]
        dfs.append(df_long)

    combined_df = reduce(lambda left, right: pd.merge(left, right, on="Variable", how="outer"), dfs)

    st.subheader("District Comparisons")
    filtered_combined_df_sorted = dataframe_explorer(combined_df, case=False)
    st.dataframe(filtered_combined_df_sorted, use_container_width=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")

    st.download_button(
        label="Export Comparison Table to Excel",
        data= (lambda buf=io.BytesIO(): (filtered_combined_df_sorted.to_excel(buf, index=False, engine="openpyxl"), buf.seek(0), buf)[2])(),
        file_name=f"comparison_table_{timestamp}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    return combined_df


def get_acerage_metrics(gdf):
        col1, col2 = st.columns(2)
        col1.metric(label="Districts", value=f"{len(gdf):,}")
        total_acre = gdf["Acres"].sum()
        col2.metric(label="**Total Acreage**", value=f"{total_acre:,.0f} acres")

def plot_acreage(gdf):
    acres_by_type = gdf.groupby("District Type")["Acres"].sum().fillna(0)
    colors = gdf.drop_duplicates("District Type")[["District Type", "hex_color"]]
    
    acres_df = acres_by_type.reset_index().merge(colors, on="District Type", how="left")
    total_acres = acres_df["Acres"].sum()
    acres_df["Percent"] = 100 * acres_df["Acres"] / total_acres

    bar_chart = alt.Chart(acres_df).mark_bar().encode(
        x=alt.X("District Type:N", sort="-y", title="Zoning Type", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("Acres:Q", title="Total Acres"),
        color=alt.Color("hex_color:N", scale=None, legend=None),
        tooltip=[
            "District Type",
            alt.Tooltip("Acres:Q", format=",.0f"),
            alt.Tooltip("Percent:Q", format=".1f", title="% of Total")
        ]
    ).properties(height=500, title="Zoning Acreage by District Type")

    return bar_chart


def clean_zoning_gdf(gdf):
    """
    Place to hold general pands operations, including hardcoded, to clean a zoning gdf. 
    """
    gdf["District Type"] = gdf["District Type"].replace({
        "Primarily Residential": "Residential",
        "Mixed with Residential": "Mixed",
        "Nonresidential": "Nonresidential",
        "Overlay not Affecting Use": "Overlay"
    })
    return gdf
        




#################################### Unused, possible to delete
def filtered_zoning_df(zoning_gdf):
    """
    Applies filters to the zoning GeoDataFrame and returns the filtered results.

    @return: Filtered GeoDataFrame based on sidebar selections.
    """
    from streamlit_extras.dataframe_explorer import dataframe_explorer

    # Define the filtered geography
    county, jurisdiction, districts, refined = zoning_geography(zoning_gdf)

    
    # Apply all filters
    filtered_gdf = filter_zoning_data(zoning_gdf, county, jurisdiction, districts)

    if filtered_gdf.empty:
        st.warning("No districts match your filters.")
        return gpd.GeoDataFrame()

    # Allow user filtering via dataframe_explorer
    filtered_pd = dataframe_explorer(filtered_gdf, case=False)

    # Re-attach geometry from original GeoDataFrame using index
    filtered_gdf = gpd.GeoDataFrame(
        filtered_pd,
        geometry=zoning_gdf.loc[filtered_pd.index, "geometry"],
        crs=zoning_gdf.crs)

    return filtered_gdf, refined




def zoning_geography(zoning_gdf):
    col1, col2, col3 = st.columns(3)
    with col1:
        county = st.selectbox("**County**", ["All Counties"] + sorted(zoning_gdf["County"].dropna().unique()))
    with col2:
        if county != "All Counties":
            jurisdiction_opts = sorted(zoning_gdf[zoning_gdf["County"] == county]["Jurisdiction"].dropna().unique())
        else:
            jurisdiction_opts = sorted(zoning_gdf["Jurisdiction"].dropna().unique())
        jurisdiction = st.selectbox("**Jurisdiction**", ["All Jurisdictions"] + jurisdiction_opts)
    with col3:
        # Filter district options based on current county and jurisdiction selection
        district_filter = zoning_gdf.copy()
        if county != "All Counties":
            district_filter = district_filter[district_filter["County"] == county]
        if jurisdiction != "All Jurisdictions":
            district_filter = district_filter[district_filter["Jurisdiction"] == jurisdiction]

        district_opts = sorted(district_filter["District Name"].dropna().unique())
        districts = st.multiselect("**District(s)**", ["All Districts"] + district_opts, default=["All Districts"])
        
        if jurisdiction == "All Jurisdictions" and county == "All Counties" and "All Districts" in districts:
            refined = False
        else:
            refined = True


        return county, jurisdiction, districts, refined




def filter_zoning_data(_gdf, county, jurisdiction, districts):
    """
    Filters the zoning GeoDataFrame based on selected county, jurisdiction, and districts.

    @param gdf: The original GeoDataFrame containing zoning data.
    @param county: Selected county name as a string, or "All Counties" for no filter.
    @param jurisdiction: Selected jurisdiction name as a string, or "All Jurisdictions" for no filter.
    @param districts: List of selected district names, or a list containing "All Districts" for no filter.
    @return: A filtered GeoDataFrame based on the specified criteria.
    """
    df = _gdf.copy()
    if county != "All Counties":
        df = df[df["County"] == county]
    if jurisdiction != "All Jurisdictions":
        df = df[df["Jurisdiction"] == jurisdiction]
    if "All Districts" not in districts:
        df = df[df["District Name"].isin(districts)]
    
    return df


