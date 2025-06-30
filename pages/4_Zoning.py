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
import json
from app_utils import render_zoning_layer, render_table, render_comparison_table, load_zoning_data


def zoning():
    # Page header
    st.header("Zoning")

    # Load the zoning data from GitHub
    load_zoning_data()
    # Define the zoning data as a GeoDataFrame
    filtered_gdf = render_zoning_layer()

    # Convert gdf into GeoJSON format
    filtered_geojson = json.loads(filtered_gdf.to_json())

    # Set each District Type to its own map color
    zoning_colors = {
        "Primarily Residential": [135, 206, 250],
        "Mixed with Residential": [255, 215, 0],
        "Nonresidential": [255, 99, 71]}
    # Assign the colors to each district type
    for feature in filtered_geojson["features"]:
        dtype = feature["properties"].get("District Type", "")
        feature["properties"]["fill_color"] = zoning_colors.get(dtype, [200, 200, 200])

    # Create a pydeck layer for mapping the zoning data
    layer = pdk.Layer(
        "GeoJsonLayer",
        data=filtered_geojson,
        get_fill_color="properties.fill_color",
        get_line_color=[80, 80, 80],
        line_width_min_pixels=0.5,
        pickable=True,
        auto_highlight=True,
        stroked=True,
        filled=True,
    )
    # Set the initial view state centered on VT
    view_state = pdk.ViewState(latitude=44.26, longitude=-72.57, zoom=7.5)

    # Define the pydeck map
    map = pdk.Deck(
        layers=[layer], 
        initial_view_state=view_state,
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json", 
        tooltip={"text": "{Jurisdiction District Name}" "\n ({District Type})"}
    )
    
    # Display the map to the page
    st.pydeck_chart(map)

    st.markdown("---")
    
    # Total acres of land plotted on the map
    st.header("Land Area")
    total_acre = filtered_gdf["Acres"].sum()
    st.metric(label="**Total Acreage**", value=f"{total_acre:,.1f}")

    # Acreage by district type
    st.subheader("District Type Land Distribution")
    # Acreage sum grouped by district type
    acres_by_type = filtered_gdf.groupby("District Type")["Acres"].sum().reindex(zoning_colors.keys()).fillna(0)

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