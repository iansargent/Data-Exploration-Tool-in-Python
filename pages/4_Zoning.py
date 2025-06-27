"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Zoning Page
"""

# Necessary imports
import streamlit as st
from app_utils import (render_zoning_layer, render_table, render_comparison_table, load_zoning_data)
from streamlit_extras.metric_cards import style_metric_cards 
import pydeck as pdk
import json


def render_zoning_pydeck():
    st.markdown("<h2 style='color: #4a4a4a;'>VT Zoning</h2>", unsafe_allow_html=True)

    # --- Load and Filter Data ---
    load_zoning_data()
    filtered_gdf = render_zoning_layer()

    # --- Convert to GeoJSON ---
    filtered_geojson = json.loads(filtered_gdf.to_json())

    # --- Color Mapping by 'District Type' ---
    zoning_colors = {
        "Primarily Residential": [135, 206, 250],
        "Mixed with Residential": [255, 215, 0],
        "Nonresidential": [255, 99, 71]}

    # Assign colors to each feature
    for feature in filtered_geojson["features"]:
        dtype = feature["properties"].get("District Type", "")
        feature["properties"]["fill_color"] = zoning_colors.get(dtype, [200, 200, 200])

    # --- Pydeck Layer ---
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

    view_state = pdk.ViewState(
        latitude=44.26,
        longitude=-72.57,
        zoom=7.5,
        pitch=0,
    )

    r = pdk.Deck(
        layers=[layer], 
        initial_view_state=view_state,
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json", 
        tooltip={"text": "{District Type}"})
    st.pydeck_chart(r)

    # --- Acreage Summary ---
    st.header("Land Area")
    total_acre = filtered_gdf["Acres"].sum()
    st.metric(label="**Total Acreage**", value=f"{total_acre:,.1f}")

    st.subheader("District Type Land Distribution")
    acres_by_type = filtered_gdf.groupby("District Type")["Acres"].sum().reindex(zoning_colors.keys())

    # Optional: metrics in columns (same as your original UI)
    c2, c3, c4 = st.columns(3)
    c2.metric("**Primarily Residential**", f"{acres_by_type.get('Primarily Residential', 0):,.0f} acres")
    c2.metric("**Primarily Residential** (%)", f"{(acres_by_type.get('Primarily Residential', 0) / total_acre) * 100:.1f}%")

    c3.metric("**Mixed with Residential**", f"{acres_by_type.get('Mixed with Residential', 0):,.0f} acres")
    c3.metric("**Mixed with Residential** (%)", f"{(acres_by_type.get('Mixed with Residential', 0) / total_acre) * 100:.1f}%")

    c4.metric("**Nonresidential**", f"{acres_by_type.get('Nonresidential', 0):,.0f} acres")
    c4.metric("**Nonresidential** (%)", f"{(acres_by_type.get('Nonresidential', 0) / total_acre) * 100:.1f}%")

    # Style cards (optional)
    style_metric_cards(background_color="whitesmoke", border_left_color="mediumseagreen")

    # --- Table + Comparison Section ---
    st.markdown("### Zoning Districts Table")
    selected = render_table(filtered_gdf)
    try:
        if not selected.empty:
            render_comparison_table(selected)
    except Exception as e:
        st.warning(f"No Selected Districts to Compare: {e}")

    return r
            
def show_mapping():
    render_zoning_pydeck()


if __name__ == "__main__":
    show_mapping()