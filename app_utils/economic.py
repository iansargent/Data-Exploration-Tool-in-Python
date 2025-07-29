"""
Open Research Community Accelorator
Vermont Data App

Economic Utility Functions
"""

import streamlit as st
import pandas as pd
import altair as alt
from streamlit_extras.metric_cards import style_metric_cards 
from app_utils.census import get_geography_title, split_name_col
import requests
import io


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


def unemployment_rate_ts_plot(unemployment_df, county, jurisdiction, title_geo):
    """
    Create a time series plot of the unemployment rate for the selected geography 
    using a time slider to select the year range.
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
        x=alt.X("year:O", title="Year", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("Unemployment_Rate:Q", title="Unemployment Rate", 
                axis=alt.Axis(format="%"),
                scale=alt.Scale(domain=(ymin, ymax))),
        color=alt.Color("Geography:O", title=None, scale=alt.Scale(
            domain=["Statewide Average", title_geo],
            range=["#83C299", "darkgreen"]),
            legend=alt.Legend(
                orient="bottom-left", 
                direction="horizontal", 
                offset=20)),
        tooltip=[alt.Tooltip("year", title="Year"), 
                 alt.Tooltip("Unemployment_Rate", title="Unemployment Rate", format=".1%"),
                 alt.Tooltip("Geography")]
    ).properties(height=500, title=f"Unemployment Rate Over Time | {title_geo}"
    ).configure_title(fontSize=19, anchor="middle").interactive()
    
    return unemployment_ts


def median_earnings_ts_plot(earnings_df, county, jurisdiction, title_geo):
    """
    Create a time series plot of the unemployment rate for the selected geography 
    using a time slider to select the year range.
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
    "DP03_0092": "Earnings for Workers",
    "DP03_0093": "Male Earnings (FTYR)",
    "DP03_0094": "Female Earnings (FTYR)"}

    plot_df = plot_df.assign(var_name = lambda df: df["variable"].map(variable_names))
    
    ymax = plot_df["Median_Earnings"].max() + 5000
    ymin = plot_df["Median_Earnings"].min() - 15000
    
    # Create a time series plot of the unemployment rate
    median_earnings_ts = alt.Chart(plot_df).mark_line(point=True).encode(
        x=alt.X("year:O", title="Year", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("Median_Earnings:Q", title="Median Earnings", 
                axis=alt.Axis(format="$,.0f"),
                scale=alt.Scale(domain=[ymin, ymax])
                ),
        color=alt.Color("var_name:N", title=None, scale=alt.Scale(
            domain=["Earnings for Workers", "Male Earnings (FTYR)", "Female Earnings (FTYR)"],
            range=["forestgreen", "dodgerblue", "deeppink"]),
            legend=alt.Legend(
                orient="bottom-left", 
                direction="horizontal", 
                offset=20))
    ).properties(height=475, title=f"Median Earnings Over Time | {title_geo}"
    ).configure_title(fontSize=19, anchor="middle").interactive()
    
    return median_earnings_ts


def economic_snapshot(county, jurisdiction, economic_gdf_2023):    
    from streamlit_theme import st_theme
    theme = st_theme()["base"]

    # Get the title of the geography for plotting
    title_geo = get_geography_title(county, jurisdiction)

    st.markdown(f"##### Report for {title_geo}")

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

        st.markdown("\1")
        st.metric(label="**Unemployment Rate (2023)**", value=f"{unemployment_rate * 100:.1f}%", delta=f"{0.8}%")
        st.metric(label="**Civilian Employment Rate**", value=f"{pct_employed:.1f}%", delta=f"{2}%")
        st.metric(label="**In Labor Force**", value=f"{pct_in_labor_force:.1f}%", delta=f"{-3}%")
        st.metric(label="**Females in Labor Force**", value=f"{pct_female_in_labor_force:.1f}%", delta=f"{10}%")

    
    st.divider()
    st.subheader("Health Insurance Coverage")
    
    pct_no_hc_coverage = economic_gdf_2023['DP03_0099PE'].mean()
    pct_no_hc_coverage_u19 = economic_gdf_2023['DP03_0101PE'].mean()
    pct_public_hc_coverage = economic_gdf_2023['DP03_0098PE'].mean()
    pct_employed_no_hc_coverage = economic_gdf_2023['DP03_0108PE'].mean()
    
    public_private_coverage_df = pd.DataFrame({
        "Coverage Type": ["_Private Insurance", "Public Insurance"],
        "Value": [100 - pct_public_hc_coverage, pct_public_hc_coverage]})

    is_dark_mode = st.get_option("theme.base") == "dark"
    text_color = "white" if is_dark_mode else "black"
    
    donut = alt.Chart(public_private_coverage_df).mark_arc(innerRadius=130).encode(
        theta=alt.Theta("Value:Q"),
        color=alt.Color("Coverage Type:N", scale=alt.Scale(
            domain=["Public Insurance", "_Private Insurance"],
            range=["mediumseagreen", "whitesmoke"]), legend=None)
        ).properties(height=350, width=200)
    
    if theme == "dark":
        text_color = "white"
    else:
        text_color = "black"

    center_label = alt.Chart(pd.DataFrame({'text': [f"{pct_public_hc_coverage:.1f}%"]})
                             ).mark_text(fontSize=45, fontWeight='lighter', font="Helvetica Neue", color=text_color).encode(
                                text='text:N')
        
    # Layer the donut and the label
    public_private_pie_chart = alt.layer(donut, center_label).properties(
        title=f"Public Health Coverage | {title_geo}").configure_title(fontSize=18, anchor="middle")
    
    h_col1, _, h_col2 = st.columns([10, 1, 10])
    h_col1.markdown("\2")
    h_col1.altair_chart(public_private_pie_chart)
    h_col2.markdown("\2")
    h_col2.metric(label="**No Health Coverage**", value=f"{pct_no_hc_coverage:.1f}%", delta=f"{0.5}%")
    h_col2.metric(label="**No Health Coverage (Age 0-19)**", 
                  value=f"{pct_no_hc_coverage_u19:.1f}%", delta=f"{0.5}%")
    h_col2.metric(label="**Employed without Health Coverage (19-64)**", 
                  value=f"{pct_employed_no_hc_coverage:.1f}%", delta=f"{0.5}%")


    st.markdown("---")
    st.subheader("Income")
    
    earn_metric_col1, earn_metric_col2, earn_metric_col3, earn_metric_col4 = st.columns(4)
    earn_metric_col1.metric(label="**Median Earnings** (All Workers)", 
                           value=f"${economic_gdf_2023['DP03_0092E'].mean():,.0f}", delta=f"{12459:,.0f}")
    earn_metric_col2.metric(label="**Median Male Earnings** (FTYR)", 
                           value=f"${economic_gdf_2023['DP03_0093E'].mean():,.0f}", delta=f"{2459:,.0f}")
    earn_metric_col3.metric(label="**Median Female Earnings** (FTYR)", 
                           value=f"${economic_gdf_2023['DP03_0094E'].mean():,.0f}", delta=f"{1047:,.0f}")
    earn_metric_col4.metric(label="**Gender Wage Gap**", 
                           value=f"${economic_gdf_2023['DP03_0093E'].mean() - economic_gdf_2023['DP03_0094E'].mean():,.0f}", delta=f"{-749:,.0f}")
    st.markdown("\2")
    st.altair_chart(median_earnings_ts_plot(earnings_df, county, jurisdiction, title_geo))

    _, income_col1, income_col2 = st.columns([2, 4, 3])

    income_per_capita = economic_gdf_2023["DP03_0088E"].mean()
    income_col1.metric(label="Income Per Capita", value=f"${income_per_capita:,.0f}", delta=f"{5492:,.0f}")
    income_col1.markdown("\2")

    median_fam_income = economic_gdf_2023["DP03_0086E"].mean()
    income_col1.metric(label="Median Family Income", value=f"${median_fam_income:,.0f}", delta=f"{4204:,.0f}")
    
    
    income_col2.markdown("##### % Families Making Less Than $35,000 (Donut Chart on Right)")
    income_col2.write("DP03_0076PE + DP03_0077PE + DP03_0078PE + DP03_0079PE")

    income_col2.markdown("##### % Families Making More Than $200,000 (Donut Chart on Right)")
    income_col2.write("DP03_0085PE")

    st.divider()
    st.subheader("Poverty")

    st.markdown("##### % Families Below the Poverty Level Within Last Year")
    st.write("DP03_0119PE")

    st.markdown("##### % (Married with Kids) Below the Poverty Level Within Last Year")
    st.write("DP03_0123PE")

    st.markdown("##### % (Single Mother with Kids) Below the Poverty Level Within Last Year")
    st.write("DP03_0126PE")

    st.markdown("##### People Below Poverty Level (Under 18)")
    st.write("DP03_0129PE")

    st.markdown("##### People Below Poverty Level (Under 18)")
    st.write("DP03_0133PE")
    st.markdown("---")


    st.subheader("Work")
    
    st.markdown("##### Average Commuting Time")
    st.write("DP03_0025E")
    
    st.markdown("##### Commute via Public Transit")
    st.write("DP03_0021E")

    st.markdown("##### Work from Home")
    st.write("DP03_0024E")

    st.markdown("---")

    # style_metric_cards(
    #     background_color="whitesmoke",
    #     border_left_color="mediumseagreen",
    #     box_shadow=True,
    #     border_size_px=0.5
    # )
