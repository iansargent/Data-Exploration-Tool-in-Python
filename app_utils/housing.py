"""
Open Research Community Accelorator
Vermont Data App

Housing Utility Functions
"""

import streamlit as st
import pandas as pd
import altair as alt
import io
import requests
from app_utils.census import get_geography_title
from app_utils.census_sections import select_census_geography, filter_census_geography
from app_utils.color import get_text_color
from app_utils.data_loading import load_census_data
from app_utils.plot import donut_chart, bar_chart


@st.cache_data
def load_population_df():
    # Read in VT historical population data on the census tract level
    # NOTE: Include a source for this as well (VT Open Data Portal)
    pop_url = "https://raw.githubusercontent.com/iansargent/Data-Exploration-Tool-in-Python/main/Data/Census/VT_Historical_Population.csv"
    response = requests.get(pop_url, verify=False)
    pop_df = pd.read_csv(io.StringIO(response.text))

    return pop_df  


def housing_snapshot_header():
    st.subheader("Housing Snapshot")
    # Include a source for the dataset (Census DP04 2023 5-year estimates)
    st.markdown("***Data Source***: U.S. Census Bureau. (2023). DP04: Selected Housing Characteristics - " \
    "County Subdivisions, Vermont. 2019-2023 American Community Survey 5-Year Estimates. " \
    "Retrieved from https://data.census.gov/")


def med_home_value_ts_plot(county, jurisdiction, filtered_med_val_df):
    med_val_df = load_census_data("https://raw.githubusercontent.com/iansargent/Data-Exploration-Tool-in-Python/main/Data/Census/med_home_value_by_year.csv")
    statewide_avg_val_df = (med_val_df.groupby("year", as_index=False)["estimate"].mean())
    
    chart_df = pd.DataFrame()
    statewide_line = statewide_avg_val_df.copy()
    statewide_line = statewide_line[["year", "estimate"]]
    statewide_line["Group"] = "Statewide Average"
    
    # Statewide Level
    if county == "All Counties" and jurisdiction == "All Jurisdictions":
        ymin = statewide_line["estimate"].min() - 5000
        ymax = statewide_line["estimate"].max() + 5000

        base = alt.Chart(statewide_avg_val_df).encode(
            x=alt.X("year:O", title="Year", axis=alt.Axis(labelAngle=0)),
            y=alt.Y("estimate:Q", title="Median Home Value", 
                    scale=alt.Scale(domain=(ymin, ymax)),
                    axis=alt.Axis(format="$,.0f")),
            tooltip=[alt.Tooltip('estimate', title='Median Home Value', format="$,.0f")]
        )

        line = base.mark_line(color='mediumseagreen')
        points = base.mark_point(color='mediumseagreen', filled=True, size=70)

        line_chart = (line + points).properties(
            title="Median Home Value Over Time (Statewide)",
            height=550
        ).configure_title(fontSize=19, anchor="middle").interactive()
    
    # County Level
    elif county != "All Counties" and jurisdiction == "All Jurisdictions":
        subtitle = f"{county} County vs Vermont Statewide Average"
        county_df = (filtered_med_val_df.groupby("year", as_index=False)["estimate"].mean().assign(Group=county))
        chart_df = pd.concat([county_df, statewide_line], ignore_index=True)
        group_label_map = {county: f"{county} County"}
        chart_df["Group"] = chart_df["Group"].replace(group_label_map)

        ymin = chart_df["estimate"].min() - 5000
        ymax = chart_df["estimate"].max() + 5000

        line_chart = alt.Chart(chart_df).mark_line(point=True).encode(
        x=alt.X("year:O", title="Year", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("estimate:Q", title="Median Home Value", 
                scale=alt.Scale(domain=(ymin, ymax)), axis=alt.Axis(format="$,.0f")),
        color=alt.Color("Group:N", scale=alt.Scale(
                    domain=[f"{county} County", "Statewide Average"],
                    range=["orangered", "#fcd1cc"]),
                legend=alt.Legend(title="", direction='horizontal', orient='top-left', offset=-38)),
            tooltip=[alt.Tooltip('estimate', title='Median Home Value', format="$,.0f")]
        ).properties(title=alt.Title("Median Home Value Over Time", subtitle=subtitle), height=550
        ).configure_title(fontSize=19,offset=45, anchor="middle").interactive()

    elif jurisdiction != "All Jurisdictions":
        subtitle = f"{jurisdiction} vs Vermont Statewide Average"
        jurisdiction_df = (filtered_med_val_df.groupby("year", as_index=False)["estimate"].mean().assign(Group=jurisdiction))
        chart_df = pd.concat([jurisdiction_df, statewide_line], ignore_index=True)
        
        ymin = chart_df["estimate"].min() - 5000
        ymax = chart_df["estimate"].max() + 5000

        line_chart = alt.Chart(chart_df).mark_line(point=True).encode(
        x=alt.X("year:O", title="Year", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("estimate:Q", title="Median Home Value", 
                scale=alt.Scale(domain=(ymin, ymax)),
                axis=alt.Axis(format="$,.0f")),
        color=alt.Color("Group:N", scale=alt.Scale(
                    domain=[jurisdiction, "Statewide Average"],
                    range=["orangered", "#fcd1cc"]),
                legend=alt.Legend(title="", direction='horizontal', orient='top-left', offset=-38)),
            tooltip=[alt.Tooltip('year', title='Year'),
                        alt.Tooltip('estimate', title='Median Home Value', format="$,.0f"),
                        alt.Tooltip('Group', title='Location')]
        ).properties(title=alt.Title("Median Home Value Over Time", subtitle=subtitle), height=550
        ).configure_title(fontSize=19, anchor="middle").interactive()

    
    return line_chart


def med_smoc_ts_plot(county, jurisdiction, filtered_med_smoc_df):
    # Create a chart for the SMOC comparison
    med_smoc_df = load_census_data("https://raw.githubusercontent.com/iansargent/Data-Exploration-Tool-in-Python/main/Data/Census/med_smoc_by_year.csv")
    statewide_avg_smoc_df = (med_smoc_df.groupby(["year", "variable"], as_index=False)["estimate"].mean())
    smoc_chart_df = pd.DataFrame()
    statewide_smoc_line = statewide_avg_smoc_df.copy()
    statewide_smoc_line = statewide_smoc_line[["year", "estimate", "variable"]]
    statewide_smoc_line["Group"] = "Statewide Average"
    
    # Statewide Level
    if county == "All Counties" and jurisdiction == "All Jurisdictions":
        ymin = statewide_smoc_line["estimate"].min() - 500
        ymax = statewide_smoc_line["estimate"].max() + 500
        
        base = alt.Chart(statewide_avg_smoc_df).encode(
            x=alt.X("year:O", title="Year", axis=alt.Axis(labelAngle=0)),
            y=alt.Y("estimate:Q", title="Median SMOC", 
                    scale=alt.Scale(domain=(ymin, ymax)),
                    axis=alt.Axis(format="$,.0f")),
            color=alt.Color("variable:N",
                legend=alt.Legend(
                    title=None, 
                    orient="top-left", 
                    direction="horizontal", 
                    offset=-30)),
            tooltip=[alt.Tooltip('estimate', title='Median Monthly Costs', format="$,.0f"),
                     alt.Tooltip('variable', title='SMOC Type')])

        line = base.mark_line(color='mediumseagreen')
        points = base.mark_point(color='mediumseagreen', filled=True, size=70)

        line_chart = (line + points).properties(
            title="Median Selected Monthly Owner Costs Over Time (SMOC)",
            height=450).configure_title(fontSize=19, anchor="middle").interactive()
    
    # County Level
    elif county != "All Counties" and jurisdiction == "All Jurisdictions":
        filtered_med_smoc_df = filtered_med_smoc_df.rename(columns={"County": "Group"})
        county_df_smoc = (filtered_med_smoc_df.groupby(["year", "variable", "Group"], as_index=False)["estimate"].mean())
        smoc_chart_df = pd.concat([county_df_smoc, statewide_smoc_line], ignore_index=True)
        smoc_chart_df["LineLabel"] = smoc_chart_df["Group"] + " " + smoc_chart_df["variable"]

        ymin = smoc_chart_df["estimate"].min() - 200
        ymax = smoc_chart_df["estimate"].max() + 200
        
        line_chart = alt.Chart(smoc_chart_df).mark_line().encode(
        x=alt.X("year:O", title="Year", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("estimate:Q", title="Median SMOC", 
                scale=alt.Scale(domain=(ymin, ymax)), axis=alt.Axis(format="$,.0f")),
        color=alt.Color("Group:N", scale=alt.Scale(
                    domain=[county, "Statewide Average"],
                    range=["orangered", "#fcd1cc"]), legend=alt.Legend(
                        title=None, orient="top-left", direction="horizontal")),
            strokeDash=alt.StrokeDash("variable:N", title=None, legend=alt.Legend(
                orient="top-left", direction="horizontal", offset=-20)),
            tooltip=[alt.Tooltip('Group', title='Location'),
                     alt.Tooltip('estimate', title='Median SMOC Value', format="$,.0f"),
                     alt.Tooltip('variable', title='SMOC Type')]
        ).properties(title=alt.Title("Median Monthly Owner Costs Over Time"), height=450
        ).configure_title(fontSize=19, anchor="middle").interactive()

    elif jurisdiction != "All Jurisdictions":
        filtered_med_smoc_df = filtered_med_smoc_df.rename(columns={"Jurisdiction": "Group"})
        jurisdiction_df_smoc = (filtered_med_smoc_df.groupby(["year", "variable", "Group"], as_index=False)["estimate"].mean())
        smoc_chart_df = pd.concat([jurisdiction_df_smoc, statewide_smoc_line], ignore_index=True)
        smoc_chart_df["LineLabel"] = smoc_chart_df["Group"] + " " + smoc_chart_df["variable"]

        ymin = smoc_chart_df["estimate"].min() - 200
        ymax = smoc_chart_df["estimate"].max() + 200
        
        line_chart = alt.Chart(smoc_chart_df).mark_line().encode(
        x=alt.X("year:O", title="Year", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("estimate:Q", title="Median SMOC", 
                scale=alt.Scale(domain=(ymin, ymax)), axis=alt.Axis(format="$,.0f")),
        color=alt.Color("Group:N", scale=alt.Scale(
                    domain=[jurisdiction, "Statewide Average"],
                    range=["orangered", "#fcd1cc"]), legend=alt.Legend(
                        title=None, orient="top-left", direction="horizontal")),
            strokeDash=alt.StrokeDash("variable:N", title=None, legend=alt.Legend(
                orient="top-left", direction="horizontal", offset=-25)),
            tooltip=[alt.Tooltip('Group', title='Location'),
                     alt.Tooltip('estimate', title='Median SMOC Value', format="$,.0f"),
                     alt.Tooltip('variable', title='SMOC Type')]
        ).properties(title=alt.Title("Median Monthly Owner Costs Over Time"), height=450
        ).configure_title(fontSize=19, anchor="middle").interactive()


    return line_chart


def housing_pop_plot(county, jurisdiction, filtered_gdf):
    pop_df = load_population_df()
    # Define a set of year ranges corresponding to new unit construction data
    year_bins = [
        "1939 and Prior", "1940 - 1949", "1950 - 1959", "1960 - 1969",
        "1970 - 1979", "1980 - 1989", "1990 - 1999", "2000 - 2009",
        "2010 - 2019", "2020 - Present"
    ]

    # Convert the "Geo-ID" column in both datasets to string type
    filtered_gdf["GEOID"] = filtered_gdf["GEOID"].astype("string")
    filtered_gdf["GEOID"] = filtered_gdf["GEOID"].str.strip()
    pop_df["_geoid"] = pop_df["_geoid"].astype("string")
    pop_df["_geoid"] = pop_df["_geoid"].str.strip()
    
    # Perform a left join on the two dataframes, joining on the respective "Geo-ID" column
    filtered_gdf_pop = pd.merge(left=filtered_gdf, right=pop_df, how="left", left_on="GEOID", right_on="_geoid")
    
    # For the plot title, dynamically change the area of interest based on user filter selections
    title_geo = get_geography_title(county, jurisdiction)
    
    # Define a list of housing counts for each year range
    raw_housing_counts = [
        filtered_gdf_pop["DP04_0026E"].sum(), # Total units built 1939 or earlier
        filtered_gdf_pop["DP04_0025E"].sum(), # Total units built 1940-1949
        filtered_gdf_pop["DP04_0024E"].sum(), # Total units built 1950-1959
        filtered_gdf_pop["DP04_0023E"].sum(), # Total units built 1960-1969
        filtered_gdf_pop["DP04_0022E"].sum(), # Total units built 1970-1979
        filtered_gdf_pop["DP04_0021E"].sum(), # Total units built 1980-1989
        filtered_gdf_pop["DP04_0020E"].sum(), # Total units built 1990-1999
        filtered_gdf_pop["DP04_0019E"].sum(), # Total units built 2000-2009
        filtered_gdf_pop["DP04_0018E"].sum(), # Total units built 2010-2019
        filtered_gdf_pop["DP04_0017E"].sum()  # Total units built 2020 or later
    ]
    # Calculate the cumulative sum (as a list) to plot total progression over time
    cumulative_housing_counts = pd.Series(raw_housing_counts).cumsum().tolist()

    # From the population dataset, gather tract-level population data for the respective years
    population_counts = [
        filtered_gdf_pop["year1930"].sum(), # Total Population in 1930
        filtered_gdf_pop["year1940"].sum(), # Total Population in 1940
        filtered_gdf_pop["year1950"].sum(), # Total Population in 1950
        filtered_gdf_pop["year1960"].sum(), # Total Population in 1960
        filtered_gdf_pop["year1970"].sum(), # Total Population in 1970
        filtered_gdf_pop["year1980"].sum(), # Total Population in 1980
        filtered_gdf_pop["year1990"].sum(), # Total Population in 1990
        filtered_gdf_pop["year2000"].sum(), # Total Population in 2000
        filtered_gdf_pop["year2010"].sum(), # Total Population in 2010
        filtered_gdf_pop["year2020"].sum()  # Total Population in 2020
    ]

    # Gather population and housing data into one dataframe
    house_pop_plot_df = pd.DataFrame({
        "Year Range": year_bins,
        "Census Year": [1930, 1940, 1950, 1960, 1970, 1980, 1990, 2000, 2010, 2020],
        "Population": population_counts,
        "Total Housing Units": cumulative_housing_counts,
        "New Housing Units": raw_housing_counts
    }).melt( # Melt / transpose the dataset (long format) for time-series plotting
        id_vars=['Year Range', 'Census Year'],
        value_vars=['Population', 'Total Housing Units', 'New Housing Units'],
        var_name='Metric',
        value_name='Value'
    )

    # Define an interactive selection feature to the plot
    selection = alt.selection_point(fields=['Metric'], bind='legend')
    # The base plot with 3 lines, one for each metric
    base = alt.Chart(house_pop_plot_df).encode(
        x=alt.X('Year Range:N', title="Year", axis=alt.Axis(labelAngle=-45)),
        color=alt.Color('Metric:N', legend=alt.Legend(
            title=None, orient="top-left", direction='horizontal', offset=-38)),
        tooltip=[alt.Tooltip('Metric'), alt.Tooltip('Value', title="Count", format=",")],
        opacity=alt.when(selection).then(alt.value(1)).otherwise(alt.value(0.2))
    ).add_params(selection)

    # Add the line markings with tooltip support
    line = base.mark_line().encode(
        y=alt.Y('Value:Q', title='')
    )
    # Add the points on the lines for better visibility
    points = base.mark_point(filled=True, size=100).encode(
        y='Value:Q',
    )
    # Layer all the features into one plot with a title
    chart = alt.layer(line, points).properties(
        title=f"Housing Units vs Population Over Time for {title_geo}",
        height=600).configure_title(fontSize=19,offset=45).interactive()

    # Display the plot on the page
    st.altair_chart(chart, use_container_width=True)


def housing_df_metric_dict(filtered_gdf_2023):
    # ---- Housing Metrics ----
    total_units_2023 = filtered_gdf_2023['DP04_0001E'].sum()
    vacant_units_2023 = filtered_gdf_2023['DP04_0003E'].sum()
    occupied_units_2023 = filtered_gdf_2023['DP04_0002E'].sum()
    pct_vac_2023 = vacant_units_2023 / total_units_2023
    pct_occ_2023 = occupied_units_2023 / total_units_2023

    owned_units_2023 = filtered_gdf_2023['DP04_0046E'].sum()
    rented_units_2023 = filtered_gdf_2023['DP04_0047E'].sum()
    pct_own_2023 = owned_units_2023 / occupied_units_2023
    pct_rent_2023 = rented_units_2023 / occupied_units_2023

    avg_med_SMOC_mortaged_2023 = filtered_gdf_2023['DP04_0101E'].mean()
    avg_med_SMOC2_non_mortgaged_2023 = filtered_gdf_2023['DP04_0109E'].mean()
    avg_med_gross_rent_2023 = filtered_gdf_2023['DP04_0134E'].mean()

    units_paying_rent_2023 = filtered_gdf_2023['DP04_0126E'].sum()
    rent_burden35_2023 = filtered_gdf_2023['DP04_0142E'].sum()
    rent_burden35_pct_2023 = (rent_burden35_2023 / units_paying_rent_2023) * 100

    one_unit_detached_2023 = filtered_gdf_2023['DP04_0007E'].sum()
    one_unit_attached_2023 = filtered_gdf_2023['DP04_0008E'].sum()
    one_unit_2023 = one_unit_detached_2023 + one_unit_attached_2023
    two_units_2023 = filtered_gdf_2023['DP04_0009E'].sum()
    three_or_four_units_2023 = filtered_gdf_2023['DP04_0010E'].sum()
    five_to_nine_units_2023 = filtered_gdf_2023['DP04_0011E'].sum()
    ten_to_nineteen_units_2023 = filtered_gdf_2023['DP04_0012E'].sum()
    twenty_or_more_units_2023 = filtered_gdf_2023['DP04_0013E'].sum()
    mobile_home_2023 = filtered_gdf_2023['DP04_0014E'].sum()
    boat_RV_van_etc_2023 = filtered_gdf_2023['DP04_0015E'].sum()

    # ---- Organize Metrics ----
    metrics = {
        "total_units": total_units_2023,
        "vacant_units": vacant_units_2023,
        "occupied_units": occupied_units_2023,
        "pct_vacant": pct_vac_2023,
        "pct_occupied": pct_occ_2023,
        "owned_units": owned_units_2023,
        "rented_units": rented_units_2023,
        "pct_owner_occupied": pct_own_2023,
        "pct_renter_occupied": pct_rent_2023,
        "avg_med_SMOC_mortgaged": avg_med_SMOC_mortaged_2023,
        "avg_med_SMOC_non_mortgaged": avg_med_SMOC2_non_mortgaged_2023,
        "avg_med_gross_rent": avg_med_gross_rent_2023,
        "units_paying_rent": units_paying_rent_2023,
        "rent_burdened_35pct_or_more": rent_burden35_2023,
        "pct_rent_burdened_35pct_or_more": rent_burden35_pct_2023,
        "units_1_unit_total": one_unit_2023,
        "units_2": two_units_2023,
        "units_3_4": three_or_four_units_2023,
        "units_5_9": five_to_nine_units_2023,
        "units_10_19": ten_to_nineteen_units_2023,
        "units_20_plus": twenty_or_more_units_2023,
        "units_mobile_home": mobile_home_2023,
        "units_boat_rv_van": boat_RV_van_etc_2023
    }

    # ---- DataFrames for Plotting ----
    plots = {
        "occupancy_occ_df": pd.DataFrame({
            'Occupancy Status': ['Occupied', 'Vacant'], 
            'Value': [pct_occ_2023, pct_vac_2023]
        }),
        "occupancy_vac_df": pd.DataFrame({
            'Occupancy Status': ['Occupied', 'Vacant'], 
            'Value': [pct_occ_2023, pct_vac_2023]
        }),
        "tenure_df": pd.DataFrame({
            'Occupied Tenure': ['Owner', 'Renter'],
            'Value': [pct_own_2023, pct_rent_2023]
        }),
        "units_in_structure_df": pd.DataFrame({
            'Structure Category': [
                '1-Unit', '2-Units', '3 - 4 Units', '5 - 9 Units', 
                '10 - 19 Units', '20+ Units', 'Mobile Homes', 'Boat/RV/Van, etc.'
            ],
            'Units': [
                one_unit_2023, two_units_2023, three_or_four_units_2023, 
                five_to_nine_units_2023, ten_to_nineteen_units_2023, 
                twenty_or_more_units_2023, mobile_home_2023, boat_RV_van_etc_2023
            ]
        })
    }

    return metrics, plots


def housing_snapshot(housing_dfs):
    # Display the Category Header with Data Source
    housing_snapshot_header()
    # Define county and jurisdiction selections with select boxes
    county, jurisdiction = select_census_geography(housing_dfs[0])
    # Filter each dataset in "housing_dfs" to the geography needed for the snapshot 
    # Returns a LIST of filtered DataFrames
    filtered_housing_dfs = filter_census_geography(housing_dfs, county, jurisdiction)

    # Unpack each dataset from "filtered_housing_dfs" by index
    # TODO: This unpacking process could be more reliable with a dictionary
    filtered_gdf_2023 = filtered_housing_dfs[0]
    filtered_med_val_df = filtered_housing_dfs[1]
    filtered_med_smoc_df = filtered_housing_dfs[2]
    
    # Get the title of the geography for plotting
    title_geo = get_geography_title(county, jurisdiction)
    # Based on the system color theme, update the text color (only used in donut plots)
    text_color = get_text_color(key="housing_snapshot")
    # Define two callable dictionaries: Metrics and Plot DataFrames
    metrics, plot_dfs = housing_df_metric_dict(filtered_gdf_2023)
    
    # Display the housing / population plot at the top of the snapshot
    housing_pop_plot(county, jurisdiction, filtered_gdf_2023)
    
    # The OCCUPANCY Section ___________________________________________________
    st.subheader("Occupancy")
    # Split section into three colunms: Metrics on the left followed by two donut charts
    _, occ_col1, occ_col2, occ_col3 = st.columns([0.5, 1, 2, 2])
    occ_col1.markdown("\2")
    occ_col1.markdown("\2")
    occ_col1.metric(
        label="**Total Housing Units**", 
        value=f"{metrics['total_units']:,.0f}", 
        help="Total number of housing units in the selected geography for 2023.")
    occ_col1.metric(
        label="**Occupied** Units", 
        value=f"{metrics['occupied_units']:,.0f}", 
        help="Total number of occupied housing units in the selected geography.")
    occ_col1.metric(
        label="**Vacant** Units", 
        value=f"{metrics['vacant_units']:,.0f}", 
        help="Total number of vacant housing units in the selected geography.")
    
    # In the middle, show the donut chart of occupied units
    occupancy_occ_chart = donut_chart(
        source=plot_dfs['occupancy_occ_df'], colorColumnName="Occupancy Status", titleFontSize=15, 
        fillColor="tomato", title="Units Occupied", text_color=text_color, 
        stat=metrics['pct_occupied'], innerRadius=135, height=400)
    # In the right column, show the donut chart of vacant units
    occupancy_vac_chart = donut_chart(
        source=plot_dfs['occupancy_vac_df'], colorColumnName="Occupancy Status", titleFontSize=15, 
        fillColor="tomato", title="Units Vacant", text_color=text_color, 
        stat=metrics['pct_vacant'], innerRadius=135, height=400, inverse=True)
    
    # Display the two donut charts
    occ_col2.altair_chart(occupancy_occ_chart, use_container_width=True)
    occ_col3.altair_chart(occupancy_vac_chart, use_container_width=True)
    st.divider()
    
    # The HOUSING TENURE Section ___________________________________________________
    st.subheader("Housing Tenure")
    # Split into three columns: Two donut charts on the left and metrics on the right
    ten_col3, ten_col2, ten_col1, _ = st.columns([10, 10, 5, 2])
        
    ten_col1.markdown("\2")
    ten_col1.metric(
        label="**Owner-Occupied** Units", 
        value=f"{metrics['owned_units']:,.0f}", 
        help="Total number of owner-occupied housing units in the selected geography.")    
    ten_col1.metric(
        label="**Renter-Occupied** Units", 
        value=f"{metrics['rented_units']:,.0f}", 
        help="Total number of renter-occupied housing units in the selected geography.")

    # Create the owner-occupied donut chart
    tenure_own_donut = donut_chart(
        plot_dfs['tenure_df'], colorColumnName="Occupied Tenure", fillColor="tomato", 
        title="Owner Occupied", stat=metrics['pct_owner_occupied'], text_color=text_color)
    # Create the renter-occupied donut chart
    tenure_rent_donut = donut_chart(
        source=plot_dfs['tenure_df'], colorColumnName="Occupied Tenure", fillColor="tomato", 
        title="Renter Occupied", stat=metrics['pct_renter_occupied'], text_color=text_color, inverse=True)
    
    # Display the two donut charts
    ten_col2.altair_chart(tenure_own_donut)
    ten_col3.altair_chart(tenure_rent_donut) 
    
    st.divider()
    # Create the median home value time series plot
    med_val_ts_plot = med_home_value_ts_plot(county, jurisdiction, filtered_med_val_df)
    # Display the time series plot
    st.altair_chart(med_val_ts_plot)

    # The OWNER-OCCUPIED Section ___________________________________________________
    st.subheader("Selected Monthly Owner Costs (SMOC)")
    # Split into two columns: Metrics on the left and time series plot on the right
    _, smoc_col1, smoc_col2 = st.columns([0.5, 6, 14])
    # Metrics
    smoc_col1.markdown("\2")
    smoc_col1.markdown("##### Median Monthly Costs")
    smoc_col1.markdown("\2")
    smoc_col1.metric(
        label="**Mortgaged** Units", 
        value=f"${metrics['avg_med_SMOC_mortgaged']:,.2f}",
        help="Average monthly owner costs for ***mortgaged*** units in the selected geography for 2023")    
    smoc_col1.divider()
    smoc_col1.metric(
        label="**Non-Mortgaged** Units", 
        value=f"${metrics['avg_med_SMOC_non_mortgaged']:,.2f}",
        help="Average monthly owner costs for ***non-mortgaged*** units in the selected geography for 2023")
    
    # Define and display the median selected monthly cost time series plot (mortgaged vs non-mortgaged units)
    median_smoc_ts_plot = med_smoc_ts_plot(county, jurisdiction, filtered_med_smoc_df)
    smoc_col2.markdown("\2")
    smoc_col2.altair_chart(median_smoc_ts_plot)

    # The RENTER-OCCUPIED Section ___________________________________________________
    st.divider()
    st.subheader("Renter-Occupied Units")
    # Split into three columns for three metrics
    rent_col1, rent_col2, rent_col3 = st.columns(3)
    # Metrics
    rent_col1.metric(
        label="Median **Gross Rent**", 
        value=f"${metrics['avg_med_gross_rent']:,.2f}",
        help="Average median gross rent in the selected geography for 2023.")
    rent_col2.metric(
        label="Occupied Units paying 35%+ of Income on Rent", 
        value=f"{metrics['rent_burdened_35pct_or_more']:,.0f}",
        help="Count of households where rent takes up 35% or more of their household income in the selected geography for 2023")
    rent_col3.metric(
        label="% Occupied Units paying 35%+ of Income on Rent", 
        value=f"{metrics['pct_rent_burdened_35pct_or_more']:.1f}%",
        help="Percentage of households where rent takes up 35% or more of their household income in the selected geography for 2023.")
    
    # Define a bar chart distribution of structure types (1 unit, 2 unit, etc.)
    units_in_structure_bar_chart = bar_chart(
        plot_dfs['units_in_structure_df'], title_geo=title_geo, XcolumnName="Structure Category", YcolumnName="Units",
        distribution=True, height=600, fillColor="tomato", title="2023 Housing Unit Type Distribution",
        barWidth=90, XlabelAngle=0, labelFontSize=12)

    st.divider()
    # Display the bar chart
    st.altair_chart(units_in_structure_bar_chart, use_container_width=True)

