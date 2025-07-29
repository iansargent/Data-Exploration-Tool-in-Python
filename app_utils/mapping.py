
import pydeck as pdk
import json
import geopandas as gpd


def build_layer(geojson, name="GeoJsonLayer"):
    """
    Function to take a geojson and make a layer from it. 
    NOTE: requires that geojson has the "properties.fill_rgba in it for a fill color. 
    """
    layer = pdk.Layer(
        name,
        data=geojson,
        get_fill_color="properties.rgba_color",
        get_line_color=[80, 80, 80, 80],
        highlight_color=[222, 102, 0, 200],
        line_width_min_pixels=0.5,
        pickable=True,
        auto_highlight=True,
        )

    return layer

def map_gdf_single_layer(gdf, view_state=None):
    """
    Function to convert gdf into geojson and then map it with tooltip. 
    """
    geojson = json.loads(gdf.to_json())

    ## create the layer
    layer = build_layer(geojson)

    # Calculate the center and zoom level of the map
    if not view_state:
        bounds = gdf.total_bounds
        center_lon = (bounds[0] + bounds[2]) / 2
        center_lat = (bounds[1] + bounds[3]) / 2
        view_state = pdk.ViewState(latitude=center_lat, longitude=center_lon, min_zoom=6.5, zoom=10)

    tooltip = {"html" : "{tooltip}"}

    # return the map with layer
    return pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tooltip,
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json")

def add_tooltip_from_dict(gdf, label_to_col):
    """
    Adds a tooltip column (for pydeck) a dictionary with format "show_name" : "column name"
    """
    gdf = gdf.copy()
    gdf['tooltip'] = gdf.apply(
        lambda row: "<br/>".join(
            f"<b>{label}:</b> {row[col]}" for label, col in label_to_col.items()
        ),
        axis=1
    )
    return gdf


def mulit_layer_map(gdfs):
    geojsons = [json.loads(gdf.to_json()) for gdf in gdfs]
    layers = [build_layer(jsn) for jsn in geojsons]
    view_state=pdk.ViewState(latitude=44.26, longitude=-72.57, min_zoom=6.5, zoom=7)
    tooltip = {"html" : "{tooltip}"}

    return pdk.Deck(layers=layers, initial_view_state=view_state, tooltip=tooltip,
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json")

def spatial_join(core_gdf, alt_gdf, columns = ['County', 'District']):

    core_gdf = core_gdf.to_crs(alt_gdf.crs)

    joined=gpd.sjoin(alt_gdf, core_gdf, how="left", predicate="intersects")
    st.write(joined)

