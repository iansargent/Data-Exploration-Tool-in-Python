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
def load_median_earnings_df():
    earnings_url = "https://raw.githubusercontent.com/iansargent/Data-Exploration-Tool-in-Python/refs/heads/main/Data/Census/median_earnings_by_year.csv"
    response = requests.get(earnings_url, verify=False)
    earnings_df = pd.read_csv(io.StringIO(response.text))
    earnings_df['variable'] = earnings_df['variable']
    earnings_df = split_name_col(earnings_df)
    # Convert the 'year' column to an object type for proper plotting
    earnings_df['year'] = earnings_df['year'].astype(str)

    return earnings_df


@st.cache_data
def load_commute_time_df():
    commute_time_url = "https://raw.githubusercontent.com/iansargent/Data-Exploration-Tool-in-Python/refs/heads/main/Data/Census/commute_time_by_year.csv"
    response = requests.get(commute_time_url, verify=False)
    commute_time_df = pd.read_csv(io.StringIO(response.text))
    commute_time_df = split_name_col(commute_time_df)
    # Convert the 'year' column to an object type for proper plotting
    commute_time_df['year'] = commute_time_df['year'].astype(str)

    return commute_time_df


@st.cache_data
def load_commute_habits_df():
    commute_habits_url = "https://raw.githubusercontent.com/iansargent/Data-Exploration-Tool-in-Python/refs/heads/main/Data/Census/commute_habits_by_year.csv"
    response = requests.get(commute_habits_url, verify=False)
    commute_habits_df = pd.read_csv(io.StringIO(response.text))
    commute_habits_df['variable'] = commute_habits_df['variable']
    commute_habits_df = split_name_col(commute_habits_df)
    # Convert the 'year' column to an object type for proper plotting
    commute_habits_df['year'] = commute_habits_df['year'].astype(str)

    return commute_habits_df


def unemployment_rate_ts_plot(unemployment_df, county, jurisdiction, title_geo):
    """
    Create a time series plot of the unemployment rate for the selected geography.
    """
    unemployment_df = unemployment_df.copy()
    unemployment_df["Unemployment_Rate"] = unemployment_df["Unemployment_Rate"] / 100
    
    # Filter data based on selection
    if county == "All Counties" and jurisdiction == "All Jurisdictions":
        filtered_unemployment_df = unemployment_df.copy()
        title_geo = "Statewide"
    else:
        filtered_unemployment_df = unemployment_df.copy()
        if county != "All Counties":
            filtered_unemployment_df = filtered_unemployment_df[filtered_unemployment_df["County"] == county]
        if jurisdiction != "All Jurisdictions":
            filtered_unemployment_df = filtered_unemployment_df[filtered_unemployment_df["Jurisdiction"] == jurisdiction]

    plot_df = filtered_unemployment_df.groupby("year").agg(Unemployment_Rate=("Unemployment_Rate", "mean")).reset_index()
    plot_df["Geography"] = title_geo
    statewide_avg_df = unemployment_df.groupby("year").agg(Unemployment_Rate=("Unemployment_Rate", "mean")).reset_index().assign(Geography="Statewide Average")

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


def median_earnings_ts_plot(earnings_df, county, jurisdiction, title_geo):
    """
    Create a time series plot of the unemployment rate for the selected geography.
    """
    earnings_df = earnings_df.copy()
    
    # Filter data based on selection
    if county == "All Counties" and jurisdiction == "All Jurisdictions":
        filtered_earnings_df = earnings_df.copy()
        title_geo = "Statewide"
    else:
        filtered_earnings_df = earnings_df.copy()
        if county != "All Counties":
            filtered_earnings_df = filtered_earnings_df[filtered_earnings_df["County"] == county]
        if jurisdiction != "All Jurisdictions":
            filtered_earnings_df = filtered_earnings_df[filtered_earnings_df["Jurisdiction"] == jurisdiction]

    plot_df = filtered_earnings_df.groupby(["year", "variable"]).agg(Median_Earnings=("estimate", "mean")).reset_index()
    
    variable_names = {
    "DP03_0092": "All Workers",
    "DP03_0093": "Male (FTYR)",
    "DP03_0094": "Female (FTYR)"}

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


def avg_commute_time_ts_plot(commute_time_df, county, jurisdiction, title_geo):
    """
    Create a time series plot of the unemployment rate for the selected geography.
    """
    commute_time_df = commute_time_df.copy()
    commute_time_df = commute_time_df.rename(columns={'estimate': 'Minutes'})
    commute_time_df["Minutes"] = commute_time_df["Minutes"]
    
    # Filter data based on selection
    if county == "All Counties" and jurisdiction == "All Jurisdictions":
        filtered_commute_time_df = commute_time_df.copy()
        title_geo = "Statewide"
    else:
        filtered_commute_time_df = commute_time_df.copy()
        if county != "All Counties":
            filtered_commute_time_df = filtered_commute_time_df[filtered_commute_time_df["County"] == county]
        if jurisdiction != "All Jurisdictions":
            filtered_commute_time_df = filtered_commute_time_df[filtered_commute_time_df["Jurisdiction"] == jurisdiction]

    plot_df = filtered_commute_time_df.groupby("year").agg(Average_Commute=("Minutes", "mean")).reset_index()
    plot_df["Geography"] = title_geo
    statewide_avg_df = commute_time_df.groupby("year").agg(Average_Commute=("Minutes", "mean")).reset_index().assign(Geography="Statewide Average")

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


def commute_habits_ts_plot(commute_habits_df, county, jurisdiction, title_geo):
    """
    Create a time series plot of the unemployment rate for the selected geography.
    """
    commute_habits_df = commute_habits_df.copy()
    
    # Filter data based on selection
    if county == "All Counties" and jurisdiction == "All Jurisdictions":
        filtered_commute_habits_df = commute_habits_df.copy()
        title_geo = "Statewide"
    else:
        filtered_commute_habits_df = commute_habits_df.copy()
        if county != "All Counties":
            filtered_commute_habits_df = filtered_commute_habits_df[filtered_commute_habits_df["County"] == county]
        if jurisdiction != "All Jurisdictions":
            filtered_commute_habits_df = filtered_commute_habits_df[filtered_commute_habits_df["Jurisdiction"] == jurisdiction]

    plot_df = filtered_commute_habits_df.groupby(["year", "variable"]).agg(Percentage=("estimate", "mean")).reset_index()
    
    variable_names = {"DP03_0019P": "Drove Alone", "DP03_0021P": "Public Transit", "DP03_0024P": "Work From Home"}

    plot_df = plot_df.assign(Commute_Type = lambda df: df["variable"].map(variable_names))
    
    plot_df["Percentage"] = plot_df["Percentage"] / 100
    
    ymax = plot_df["Percentage"].max() + 0.10
    ymin = 0 
    
    # Create a time series plot of the unemployment rate
    commute_habits_ts = alt.Chart(plot_df).mark_line(point=True).encode(
        x=alt.X("year:O", title="Year", axis=alt.Axis(labelAngle=0, labelFontSize=15, labelFont="Helvetica Neue", labelFontWeight='normal', titleFont="Helvetica Neue")),
        y=alt.Y("Percentage:Q", title="Percentage of Workers (16+)", 
                axis=alt.Axis(format=".0%", labelFont="Helvetica Neue", labelFontWeight='normal', titleFont="Helvetica Neue"),
                scale=alt.Scale(domain=[ymin, ymax])
                ),
        color=alt.Color("Commute_Type:N", title=None, scale=alt.Scale(
            domain=["Drove Alone", "Work From Home", "Public Transit"],
            range=["tomato", "dodgerblue", "mediumseagreen"]),
            legend=alt.Legend(
                orient="top", 
                direction="horizontal", 
                offset=0,
                labelFont="Helvetica Neue")),
        tooltip=[alt.Tooltip("year", title="Year"), alt.Tooltip("Percentage", format=".1%"), alt.Tooltip("Commute_Type", title="Commute Type")]
    ).properties(height=450, title=alt.Title(f"Commute Habits | {title_geo}")
    ).configure_title(fontSize=19, anchor="start", dx=78, offset=10).interactive()
    
    return commute_habits_ts


# NOTE: This function will get very VERY ugly before it gets refractored . . . just gotta live with it
# NOTE: st.metric delta (^change) values are simply placeholders for now (not real data)
# This has officially reached full ugly stage TODO: Refractor and make it less of a mess :)
def economic_snapshot(county, jurisdiction, economic_gdf_2023):    
    from streamlit_theme import st_theme
    theme_dict = st_theme(key="theme_econ_snapshot")
    if theme_dict is not None:
        theme = theme_dict["base"]
    else:
        theme = "light"  # or your fallback default
    text_color = "white" if theme == "dark" else "black"

    # Get the title of the geography for plotting
    title_geo = get_geography_title(county, jurisdiction)

    # Employment Section
    unemployment_df = load_unemployment_df()
    earnings_df = load_median_earnings_df()

    st.divider()
    st.subheader("Employment")
    metric_col, chart_col = st.columns([1, 4])
    with chart_col:
        unemployment_chart = unemployment_rate_ts_plot(unemployment_df, county, jurisdiction, title_geo)
        if unemployment_chart is None:
            return
        st.altair_chart(unemployment_chart)
    
    with metric_col:
        # Display the current unemployment rate
        unemployment_rate = economic_gdf_2023['DP03_0009PE'].mean() / 100
        pct_in_labor_force = economic_gdf_2023['DP03_0002PE'].mean()
        pct_employed = economic_gdf_2023['DP03_0004PE'].mean()
        pct_female_in_labor_force = economic_gdf_2023['DP03_0011PE'].mean()

        st.markdown("\2")
        st.metric(label="**Unemployment Rate (2023)**", value=f"{unemployment_rate * 100:.1f}%", delta=f"{0.8}%", delta_color='inverse')
        st.metric(label="**Civilian Employment Rate**", value=f"{pct_employed:.1f}%", delta=f"{2}%")
        st.metric(label="**In Labor Force**", value=f"{pct_in_labor_force:.1f}%", delta=f"{-3}%")
        st.metric(label="**Females in Labor Force**", value=f"{pct_female_in_labor_force:.1f}%", delta=f"{10}%")

    
    st.divider()
    st.subheader("Health Insurance Coverage")
    
    pct_no_hc_coverage = economic_gdf_2023['DP03_0099PE'].mean()
    pct_no_hc_coverage_u19 = economic_gdf_2023['DP03_0101PE'].mean()
    pct_public_hc_coverage = economic_gdf_2023['DP03_0098PE'].mean() / 100
    pct_employed_no_hc_coverage = economic_gdf_2023['DP03_0108PE'].mean()
    
    public_private_coverage_df = pd.DataFrame({
        "Coverage Type": ["_Private Insurance", "Public Insurance"],
        "Value": [1 - pct_public_hc_coverage, pct_public_hc_coverage]})
    
    donut = alt.Chart(public_private_coverage_df).mark_arc(innerRadius=130).encode(
        theta=alt.Theta("Value:Q"),
        color=alt.Color("Coverage Type:N", scale=alt.Scale(
            domain=["Public Insurance", "_Private Insurance"],
            range=["mediumseagreen", "whitesmoke"]), legend=None),
        tooltip=["Coverage Type:N", alt.Tooltip("Value:Q", title="Percentage", format=".1%")]
        ).properties(height=350, width=200)

    center_label = alt.Chart(pd.DataFrame({'text': [f"{pct_public_hc_coverage:.1%}"]})
                             ).mark_text(fontSize=45, fontWeight='lighter', font="Helvetica Neue", color=text_color).encode(
                                text='text:N')
        
    # Layer the donut and the label
    public_private_pie_chart = alt.layer(donut, center_label).properties(
        title=f"Public Health Coverage | {title_geo}").configure_title(fontSize=18, anchor="middle")
    
    h_col1, _, h_col2 = st.columns([10, 2, 10])
    h_col1.markdown("\2")
    h_col1.altair_chart(public_private_pie_chart)
    h_col2.markdown("\2")
    h_col2.metric(label="**No Health Coverage**", value=f"{pct_no_hc_coverage:.1f}%", delta=f"{0.5}%", delta_color='inverse')
    h_col2.metric(label="**No Health Coverage (Age 0-19)**", 
                  value=f"{pct_no_hc_coverage_u19:.1f}%", delta=f"{-0.4}%", delta_color='inverse')
    h_col2.metric(label="**Employed without Health Coverage (19-64)**", 
                  value=f"{pct_employed_no_hc_coverage:.1f}%", delta=f"{1.8}%", delta_color='inverse')


    st.divider()
    st.subheader("Income")
    
    _, earn_metric_col1, earn_metric_col2, earn_metric_col3, earn_metric_col4 = st.columns([0.5, 1, 1, 1, 1])
    earn_metric_col1.metric(label="**Median Earnings** (All Workers)", 
                           value=f"${economic_gdf_2023['DP03_0092E'].mean():,.0f}", delta=f"{12459:,.0f}")
    earn_metric_col2.metric(label="**Median Male Earnings** (FTYR)", 
                           value=f"${economic_gdf_2023['DP03_0093E'].mean():,.0f}", delta=f"{2459:,.0f}")
    earn_metric_col3.metric(label="**Median Female Earnings** (FTYR)", 
                           value=f"${economic_gdf_2023['DP03_0094E'].mean():,.0f}", delta=f"{1047:,.0f}")
    earn_metric_col4.metric(label="**Gender Wage Gap**", 
                            value=f"${economic_gdf_2023['DP03_0093E'].mean() - economic_gdf_2023['DP03_0094E'].mean():,.0f}", 
                            delta=f"{-749:,.0f}", delta_color='inverse')
    st.markdown("\2")
    st.altair_chart(median_earnings_ts_plot(earnings_df, county, jurisdiction, title_geo))

    income_col1, income_col2 = st.columns([2, 11])

    income_per_capita = economic_gdf_2023["DP03_0088E"].mean()
    median_family_income = economic_gdf_2023["DP03_0086E"].mean()
    income_col1.markdown("\2")
    income_col1.metric(label="Income Per Capita", value=f"${income_per_capita:,.0f}", delta=f"{5492:,.0f}")
    income_col1.markdown("\2")
    income_col1.metric(label="Median Family Income", value=f"${median_family_income:,.0f}", delta=f"{4204:,.0f}")
    
    family_income_dist = pd.DataFrame({
        "Income Bin": ["Under $10,000", "$10,000 - $14,999", "$15,000 - $24,999", "$25,000 - $34,999", "$35,000 - $49,999",
                        "$50,000 - $74,999", "$75,000 - $99,999", "$100,000 - $149,999", "$150,000 - $199,999", "$200,000 +"],
        "Estimated Families": [economic_gdf_2023["DP03_0076E"].sum(), economic_gdf_2023["DP03_0077E"].sum(), economic_gdf_2023["DP03_0078E"].sum(), 
                  economic_gdf_2023["DP03_0079E"].sum(), economic_gdf_2023["DP03_0080E"].sum(), economic_gdf_2023["DP03_0081E"].sum(), 
                  economic_gdf_2023["DP03_0082E"].sum(), economic_gdf_2023["DP03_0083E"].sum(), economic_gdf_2023["DP03_0084E"].sum(), 
                  economic_gdf_2023["DP03_0085E"].sum()]
    })

    family_income_dist["Estimated % of Families"] = family_income_dist["Estimated Families"] / family_income_dist["Estimated Families"].sum()

    family_income_dist_chart = alt.Chart(family_income_dist).mark_bar().encode(
            x=alt.X("Income Bin:N", title="Family Income", sort=family_income_dist['Income Bin'].tolist(),
                    axis=alt.Axis(labelAngle=-50, labelFont="Helvetica Neue", labelFontWeight='normal', labelFontSize=10.5, titleFont="Helvetica Neue")),
            y=alt.Y("Estimated Families:Q", axis=alt.Axis(labelFont="Helvetica Neue", labelFontWeight='normal', titleFont="Helvetica Neue")),
            tooltip=["Income Bin", alt.Tooltip("Estimated Families", format=",.0f"), alt.Tooltip("Estimated % of Families", format=".1%")]
        ).configure_mark(color="mediumseagreen", width=75
        ).properties(height=400, title=alt.Title(f"Family Income Distribution | {title_geo}", anchor='middle', fontSize=19))
    
    # Disply the chart
    income_col2.altair_chart(family_income_dist_chart, use_container_width=True)

    st.divider()
    st.subheader("Poverty")

    pov_col1, pov_col2 = st.columns([2, 3])
    
    pov_col1.markdown("\2")    
    pct_people_below_pov = economic_gdf_2023["DP03_0128PE"].mean() / 100
    
    
    pov_people_df = pd.DataFrame({
        "Category": ["Below Poverty Level", "Over Poverty Level"],
        "Percentage": [pct_people_below_pov, 1 - pct_people_below_pov]})
    
    pov_people_donut = alt.Chart(pov_people_df).mark_arc(innerRadius=85).encode(
        theta=alt.Theta("Percentage:Q"),
        color=alt.Color("Category:N", scale=alt.Scale(
            domain=["Below Poverty Level", "Over Poverty Level"],
            range=["mediumseagreen", "whitesmoke"]), legend=None),
        tooltip=["Category:N", alt.Tooltip("Percentage:Q", title="Percentage", format=".1%")]
        ).properties(height=250, width=175)

    pov_people_center_label = alt.Chart(pd.DataFrame({'text': [f"{pct_people_below_pov:.1%}"]})
                             ).mark_text(fontSize=45, fontWeight='lighter', font="Helvetica Neue", color=text_color).encode(
                                text='text:N')
        
    # Layer the donut and the label
    pov_people_pie_chart = alt.layer(pov_people_donut, pov_people_center_label).properties(
        title=f"People Below Poverty Level | {title_geo}").configure_title(fontSize=14, anchor="middle")
    
    pov_col1.altair_chart(pov_people_pie_chart)

    
    pct_families_below_pov = economic_gdf_2023["DP03_0119PE"].mean() / 100
    
    pov_families_df = pd.DataFrame({
        "Category": ["Below Poverty Level", "Over Poverty Level"],
        "Percentage": [pct_families_below_pov, 1 - pct_families_below_pov]})
    
    pov_families_donut = alt.Chart(pov_families_df).mark_arc(innerRadius=85).encode(
        theta=alt.Theta("Percentage:Q"),
        color=alt.Color("Category:N", scale=alt.Scale(
            domain=["Below Poverty Level", "Over Poverty Level"],
            range=["mediumseagreen", "whitesmoke"]), legend=None),
        tooltip=["Category:N", alt.Tooltip("Percentage:Q", title="Percentage", format=".1%")]
        ).properties(height=250, width=175)

    pov_families_center_label = alt.Chart(pd.DataFrame({'text': [f"{pct_families_below_pov:.1%}"]})
                             ).mark_text(fontSize=45, fontWeight='lighter', font="Helvetica Neue", color=text_color).encode(
                                text='text:N')
        
    # Layer the donut and the label
    pov_families_pie_chart = alt.layer(pov_families_donut, pov_families_center_label).properties(
        title=f"Families Below Poverty Level | {title_geo}").configure_title(fontSize=14, anchor="middle")
    
    pov_col1.altair_chart(pov_families_pie_chart)


    poverty_by_age_dist = pd.DataFrame({
        "Age": ["Under 18 years", "18 - 64 years", "65+ years"],
        "Poverty Rate": [economic_gdf_2023["DP03_0129PE"].mean(), economic_gdf_2023["DP03_0134PE"].mean(), 
                                         economic_gdf_2023["DP03_0135PE"].mean()]
    })

    poverty_by_age_dist["Poverty Rate"] = poverty_by_age_dist["Poverty Rate"] / 100

    age_chart_ymax = poverty_by_age_dist["Poverty Rate"].max() + 0.03

    pov_by_age_chart = alt.Chart(poverty_by_age_dist).mark_bar(width=130).encode(
            x=alt.X("Age:N", title="Age Group", sort=poverty_by_age_dist['Age'].tolist(),
                    axis=alt.Axis(
                        labelAngle=0, 
                        labelFont="Helvetica Neue", 
                        labelFontWeight='normal', 
                        labelFontSize=14, 
                        titleFont="Helvetica Neue")),
            y=alt.Y("Poverty Rate:Q", 
                    axis=alt.Axis(labelFont="Helvetica Neue", 
                                  labelFontWeight='normal', 
                                  titleFont="Helvetica Neue", 
                                  format=".0%"),
                    scale=alt.Scale(domain=(0, age_chart_ymax))),
            color=alt.Color("Age:O", legend=None, 
                        scale=alt.Scale(
                            domain=poverty_by_age_dist['Age'].tolist(), 
                            range=["lightgreen", "mediumseagreen", "darkgreen"]))
        ).configure_mark(width=75).properties(height=600, title=alt.Title(f"Poverty Rate by Age Group | {title_geo}", anchor="middle", fontSize=19))
    
    pov_col2.altair_chart(pov_by_age_chart)
    
    
    st.divider()


    st.subheader("Work")
    st.markdown("\2")
    commute_time_df = load_commute_time_df()
    commute_time_ts = avg_commute_time_ts_plot(commute_time_df, county, jurisdiction, title_geo)

    st.altair_chart(commute_time_ts)

    commute_habits_df = load_commute_habits_df()
    commute_habits_ts = commute_habits_ts_plot(commute_habits_df, county, jurisdiction, title_geo)
    st.altair_chart(commute_habits_ts)
