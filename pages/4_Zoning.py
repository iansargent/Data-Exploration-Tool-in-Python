"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Zoning Page
"""

# Necessary imports
import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards 
import pydeck as pdk
import altair as alt
import json
from app_utils import render_zoning_layer, render_table, render_comparison_table, load_zoning_data


def zoning():
    # Page header
    st.header("Zoning")

    # Load the zoning data from GitHub
    load_zoning_data()
    # Define the zoning data as a GeoDataFrame
    filtered_gdf = render_zoning_layer()
    # Simplify the geometry for computing performance
    filtered_gdf["geometry"] = filtered_gdf["geometry"].simplify(0.0001, preserve_topology=True)

    filtered_gdf_map = filtered_gdf[["Jurisdiction District Name", "District Type", "geometry"]]
    # Convert gdf into GeoJSON format
    filtered_geojson = json.loads(filtered_gdf_map.to_json())

    # Create a pydeck layer for mapping the zoning data
    layer = pdk.Layer(
        "GeoJsonLayer",
        data=filtered_geojson,
        get_fill_color=[95, 165, 231, 200],
        get_line_color=[80, 80, 80, 80],
        highlight_color=[222, 102, 0, 200],
        line_width_min_pixels=0.5,
        pickable=True,
        auto_highlight=True
    )

    # Calculate the center and zoom level of the map
    bounds = filtered_gdf.total_bounds
    center_lon = (bounds[0] + bounds[2]) / 2
    center_lat = (bounds[1] + bounds[3]) / 2
    view_state = pdk.ViewState(latitude=center_lat, longitude=center_lon, zoom=9)

    # Define the pydeck map
    map = pdk.Deck(
        layers=[layer], 
        initial_view_state=view_state,
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json", 
        tooltip={"text": "{Jurisdiction District Name}" "\n ({District Type})"},
    )
    
    # Display the map to the page
    st.pydeck_chart(map, height=550)

    st.markdown("---")
    
    # Total acres of land plotted on the map
    st.header("Land Area")
    total_acre = filtered_gdf["Acres"].sum()
    st.metric(label="**Total Acreage**", value=f"{total_acre:,.1f}")

    # Acreage by district type
    st.subheader("District Type Land Distribution")
    # Acreage sum grouped by district type
    acres_by_type = filtered_gdf.groupby("District Type")["Acres"].sum().fillna(0)
    acres_df = acres_by_type.reset_index()
    acres_df.columns = ["District Type", "Acres"]
    acres_df["District Type"] = acres_df["District Type"].replace({
        "Primarily Residential": "Residential",
        "Mixed with Residential": "Mixed",
        "Nonresidential": "Nonresidential",
        "Overlay not Affecting Use": "Overlay"
    })

    # Altair bar chart
    bar_chart = alt.Chart(acres_df).mark_bar().encode(
        x=alt.X("District Type:N", sort="-y", title="Zoning Type", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("Acres:Q", title="Total Acres"),
        color=alt.Color("District Type:N", legend=None),
        tooltip=["District Type", alt.Tooltip("Acres:Q", format=",")]
    ).properties(height=500, title="Zoning Acreage by District Type")

    st.altair_chart(bar_chart, use_container_width=True)


    # Display acreage for residential, mixed, and nonresidential (with relative % land)
    c2, c3, c4 = st.columns(3)
    c2.metric("**Primarily Residential**", f"{acres_by_type.get('Primarily Residential', 0):,.0f} acres")
    c2.metric("**Primarily Residential** (%)", f"{(acres_by_type.get('Primarily Residential', 0) / total_acre) * 100:.1f}%")

    c3.metric("**Mixed with Residential**", f"{acres_by_type.get('Mixed with Residential', 0):,.0f} acres")
    c3.metric("**Mixed with Residential** (%)", f"{(acres_by_type.get('Mixed with Residential', 0) / total_acre) * 100:.1f}%")

    c4.metric("**Nonresidential**", f"{acres_by_type.get('Nonresidential', 0):,.0f} acres")
    c4.metric("**Nonresidential** (%)", f"{(acres_by_type.get('Nonresidential', 0) / total_acre) * 100:.1f}%")

    # Style cards to look better
    style_metric_cards(background_color="whitesmoke", border_left_color="mediumseagreen")

    # Selectable Table for comparisons
    st.subheader("Zoning Districts Table")
    selected = render_table(filtered_gdf)
    
    try:
        # If a district(s) is selected from the table above, show the comparison table
        if not selected.empty:
            render_comparison_table(selected)
    except Exception as e:
        st.warning(f"No Selected Districts to Compare: {e}")

    return map
            
def show_zoning():
    zoning()


if __name__ == "__main__":
    show_zoning()