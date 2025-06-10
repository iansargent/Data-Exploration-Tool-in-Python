"""
Ian Sargent
ORCA
Streamlit Data Visualization App

Housing Page (Census)

This data was extracted from the DP04 
"Selected Housing Variables" Dataset
"""

# Necessary imports
import streamlit as st
import pandas as pd
import geopandas as gpd
import leafmap.foliumap as leafmap
from app_utils import split_name_col
from streamlit_extras.metric_cards import style_metric_cards
import altair as alt


def render_mapping():
    st.markdown("<h2 style='color: #4a4a4a;'>VT Housing</h2>", unsafe_allow_html=True)

    m = leafmap.Map(center=[44.26, -72.57], zoom=8, zoom_snap=0.5)
    m.add_basemap("CartoDB.Positron")

    housing_gdf = gpd.read_file('/Users/iansargent/Desktop/ORCA/Steamlit App Testing/Census/VT_HOUSING_ALL.fgb')
    housing_gdf = split_name_col(housing_gdf)

    numeric_cols = [col for col in housing_gdf.columns if housing_gdf[col].dtype in ['int64', 'float64']]
    housing_variable = st.selectbox("Select a Housing variable", numeric_cols)

    # Create map
    housing_gdf_map = housing_gdf[["County", "Jurisdiction", housing_variable, "geometry"]].dropna()

    m.add_data(
        housing_gdf_map,
        column=housing_variable,
        scheme="NaturalBreaks",
        cmap="Reds",
        legend_title=housing_variable,
        layer_name="Housing",
        color = "pink")

    # --- Always Show the Map ---
    m.to_streamlit(height=600)

    st.header("Census Snapshot", divider="grey")

    col1, col2 = st.columns(2)
    with col1:
        county = st.selectbox("**County**", ["All Counties"] + sorted(housing_gdf["County"].dropna().unique()))

    with col2:
        if county != "All Counties":
            jurisdiction_list = sorted(housing_gdf[housing_gdf["County"] == county]["Jurisdiction"].dropna().unique())
        else:
            jurisdiction_list = sorted(housing_gdf["Jurisdiction"].dropna().unique())
        jurisdiction = st.selectbox("**Jurisdiction**", ["All Jurisdictions"] + jurisdiction_list)


    filtered_gdf = housing_gdf.copy()

    if county != "All Counties":
        filtered_gdf = filtered_gdf[filtered_gdf["County"] == county]

    if jurisdiction != "All Jurisdictions":
        filtered_gdf = filtered_gdf[filtered_gdf["Jurisdiction"] == jurisdiction]


    # HOUSING METRICS
    # Total units, occupied, vacant
    st.subheader("Occupancy")
    c1, c2, c3 = st.columns(3)
    c5, c6 = st.columns(2)
    c1.metric(label="Housing Units", value=f"{filtered_gdf['DP04_0001E'].sum():,.0f}")
    c2.metric(label="Units Occupied", value=f"{filtered_gdf['DP04_0002E'].sum():,.0f}")
    c3.metric(label="Units Vacant", value=f"{filtered_gdf['DP04_0003E'].sum():,.0f}")
    # % Occupied, % Vacant
    pct_occ = (filtered_gdf['DP04_0002E'].sum() / filtered_gdf['DP04_0001E'].sum()) * 100
    pct_vac = (filtered_gdf['DP04_0003E'].sum() / filtered_gdf['DP04_0001E'].sum()) * 100
    c5.metric(label="Percentage of Units Occupied", value=f"{pct_occ:.1f}%")
    c6.metric(label="Percentage of Units Vacant", value=f"{pct_vac:.1f}%")

    
    mobile_homes = filtered_gdf['DP04_0015E'].sum()
    if mobile_homes > 0:
        st.subheader("Units in Structure")
        c7 = st.container()
        c7.metric(label="Mobile Homes", value=f"{filtered_gdf['DP04_0015E'].sum():,.0f}")


    st.subheader("Construction")
    pop_df = pd.read_csv('/Users/iansargent/Desktop/ORCA/Steamlit App Testing/Census/historical_county_populations_v2.csv')
    pop_df = pop_df[pop_df['cty'].str.lower().str.endswith("vermont")].copy()
    # --- Map housing bins to corresponding decades ---
    year_bins = [
        "1939 or Earlier", "1940 - 1949", "1950 - 1959", "1960 - 1969",
        "1970 - 1979", "1980 - 1989", "1990 - 1999", "2000 - 2009",
        "2010 - 2019", "2020 - Present"
    ]
    pop_years = [1930, 1940, 1950, 1960, 1970, 1980, 1990, 2000, 2010, 2020]

    # --- Get housing unit counts ---
    raw_housing_counts = [
        filtered_gdf["DP04_0026E"].sum(),
        filtered_gdf["DP04_0025E"].sum(),
        filtered_gdf["DP04_0024E"].sum(),
        filtered_gdf["DP04_0023E"].sum(),
        filtered_gdf["DP04_0022E"].sum(),
        filtered_gdf["DP04_0021E"].sum(),
        filtered_gdf["DP04_0020E"].sum(),
        filtered_gdf["DP04_0019E"].sum(),
        filtered_gdf["DP04_0018E"].sum(),
        filtered_gdf["DP04_0017E"].sum()
    ]

    cumulative_housing_counts = pd.Series(raw_housing_counts).cumsum().tolist()

    pop_cols = [f"pop_{year}" for year in pop_years]

    for col in pop_cols:
        pop_df[col] = pd.to_numeric(pop_df[col], errors='coerce').fillna(0)

    # sum only population columns
    state_totals = pop_df[pop_cols].sum()

    # add a new row for Vermont with cty = 'Vermont'
    vermont_row = pd.DataFrame([["Vermont"] + state_totals.tolist()], columns=["cty"] + pop_cols)
    pop_df = pd.concat([pop_df, vermont_row], ignore_index=True)
    

    if county == "All Counties":
        county = "Vermont"
        county_plot_title = "Vermont"
        pop_label = "Statewide Population"
    elif county != "All Counties" and jurisdiction == "All Jurisdictions":
        county_plot_title = f"{county} County"
        county = f"{county} County, Vermont"
        pop_label = "County Level Population"
    elif county != "All Counties" and jurisdiction != "All Jurisdictions":
        county_plot_title = f"{jurisdiction}, {county} County"
        county = f"{county} County, Vermont"
        pop_label = "County Level Population"


    # --- Match county and extract population values ---
    county_row = pop_df[pop_df['cty'].str.lower() == county.lower()]

    if county_row.empty:
        st.error(f"No population data found for: {county}")
    else:
        pop_values = [county_row[f"pop_{year}"].values[0] for year in pop_years]

        # --- Build DataFrame for plotting ---
        overlay_df = pd.DataFrame({
            "Year Bin": year_bins,
            "Housing Units": cumulative_housing_counts,
            f"{pop_label}": pop_values
        })

        overlay_df['Census Year'] = pop_years

        melted = overlay_df.melt(id_vars=["Year Bin", "Census Year"], var_name="Metric", value_name="Value")

        # Base chart with color-encoded Metric (enables legend)
        base = alt.Chart(melted).encode(
            x=alt.X("Year Bin", sort=year_bins, title="Year Built"),
            y=alt.Y("Value"),
            color=alt.Color("Metric", scale=alt.Scale(
                domain=["Housing Units", pop_label],
                range=["steelblue", "red"]), 
                legend=alt.Legend(
                    title="",
                    orient="bottom-right",
                    offset=-2))
        ).interactive()

        final_chart = base.mark_line(point=True).properties(
            height=500,
            title=f"Housing Units vs Population in {county_plot_title}")

        st.altair_chart(final_chart, use_container_width=True)

    style_metric_cards(
        background_color="whitesmoke",
        border_left_color="red",
        box_shadow=True,
        border_size_px=0.5
    )



    st.subheader("Housing Data")
    st.dataframe(filtered_gdf)

    # st.dataframe(housing_gdf[["County", "Jurisdiction", housing_variable]])

    return m


def show_mapping():
    # Display the page
    render_mapping()


if __name__ == "__main__":
    show_mapping()