"""
Open Research Community Accelorator
Vermont Data App

Housing Utility Functions
"""

import streamlit as st
from streamlit_extras.metric_cards import style_metric_cards 
import pandas as pd
import altair as alt
from app_utils.census import get_geography_title, calculate_delta_values


def housing_snapshot(county, jurisdiction, 
                     filtered_gdf_2013, filtered_gdf_2023, housing_gdf_2023, 
                     filtered_med_val_df, filtered_med_smoc_df,
                     statewide_avg_val_df, statewide_avg_smoc_df, compare_to):
    # For the plot title, dynamically change the area of interest based on user filter selections
    title_geo = get_geography_title(county, jurisdiction)
    
    delta_dict = calculate_delta_values(filtered_gdf_2023, compare_to, filtered_gdf_2013, housing_gdf_2023)

    # Housing Units Section
    st.subheader("Occupancy")
    # Split section into two colunms
    left_col1, right_col2 = st.columns([2, 3])
    # In the left column, show the metrics
    with left_col1:
        st.markdown("\2")
        # Caclulate total units, vacant units, and occupied units (2013 + 2023) with percentages
        total_units_2023 = filtered_gdf_2023['DP04_0001E'].sum()

        vacant_units_2023 = filtered_gdf_2023['DP04_0003E'].sum()
        occupied_units_2023 = filtered_gdf_2023['DP04_0002E'].sum()
        pct_vac_2023 = (vacant_units_2023 / total_units_2023) * 100
        pct_occ_2023 = (occupied_units_2023 / total_units_2023) * 100

        # Total units
        st.metric(label="**Total Housing Units**", value=f"{total_units_2023:,.0f}", 
                  delta=delta_dict['total_units_delta'],
                  help="Total number of housing units in the selected geography for 2023 compared to 2013.")

        # Split metrics for vacant and occupied
        subcol1, subcol2 = st.columns(2)
        # Occupied Units metric card with %
        subcol1.metric(label="**Occupied Units**", value=f"{occupied_units_2023:,.0f}", delta=delta_dict['occupied_units_delta'], 
                       help="Total number of occupied housing units in the selected geography.")
        subcol1.metric(label="**Occupied Units (%)**", value=f"{pct_occ_2023:.1f}%", delta=f"{delta_dict['pct_occ_delta']:.1f}%", 
                       help="Percentage of units that are occupied in the selected geography.")
        # Vacant Units metric card with %
        subcol2.metric(label="**Vacant Units**", value=f"{vacant_units_2023:,.0f}", delta=delta_dict['vacant_units_delta'], 
                       help="Total number of vacant housing units in the selected geography.")
        subcol2.metric(label="**Vacant Units (%)**", value=f"{pct_vac_2023:.1f}%", delta=f"{delta_dict['pct_vac_delta']:.1f}%", 
                       help="Percentage of units that are vacant in the selected geography.")

    # In the right column, show the pie chart distribution of occupied vs vacant units
    pie_df = pd.DataFrame({'Status': ['Occupied', 'Vacant'], 'Units': [occupied_units_2023, vacant_units_2023]})

    pie_chart = alt.Chart(pie_df).mark_arc(innerRadius=130).encode(
        theta=alt.Theta(field="Units", type="quantitative", aggregate="sum"),
        color=alt.Color(field="Status", type="nominal", scale=alt.Scale(
            domain=["Occupied", "Vacant"],
            range=["tomato", "whitesmoke"])),
            tooltip=[alt.Tooltip("Status:N"), alt.Tooltip("Units")]
    ).properties(width=300, height=440).configure_legend(orient='top-left')
    # Display the pie chart
    right_col2.altair_chart(pie_chart, use_container_width=True)
    # Divider
    st.divider()
    
    # HOUSING TENURE SECTION
    st.subheader("Housing Tenure")
    left_col2, right_col2 = st.columns(2)
    
    with right_col2:
        c4, c5 = st.columns(2)
        
        # Owner-Occupied Units
        owned_units_2023 = filtered_gdf_2023['DP04_0046E'].sum()
        pct_own_2023 = (owned_units_2023 / occupied_units_2023) * 100
        
        c4.metric(label="**Owner-Occupied**", value=f"{owned_units_2023:,.0f}", 
                  delta=delta_dict['owned_units_delta'], 
                  help="Total number of owner-occupied housing units in the selected geography.")
        c4.metric(label="**Owner-Occupied** (%)", value=f"{pct_own_2023:.1f}%", 
                  delta=f"{delta_dict['pct_own_delta']:.1f}%",
                  help="Percentage of occupied units that are owner-occupied in the selected geography.")
    
        # Renter-Occupied Units
        rented_units_2023 = filtered_gdf_2023['DP04_0047E'].sum()
        pct_rent_2023 = (rented_units_2023 / occupied_units_2023) * 100
        
        c5.metric(label="**Renter-Occupied**", value=f"{rented_units_2023:,.0f}", 
                  delta=delta_dict['rented_units_delta'],
                  help="Total number of renter-occupied housing units in the selected geography.")
        # Units Rented (%)
        c5.metric(label="**Renter-Occupied** (%)", value=f"{pct_rent_2023:.1f}%", 
                  delta=f"{delta_dict['pct_rent_delta']:.1f}%",
                  help="Percentage of occupied units that are renter-occupied in the selected geography.")

    # Pie chart for Housing Tenure
    pie_df = pd.DataFrame({
        'Occupied Tenure': ['Owner', 'Renter'],
        'Units': [owned_units_2023, rented_units_2023]})

    pie_chart = alt.Chart(pie_df).mark_arc(innerRadius=75).encode(
        theta=alt.Theta(field="Units", type="quantitative", aggregate="sum"),
        color=alt.Color(field="Occupied Tenure", scale=alt.Scale(
            domain=["Owner", "Renter"],
            range=['tomato', 'whitesmoke'])), 
            tooltip=[alt.Tooltip("Occupied Tenure:N"), alt.Tooltip("Units")]
            ).properties(width=250, height=300).configure_legend(orient="top-left")
    
    left_col2.altair_chart(pie_chart)
    
    st.divider()
    
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
        ).configure_title(fontSize=19,offset=45).interactive()

        st.altair_chart(line_chart, use_container_width=True)
    
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
        ).configure_title(fontSize=19,offset=45,dx=30).interactive()

        st.altair_chart(line_chart, use_container_width=True)

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
        ).configure_title(fontSize=19,offset=45,dx=30).interactive()

        st.altair_chart(line_chart, use_container_width=True)

    # OWNER-OCCUPIED SECTION
    st.subheader("Monthly Owner Costs")
    c8, c8_2 = st.columns(2)
    # Average Median Monthly Owner Cost (SMOC) (For units with and without a mortgage)
    avg_med_SMOC_2023 = filtered_gdf_2023['DP04_0101E'].mean()
    avg_med_SMOC2_2023 = filtered_gdf_2023['DP04_0109E'].mean()
    
    c8.metric(label="Selected Monthly **Owner Costs** for *mortgaged* units", value=f"${avg_med_SMOC_2023:,.2f}",
        delta=f"{delta_dict['avg_med_SMOC_delta']:,.2f}", delta_color="inverse",
        help="Average monthly owner costs for ***mortgaged*** units in the selected geography for 2023 compared to 2013.")    
    c8_2.metric(label="Selected Monthly **Owner Costs** for *non-mortgaged* units", value=f"${avg_med_SMOC2_2023:,.2f}",
        delta=f"{delta_dict['avg_med_SMOC2_delta']:,.2f}", delta_color='inverse',
        help="Average monthly owner costs for ***non-mortgaged*** units in the selected geography for 2023 compared to 2013.")
    
    # Create a chart for the SMOC comparison
    st.divider()
    
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
            color=alt.Color("variable:N",legend=alt.Legend(
                                            title=None, orient="top-left", 
                                            direction="horizontal", offset=-30)),
            tooltip=[alt.Tooltip('estimate', title='Median Monthly Costs', format="$,.0f"),
                     alt.Tooltip('variable', title='SMOC Type')])

        line = base.mark_line(color='mediumseagreen')
        points = base.mark_point(color='mediumseagreen', filled=True, size=70)

        line_chart = (line + points).properties(
            title="Median Selected Monthly Owner Costs Over Time (SMOC)",
            height=550).configure_title(fontSize=19,offset=40, dx=40).interactive()

        st.altair_chart(line_chart, use_container_width=True)
    
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
        ).properties(title=alt.Title("Median Monthly Owner Costs Over Time"), height=550
        ).configure_title(fontSize=19,offset=30,dx=30).interactive()

        st.altair_chart(line_chart, use_container_width=True)

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
        ).properties(title=alt.Title("Median Monthly Owner Costs Over Time"), height=550
        ).configure_title(fontSize=19,offset=30,dx=30).interactive()

        st.altair_chart(line_chart, use_container_width=True)
     
    st.divider()

    # RENTER-OCCUPIED SECTION
    st.subheader("Renter-Occupied Units")
    c9 = st.container()
    c10, c11 = st.columns(2)
    
    # Average Median Gross Rent
    avg_med_gross_rent_2023 = filtered_gdf_2023['DP04_0134E'].mean()
    avg_med_gross_rent_2013 = filtered_gdf_2013['DP04_0132E'].mean()
    avg_med_gross_rent_delta = avg_med_gross_rent_2023 - avg_med_gross_rent_2013
    c9.metric(label="Median **Gross Rent**", value=f"${avg_med_gross_rent_2023:,.2f}",
        delta=f"{avg_med_gross_rent_delta:,.2f}", delta_color="inverse",
        help="Average median gross rent in the selected geography for 2023 compared to 2013.")
    
    # Count of Households where rent takes up 35% or more of their household income
    units_paying_rent_2023 = filtered_gdf_2023['DP04_0126E'].sum()
    rent_burden35_2023 = filtered_gdf_2023['DP04_0142E'].sum()
    rent_burden35_pct_2023 = (rent_burden35_2023 / units_paying_rent_2023) * 100
    c10.metric(label="Occupied Units paying 35%+ of Income on Rent", value=f"{rent_burden35_2023:,.0f}",
        delta=delta_dict['rent_burden35_delta'], delta_color="inverse",
        help="Count of households where rent takes up 35% or more of their household income in the selected geography for 2023 compared to 2013.")
    # Percentage of households where rent takes up 35% or more of their household income
    c11.metric(label="% Occupied Units paying 35%+ of Income on Rent", value=f"{rent_burden35_pct_2023:.1f}%",
        delta=f"{delta_dict['rent_burden35_pct_delta']:.1f}%", delta_color="inverse",
        help="Percentage of households where rent takes up 35% or more of their household income in the selected geography for 2023 compared to 2013.")

    st.divider()

    # UNITS IN STRUCTURE SECTION
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
    
    # Create a DataFrame for a grouped bar chart
    units_in_structure_df = pd.DataFrame({
        'Structure Category': [
            '1-Unit', '2-Units', '3 - 4 Units', 
            '5 - 9 Units','10 - 19 Units', '20+ Units',
            'Mobile Homes', 'Boat/RV/Van, etc.'
        ],
        '2023 Units': [
            one_unit_2023, two_units_2023,
            three_or_four_units_2023, five_to_nine_units_2023,
            ten_to_nineteen_units_2023, twenty_or_more_units_2023,
            mobile_home_2023, boat_RV_van_etc_2023
        ]})  

    category_order = [
        '1-Unit', '2-Units', '3 - 4 Units', 
        '5 - 9 Units','10 - 19 Units', '20+ Units',
        'Mobile Homes', 'Boat/RV/Van, etc.'
    ]  
    
    units_in_structure_chart = alt.Chart(units_in_structure_df).mark_bar(color="tomato").encode(
        x=alt.X('Structure Category:N', title="Structure Category", axis=alt.Axis(labelAngle=0), sort=category_order),
        y=alt.Y('2023 Units:Q', title='Total Units'),
        tooltip=[alt.Tooltip('2023 Units:Q', title = "Total Units", format=',')]
    ).properties(height=600, title=f"Structure Category Distribution in {title_geo} (2023)"
    ).configure_title(fontSize=19,offset=30,dx=30).interactive()

    # Display the grouped bar chart
    st.altair_chart(units_in_structure_chart, use_container_width=True)
    
    # Style the metric cards
    # style_metric_cards(
    #     background_color="whitesmoke",
    #     border_left_color="salmon",
    #     box_shadow=True,
    #     border_size_px=0.5
    # )


def housing_pop_plot(county, jurisdiction, filtered_gdf, pop_df):
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

