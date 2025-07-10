"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Housing Page (Census)

"""

# Necessary imports
import streamlit as st
import pandas as pd
import matplotlib.cm as cm
from  matplotlib import colormaps
import matplotlib.colors as colors
import pydeck as pdk
import pyogrio
import requests
import io
from app_utils.census import split_name_col, rename_and_merge_census_cols
from app_utils.housing import housing_pop_plot, housing_snapshot
from app_utils.color import render_colorbar, map_outlier_yellow, jenks_color_map, get_colornorm_stats, TopHoldNorm
from streamlit_rendering import filter_dataframe


@st.cache_data()
def load_data():
    # TODO: consider more elaborate caching in session_state vars, etc. 
    # TODO: consider packaging the data directly into the repository.
    st.write("Load Data Function")


@st.cache_data
def load_2023_housing():
    url_2023 = 'https://raw.githubusercontent.com/iansargent/Data-Exploration-Tool-in-Python/main/Data/Census/VT_HOUSING_ALL.fgb'
    housing_gdf_2023 = pyogrio.read_dataframe(url_2023)
    housing_gdf_2023 = split_name_col(housing_gdf_2023)
    
    return housing_gdf_2023


@st.cache_data
def load_2013_housing():
    url_2013 = 'https://raw.githubusercontent.com/iansargent/Data-Exploration-Tool-in-Python/main/Data/Census/VT_HOUSING_ALL_2013.fgb'
    housing_gdf_2013 = pyogrio.read_dataframe(url_2013)
    housing_gdf_2013 = split_name_col(housing_gdf_2013)
    
    return housing_gdf_2013


@st.cache_data
def load_med_value_by_year():
    import requests

    med_value_url = "https://raw.githubusercontent.com/iansargent/Data-Exploration-Tool-in-Python/main/Data/Census/med_home_value_by_year.csv"
    response = requests.get(med_value_url, verify=True) # disables SSL verification
    med_value_df = pd.read_csv(io.StringIO(response.text))     
    med_value_df = split_name_col(med_value_df)
    
    return med_value_df


@st.cache_data
def load_med_smoc_by_year():
    import requests

    med_smoc_url = "https://raw.githubusercontent.com/iansargent/Data-Exploration-Tool-in-Python/main/Data/Census/med_smoc_by_year.csv"
    response = requests.get(med_smoc_url, verify=True) # disables SSL verification
    med_smoc_df = pd.read_csv(io.StringIO(response.text))

    med_smoc_df = split_name_col(med_smoc_df)     
    
    return med_smoc_df


@st.cache_data
def census_housing():
    # Read the Census Housing Datasets (Name column is split here as well!)
    housing_gdf_2023 = load_2023_housing()
    housing_gdf_2013 = load_2013_housing()
    med_val_df = load_med_value_by_year()

    # Split the "name" column into separate "County" and "Jurisdiction" columns, then rename the cols
    tidy_2023 = rename_and_merge_census_cols(housing_gdf_2023)

    return housing_gdf_2023, housing_gdf_2013, med_val_df, tidy_2023


def census_housing_page():
    # Page title
    st.header("Housing", divider="grey")

    mapping, snapshot = st.tabs(tabs=["Mapping", "Snapshot"])

    #TODO: Working on a load_data function above
    # housing_gdf_2023, housing_gdf_2013, med_val_df, tidy_2023 = load_data()
    
    # Define and load the datasets
    housing_gdf_2023, housing_gdf_2013, med_val_df, tidy_2023 = census_housing()
    med_smoc_df = load_med_smoc_by_year()
    
    # Compute statewide average median home value by year
    statewide_avg_val_df = (med_val_df.groupby("year", as_index=False)["estimate"].mean())
    statewide_avg_smoc_df = (med_smoc_df.groupby(["year", "variable"], as_index=False)["estimate"].mean())

    ##  The map section ## 
    with mapping:
        st.subheader("Mapping")
        
        # Project meaningful columns to lat/long
        filtered_2023 = filter_dataframe(tidy_2023, filter_columns=["Category", "Subcategory", "Variable", "Measure"])
        filtered_2023 = filtered_2023.to_crs(epsg=4326)

        # Normalize the housing variable for monochromatic chloropleth coloring
        vmin, vmax, cutoff  = get_colornorm_stats(filtered_2023, 5)
        cmap = colormaps["Reds"]
        
        norm = colors.Normalize(vmin=vmin, vmax=vmax)
        cmap = cm.get_cmap("Reds")

        style = st.radio("Outlier Handling:", options=["Holdout", "Yellow", "Jenk's Natural Breaks"], horizontal=True)

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


    # Housing Snapshot
    with snapshot:
        st.subheader("Housing Snapshot")
        # Include a source for the dataset (Census DP04 2023 5-year estimates)
        st.markdown("***Data Source***: U.S. Census Bureau. (2023). DP04: Selected Housing Characteristics - " \
        "County Subdivisions, Vermont. 2019-2023 American Community Survey 5-Year Estimates. " \
        "Retrieved from https://data.census.gov/")

        # Allow user to filter on the county and jurisdiction level for tailored reports 
        # TODO: (maybe) put the filtering into it's own logic so that we can use it across pages. 
        col1, col2, col3 = st.columns(3)
        # County selection
        with col1:
            county = st.selectbox("**County**", ["All Counties"] + sorted(housing_gdf_2023["County"].dropna().unique()))
        # Jurisdiction selection
        with col2:
            if county != "All Counties":
                jurisdiction_list = sorted(housing_gdf_2023[housing_gdf_2023["County"] == county]["Jurisdiction"].dropna().unique())
            else:
                jurisdiction_list = sorted(housing_gdf_2023["Jurisdiction"].dropna().unique())
            jurisdiction = st.selectbox("**Jurisdiction**", ["All Jurisdictions"] + jurisdiction_list)

        # Create a "filtered" 2023 dataset with the selected county and jurisdiction options
        filtered_gdf_2023 = housing_gdf_2023.copy()
        filtered_gdf_2013 = housing_gdf_2013.copy()
        filtered_med_val_df = med_val_df.copy()
        filtered_med_smoc_df = med_smoc_df.copy()
        if county != "All Counties":
            filtered_gdf_2023 = filtered_gdf_2023[filtered_gdf_2023["County"] == county]
            filtered_gdf_2013 = filtered_gdf_2013[filtered_gdf_2013["County"] == county]
            filtered_med_val_df = filtered_med_val_df[filtered_med_val_df["County"] == county]
            filtered_med_smoc_df = filtered_med_smoc_df[filtered_med_smoc_df["County"] == county]
        
        if jurisdiction != "All Jurisdictions":
            filtered_gdf_2023 = filtered_gdf_2023[filtered_gdf_2023["Jurisdiction"] == jurisdiction]
            filtered_gdf_2013 = filtered_gdf_2013[filtered_gdf_2013["Jurisdiction"] == jurisdiction]
            filtered_med_val_df = filtered_med_val_df[filtered_med_val_df["Jurisdiction"] == jurisdiction]
            filtered_med_smoc_df = filtered_med_smoc_df[filtered_med_smoc_df["Jurisdiction"] == jurisdiction]
        
        # Selection for the baseline comparison (same area 10 years ago OR current statewide averages)
        with col3:
            # Add a selection for the baseline metrics to compare to
            compare_to = st.selectbox(
                label = "**Comparison Basis**",
                options = ["2013 Local Data (10-Year Change)", "2023 Vermont Statewide Averages"],
                index=0)

        # Read in VT historical population data on the census tract level
        # NOTE: Include a source for this as well (VT Open Data Portal)
        pop_url = "https://raw.githubusercontent.com/iansargent/Data-Exploration-Tool-in-Python/main/Data/Census/VT_Historical_Population.csv"
        response = requests.get(pop_url, verify=False)
        pop_df = pd.read_csv(io.StringIO(response.text))    
        # Display the time series plot of population, housing units, and new housing units
        housing_pop_plot(county, jurisdiction, filtered_gdf_2023, pop_df)
        
        # Display formatted housing metrics vs statewide averages
        housing_snapshot(county, jurisdiction, 
                        filtered_gdf_2013, filtered_gdf_2023, housing_gdf_2023, 
                        filtered_med_val_df, filtered_med_smoc_df, 
                        statewide_avg_val_df, statewide_avg_smoc_df, compare_to)


def show_housing():
    # Display the page
    census_housing_page()


if __name__ == "__main__":
    show_housing()