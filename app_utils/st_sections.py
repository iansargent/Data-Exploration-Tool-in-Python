import streamlit as st
from app_utils.color import render_colorbar, map_outlier_yellow, jenks_color_map, get_colornorm_stats, TopHoldNorm
from  matplotlib import colormaps
import matplotlib.cm as cm
import matplotlib.colors as colors
import pydeck as pdk
from streamlit_rendering import filter_dataframe


def mapping_tab(data): 
    st.subheader("Mapping")
    
    # Project meaningful columns to lat/long
    filtered_2023 = filter_dataframe(data, filter_columns=["Category", "Subcategory", "Variable", "Measure"])
    filtered_2023 = filtered_2023.to_crs(epsg=4326)

    # Normalize the housing variable for monochromatic chloropleth coloring
    vmin, vmax, cutoff  = get_colornorm_stats(filtered_2023, 5)
    cmap = colormaps["Reds"]
    
    norm = colors.Normalize(vmin=vmin, vmax=vmax)
    cmap = cm.get_cmap("Reds")

    style = st.radio("Outlier Handling:", options=["Jenk's Natural Breaks", "Yellow", "Holdout"], horizontal=True)

    if style == "Holdout":
        # Option One:  Outliers get the top 10% of the norm (same color, just gradation shifts)
        norm = TopHoldNorm(vmin=vmin, vmax=vmax, cutoff=cutoff, outlier_fraction=0.1)
        # Convert colors to [R, G, B, A] values
        filtered_2023["fill_color"] = filtered_2023['Value'].apply(
            lambda x: [int(c * 255) for c in cmap(norm(x))[:3]] + [180])
        render_colorbar(cmap=cmap, norm=norm, vmin=vmin, vmax=vmax, cutoff=cutoff, style=style)
    
    elif style == "Yellow":
        # Option Two: Outliers get a separate color (yellow)
        norm = colors.Normalize(vmin=vmin, vmax=cutoff, clip=False)
        filtered_2023["fill_color"] = filtered_2023["Value"].apply(
            lambda x: map_outlier_yellow(x, cmap, norm, cutoff))
        render_colorbar(cmap=cmap, norm=norm, vmin=vmin, vmax=vmax, cutoff=cutoff, style=style)
    
    elif style == "Jenk's Natural Breaks":
        # Option Two: Jenk's Natural Breaks Algorithm
        # Using a slider, adjust the number of "groups" in the data
        col1, _, _ = st.columns(3)
        n_classes = col1.slider(label="Adjust the level of detail", value=10, min_value=5, max_value=15)
        # Define the Jenk's colormap and apply it to the dataframe
        jenks_cmap_dict = jenks_color_map(filtered_2023, n_classes, "Reds")
        filtered_2023['fill_color'] = filtered_2023['color_groups'].astype(str).map(jenks_cmap_dict)
        # Fill null values with a transparent color
        filtered_2023['fill_color'] = filtered_2023['fill_color'].fillna("(0, 0, 0, 0)")

    # Convert the geometry column to GeoJSON coordinates
    filtered_2023["coordinates"] = filtered_2023.geometry.apply(
        lambda geom: geom.__geo_interface__["coordinates"]) 

    # Chloropleth map layer
    polygon_layer = pdk.Layer(
        "PolygonLayer",
        data=filtered_2023,
        get_polygon="coordinates[0]",
        get_fill_color="fill_color",
        pickable=True,
        auto_highlight=True)

    # Set the map center and zoom settings
    view_state = pdk.ViewState(latitude=44.26, longitude=-72.57, min_zoom=6.5, zoom=7)

    # Display the map to the page
    st.pydeck_chart(pdk.Deck(
        layers=[polygon_layer],
        initial_view_state=view_state,
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
        tooltip={"text": "{Jurisdiction}: {Value}"}), height=550)
    

def compare_tab(data):
    st.radio("Hmm", ["help", "please"])