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

    st.header("Housing Snapshot")
    st.markdown("***Data Source***: U.S. Census Bureau. (2023). DP04: Selected Housing Characteristics - " \
    "County Subdivisions, Vermont. 2019-2023 American Community Survey 5-Year Estimates. " \
    "Retrieved June 11, 2025, from https://data.census.gov/")
    st.markdown("*Note*: The displayed deviations in the metric cards are comparing values to VT statewide averages.")

    col1, col2 = st.columns(2)
    with col1:
        county = st.selectbox("**County**", ["All Counties"] + sorted(housing_gdf["County"].dropna().unique()))

    with col2:
        if county != "All Counties":
            jurisdiction_list = sorted(housing_gdf[housing_gdf["County"] == county]["Jurisdiction"].dropna().unique())
        else:
            jurisdiction_list = sorted(housing_gdf["Jurisdiction"].dropna().unique())
        jurisdiction = st.selectbox("**Jurisdiction**", ["All Jurisdictions"] + jurisdiction_list)

    st.markdown("---")
    
    filtered_gdf = housing_gdf.copy()

    if county != "All Counties":
        filtered_gdf = filtered_gdf[filtered_gdf["County"] == county]

    if jurisdiction != "All Jurisdictions":
        filtered_gdf = filtered_gdf[filtered_gdf["Jurisdiction"] == jurisdiction]


    # HOUSING METRICS
    st.subheader("Housing Units")
    c1 = st.container()
    c2, c3 = st.columns(2)
    st.markdown("---")
    
    st.subheader("Occupied Housing Tenure")
    c4, c5, c6 = st.columns(3)
    st.markdown("---")
    
    st.subheader("Owner Occupied Units")
    c7, c8 = st.columns(2)
    st.markdown("---")
    
    st.subheader("Rented Units")
    c9, c10 = st.columns(2)
    st.markdown("---")

    # Total units
    c1.metric(
        label="**Total** Housing Units", 
        value=f"{filtered_gdf['DP04_0001E'].sum():,.0f}"
    )

    # Vacant Units    
    pct_vac = (filtered_gdf['DP04_0003E'].sum() / filtered_gdf['DP04_0001E'].sum()) * 100
    state_pct_vac = (housing_gdf['DP04_0003E'].sum() / housing_gdf['DP04_0001E'].sum()) * 100
    pct_vac_delta = pct_vac - state_pct_vac
    c2.metric(
        label="**Vacant** Units", 
        value=f"{filtered_gdf['DP04_0003E'].sum():,.0f}"
    )
    c2.metric(
        label="**Vacant** Units (%)", 
        value=f"{pct_vac:.1f}%",
        delta=f"{pct_vac_delta:.1f}%"
    )
        
    # Occupied Units
    pct_occ = (filtered_gdf['DP04_0002E'].sum() / filtered_gdf['DP04_0001E'].sum()) * 100
    state_pct_occ = (housing_gdf['DP04_0002E'].sum() / housing_gdf['DP04_0001E'].sum()) * 100
    pct_occ_delta = pct_occ - state_pct_occ
    c3.metric(
        label="**Occupied** Units", 
        value=f"{filtered_gdf['DP04_0002E'].sum():,.0f}"
    ) 
    c3.metric(
        label="**Occupied** Units (%)", 
        value=f"{pct_occ:.1f}%",
        delta=f"{pct_occ_delta:.1f}%"
    )   

    # Units Owned
    state_pct_own = (housing_gdf['DP04_0046E'].sum() / housing_gdf['DP04_0002E'].sum()) * 100
    pct_own = (filtered_gdf['DP04_0046E'].sum() / filtered_gdf['DP04_0002E'].sum()) * 100
    pct_own_delta = pct_own - state_pct_own
    c4.metric(
        label="**Owned**", 
        value=f"{filtered_gdf['DP04_0046E'].sum():,.0f}"
    )
    c4.metric(
        label="**Owned** (%)", 
        value=f"{pct_own:.1f}%",
        delta=f"{pct_own_delta:.1f}%"
    )
    
    # Units Rented
    state_pct_rent = (housing_gdf['DP04_0047E'].sum() / housing_gdf['DP04_0002E'].sum()) * 100
    pct_rent = (filtered_gdf['DP04_0047E'].sum() / filtered_gdf['DP04_0002E'].sum()) * 100
    pct_rent_delta = pct_rent - state_pct_rent
    c5.metric(
        label="**Rented**", 
        value=f"{filtered_gdf['DP04_0047E'].sum():,.0f}"
    )
    c5.metric(
        label="**Rented** (%)", 
        value=f"{pct_rent:.1f}%",
        delta=f"{pct_rent_delta:.1f}%"
    )
    
    # Units with Lack of Complete Plumbing
    state_pct_lack_plumbing = (housing_gdf['DP04_0073E'].sum() / housing_gdf['DP04_0002E'].sum()) * 100
    pct_lack_plumbing = (filtered_gdf['DP04_0073E'].sum() / filtered_gdf['DP04_0002E'].sum()) * 100
    pct_lack_plumbing_delta = pct_lack_plumbing - state_pct_lack_plumbing
    c6.metric(
        label="Units **Lacking Plumbing**", 
        value=f"{filtered_gdf['DP04_0073E'].sum():,.0f}"
    )
    c6.metric(
        label="Units **Lacking Plumbing** (%)", 
        value=f"{pct_lack_plumbing:.1f}%",
        delta=f"{pct_lack_plumbing_delta:.1f}%",
        delta_color="inverse"
    )
    
    state_avg_med_val = housing_gdf['DP04_0089E'].mean()
    avg_med_val = filtered_gdf['DP04_0089E'].mean()
    avg_med_val_delta = avg_med_val - state_avg_med_val
    c7.metric(
        label="(Average) Median **Home Value**", 
        value=f"${avg_med_val:,.2f}",
        delta=f"{avg_med_val_delta:,.2f}",
        delta_color="inverse"
    )
    
    state_avg_med_mort = housing_gdf['DP04_0101E'].mean()
    avg_med_mort = filtered_gdf['DP04_0101E'].mean()
    avg_med_mort_delta = avg_med_mort - state_avg_med_mort
    c8.metric(
        label="(Average) Median **Mortgage Payment**", 
        value=f"${avg_med_mort:,.2f}",
        delta=f"{avg_med_mort_delta:,.2f}",
        delta_color="inverse"
    )
    
    state_avg_med_gross_rent = housing_gdf['DP04_0134E'].mean()
    avg_med_gross_rent = filtered_gdf['DP04_0134E'].mean()
    avg_med_gross_rent_delta = avg_med_gross_rent - state_avg_med_gross_rent
    c9.metric(
        label="(Average) Median **Gross Rent**", 
        value=f"${avg_med_gross_rent:,.2f}",
        delta=f"{avg_med_gross_rent_delta:,.2f}",
        delta_color="inverse"
    )
    
    state_rent_burden_pct = (housing_gdf['DP04_0142E'].sum() / housing_gdf['DP04_0126E'].sum()) * 100
    rent_burden_pct = (filtered_gdf['DP04_0142E'].sum() / filtered_gdf['DP04_0126E'].sum()) * 100
    rent_burden_pct_delta = rent_burden_pct - state_rent_burden_pct
    c10.metric(
        label="Occupied Units paying 35%+ of Income on Rent", 
        value=f"{filtered_gdf['DP04_0142E'].sum():,.0f}"
    )
    c10.metric(
        label="Occupied Units paying 35%+ of Income on Rent", 
        value=f"{rent_burden_pct:.1f}%",
        delta=f"{rent_burden_pct_delta:.1f}%",
        
        delta_color="inverse"
    )

    
    pop_df = pd.read_csv('/Users/iansargent/Desktop/ORCA/Steamlit App Testing/Census/VT_Municipal_Pop.csv')
    
    # --- Map housing bins to corresponding decades ---
    year_bins = [
        "1939 and Prior", "1940 - 1949", "1950 - 1959", "1960 - 1969",
        "1970 - 1979", "1980 - 1989", "1990 - 1999", "2000 - 2009",
        "2010 - 2019", "2020 - Present"
    ]

    filtered_gdf["GEOID"] = filtered_gdf["GEOID"].astype("string")
    filtered_gdf["GEOID"] = filtered_gdf["GEOID"].str.strip()
    
    pop_df["_geoid"] = pop_df["_geoid"].astype("string")
    pop_df["_geoid"] = pop_df["_geoid"].str.strip()
    
    filtered_gdf_pop = pd.merge(left=filtered_gdf, right=pop_df, how="left", left_on="GEOID", right_on="_geoid")
    
    
    if county == "All Counties":
        title_geo = "Vermont (Statewide)"
    elif county != "All Counties" and jurisdiction == "All Jurisdictions":
        title_geo = f"{county} County"
    elif jurisdiction != "All Jurisdictions":
        title_geo = f"{jurisdiction}, Vermont"
    
    
    # --- Get housing unit counts ---
    raw_housing_counts = [
        filtered_gdf_pop["DP04_0026E"].sum(),
        filtered_gdf_pop["DP04_0025E"].sum(),
        filtered_gdf_pop["DP04_0024E"].sum(),
        filtered_gdf_pop["DP04_0023E"].sum(),
        filtered_gdf_pop["DP04_0022E"].sum(),
        filtered_gdf_pop["DP04_0021E"].sum(),
        filtered_gdf_pop["DP04_0020E"].sum(),
        filtered_gdf_pop["DP04_0019E"].sum(),
        filtered_gdf_pop["DP04_0018E"].sum(),
        filtered_gdf_pop["DP04_0017E"].sum()
    ]
    cumulative_housing_counts = pd.Series(raw_housing_counts).cumsum().tolist()

    population_counts = [
        filtered_gdf_pop["year1930"].sum(),
        filtered_gdf_pop["year1940"].sum(),
        filtered_gdf_pop["year1950"].sum(),
        filtered_gdf_pop["year1960"].sum(),
        filtered_gdf_pop["year1970"].sum(),
        filtered_gdf_pop["year1980"].sum(),
        filtered_gdf_pop["year1990"].sum(),
        filtered_gdf_pop["year2000"].sum(),
        filtered_gdf_pop["year2010"].sum(),
        filtered_gdf_pop["year2020"].sum(),
    ]

    house_pop_plot_df = pd.DataFrame({
        "Year Range": year_bins,
        "Census Year": [1930, 1940, 1950, 1960, 1970, 1980, 1990, 2000, 2010, 2020],
        "Population": population_counts,
        "Total Housing Units": cumulative_housing_counts,
        "New Housing Units": raw_housing_counts
    }).melt(
        id_vars=['Year Range', 'Census Year'],
        value_vars=['Population', 'Total Housing Units', 'New Housing Units'],
        var_name='Metric',
        value_name='Value'
    )

    base = alt.Chart(house_pop_plot_df).encode(
        x=alt.X('Year Range:N', title="Year", axis=alt.Axis(labelAngle=-45)),
        color=alt.Color('Metric:N', legend=alt.Legend(
            title="", orient="top-left", direction='horizontal', offset=-38))
    )
    line = base.mark_line().encode(
        y=alt.Y('Value:Q', title='')
    )
    points = base.mark_point(filled=True, size=100).encode(
        y='Value:Q',
    )
    # Bar chart for just "New Housing Units per Year"
    bars = alt.Chart(house_pop_plot_df).transform_filter(
        alt.datum.Metric == 'New Housing Units'
    ).mark_bar(opacity=0.4).encode(
        x='Year Range:N',
        y='Value:Q',
        color=alt.value('cornflowerblue')
    )
    chart = alt.layer(bars, line, points).properties(
        title=f"Housing Units vs Population Over Time for {title_geo}",
        height=600
    ).configure_title(
        fontSize=19,
        offset=45
    ).interactive()

    st.altair_chart(chart, use_container_width=True)

    st.markdown("---")
    
    
    
    style_metric_cards(
        background_color="whitesmoke",
        border_left_color="thistle",
        box_shadow=True,
        border_size_px=0.5
    )
    
    
    
    return m


def show_mapping():
    # Display the page
    render_mapping()


if __name__ == "__main__":
    show_mapping()