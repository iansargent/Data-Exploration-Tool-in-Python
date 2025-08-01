"""
Open Research Community Accelorator
Vermont Data App

Economic Utility Functions
"""

import streamlit as st
import pandas as pd
import altair as alt
import requests
import io
from app_utils.census import get_geography_title, split_name_col
from app_utils.census_sections import filter_census_geography, select_census_geography
from app_utils.color import get_text_color



def donut_chart(source, colorColumnName, height=300, width=300, innerRadius=90, fontSize=40, titleFontSize=14, fillColor="mediumseagreen", title="Donut Chart", 
                stat=0, text_color="grey"):
    donut = alt.Chart(source).mark_arc(innerRadius=innerRadius).encode(
        theta=alt.Theta("Value:Q"),
        color=alt.Color(f"{colorColumnName}:N", scale=alt.Scale(
            range=[fillColor, "whitesmoke"]), legend=None),
        tooltip=[f"{colorColumnName}:N", alt.Tooltip("Value:Q", title="Percentage", format=".1%")]
        ).properties(height=height, width=width)

    center_label = alt.Chart(pd.DataFrame({'text': [f"{stat:.1%}"]})
                             ).mark_text(fontSize=fontSize, fontWeight='lighter', font="Helvetica Neue", color=text_color).encode(
                                text='text:N')
        
    # Layer the donut and the label
    donut_chart = alt.layer(donut, center_label).properties(
        title=title).configure_title(fontSize=titleFontSize, anchor="middle")
    
    return donut_chart


def bar_chart(source, title_geo, XcolumnName, YcolumnName, xType=":N", yType=":Q", YtooltipFormat=",.0f", yFormat=",.0f", XlabelAngle=-50, 
                     fillColor="mediumseagreen", height=400, width=400, barWidth=60, title="Bar Chart", titleFontSize=17, distribution=True,
                     labelFontSize=10.5):
    
    tooltip_list = [XcolumnName, alt.Tooltip(YcolumnName, format=YtooltipFormat)]
    
    if distribution:
        source[f"% of {YcolumnName}"] = source[YcolumnName] / source[YcolumnName].sum()
        tooltip_list.append(alt.Tooltip(f"% of {YcolumnName}", format=".1%"))

    bar_chart = alt.Chart(source).mark_bar().encode(
        x=alt.X(XcolumnName + xType, sort=source[XcolumnName].tolist(),
                    axis=alt.Axis(labelAngle=XlabelAngle, labelFont="Helvetica Neue", labelFontWeight='normal', labelFontSize=labelFontSize, titleFont="Helvetica Neue")),
        y=alt.Y(YcolumnName + yType, axis=alt.Axis(labelFont="Helvetica Neue", labelFontWeight='normal', titleFont="Helvetica Neue", format=yFormat)),
        tooltip=tooltip_list).configure_mark(color=fillColor, width=barWidth
        ).properties(height=height, width=width, title=alt.Title(f"{title} | {title_geo}", anchor='middle', fontSize=titleFontSize)).interactive()
    
    return bar_chart
    

@st.cache_data
def load_unemployment_df():
    unemployment_url = "https://raw.githubusercontent.com/iansargent/Data-Exploration-Tool-in-Python/main/Data/Census/unemployment_rate_by_year.csv"
    response = requests.get(unemployment_url, verify=False)
    unemployment_df = pd.read_csv(io.StringIO(response.text))
    unemployment_df = split_name_col(unemployment_df)
    # Convert the 'year' column to an object type for proper plotting
    unemployment_df['year'] = unemployment_df['year'].astype(str)

    return unemployment_df


@st.cache_data
def load_commute_time_df():
    commute_time_url = "https://raw.githubusercontent.com/iansargent/Data-Exploration-Tool-in-Python/refs/heads/main/Data/Census/commute_time_by_year.csv"
    response = requests.get(commute_time_url, verify=False)
    commute_time_df = pd.read_csv(io.StringIO(response.text))
    commute_time_df = split_name_col(commute_time_df)
    # Convert the 'year' column to an object type for proper plotting
    commute_time_df['year'] = commute_time_df['year'].astype(str)

    return commute_time_df


def economic_snapshot_header():
    st.subheader("Economic Snapshot")
    st.markdown("***Data Source***: U.S. Census Bureau. (2023). DP03: Selected Economic Characteristics - " \
        "County Subdivisions, Vermont. 2019-2023 American Community Survey 5-Year Estimates. " \
        "Retrieved from https://data.census.gov/")


def unemployment_rate_ts_plot(filtered_unemployment_df, title_geo):
    """
    Create a time series plot of the unemployment rate for the selected geography.
    """
    
    unemployment_df = load_unemployment_df()

    # Filter data based on selection
    plot_df = filtered_unemployment_df.groupby("year").agg(Unemployment_Rate=("Unemployment_Rate", "mean")).reset_index()
    plot_df["Unemployment_Rate"] = plot_df["Unemployment_Rate"] / 100
    plot_df["Geography"] = title_geo
    
    statewide_avg_df = unemployment_df.groupby("year").agg(Unemployment_Rate=("Unemployment_Rate", "mean")).reset_index().assign(Geography="Statewide Average")
    statewide_avg_df["Unemployment_Rate"] = statewide_avg_df["Unemployment_Rate"] / 100

    # If we’re statewide only, skip adding the comparison line
    if title_geo != "Vermont (Statewide)":
        plot_df = pd.concat([plot_df, statewide_avg_df], ignore_index=True)

    if len(plot_df[plot_df["Geography"] != "Statewide Average"]) <= 1:
        st.warning("Not enough unemployment data available for the selected geography.")
        return None
    
    ymax = plot_df["Unemployment_Rate"].max() + 0.01
    ymin = plot_df["Unemployment_Rate"].min() - 0.01

    # Create a time series plot of the unemployment rate
    unemployment_ts = alt.Chart(plot_df).mark_line(point=True).encode(
        x=alt.X("year:O", title="Year", axis=alt.Axis(labelAngle=0, labelFontSize=15, labelFont="Helvetica Neue", labelFontWeight='normal', titleFont="Helvetica Neue")),
        y=alt.Y("Unemployment_Rate:Q", title="Unemployment Rate", 
                axis=alt.Axis(format="%", labelFont="Helvetica Neue", labelFontWeight='normal', titleFont="Helvetica Neue"),
                scale=alt.Scale(domain=(ymin, ymax))),
        color=alt.Color("Geography:O", title=None, scale=alt.Scale(
            domain=["Statewide Average", title_geo],
            range=["#83C299", "darkgreen"]),
            legend=alt.Legend(
                orient="bottom-left", 
                direction="horizontal", 
                offset=20,
                labelFont="Helvetica Neue")),
        tooltip=[alt.Tooltip("year", title="Year"), 
                 alt.Tooltip("Unemployment_Rate", title="Unemployment Rate", format=".1%"),
                 alt.Tooltip("Geography")]
    ).properties(height=500, title=f"Unemployment Rate Over Time | {title_geo}"
    ).configure_title(fontSize=19, anchor="middle").interactive()
    
    return unemployment_ts


def median_earnings_ts_plot(filtered_earnings_df, title_geo):
    """
    Create a time series plot of the unemployment rate for the selected geography.
    """

    plot_df = filtered_earnings_df.groupby(["year", "variable"]).agg(Median_Earnings=("estimate", "mean")).reset_index()
    
    variable_names = {"DP03_0092": "All Workers", "DP03_0093": "Male (FTYR)", "DP03_0094": "Female (FTYR)"}
    plot_df = plot_df.assign(Population = lambda df: df["variable"].map(variable_names))
    
    ymax = plot_df["Median_Earnings"].max() + 5000
    ymin = plot_df["Median_Earnings"].min() - 15000
    
    # Create a time series plot of the unemployment rate
    median_earnings_ts = alt.Chart(plot_df).mark_line(point=True).encode(
        x=alt.X("year:O", title="Year", axis=alt.Axis(labelAngle=0, labelFontSize=15, labelFont="Helvetica Neue", labelFontWeight='normal', titleFont="Helvetica Neue")),
        y=alt.Y("Median_Earnings:Q", title="Median Earnings", 
                axis=alt.Axis(format="$,.0f", labelFont="Helvetica Neue", labelFontWeight='normal', titleFont="Helvetica Neue"),
                scale=alt.Scale(domain=[ymin, ymax])
                ),
        color=alt.Color("Population:N", title=None, scale=alt.Scale(
            domain=["All Workers", "Male (FTYR)", "Female (FTYR)"],
            range=["forestgreen", "dodgerblue", "deeppink"]),
            legend=alt.Legend(
                orient="bottom-left", 
                direction="horizontal", 
                offset=20,
                labelFont="Helvetica Neue"))
    ).properties(height=475, title=alt.Title(f"Median Earnings | {title_geo}")
    ).configure_title(fontSize=19, anchor="middle").interactive()
    
    return median_earnings_ts


def avg_commute_time_ts_plot(filtered_commute_time_df, title_geo):
    """
    Create a time series plot of the unemployment rate for the selected geography.
    """
    commute_time_df = load_commute_time_df()
    
    plot_df = filtered_commute_time_df.groupby("year").agg(Average_Commute=("estimate", "mean")).reset_index()
    plot_df["Geography"] = title_geo
    
    statewide_avg_df = commute_time_df.groupby("year").agg(Average_Commute=("estimate", "mean")).reset_index().assign(Geography="Statewide Average")

    # If we’re statewide only, skip adding the comparison line
    if title_geo != "Vermont (Statewide)":
        plot_df = pd.concat([plot_df, statewide_avg_df], ignore_index=True)

    if len(plot_df[plot_df["Geography"] != "Statewide Average"]) <= 1:
        st.warning("Not enough commuting data available for the selected geography.")
        return None
    
    ymax = plot_df["Average_Commute"].max() + 5
    ymin = plot_df["Average_Commute"].min() - 5

    # Create a time series plot of the unemployment rate
    commute_time_ts = alt.Chart(plot_df).mark_line(point=True).encode(
        x=alt.X("year:O", title="Year", axis=alt.Axis(labelAngle=0, labelFontSize=15, labelFont="Helvetica Neue", labelFontWeight='normal', titleFont="Helvetica Neue")),
        y=alt.Y("Average_Commute:Q", title="Average Commute (Minutes)", 
                axis=alt.Axis(labelFont="Helvetica Neue", labelFontWeight='normal', titleFont="Helvetica Neue"),
                scale=alt.Scale(domain=(ymin, ymax))),
        color=alt.Color("Geography:O", title=None, scale=alt.Scale(
            domain=["Statewide Average", title_geo],
            range=["#83C299", "darkgreen"]),
            legend=alt.Legend(
                orient="top", 
                direction="horizontal", 
                offset=0,
                labelFont="Helvetica Neue")),
        tooltip=[alt.Tooltip("year", title="Year"), 
                 alt.Tooltip("Average_Commute:Q", title="Average Commute (Minutes)", format=".0f"),
                 alt.Tooltip("Geography")]
    ).properties(height=450, title=f"Average Commuting Time | {title_geo}"
    ).configure_title(fontSize=19, anchor="start", dx=68, offset=10).interactive()
    
    return commute_time_ts


def commute_habits_ts_plot(filtered_commute_habits_df, title_geo):
    """
    Create a time series plot of the unemployment rate for the selected geography.
    """
    filtered_commute_habits_df
    plot_df = filtered_commute_habits_df.groupby(["year", "variable"]).agg(Percentage=("estimate", "mean")).reset_index()
    
    variable_names = {"DP03_0019P": "Drove Alone", "DP03_0021P": "Public Transit", "DP03_0024P": "Work From Home"}
    plot_df = plot_df.assign(Commute_Type = lambda df: df["variable"].map(variable_names))
    plot_df["Percentage"] = plot_df["Percentage"] / 100
    
    # Pivot to calculate 'Other'
    pivot_df = plot_df.pivot(index="year", columns="Commute_Type", values="Percentage").fillna(0)
    pivot_df["Other"] = 1.0 - pivot_df.sum(axis=1)

    # Reformat back to long form
    other_df = pivot_df[["Other"]].reset_index().melt(id_vars="year", var_name="Commute_Type", value_name="Percentage")

    final_plot_df = pd.concat([plot_df[["year", "Commute_Type", "Percentage"]], other_df], ignore_index=True)
    
    # Create a time series plot of the unemployment rate
    commute_habits_ts = alt.Chart(final_plot_df).mark_line(point=True).encode(
        x=alt.X("year:O", title="Year", axis=alt.Axis(labelAngle=0, labelFontSize=15, labelFont="Helvetica Neue", labelFontWeight='normal', titleFont="Helvetica Neue")),
        y=alt.Y("Percentage:Q", title="Percentage of Workers (16+)", 
                axis=alt.Axis(format=".0%", labelFont="Helvetica Neue", labelFontWeight='normal', titleFont="Helvetica Neue")),
        color=alt.Color("Commute_Type:N", title=None, scale=alt.Scale(
            domain=["Drove Alone", "Other", "Work From Home", "Public Transit"],
            range=["tomato", "grey", "dodgerblue", "mediumseagreen"]),
            legend=alt.Legend(
                orient="top", 
                direction="horizontal", 
                offset=0,
                labelFont="Helvetica Neue")),
        tooltip=[alt.Tooltip("year", title="Year"), alt.Tooltip("Percentage", format=".1%"), alt.Tooltip("Commute_Type", title="Commute Type")]
    ).properties(height=450, title=alt.Title(f"How People Commute to Work | {title_geo}")
    ).configure_title(fontSize=19, anchor="start", dx=78, offset=10).interactive()
    
    return commute_habits_ts


# NOTE: The `st.metric` delta (^change) values are simply placeholders for now (not real data!)
def economic_snapshot(econ_dfs):    
    # Display the Category Header with Data Source
    economic_snapshot_header()
    # Define county and jurisdiction selections with select boxes
    county, jurisdiction = select_census_geography(econ_dfs[0])
    # Filter each dataset in "econ_dfs" to the geography needed for the snapshot 
    # Returns a LIST of filtered DataFrames
    filtered_econ_dfs = filter_census_geography(econ_dfs, county, jurisdiction)
    
    # Unpack each dataset from "filtered_econ_dfs" by index
    # TODO: This unpacking process could be more reliable with a dictionary
    filtered_gdf_2023 = filtered_econ_dfs[0]
    filtered_unemployment_df = filtered_econ_dfs[1]
    filtered_median_earnings_df = filtered_econ_dfs[2]
    filtered_commute_time_df = filtered_econ_dfs[3]
    filtered_commute_habits_df = filtered_econ_dfs[4]

    # Get the title of the geography for plotting
    title_geo = get_geography_title(county, jurisdiction)
    # Based on the system color theme, update the text color (only used in donut plots)
    text_color = get_text_color(key="economic_snapshot")

    # Calculate all stats needed for the snapshot (By economic category)
    # Employment
    unemployment_rate = filtered_gdf_2023['DP03_0009PE'].mean() / 100
    pct_employed = filtered_gdf_2023['DP03_0004PE'].mean()
    pct_in_labor_force = filtered_gdf_2023['DP03_0002PE'].mean()
    pct_female_in_labor_force = filtered_gdf_2023['DP03_0011PE'].mean()
    # Healthcare Coverage
    pct_no_hc_coverage = filtered_gdf_2023['DP03_0099PE'].mean()
    pct_no_hc_coverage_u19 = filtered_gdf_2023['DP03_0101PE'].mean()
    pct_public_hc_coverage = filtered_gdf_2023['DP03_0098PE'].mean() / 100
    pct_employed_no_hc_coverage = filtered_gdf_2023['DP03_0108PE'].mean()
    # Income
    income_per_capita = filtered_gdf_2023["DP03_0088E"].mean()
    median_family_income = filtered_gdf_2023["DP03_0086E"].mean()
    # Poverty
    pct_people_below_pov = filtered_gdf_2023["DP03_0128PE"].mean() / 100
    pct_families_below_pov = filtered_gdf_2023["DP03_0119PE"].mean() / 100


    # The EMPLOYMENT Section
    st.divider()
    st.subheader("Employment")
    # Set two columns (Left for metrics, right for line plot)
    metric_col, chart_col = st.columns([1, 4])
    
    # Display employment metrics
    metric_col.metric(
        label="**Unemployment Rate (2023)**", 
        value=f"{unemployment_rate * 100:.1f}%", 
        delta=f"{0.8}%", 
        delta_color='inverse')
    metric_col.metric(
        label="**Civilian Employment Rate**", 
        value=f"{pct_employed:.1f}%", 
        delta=f"{2}%")
    metric_col.metric(
        label="**In Labor Force**", 
        value=f"{pct_in_labor_force:.1f}%", 
        delta=f"{-3}%")
    metric_col.metric(
        label="**Females in Labor Force**", 
        value=f"{pct_female_in_labor_force:.1f}%", 
        delta=f"{10}%")
    
    # Define and display unemployment time series plot
    unemployment_chart = unemployment_rate_ts_plot(filtered_unemployment_df, title_geo)
    chart_col.altair_chart(unemployment_chart)
    metric_col.markdown("\2")


    # The HEALTH INSURANCE COVERAGE Section
    st.divider()
    st.subheader("Health Insurance Coverage")
    st.markdown("\2")
    
    # Set two columns (with a middle spacer) for donut chart on the left and metrics on the right
    h_col1, _, h_col2 = st.columns([10, 2, 10])
    
    # Define a DataFrame needed for the donut chart
    public_private_coverage_df = pd.DataFrame({
        "Coverage Type": ["Private Insurance", "Public Insurance"],
        "Value": [1 - pct_public_hc_coverage, pct_public_hc_coverage]})
    
    # Use the `donut_chart` function  to create a tailored chart using info from the dataframe above
    public_private_pie_chart = donut_chart(
        source=public_private_coverage_df, colorColumnName="Coverage Type", height=350, width=200, 
        innerRadius=130, fontSize=45, titleFontSize=18, fillColor="mediumseagreen", 
        title=f"Private Health Coverage | {title_geo}", stat=(1 - pct_public_hc_coverage), text_color=text_color)
    
    # Display the donut chart on the left
    h_col1.altair_chart(public_private_pie_chart)
    
    # On the right, display useful insurance metrics
    h_col2.metric(
        label="**No Health Coverage**", 
        value=f"{pct_no_hc_coverage:.1f}%", 
        delta=f"{0.5}%", 
        delta_color='inverse')
    h_col2.metric(
        label="**No Health Coverage (Age 0-19)**", 
        value=f"{pct_no_hc_coverage_u19:.1f}%", 
        delta=f"{-0.4}%", 
        delta_color='inverse')
    h_col2.metric(
        label="**Employed without Health Coverage (19-64)**", 
        value=f"{pct_employed_no_hc_coverage:.1f}%", 
        delta=f"{1.8}%", 
        delta_color='inverse')


    # The INCOME Section
    st.divider()
    st.subheader("Income")
    
    # Define 4 columns (with left spacer) to display important income metrics
    _, earn_metric_col1, earn_metric_col2, earn_metric_col3, earn_metric_col4 = st.columns([0.5, 1, 1, 1, 1])
    earn_metric_col1.metric(
        label="**Median Earnings** (All Workers)", 
        value=f"${filtered_gdf_2023['DP03_0092E'].mean():,.0f}", 
        delta=f"{12459:,.0f}")
    earn_metric_col2.metric(
        label="**Median Male Earnings** (FTYR)", 
        value=f"${filtered_gdf_2023['DP03_0093E'].mean():,.0f}", 
        delta=f"{2459:,.0f}")
    earn_metric_col3.metric(
        label="**Median Female Earnings** (FTYR)", 
        value=f"${filtered_gdf_2023['DP03_0094E'].mean():,.0f}", 
        delta=f"{1047:,.0f}")
    earn_metric_col4.metric(
        label="**Gender Wage Gap**", 
        value=f"${filtered_gdf_2023['DP03_0093E'].mean() - filtered_gdf_2023['DP03_0094E'].mean():,.0f}", 
        delta=f"{-749:,.0f}", delta_color='inverse')
    
    st.markdown("\2")
    
    # Display the median earnings time series plot directly below the metrics
    st.altair_chart(median_earnings_ts_plot(filtered_median_earnings_df, title_geo))

    # Define two columns for metrics on the left and a bar plot on the right
    income_col1, income_col2 = st.columns([2, 11])
    income_col1.markdown("\2")
    
    # On the left, display more useful income metrics
    income_col1.metric(
        label="Income Per Capita", 
        value=f"${income_per_capita:,.0f}", 
        delta=f"{5492:,.0f}")
    income_col1.markdown("\2")
    income_col1.metric(
        label="Median Family Income", 
        value=f"${median_family_income:,.0f}", 
        delta=f"{4204:,.0f}")
    
    # Define a DataFrame of family income distribution to use when plotting a bar chart
    family_income_df = pd.DataFrame({
        "Family Income": ["Under $10,000", "$10,000 - $14,999", "$15,000 - $24,999", "$25,000 - $34,999", "$35,000 - $49,999",
                        "$50,000 - $74,999", "$75,000 - $99,999", "$100,000 - $149,999", "$150,000 - $199,999", "$200,000 +"],
        "Estimated Families": [filtered_gdf_2023["DP03_0076E"].sum(), filtered_gdf_2023["DP03_0077E"].sum(), filtered_gdf_2023["DP03_0078E"].sum(), 
                  filtered_gdf_2023["DP03_0079E"].sum(), filtered_gdf_2023["DP03_0080E"].sum(), filtered_gdf_2023["DP03_0081E"].sum(), 
                  filtered_gdf_2023["DP03_0082E"].sum(), filtered_gdf_2023["DP03_0083E"].sum(), filtered_gdf_2023["DP03_0084E"].sum(), 
                  filtered_gdf_2023["DP03_0085E"].sum()]})
    
    # Use the `census_bar_chart` function to create a highly customizable bar chart
    family_income_dist_chart = bar_chart(
        source=family_income_df, title_geo=title_geo, XcolumnName="Family Income", xType=":N", yType=":Q",
        YcolumnName="Estimated Families", barWidth=75, titleFontSize=19, title="Family Income Distribution")

    # Display the bar chart on the right
    income_col2.altair_chart(family_income_dist_chart, use_container_width=True)


    # The POVERTY Section
    st.divider()
    st.subheader("Poverty")

    # Define two columns with two donut charts on the left and a barplot on the right
    pov_col1, pov_col2 = st.columns([2, 3])
    
    # Define a DataFrame of PEOPLE below the poverty level for plotting
    pov_people_df = pd.DataFrame({
        "Category": ["Below Poverty Level", "Over Poverty Level"],
        "Value": [pct_people_below_pov, 1 - pct_people_below_pov]})
    # Create a donut chart to show the % of people below the poverty level
    pov_people_pie_chart = donut_chart(
        source=pov_people_df, colorColumnName="Category", height=250, width=175, 
        innerRadius=85,fontSize=40, title=f"People Below Poverty Level | {title_geo}",
        stat=pct_people_below_pov, text_color=text_color)
    
    # Define a DataFrame of FAMILIES below the poverty level for plotting
    pov_families_df = pd.DataFrame({
        "Category": ["Below Poverty Level", "Over Poverty Level"],
        "Value": [pct_families_below_pov, 1 - pct_families_below_pov]})
    # Create a donut chart to show the % of families below the poverty level
    pov_families_pie_chart = donut_chart(
        source=pov_families_df, colorColumnName="Category", height=250, width=175, 
        innerRadius=85, fontSize=40, titleFontSize=14, fillColor="mediumseagreen", 
        title=f"Families Below Poverty Level | {title_geo}", stat=pct_families_below_pov, text_color=text_color)
    
    # Display the two donut charts
    pov_col1.markdown("\2") 
    pov_col1.altair_chart(pov_people_pie_chart)
    pov_col1.altair_chart(pov_families_pie_chart)

    # Define a DataFrame of poverty rates among different age groups for plotting
    poverty_by_age_dist = pd.DataFrame({
        "Age": ["Under 18 years", "18 - 64 years", "65+ years"],
        "Poverty Rate": [filtered_gdf_2023["DP03_0129PE"].mean(), filtered_gdf_2023["DP03_0134PE"].mean(), 
                        filtered_gdf_2023["DP03_0135PE"].mean()]})
    # Change the "Poverty Rate" columns from a percentage to a proportion
    poverty_by_age_dist["Poverty Rate"] = poverty_by_age_dist["Poverty Rate"] / 100
    # Create a highly customizable bar chart using the `census_bar_chart` function
    pov_by_age_chart = bar_chart(
        source=poverty_by_age_dist, title_geo=title_geo, XcolumnName="Age", YcolumnName="Poverty Rate",
        xType=":O", yType=":Q", yFormat=".0%", YtooltipFormat=".1%", barWidth=130, XlabelAngle=0, height=600, titleFontSize=19, 
        labelFontSize=13, title="Poverty Rate by Age Group", distribution=False)
    
    # Display the bar chart on the right
    pov_col2.altair_chart(pov_by_age_chart)
    

    # The WORK Section
    st.divider()
    st.subheader("Work")
    st.markdown("\2")
    
    # Define and display a time series plot of average commute time
    commute_time_ts = avg_commute_time_ts_plot(filtered_commute_time_df, title_geo)
    st.altair_chart(commute_time_ts)

    # Define and display a time series plot of commute methods
    commute_habits_ts = commute_habits_ts_plot(filtered_commute_habits_df, title_geo)
    st.altair_chart(commute_habits_ts)
