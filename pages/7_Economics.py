"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Economics Page (Census)
"""

# Necessary imports
import streamlit as st
import pydeck as pdk
import pyogrio
from app_utils.color import jenks_color_map
from app_utils.economic import economic_snapshot
from app_utils.census import split_name_col, rename_and_merge_census_cols
from streamlit_rendering import filter_dataframe


@st.cache_data
def load_2023_economics():
    url_2023 = 'https://raw.githubusercontent.com/iansargent/Data-Exploration-Tool-in-Python/main/Data/Census/VT_ECONOMIC_ALL.fgb'
    economics_gdf_2023 = pyogrio.read_dataframe(url_2023)
    economics_gdf_2023 = split_name_col(economics_gdf_2023)
    
    return economics_gdf_2023


def census_economics_page():
    # Page header
    st.header("Economics", divider="grey")

    mapping, snapshot = st.tabs(tabs=["Mapping", "Snapshot"])

    econ_gdf_2023 = load_2023_economics()
    tidy_2023 = rename_and_merge_census_cols(econ_gdf_2023)

    with mapping:
        st.subheader("Mapping")
        
        # Select the combination of vars we're interested in
        filtered_2023 = filter_dataframe(tidy_2023, filter_columns=["Category", "Subcategory", "Variable", "Measure"])
        # Project geometry to latitude and longitude coordinates
        filtered_2023 = filtered_2023.to_crs(epsg=4326)

        col1, _, _ = st.columns(3)
        n_classes = col1.slider(label="Adjust the level of detail", value=10, min_value=5, max_value=15)
        # Define the Jenk's colormap and apply it to the dataframe
        jenks_cmap_dict = jenks_color_map(filtered_2023, n_classes, "Greens")
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
            auto_highlight=True,
        )

        # Set the map center and zoom level
        view_state = pdk.ViewState(latitude=44.26, longitude=-72.57, min_zoom=6.5, zoom=7)

        # Display the map to the page
        st.pydeck_chart(pdk.Deck(
            layers=[polygon_layer],
            initial_view_state=view_state,
            map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
            tooltip={"text": "{Jurisdiction}: {Value}"}), height=550)

    ## Economic Snapshot
    with snapshot:
        st.subheader("Economic Snapshot")
        st.markdown("***Data Source***: U.S. Census Bureau. (2023). DP03: Selected Economic Characteristics - " \
        "County Subdivisions, Vermont. 2019-2023 American Community Survey 5-Year Estimates. " \
        "Retrieved from https://data.census.gov/")
        # Allow user to filter on the county and jurisdiction level for tailored reports 
        # TODO: (maybe) put the filtering into it's own logic so that we can use it across pages. 
        col1, col2, col3 = st.columns(3)
        # County selection
        with col1:
            county = st.selectbox("**County**", ["All Counties"] + sorted(econ_gdf_2023["County"].dropna().unique()))
        # Jurisdiction selection
        with col2:
            if county != "All Counties":
                jurisdiction_list = sorted(econ_gdf_2023[econ_gdf_2023["County"] == county]["Jurisdiction"].dropna().unique())
            else:
                jurisdiction_list = sorted(econ_gdf_2023["Jurisdiction"].dropna().unique())
            jurisdiction = st.selectbox("**Jurisdiction**", ["All Jurisdictions"] + jurisdiction_list)

        # Create a "filtered" 2023 dataset with the selected county and jurisdiction options
        filtered_gdf_2023 = econ_gdf_2023.copy()
        
        if county != "All Counties":
            filtered_gdf_2023 = filtered_gdf_2023[filtered_gdf_2023["County"] == county]
        
        if jurisdiction != "All Jurisdictions":
            filtered_gdf_2023 = filtered_gdf_2023[filtered_gdf_2023["Jurisdiction"] == jurisdiction]
        
        # Selection for the baseline comparison (same area 10 years ago OR current statewide averages)
        with col3:
            # Add a selection for the baseline metrics to compare to
            compare_to = st.selectbox(
                label = "**Comparison Basis**",
                options = ["2013 Local Data (10-Year Change)", "2023 Vermont Statewide Averages"],
                index=0)

        # Read in VT historical population data on the census tract level
        # Display the time series plot of population, housing units, and new housing units
        
        # Display formatted housing metrics vs statewide averages
        economic_snapshot(county, jurisdiction, filtered_gdf_2023)


            
def show_economics():
    # Display the page
    census_economics_page()


if __name__ == "__main__":
    show_economics()